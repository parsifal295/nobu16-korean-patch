#!/usr/bin/env python3
"""Prepare the PC-only ``\u8981\u6240`` location-meaning correction at coordinate 9013.

The same source text occurs in base ``ev_strdata`` and PK ``msgev``.  In both
live Korean tables, ``\u8981\u6240`` (a key location in this construction
context) was rendered as ``\uc694\uc18c`` (element).  This generator proposes the
locative Korean term ``\uc694\ucc98`` and verifies it against PC Japanese plus the
PC SC/TC wording; MS GEV also has a PC EN reference to burial beneath a
construction foundation.

It reads PC paths only.  It never opens Switch or historical Korean files and
writes only deterministic private review JSONL when ``--write`` is requested.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PC_BASE_SOURCE_ROOT = Path(r"F:\Games\NOBU16")
PC_PK_JP_ORIGINAL = (
    STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
TMP_ROOT = REPO / "tmp" / "translation_quality_audit_v1"
SEMANTIC_ROOT = TMP_ROOT / "semantic"
OUTPUT = SEMANTIC_ROOT / "yousho_location_clarity_candidates.v1.jsonl"
HOLD_OUTPUT = SEMANTIC_ROOT / "yousho_location_clarity_holds.v1.jsonl"

REVIEW_BATCH = "yousho_location_clarity_v1"
COORDINATE = 9013
MAX_LOGICAL_COLUMNS = 76
YOUSHO = "\u8981\u6240"
YOUDI = "\u8981\u5730"
CURRENT_KO_TERM = "\uc694\uc18c"
PROPOSED_KO_TERM = "\uc694\ucc98"

EXPECTED_FILE_HASHES = {
    "ev_jp": "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB",
    "ev_ko": "6A7D90C1A95AD42DCAE2D3C3719508EDD00588288659A1D192B680CF70EAE6E4",
    "ev_sc": "77E87C6FEC67859543FCB4134660A7274A2374F6881B956421B561E61BD7B685",
    "ev_tc": "9E9346B942CAFA99432D675F6BA74DD04D48F56095F35F46392697011D9CFEF3",
    "msgev_jp": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    "msgev_ko": "B8B3B1C5A635419E590DB866C240A1B6609799E0FEA0E69F86D6208F27E5C52B",
    "msgev_en": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
    "msgev_sc": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
    "msgev_tc": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
}
EXPECTED_TEXT_HASHES = {
    "jp": "9C83737E17A073DA34787DF5A6D1C1B92C5ADBCB952DE86FD21326035657FF85",
    "ko": "0FC3A83B1F62C794D827F4A50B324915366B36327708DC8AF94794886DBA1BCE",
}

ESC_TOKEN_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ID_RE = re.compile(r'"id"\s*:\s*(\d+)')


@dataclass(frozen=True)
class ResourceSpec:
    key: str
    resource: str
    jp_path: Path
    ko_path: Path
    reference_paths: dict[str, Path]


SPECS = (
    ResourceSpec(
        key="ev",
        resource="MSG/JP/ev_strdata.bin",
        jp_path=PC_BASE_SOURCE_ROOT / "MSG" / "JP" / "ev_strdata.bin",
        ko_path=STEAM_ROOT / "MSG" / "JP" / "ev_strdata.bin",
        reference_paths={
            "sc": STEAM_ROOT / "MSG" / "SC" / "ev_strdata.bin",
            "tc": STEAM_ROOT / "MSG" / "TC" / "ev_strdata.bin",
        },
    ),
    ResourceSpec(
        key="msgev",
        resource="MSG_PK/JP/msgev.bin",
        jp_path=PC_PK_JP_ORIGINAL,
        ko_path=STEAM_ROOT / "MSG_PK" / "JP" / "msgev.bin",
        reference_paths={
            "en": STEAM_ROOT / "MSG_PK" / "EN" / "msgev.bin",
            "sc": STEAM_ROOT / "MSG_PK" / "SC" / "msgev.bin",
            "tc": STEAM_ROOT / "MSG_PK" / "TC" / "msgev.bin",
        },
    ),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def file_hash(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def parse_common(path: Path) -> tuple[str, ...]:
    sys.path.insert(0, str(REPO / "tools"))
    from nobu16_lz4 import decompress_wrapper
    from nobu16_msg_table import parse_message_table

    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def format_signature(text: str) -> dict[str, Any]:
    return {
        "escape_tokens": ESC_TOKEN_RE.findall(text),
        "runtime_tokens": RUNTIME_RE.findall(text),
        "printf_tokens": PRINTF_RE.findall(text),
        "linebreaks": re.findall(r"\r\n|\n|\r", text),
        "leading_ascii_whitespace": text[: len(text) - len(text.lstrip(" \t"))],
        "trailing_ascii_whitespace": text[len(text.rstrip(" \t")) :],
    }


def logical_columns(line: str) -> int:
    rendered = ESC_TOKEN_RE.sub("", line)
    rendered = RUNTIME_RE.sub("XXXXXXXX", rendered)
    total = 0
    for char in rendered:
        if unicodedata.combining(char):
            continue
        total += 2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1
    return total


def layout(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    return {
        "line_count": len(lines),
        "logical_display_columns": [logical_columns(line) for line in lines],
    }


def existing_coordinate_overlap(spec: ResourceSpec) -> list[str]:
    """Check only numeric IDs in private same-resource artifacts."""

    matches: list[str] = []
    marker = "*msgev*.jsonl" if spec.key == "msgev" else "*ev_strdata*.jsonl"
    for path in sorted(SEMANTIC_ROOT.glob(marker)):
        if path.resolve() in {OUTPUT.resolve(), HOLD_OUTPUT.resolve()}:
            continue
        if any(int(match.group(1)) == COORDINATE for match in ID_RE.finditer(path.read_text(encoding="utf-8"))):
            matches.append(path.relative_to(REPO).as_posix())
    return matches


def row_for(spec: ResourceSpec) -> dict[str, Any]:
    source_hash = file_hash(spec.jp_path)
    current_hash = file_hash(spec.ko_path)
    if source_hash != EXPECTED_FILE_HASHES[f"{spec.key}_jp"]:
        raise RuntimeError(f"unexpected PC Japanese hash for {spec.key}: {source_hash}")
    if current_hash != EXPECTED_FILE_HASHES[f"{spec.key}_ko"]:
        raise RuntimeError(f"unexpected PC Korean hash for {spec.key}: {current_hash}")
    source_table = parse_common(spec.jp_path)
    current_table = parse_common(spec.ko_path)
    source = source_table[COORDINATE]
    current = current_table[COORDINATE]
    if text_hash(source) != EXPECTED_TEXT_HASHES["jp"] or source.count(YOUSHO) != 1:
        raise RuntimeError(f"unexpected \u8981\u6240 source text at {spec.key}:{COORDINATE}")
    if text_hash(current) != EXPECTED_TEXT_HASHES["ko"] or current.count(CURRENT_KO_TERM) != 1:
        raise RuntimeError(f"unexpected \uc694\uc18c target text at {spec.key}:{COORDINATE}")
    proposed = current.replace(CURRENT_KO_TERM, PROPOSED_KO_TERM)
    if proposed.count(PROPOSED_KO_TERM) != current.count(PROPOSED_KO_TERM) + 1:
        raise RuntimeError(f"expected exactly one \uc694\ucc98 replacement at {spec.key}:{COORDINATE}")
    if format_signature(current) != format_signature(proposed):
        raise RuntimeError(f"format contract drift at {spec.key}:{COORDINATE}")
    current_layout = layout(current)
    proposed_layout = layout(proposed)
    if current_layout != proposed_layout:
        raise RuntimeError(f"layout drift at {spec.key}:{COORDINATE}")
    if proposed_layout["line_count"] > 3 or max(
        proposed_layout["logical_display_columns"], default=0
    ) > MAX_LOGICAL_COLUMNS:
        raise RuntimeError(f"layout budget failed at {spec.key}:{COORDINATE}")
    references: dict[str, str] = {}
    reference_hashes: dict[str, str] = {}
    for language, path in spec.reference_paths.items():
        digest = file_hash(path)
        if digest != EXPECTED_FILE_HASHES[f"{spec.key}_{language}"]:
            raise RuntimeError(f"unexpected PC {language} hash for {spec.key}: {digest}")
        text = parse_common(path)[COORDINATE]
        references[language] = text
        reference_hashes[language] = digest
        if language in {"sc", "tc"} and YOUDI not in text:
            raise RuntimeError(f"PC {language} lacks the key-location marker at {spec.key}:{COORDINATE}")
    if spec.key == "msgev" and "foundation" not in references["en"].casefold():
        raise RuntimeError("PC EN does not retain the construction-foundation context")
    overlap_files = existing_coordinate_overlap(spec)
    if overlap_files:
        raise RuntimeError(f"existing same-resource candidate overlap at {spec.key}:{COORDINATE}: {overlap_files}")
    return {
        "schema_version": REVIEW_BATCH,
        "review_batch": REVIEW_BATCH,
        "record_type": "candidate",
        "confidence": "high",
        "resource": spec.resource,
        "id": COORDINATE,
        "issue_type": "yousho_key_location_not_generic_element",
        "source_japanese": source,
        "current_korean": current,
        "proposed_korean": proposed,
        "rationale": "\u8981\u6240 is the key location of a construction project where the sacrifice is buried. PC SC/TC render the location as \u8981\u5730; PC EN additionally describes burial beneath the construction foundation. Korean \uc694\uc18c is an abstract element, while \uc694\ucc98 is locative.",
        "pc_references": references,
        "input_file_sha256": {
            "jp": source_hash,
            "ko": current_hash,
            **reference_hashes,
        },
        "current_text_sha256": text_hash(current),
        "proposed_text_sha256": text_hash(proposed),
        "format_contract": format_signature(current),
        "current_layout": current_layout,
        "proposed_layout": proposed_layout,
        "logical_width_budget": MAX_LOGICAL_COLUMNS,
        "existing_same_resource_candidate_overlap": False,
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }


def build() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [row_for(spec) for spec in SPECS]
    if rows[0]["source_japanese"] != rows[1]["source_japanese"]:
        raise RuntimeError("the two PC Japanese source texts must be identical")
    if rows[0]["current_korean"] != rows[1]["current_korean"]:
        raise RuntimeError("the two live PC Korean texts must be identical")
    if rows[0]["proposed_korean"] != rows[1]["proposed_korean"]:
        raise RuntimeError("the two proposed Korean texts must be identical")
    return rows, {
        "review_batch": REVIEW_BATCH,
        "candidate_count": len(rows),
        "coordinates": [{"resource": row["resource"], "id": row["id"]} for row in rows],
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }


def canonical_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )


def atomic_write(path: Path, payload: str) -> None:
    root = TMP_ROOT.resolve()
    resolved = path.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise RuntimeError(f"output must remain below {TMP_ROOT}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows, summary = build()
    if args.write:
        atomic_write(OUTPUT, canonical_jsonl(rows))
        atomic_write(HOLD_OUTPUT, "")
        summary["candidate_output"] = OUTPUT.relative_to(REPO).as_posix()
        summary["candidate_output_sha256"] = file_hash(OUTPUT)
        summary["hold_output"] = HOLD_OUTPUT.relative_to(REPO).as_posix()
        summary["hold_output_sha256"] = file_hash(HOLD_OUTPUT)
    print("@@SUMMARY@@")
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
