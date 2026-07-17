#!/usr/bin/env python3
"""Create a full, private quality-review inventory for the live Steam text.

The scanner reads every text coordinate in the Korean JP route and compares it
with the same coordinate in the PC EN/SC/TC routes.  It writes source-bearing
review rows only below ``tmp`` and a source-free summary beside them.  It does
not rebuild or modify a game resource.

Switch translation output is deliberately not an input to this audit.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp"
DEFAULT_GAME_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "translation_quality_audit_v1" / "run_001"

LZ4_PATH = REPO / "tools" / "nobu16_lz4.py"
MESSAGE_PATH = REPO / "tools" / "nobu16_msg_table.py"
MSGGAME_PATH = REPO / "workstreams" / "msggame" / "msggame_format.py"
STRDATA_PATH = REPO / "workstreams" / "strdata" / "strdata_format.py"

RUNTIME_TOKEN_RE = re.compile(r"\[([a-z]+\d+)\]")
PRINTF_TOKEN_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESCAPE_TAG_RE = re.compile(r"\x1bC[A-Za-z]|<ESC>C[A-Za-z]")
# U+30FB (・) is used as a Korean list separator in this patch; do not treat
# that punctuation as unfinished Japanese text.
KANA_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f]")
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]")
LATIN_RE = re.compile(r"[A-Za-z]")
PLACEHOLDER_RE = re.compile(r"(?:\?{3,}|TODO|TRANSLATE|NULL)", re.IGNORECASE)
SPACE_BEFORE_PUNCT_RE = re.compile(r"\s+[,.!?:;\)\]\}]")
MULTI_SPACE_RE = re.compile(r" {2,}")


class AuditError(ValueError):
    pass


@dataclass(frozen=True)
class ResourceSpec:
    name: str
    relative: str
    parser: str
    source_languages: tuple[str, ...]


RESOURCE_SPECS = (
    ResourceSpec("ev_strdata", "MSG/JP/ev_strdata.bin", "common", ("SC", "TC")),
    ResourceSpec("base_msggame", "MSG/JP/msggame.bin", "msggame", ("SC", "TC")),
    ResourceSpec("strdata", "MSG/JP/strdata.bin", "strdata", ("SC", "TC")),
    ResourceSpec("msgbre", "MSG_PK/JP/msgbre.bin", "common", ("EN", "SC", "TC")),
    ResourceSpec("msgdata", "MSG_PK/JP/msgdata.bin", "common", ("EN", "SC", "TC")),
    ResourceSpec("msgev", "MSG_PK/JP/msgev.bin", "common", ("EN", "SC", "TC")),
    ResourceSpec("pk_msggame", "MSG_PK/JP/msggame.bin", "msggame", ("EN", "SC", "TC")),
    ResourceSpec("msgire", "MSG_PK/JP/msgire.bin", "common", ("EN", "SC", "TC")),
    ResourceSpec("msgstf", "MSG_PK/JP/msgstf.bin", "common", ("EN", "SC", "TC")),
    ResourceSpec("msgui", "MSG_PK/JP/msgui.bin", "common", ("EN", "SC", "TC")),
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


LZ4 = load_module("translation_quality_lz4", LZ4_PATH)
MESSAGE = load_module("translation_quality_message", MESSAGE_PATH)
MSGGAME = load_module("translation_quality_msggame", MSGGAME_PATH)
STRDATA = load_module("translation_quality_strdata", STRDATA_PATH)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def safe_under(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root_resolved = root.resolve(strict=False)
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise AuditError(f"{label} must remain below {root_resolved}: {resolved}")
    return resolved


def atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def language_relative(relative: str, language: str) -> Path:
    parts = list(Path(relative).parts)
    try:
        index = parts.index("JP")
    except ValueError as exc:
        raise AuditError(f"resource path has no JP language component: {relative}") from exc
    parts[index] = language
    return Path(*parts)


def parse_common(path: Path) -> dict[str, str]:
    _header, raw = LZ4.decompress_wrapper(path.read_bytes())
    table = MESSAGE.parse_message_table(raw)
    return {str(entry_id): text for entry_id, text in enumerate(table.texts)}


def parse_msggame(path: Path) -> dict[str, str]:
    archive = MSGGAME.parse_packed_msggame(path.read_bytes()).archive
    return {
        f"{literal.block_id}:{literal.record_id}:{literal.literal_id}": literal.text
        for literal in MSGGAME.iter_literals(archive)
    }


def parse_strdata(path: Path) -> dict[str, str]:
    _header, raw = LZ4.decompress_wrapper(path.read_bytes())
    archive = STRDATA.parse_raw_strdata(raw)
    return {
        f"{block_id}:{slot_id}": text
        for (block_id, slot_id), text in STRDATA.coordinate_texts(archive).items()
    }


PARSERS: dict[str, Callable[[Path], dict[str, str]]] = {
    "common": parse_common,
    "msggame": parse_msggame,
    "strdata": parse_strdata,
}


def visible_text(text: str) -> str:
    value = ESCAPE_TAG_RE.sub("", text)
    value = RUNTIME_TOKEN_RE.sub("", value)
    value = PRINTF_TOKEN_RE.sub("", value)
    return "".join(character for character in value if character.isprintable()).strip()


def protected_signature(text: str) -> dict[str, tuple[str, ...]]:
    return {
        "runtime": tuple(RUNTIME_TOKEN_RE.findall(text)),
        "printf": tuple(PRINTF_TOKEN_RE.findall(text)),
        "escape": tuple(ESCAPE_TAG_RE.findall(text)),
    }


def is_meaningful(text: str) -> bool:
    return bool(visible_text(text))


def stable_source_tokens(sources: dict[str, str], key: str) -> tuple[str, ...] | None:
    values = {protected_signature(text)[key] for text in sources.values()}
    values.discard(())
    if len(values) == 1:
        return next(iter(values))
    return None


def quality_flags(ko: str, sources: dict[str, str]) -> list[str]:
    """Return conservative, review-worthy flags; none alone is an automatic rewrite."""
    flags: list[str] = []
    visible = visible_text(ko)
    source_visible = [visible_text(source) for source in sources.values()]
    source_nonempty = [text for text in source_visible if text]
    has_hangul = bool(HANGUL_RE.search(visible))
    has_foreign = bool(KANA_RE.search(visible) or HAN_RE.search(visible) or LATIN_RE.search(visible))

    if KANA_RE.search(visible):
        flags.append("untranslated_kana")
    if source_nonempty and visible and not has_hangul and has_foreign:
        flags.append("non_korean_visible_text")
    if PLACEHOLDER_RE.search(visible):
        flags.append("placeholder_or_garbled_text")
    if MULTI_SPACE_RE.search(ko):
        flags.append("repeated_ascii_space")
    if SPACE_BEFORE_PUNCT_RE.search(ko):
        flags.append("space_before_punctuation")

    target_signature = protected_signature(ko)
    for key, flag in (("runtime", "runtime_token_mismatch"), ("printf", "printf_token_mismatch")):
        expected = stable_source_tokens(sources, key)
        if expected is not None and target_signature[key] != expected:
            flags.append(flag)

    # A long localized source paired with a one-character Korean value is often
    # truncation.  It remains a manual-review candidate because UI controls may
    # legitimately be short.
    if source_nonempty and len(visible) <= 1 and max(map(len, source_nonempty)) >= 18:
        flags.append("possible_truncation")
    return flags


def resource_rows(game_root: Path, spec: ResourceSpec) -> tuple[dict[str, str], dict[str, dict[str, str]], dict[str, Any]]:
    parser = PARSERS[spec.parser]
    target_path = game_root / Path(spec.relative)
    if not target_path.is_file():
        raise AuditError(f"Korean target is absent: {target_path}")
    target = parser(target_path)
    sources: dict[str, dict[str, str]] = {}
    source_specs: dict[str, dict[str, Any]] = {}
    for language in spec.source_languages:
        source_path = game_root / language_relative(spec.relative, language)
        if not source_path.is_file():
            raise AuditError(f"parallel {language} source is absent: {source_path}")
        parsed = parser(source_path)
        sources[language] = parsed
        source_specs[language] = {
            "relative_path": str(language_relative(spec.relative, language)).replace("\\", "/"),
            "size": source_path.stat().st_size,
            "sha256": sha256_file(source_path),
            "coordinate_count": len(parsed),
            "overlap_coordinate_count": len(set(parsed).intersection(target)),
        }
    target_spec = {
        "relative_path": spec.relative,
        "size": target_path.stat().st_size,
        "sha256": sha256_file(target_path),
    }
    return target, sources, {"target": target_spec, "sources": source_specs}


def audit(game_root: Path, output_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    output_root = safe_under(output_root, TMP_ROOT, "output root")
    if output_root.exists():
        raise AuditError(f"refusing to overwrite an existing audit run: {output_root}")

    private_rows: list[dict[str, Any]] = []
    resource_summary: dict[str, dict[str, Any]] = {}
    flag_counts: Counter[str] = Counter()
    total_coordinates = 0
    nonempty_coordinates = 0

    for spec in RESOURCE_SPECS:
        target, sources, file_specs = resource_rows(game_root, spec)
        coordinate_count = len(target)
        meaningful_count = 0
        candidate_count = 0
        per_resource_flags: Counter[str] = Counter()
        for coordinate in sorted(target, key=lambda value: tuple(int(part) for part in value.split(":"))):
            ko = target[coordinate]
            source_texts = {
                language: rows[coordinate]
                for language, rows in sources.items()
                if coordinate in rows
            }
            if is_meaningful(ko):
                meaningful_count += 1
                nonempty_coordinates += 1
            flags = quality_flags(ko, source_texts)
            if flags:
                candidate_count += 1
                flag_counts.update(flags)
                per_resource_flags.update(flags)
                private_rows.append(
                    {
                        "resource": spec.name,
                        "coordinate": coordinate,
                        "flags": flags,
                        "ko": ko,
                        "ko_utf16le_sha256": sha256_text(ko),
                        "sources": source_texts,
                    }
                )
        total_coordinates += coordinate_count
        resource_summary[spec.name] = {
            "relative_path": spec.relative,
            "parser": spec.parser,
            "coordinate_count": coordinate_count,
            "meaningful_korean_coordinate_count": meaningful_count,
            "review_candidate_count": candidate_count,
            "flag_counts": dict(sorted(per_resource_flags.items())),
            "file_specs": file_specs,
        }

    output_root.mkdir(parents=True, exist_ok=False)
    private_path = output_root / "private_review_candidates.jsonl"
    private_payload = "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
        for row in private_rows
    )
    atomic_write(private_path, private_payload)
    summary = {
        "schema": "nobu16.kr.translation-quality-audit.v1",
        "scope": "Steam PC JP Korean route compared only with PC EN/SC/TC parallel resources",
        "switch_korean_translation_used": False,
        "game_root": str(game_root),
        "resource_count": len(RESOURCE_SPECS),
        "coordinate_count": total_coordinates,
        "meaningful_korean_coordinate_count": nonempty_coordinates,
        "review_candidate_count": len(private_rows),
        "flag_counts": dict(sorted(flag_counts.items())),
        "resources": resource_summary,
        "private_candidate_path": str(private_path.relative_to(REPO)).replace("\\", "/"),
        "private_candidate_contains_source_text": True,
        "game_files_written": False,
    }
    atomic_write(output_root / "summary.source_free.json", json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    try:
        report = audit(args.game_root, args.output_root)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0
    except (AuditError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
