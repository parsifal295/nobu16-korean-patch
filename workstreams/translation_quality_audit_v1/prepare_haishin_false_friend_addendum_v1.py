#!/usr/bin/env python3
"""Prepare PC-only corrections for the ``陪臣``/``배신`` false friend.

``陪臣`` means a retainer serving through another retainer ("a vassal's
vassal"), not a traitor.  This small addendum fixes only four visible PC
coordinates where the live Korean text uses the unrelated word ``배신``.

Evidence is deliberately limited to the pristine PC Japanese resource and
the installed PC Korean/EN/SC/TC resources.  No Switch Korean path is
defined, opened, or used.  The only write target is a private JSONL review
artifact under ``tmp``; this tool never writes a game resource.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
SEMANTIC = REPO / "tmp" / "translation_quality_audit_v1" / "semantic"
OUTPUT = SEMANTIC / "haishin_false_friend_addendum.v1.jsonl"

sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "workstreams" / "msggame"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402
from msggame_format import iter_literals, parse_packed_msggame  # noqa: E402


PC_FILES = {
    "ev_strdata": {
        "relative": Path("MSG") / "JP" / "ev_strdata.bin",
        "parser": "common",
        "languages": ("JP", "SC", "TC"),
        # The base-event pristine PC Japanese file is preserved separately
        # from the PK backup, and is pinned by the same v1.1.7 source hash.
        "pristine_path": Path(r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root\MSG\JP\ev_strdata.bin"),
        "pristine_sha256": "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB",
    },
    "pk_msggame": {
        "relative": Path("MSG_PK") / "JP" / "msggame.bin",
        "parser": "msggame",
        "languages": ("JP", "EN", "SC", "TC"),
        "pristine_sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    },
}

# The first three sentences are base event strings.  They are deliberately
# rephrased instead of simply inserting more characters: each proposed line
# stays no longer than its current counterpart while restoring the status
# relation.  The fourth is a PK event literal with a short second line.
@dataclass(frozen=True)
class Change:
    resource: str
    coordinate: str
    replacements: tuple[tuple[str, str], ...]
    expected_pc_terms: tuple[str, ...]
    corroboration: Mapping[str, tuple[str, ...]]
    rationale: str


CHANGES = (
    Change(
        "ev_strdata",
        "3444",
        (("가 보기에는 배신에 지나지 않는다.", "가 보기엔 가신의 가신일 뿐이다."),),
        ("陪臣",),
        {"SC": ("陪臣",), "TC": ("陪臣",)},
        "陪臣 is a subordinate retainer relation.  The current Korean word 배신 means traitor; the shorter rewrite preserves the relation without widening the event line.",
    ),
    Change(
        "ev_strdata",
        "4050",
        (("일개 배신에 지나지 않는 나에게", "가신의 가신인 내게"),),
        ("陪臣",),
        {"SC": ("陪臣",), "TC": ("卑微的家臣",)},
        "The speaker describes themself as a 陪臣, not a traitor.  The concise Korean phrasing preserves the humble rank relation and stays below the current line length.",
    ),
    Change(
        "ev_strdata",
        "4487",
        (("배신의 지위에 지나지 않사옵니다.", "가신의 가신일 뿐이옵니다."),),
        ("陪臣",),
        {"SC": ("陪臣",), "TC": ("陪臣",)},
        "陪臣 denotes a vassal's vassal.  The old Korean says the speaker holds a traitor's rank, reversing the meaning.",
    ),
    Change(
        "pk_msggame",
        "17:393:2",
        (("일개 배신 주제에", "가신의 가신 주제에"),),
        ("陪臣",),
        {"EN": ("unranked vassal",), "TC": ("陪臣",)},
        "PC English and Traditional Chinese both corroborate the subordinate-vassal sense; 배신 is the unrelated Korean word for traitor.",
    ),
)

EXISTING_ARTIFACTS = {
    "ev_strdata": (
        "ev_strdata_quality_findings.v1.jsonl",
        "ev_strdata_semantic_quality_v2.jsonl",
        "ev_strdata_semantic_relationship_addendum_v1.jsonl",
        "ev_strdata_semantic_quality_v3.jsonl",
        "ev_strdata_semantic_quality_v4.jsonl",
        "ev_strdata_proper_name_quality_v5.jsonl",
        "ev_strdata_semantic_quality_v6r.jsonl",
    ),
    "pk_msggame": (
        "pk_msggame_broad_candidates.v1.jsonl",
        "pk_msggame_broad_candidates.v2.jsonl",
        "pk_msggame_broad_candidates.v3.jsonl",
        "pk_msggame_block17_candidates.v1.jsonl",
        "pk_msggame_block17_candidates.v2.jsonl",
        "pk_msggame_block17_candidates.v3.jsonl",
        "pk_msggame_block17_candidates.v4.jsonl",
        "pk_msggame_crossblock_candidates.v1.jsonl",
        "pk_msggame_crossblock_candidates.v2.jsonl",
        "pk_msggame_crossblock_candidates.v3r.jsonl",
        "pk_msggame_crossblock_candidates.v4.jsonl",
        "pk_msggame_crossblock_candidates.v5r.jsonl",
        "pk_msggame_japanese_punctuation_candidates.v2r.jsonl",
        "pk_msggame_dynamic_child_candidates.v1.jsonl",
    ),
}

ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
CJK_OR_KANA_RE = re.compile(r"[\u3041-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
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


def language_path(relative: Path, language: str) -> Path:
    parts = list(relative.parts)
    index = parts.index("JP")
    parts[index] = language
    return Path(*parts)


def parse_common(path: Path) -> dict[str, str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return {str(index): text for index, text in enumerate(parse_message_table(raw).texts)}


def parse_msggame(path: Path) -> dict[str, str]:
    archive = parse_packed_msggame(path.read_bytes()).archive
    return {f"{item.block_id}:{item.record_id}:{item.literal_id}": item.text for item in iter_literals(archive)}


def load_resource_tables(resource: str) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    spec = PC_FILES[resource]
    parser = parse_common if spec["parser"] == "common" else parse_msggame
    relative = spec["relative"]
    tables: dict[str, dict[str, str]] = {}
    hashes: dict[str, str] = {}
    for language in spec["languages"]:
        path = (
            spec.get("pristine_path", PRISTINE / language_path(relative, language))
            if language == "JP"
            else (STEAM / language_path(relative, language))
        )
        if not path.is_file():
            raise ValueError(f"PC {language} resource is absent: {path}")
        tables[language] = parser(path)
        hashes[language] = sha256_file(path)
    if hashes["JP"] != spec["pristine_sha256"]:
        raise ValueError(f"pristine PC JP hash differs for {resource}: {hashes['JP']}")
    # PC msggame language archives legitimately have different overall record
    # counts.  The candidate gate below requires the specific literal to be
    # present in every cited PC language instead of assuming table lengths
    # are globally identical.
    return tables, hashes


def load_live_korean(resource: str) -> tuple[dict[str, str], str]:
    spec = PC_FILES[resource]
    parser = parse_common if spec["parser"] == "common" else parse_msggame
    path = STEAM / spec["relative"]
    if not path.is_file():
        raise ValueError(f"live PC Korean resource is absent: {path}")
    return parser(path), sha256_file(path)


def profile(value: str) -> dict[str, Any]:
    escaped = {index for match in ESC_RE.finditer(value) for index in range(match.start(), match.end())}
    return {
        "escape_tags": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf": PRINTF_RE.findall(value),
        "linebreaks": LINEBREAK_RE.findall(value),
        "leading_whitespace": value[: len(value) - len(value.lstrip())],
        "trailing_whitespace": value[len(value.rstrip()) :],
        "non_esc_control_offsets": [
            index
            for index, char in enumerate(value)
            if ord(char) < 32 and char not in ("\r", "\n") and index not in escaped
        ],
    }


def visible_line_lengths(value: str) -> list[int]:
    """Conservative Korean cell-count check for unchanged manual line breaks."""

    stripped = ESC_RE.sub("", value)
    stripped = RUNTIME_RE.sub("□", stripped)
    return [len(line) for line in LINEBREAK_RE.split(stripped)]


def apply_replacements(value: str, replacements: tuple[tuple[str, str], ...]) -> str:
    candidate = value
    for old, new in replacements:
        if candidate.count(old) != 1:
            raise ValueError(f"expected exactly one Korean fragment occurrence: {old!r}")
        candidate = candidate.replace(old, new)
    return candidate


def artifact_coordinates(resource: str) -> set[str]:
    coordinates: set[str] = set()
    for name in EXISTING_ARTIFACTS[resource]:
        path = SEMANTIC / name
        if not path.is_file():
            raise ValueError(f"expected existing review artifact is absent: {path}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"invalid review row: {path}:{number}")
            key = row.get("coordinate") if resource == "pk_msggame" else row.get("id")
            if resource == "pk_msggame":
                if isinstance(key, str):
                    coordinates.add(key)
            elif isinstance(key, int):
                coordinates.add(str(key))
    return coordinates


def build_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_resource: dict[str, list[Change]] = {}
    for change in CHANGES:
        by_resource.setdefault(change.resource, []).append(change)

    rows: list[dict[str, Any]] = []
    summary: dict[str, Any] = {"resource_counts": {}, "pc_file_sha256": {}}
    for resource, changes in by_resource.items():
        context, context_hashes = load_resource_tables(resource)
        live_ko, live_hash = load_live_korean(resource)
        existing = artifact_coordinates(resource)
        for change in changes:
            if change.coordinate in existing:
                raise ValueError(f"candidate already appears in an existing {resource} review artifact: {change.coordinate}")
            if change.coordinate not in live_ko or any(change.coordinate not in table for table in context.values()):
                raise ValueError(f"coordinate is absent from a required PC table: {resource}:{change.coordinate}")
            source = context["JP"][change.coordinate]
            current = live_ko[change.coordinate]
            if not all(marker in source for marker in change.expected_pc_terms):
                raise ValueError(f"PC JP source markers differ at {resource}:{change.coordinate}")
            for language, markers in change.corroboration.items():
                if not all(marker.casefold() in context[language][change.coordinate].casefold() for marker in markers):
                    raise ValueError(f"PC {language} corroboration differs at {resource}:{change.coordinate}")
            proposed = apply_replacements(current, change.replacements)
            if "배신" in proposed:
                raise ValueError(f"false-friend Korean word remains at {resource}:{change.coordinate}")
            if CJK_OR_KANA_RE.search(proposed):
                raise ValueError(f"candidate retains CJK/Kana at {resource}:{change.coordinate}")
            before_profile = profile(current)
            after_profile = profile(proposed)
            if before_profile != after_profile:
                raise ValueError(f"format profile differs at {resource}:{change.coordinate}")
            before_lengths = visible_line_lengths(current)
            after_lengths = visible_line_lengths(proposed)
            if len(before_lengths) != len(after_lengths):
                raise ValueError(f"manual line count differs at {resource}:{change.coordinate}")
            # All base-event lines are shortened or unchanged.  The PK
            # dialogue's edited line grows by one cell only and stays short.
            if resource == "ev_strdata" and any(after > before for before, after in zip(before_lengths, after_lengths)):
                raise ValueError(f"base event line grew at {resource}:{change.coordinate}")
            if resource == "pk_msggame" and any(after > before + 1 for before, after in zip(before_lengths, after_lengths)):
                raise ValueError(f"PK dialogue line grew beyond one cell at {resource}:{change.coordinate}")
            row: dict[str, Any] = {
                "allowed_format_delta": [],
                "confidence": "high",
                "current_hash": text_hash(current),
                "format_validation": {
                    "all_nontext_format_fields": "match",
                    "candidate_visible_line_lengths": after_lengths,
                    "current_visible_line_lengths": before_lengths,
                    "manual_line_count": len(after_lengths),
                    "manual_line_count_matches_current": True,
                },
                "issue_type": "haishin_false_friend_traitor_for_subordinate_retainer",
                "jp_source_hash": text_hash(source),
                "ko": current,
                "pc_semantic_evidence": {
                    "jp_terms": list(change.expected_pc_terms),
                    "corroboration": {language: list(markers) for language, markers in change.corroboration.items()},
                },
                "proposed_ko": proposed,
                "rationale": change.rationale,
                "reference_basis": ["pristine_pc_jp", *[f"pc_{language.lower()}" for language in change.corroboration]],
                "reference_file_sha256": context_hashes,
                "resource": resource,
                "source_file_sha256": context_hashes["JP"],
                "steam_ko_file_sha256": live_hash,
                "switch_korean_translation_used": False,
            }
            if resource == "pk_msggame":
                row["coordinate"] = change.coordinate
            else:
                row["id"] = int(change.coordinate)
            rows.append(row)
        summary["resource_counts"][resource] = len(changes)
        summary["pc_file_sha256"][resource] = {**context_hashes, "KO": live_hash}
    rows.sort(key=lambda row: (row["resource"], tuple(int(part) for part in row.get("coordinate", str(row.get("id"))).split(":"))))
    summary.update(
        {
            "candidate_count": len(rows),
            "game_files_written": False,
            "output": str(OUTPUT),
            "switch_korean_translation_used": False,
        }
    )
    return rows, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the private JSONL candidate below tmp")
    args = parser.parse_args()
    rows, summary = build_rows()
    if args.write:
        text = "".join(json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
        atomic_write(OUTPUT, text)
        summary["output_sha256"] = sha256_file(OUTPUT)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
