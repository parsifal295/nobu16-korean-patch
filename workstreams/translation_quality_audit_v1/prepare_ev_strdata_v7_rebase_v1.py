#!/usr/bin/env python3
"""Rebase two superseded base-event findings onto the PC-only v7 review.

The historic residual review and the later all-coordinate review both contain
6259 and 7966.  The v7 wording is the stricter review, so this helper keeps
the historic file untouched and produces a private replacement file with only
those two rows updated.  It reads pristine PC Japanese, current PC Korean,
and private review artifacts only; no Switch asset is read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_JP = Path(r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root\MSG\JP\ev_strdata.bin")
LIVE_KO = STEAM / "MSG" / "JP" / "ev_strdata.bin"
TMP_ROOT = REPO / "tmp"
LEGACY = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "ev_strdata_findings.v1.jsonl"
V7 = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "ev_strdata_semantic_quality_v7.jsonl"
OUTPUT = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "ev_strdata_findings_rebased_v7.v1.jsonl"
SUPERSEDED_IDS = frozenset({6259, 7966})


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-16-le")).hexdigest().upper()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"review input is absent: {path}")
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or not isinstance(row.get("id"), int):
            raise ValueError(f"invalid review row: {path}:{number}")
        rows.append(row)
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError(f"duplicate review IDs: {path}")
    return rows


def load_table(path: Path) -> list[str]:
    import sys

    sys.path.insert(0, str(REPO / "tools"))
    from nobu16_lz4 import decompress_wrapper
    from nobu16_msg_table import parse_message_table

    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def safe_under_tmp(path: Path) -> Path:
    root = TMP_ROOT.resolve()
    resolved = path.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"output escapes tmp: {resolved}")
    return resolved


def atomic_write(path: Path, payload: str) -> None:
    path = safe_under_tmp(path)
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


def build() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    jp = load_table(PRISTINE_JP)
    ko = load_table(LIVE_KO)
    if len(jp) != 17868 or len(ko) != 17868:
        raise ValueError("base event coordinate count changed")

    legacy = load_jsonl(LEGACY)
    v7 = load_jsonl(V7)
    v7_by_id = {row["id"]: row for row in v7}
    if set(v7_by_id) != SUPERSEDED_IDS:
        raise ValueError("v7 coordinate set differs from the expected superseded pair")

    for row in v7:
        identifier = row["id"]
        if row.get("jp_source") != jp[identifier] or row.get("ko") != ko[identifier]:
            raise ValueError(f"v7 source/current text gate differs: {identifier}")
        if row.get("jp_source_hash") != sha_text(jp[identifier]):
            raise ValueError(f"v7 Japanese source hash differs: {identifier}")
        if row.get("current_hash") != sha_text(ko[identifier]) or row.get("source_hash") != sha_text(ko[identifier]):
            raise ValueError(f"v7 Korean current hash differs: {identifier}")
        if row.get("native_jp_file_sha256") != sha_file(PRISTINE_JP):
            raise ValueError(f"v7 Japanese file hash differs: {identifier}")
        if row.get("steam_ko_file_sha256") != sha_file(LIVE_KO):
            raise ValueError(f"v7 Korean file hash differs: {identifier}")
        if row.get("switch_korean_translation_used") is not False:
            raise ValueError(f"v7 Switch policy differs: {identifier}")
        if not isinstance(row.get("proposed_ko"), str) or not row["proposed_ko"]:
            raise ValueError(f"v7 Korean proposal is absent: {identifier}")
        layout = row.get("manual_layout_validation")
        if not isinstance(layout, dict) or layout.get("within_manual_line_budget") is not True:
            raise ValueError(f"v7 manual layout proof is absent: {identifier}")

    legacy_ids = {row["id"] for row in legacy}
    if not SUPERSEDED_IDS.issubset(legacy_ids):
        raise ValueError("legacy review does not contain every superseded coordinate")
    rebased: list[dict[str, Any]] = []
    for row in legacy:
        identifier = row["id"]
        if not 0 <= identifier < len(ko):
            raise ValueError(f"legacy ID is outside the base event table: {identifier}")
        if row.get("ko") != ko[identifier] or row.get("current_hash") != sha_text(ko[identifier]):
            raise ValueError(f"legacy current-text gate differs: {identifier}")
        rebased.append(v7_by_id[identifier] if identifier in SUPERSEDED_IDS else row)
    rebased.sort(key=lambda row: row["id"])
    summary = {
        "legacy_row_count": len(legacy),
        "rebased_row_count": len(rebased),
        "superseded_ids": sorted(SUPERSEDED_IDS),
        "source_current_hashes": "all_exact_utf16le",
        "switch_korean_translation_used": False,
        "game_files_written": False,
        "json_encoding": "ensure_ascii_true_utf8",
    }
    return rebased, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rebased, summary = build()
    if args.write:
        atomic_write(OUTPUT, "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rebased))
        print(json.dumps({**summary, "output": str(OUTPUT)}, ensure_ascii=True, sort_keys=True))
    else:
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
