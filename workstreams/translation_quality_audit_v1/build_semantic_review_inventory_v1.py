#!/usr/bin/env python3
"""Build a private, source-paired inventory for the PC Korean text audit.

Every live Steam Korean coordinate is paired with the matching pristine PC
Japanese coordinate.  PC EN/SC/TC at the same coordinate are supplementary
context only.  Switch Korean text is intentionally neither read nor emitted.
All source-bearing files are restricted to ``tmp``.
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
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_ORIGINAL_ROOT = DEFAULT_STEAM_ROOT / "KR_PATCH_BACKUP" / "file_only_transaction" / "steam-jp-1.1.7-v0.6.0" / "originals"
DEFAULT_OUTPUT = TMP / "translation_quality_audit_v1" / "semantic_inventory_v1"
BASE_ORIGINALS = {
    "MSG/JP/ev_strdata.bin": Path(r"F:\Games\NOBU16\MSG\JP\ev_strdata.bin"),
    "MSG/JP/msggame.bin": Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
}
# This audit is pinned to the PC v1.1.7 Japanese originals used to build the
# installed Korean patch.  In particular, the live Steam ``JP`` route is a
# Korean-patched target at audit time and must never be silently accepted as
# the source merely because its coordinates happen to line up.
PRISTINE_JP_SHA256 = {
    "MSG/JP/ev_strdata.bin": "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB",
    "MSG/JP/msggame.bin": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    "MSG/JP/strdata.bin": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
    "MSG_PK/JP/msgbre.bin": "945A0E9157E2DBD12781FFA5A986D93681325F40B6486348B1AB311D3BEE1D6D",
    "MSG_PK/JP/msgdata.bin": "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E",
    "MSG_PK/JP/msgev.bin": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    "MSG_PK/JP/msggame.bin": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "MSG_PK/JP/msgire.bin": "0AFBFE11A380A9C98FB3B368092A05B39ABB6F80C4B0723AD3B6DB55C2559C5D",
    "MSG_PK/JP/msgstf.bin": "01EEB0B1B4879B6C70E9D7564F9D2FBD93E7B537CF8C614A58EEA82A83785A29",
    "MSG_PK/JP/msgui.bin": "9775D4B7253828899F7EF0DF2E88AB28121ACB260E1381F3D706C6A1065D504A",
}

# U+30FB (・) is the Korean patch's ordinary list separator, not residual
# Japanese text.  Keep it out of the detector so it cannot drown real kana.
KANA_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f]")
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]")
RUNTIME_RE = re.compile(r"\[([a-z]+\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
# These are review signals only.  Some message tables retain disabled or
# developer-only slots, so neither condition authorizes an automatic rewrite.
PLACEHOLDER_DUMMY_RE = re.compile(r"^dummy\d*$", re.IGNORECASE)
LOCALIZATION_IDENTIFIER_RE = re.compile(r"^(?:[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+|[A-Z][A-Z0-9_]{5,})$")


class SemanticAuditError(ValueError):
    pass


@dataclass(frozen=True)
class Spec:
    name: str
    relative: str
    parser: str
    context_languages: tuple[str, ...]


SPECS = (
    Spec("ev_strdata", "MSG/JP/ev_strdata.bin", "common", ("SC", "TC")),
    Spec("base_msggame", "MSG/JP/msggame.bin", "msggame", ("SC", "TC")),
    Spec("strdata", "MSG/JP/strdata.bin", "strdata", ("SC", "TC")),
    Spec("msgbre", "MSG_PK/JP/msgbre.bin", "common", ("EN", "SC", "TC")),
    Spec("msgdata", "MSG_PK/JP/msgdata.bin", "common", ("EN", "SC", "TC")),
    Spec("msgev", "MSG_PK/JP/msgev.bin", "common", ("EN", "SC", "TC")),
    Spec("pk_msggame", "MSG_PK/JP/msggame.bin", "msggame", ("EN", "SC", "TC")),
    Spec("msgire", "MSG_PK/JP/msgire.bin", "common", ("EN", "SC", "TC")),
    Spec("msgstf", "MSG_PK/JP/msgstf.bin", "common", ("EN", "SC", "TC")),
    Spec("msgui", "MSG_PK/JP/msgui.bin", "common", ("EN", "SC", "TC")),
)


def load_module(name: str, path: Path) -> Any:
    module_spec = importlib.util.spec_from_file_location(name, path)
    if module_spec is None or module_spec.loader is None:
        raise SemanticAuditError(f"cannot load {path}")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[name] = module
    module_spec.loader.exec_module(module)
    return module


LZ4 = load_module("semantic_audit_lz4", REPO / "tools" / "nobu16_lz4.py")
MESSAGE = load_module("semantic_audit_message", REPO / "tools" / "nobu16_msg_table.py")
MSGGAME = load_module("semantic_audit_msggame", REPO / "workstreams" / "msggame" / "msggame_format.py")
STRDATA = load_module("semantic_audit_strdata", REPO / "workstreams" / "strdata" / "strdata_format.py")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def language_path(relative: str, language: str) -> Path:
    parts = list(Path(relative).parts)
    index = parts.index("JP")
    parts[index] = language
    return Path(*parts)


def parse_common(path: Path) -> dict[str, str]:
    _header, raw = LZ4.decompress_wrapper(path.read_bytes())
    table = MESSAGE.parse_message_table(raw)
    return {str(index): text for index, text in enumerate(table.texts)}


def parse_msggame(path: Path) -> dict[str, str]:
    archive = MSGGAME.parse_packed_msggame(path.read_bytes()).archive
    return {f"{item.block_id}:{item.record_id}:{item.literal_id}": item.text for item in MSGGAME.iter_literals(archive)}


def parse_strdata(path: Path) -> dict[str, str]:
    _header, raw = LZ4.decompress_wrapper(path.read_bytes())
    archive = STRDATA.parse_raw_strdata(raw)
    return {f"{block}:{slot}": text for (block, slot), text in STRDATA.coordinate_texts(archive).items()}


PARSERS: dict[str, Callable[[Path], dict[str, str]]] = {"common": parse_common, "msggame": parse_msggame, "strdata": parse_strdata}


def coordinate_sort_key(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split(":"))


def profile(text: str) -> dict[str, Any]:
    return {
        "runtime": RUNTIME_RE.findall(text),
        "printf": PRINTF_RE.findall(text),
        "escape": ESC_RE.findall(text),
        "line_break_count": len(re.findall(r"\r\n|\n|\r", text)),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
    }


def review_flags(jp: str, ko: str, contexts: dict[str, str]) -> list[str]:
    flags: list[str] = []
    if KANA_RE.search(ko):
        flags.append("target_kana_residual")
    if HAN_RE.search(ko) and not HANGUL_RE.search(ko):
        flags.append("target_han_residual")
    jp_profile = profile(jp)
    ko_profile = profile(ko)
    if jp_profile["runtime"] != ko_profile["runtime"]:
        flags.append("runtime_token_mismatch_against_pristine_jp")
    if jp_profile["printf"] != ko_profile["printf"]:
        flags.append("printf_token_mismatch_against_pristine_jp")
    if jp_profile["escape"] != ko_profile["escape"]:
        flags.append("escape_tag_mismatch_against_pristine_jp")
    if jp_profile["line_break_count"] != ko_profile["line_break_count"]:
        flags.append("linebreak_count_mismatch_against_pristine_jp")
    if jp_profile["leading_whitespace"] != ko_profile["leading_whitespace"] or jp_profile["trailing_whitespace"] != ko_profile["trailing_whitespace"]:
        flags.append("external_whitespace_mismatch_against_pristine_jp")
    if not ko and jp:
        flags.append("empty_target_for_nonempty_jp")
    source_visible = jp.strip()
    target_visible = ko.strip()
    if source_visible and target_visible and target_visible != source_visible:
        if PLACEHOLDER_DUMMY_RE.fullmatch(target_visible):
            flags.append("target_dummy_placeholder_for_nonempty_jp")
        if LOCALIZATION_IDENTIFIER_RE.fullmatch(target_visible):
            flags.append("target_localization_identifier_for_nonempty_jp")
    # A Korean string that is dramatically shorter than a full Japanese sentence
    # may be a truncation, but UI labels can legitimately be concise.  It is a
    # review candidate, never an automatic rewrite.
    visible_jp = re.sub(r"\[[a-z]+\d+\]|%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]|\x1bC.", "", jp)
    visible_ko = re.sub(r"\[[a-z]+\d+\]|%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]|\x1bC.", "", ko)
    if len(visible_jp.strip()) >= 30 and 0 < len(visible_ko.strip()) <= 3:
        flags.append("possible_semantic_truncation")
    return flags


def cross_resource_duplicate_renderings(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collect inconsistent Korean renderings of one PC-Japanese string.

    The per-resource duplicate pass above catches repeated source strings
    within one table.  Many UI labels also occur in a different table, though,
    so this second private-only report exposes cross-resource terminology
    drift.  It is a review signal, not an automatic correction: identical
    Japanese can legitimately be a personal name, a place name, or a generic
    UI fragment in different contexts.
    """
    grouped: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        jp = row["jp"]
        if not isinstance(jp, str):
            raise SemanticAuditError("source text is not a string")
        visible = jp.strip()
        if len(visible) < 2 or visible.casefold() in {"dummy", "none", "null"}:
            continue
        ko = row["ko"]
        if not isinstance(ko, str):
            raise SemanticAuditError("Korean target text is not a string")
        grouped[jp][ko].append({"resource": row["resource"], "coordinate": row["coordinate"]})

    result: list[dict[str, Any]] = []
    for jp, renderings in grouped.items():
        resources = {location["resource"] for locations in renderings.values() for location in locations}
        if len(resources) < 2 or len(renderings) < 2:
            continue
        result.append(
            {
                "jp": jp,
                "jp_utf16le_sha256": sha256_text(jp),
                "resources": sorted(resources),
                "renderings": [
                    {
                        "ko": ko,
                        "locations": sorted(
                            locations,
                            key=lambda location: (location["resource"], coordinate_sort_key(location["coordinate"])),
                        ),
                    }
                    for ko, locations in sorted(renderings.items(), key=lambda item: item[0])
                ],
            }
        )
    return sorted(result, key=lambda row: (row["jp_utf16le_sha256"], row["jp"]))


def source_path_for(spec: Spec, original_root: Path) -> Path:
    return BASE_ORIGINALS.get(spec.relative, original_root / spec.relative)


def audit(steam_root: Path, original_root: Path, output: Path) -> dict[str, Any]:
    steam_root = steam_root.resolve()
    original_root = original_root.resolve()
    output = output.resolve()
    tmp_root = TMP.resolve()
    if output == tmp_root or tmp_root not in output.parents:
        raise SemanticAuditError(f"output must remain under {tmp_root}")
    if output.exists():
        raise SemanticAuditError(f"refusing to overwrite existing output: {output}")

    all_rows: list[dict[str, Any]] = []
    duplicate_groups: list[dict[str, Any]] = []
    resource_summary: dict[str, Any] = {}
    total_flags: Counter[str] = Counter()
    for spec in SPECS:
        parser = PARSERS[spec.parser]
        live_path = steam_root / spec.relative
        original_path = source_path_for(spec, original_root)
        if not live_path.is_file() or not original_path.is_file():
            raise SemanticAuditError(f"missing live/original pair for {spec.name}")
        original_sha256 = sha256_file(original_path)
        if original_sha256 != PRISTINE_JP_SHA256[spec.relative]:
            raise SemanticAuditError(
                f"pristine PC Japanese hash differs for {spec.name}: "
                f"expected {PRISTINE_JP_SHA256[spec.relative]}, got {original_sha256}"
            )
        ko_rows = parser(live_path)
        jp_rows = parser(original_path)
        if set(ko_rows) != set(jp_rows):
            raise SemanticAuditError(f"coordinate mismatch between live Korean and pristine JP: {spec.name}")
        contexts: dict[str, dict[str, str]] = {}
        context_metadata: dict[str, Any] = {}
        for language in spec.context_languages:
            path = steam_root / language_path(spec.relative, language)
            if not path.is_file():
                continue
            rows = parser(path)
            contexts[language] = rows
            context_metadata[language] = {"relative_path": str(language_path(spec.relative, language)).replace("\\", "/"), "sha256": sha256_file(path), "coordinate_count": len(rows), "overlap_coordinate_count": len(set(rows).intersection(ko_rows))}
        duplicate_map: dict[str, set[str]] = defaultdict(set)
        duplicate_coordinates: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        for coordinate, jp in jp_rows.items():
            if jp.strip():
                duplicate_map[jp].add(ko_rows[coordinate])
                duplicate_coordinates[jp][ko_rows[coordinate]].append(coordinate)
        duplicate_inconsistent_jp = {jp for jp, values in duplicate_map.items() if len(values) > 1}
        for jp in sorted(duplicate_inconsistent_jp, key=lambda value: (sha256_text(value), value)):
            if len(jp.strip()) < 2:
                continue
            renderings = [
                {"ko": ko, "coordinates": sorted(coordinates, key=coordinate_sort_key)}
                for ko, coordinates in sorted(duplicate_coordinates[jp].items(), key=lambda item: item[0])
            ]
            duplicate_groups.append({"resource": spec.name, "jp": jp, "jp_utf16le_sha256": sha256_text(jp), "renderings": renderings})
        resource_flags: Counter[str] = Counter()
        for coordinate in sorted(ko_rows, key=coordinate_sort_key):
            jp = jp_rows[coordinate]
            ko = ko_rows[coordinate]
            row_context = {language: rows[coordinate] for language, rows in contexts.items() if coordinate in rows}
            flags = review_flags(jp, ko, row_context)
            if jp in duplicate_inconsistent_jp and len(jp.strip()) >= 2:
                flags.append("same_pristine_jp_has_multiple_korean_renderings")
            resource_flags.update(flags)
            total_flags.update(flags)
            all_rows.append({
                "resource": spec.name,
                "coordinate": coordinate,
                "jp": jp,
                "ko": ko,
                "jp_utf16le_sha256": sha256_text(jp),
                "ko_utf16le_sha256": sha256_text(ko),
                "contexts": row_context,
                "flags": flags,
            })
        resource_summary[spec.name] = {
            "relative_path": spec.relative,
            "parser": spec.parser,
            "coordinate_count": len(ko_rows),
            "pristine_jp": {"path_class": "local_PC_pristine", "sha256": original_sha256, "coordinate_count": len(jp_rows)},
            "context_resources": context_metadata,
            "inconsistent_same_jp_source_count": len(duplicate_inconsistent_jp),
            "flag_counts": dict(sorted(resource_flags.items())),
        }

    output.mkdir(parents=True, exist_ok=False)
    full_pairs = output / "private_full_pairs.jsonl"
    atomic_write(full_pairs, "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in all_rows))
    queue = [row for row in all_rows if row["flags"]]
    priority = {
        "target_kana_residual": 0,
        "target_han_residual": 0,
        "runtime_token_mismatch_against_pristine_jp": 0,
        "printf_token_mismatch_against_pristine_jp": 0,
        "escape_tag_mismatch_against_pristine_jp": 0,
        "empty_target_for_nonempty_jp": 0,
        "target_dummy_placeholder_for_nonempty_jp": 0,
        "target_localization_identifier_for_nonempty_jp": 0,
        "linebreak_count_mismatch_against_pristine_jp": 1,
        "external_whitespace_mismatch_against_pristine_jp": 1,
        "possible_semantic_truncation": 2,
        "same_pristine_jp_has_multiple_korean_renderings": 3,
    }
    queue.sort(key=lambda row: (min(priority[flag] for flag in row["flags"]), row["resource"], coordinate_sort_key(row["coordinate"])))
    review_path = output / "private_review_queue.jsonl"
    atomic_write(review_path, "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in queue))
    duplicate_path = output / "private_duplicate_renderings.jsonl"
    atomic_write(duplicate_path, "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in duplicate_groups))
    cross_resource_groups = cross_resource_duplicate_renderings(all_rows)
    cross_resource_duplicate_path = output / "private_cross_resource_duplicate_renderings.jsonl"
    atomic_write(
        cross_resource_duplicate_path,
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in cross_resource_groups),
    )
    summary = {
        "schema": "nobu16.kr.translation-semantic-review-inventory.v1",
        "scope": "all live Steam PC Korean text coordinates paired one-to-one with local pristine PC Japanese originals; PC EN/SC/TC supplementary only",
        "switch_korean_translation_used": False,
        "resource_count": len(SPECS),
        "coordinate_count": len(all_rows),
        "review_queue_count": len(queue),
        "duplicate_rendering_group_count": len(duplicate_groups),
        "cross_resource_duplicate_rendering_group_count": len(cross_resource_groups),
        "flag_counts": dict(sorted(total_flags.items())),
        "resources": resource_summary,
        "private_full_pair_path": str(full_pairs.relative_to(REPO)).replace("\\", "/"),
        "private_review_queue_path": str(review_path.relative_to(REPO)).replace("\\", "/"),
        "private_duplicate_rendering_path": str(duplicate_path.relative_to(REPO)).replace("\\", "/"),
        "private_cross_resource_duplicate_rendering_path": str(cross_resource_duplicate_path.relative_to(REPO)).replace("\\", "/"),
        "private_files_contain_commercial_source_text": True,
        "steam_installation_written": False,
    }
    atomic_write(output / "summary.source_free.json", json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--original-root", type=Path, default=DEFAULT_ORIGINAL_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.steam_root, args.original_root, args.output), ensure_ascii=False, sort_keys=True))
        return 0
    except (SemanticAuditError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
