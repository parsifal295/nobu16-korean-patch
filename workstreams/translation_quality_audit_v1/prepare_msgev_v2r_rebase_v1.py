#!/usr/bin/env python3
"""Rebase three superseded MS GEV proposals onto the PC-only v2r audit.

The original residual-review file contains three coordinates that the later
full PC audit improves.  This helper leaves that historic review file intact,
creates a replacement review file below ``tmp``, and emits a second file with
only the novel v2r coordinates.  It reads only local pristine PC Japanese,
the current Steam PC Korean target, and the two private PC-review JSONL files.
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
PRISTINE_JP = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
LIVE_KO = STEAM / "MSG_PK" / "JP" / "msgev.bin"
TMP_ROOT = REPO / "tmp"
LEGACY = TMP_ROOT / "translation_quality_audit_v1" / "proposals" / "msgev_ko.jsonl"
V2R = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgev_semantic_quality_v2r.jsonl"
REBASING_OUTPUT = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgev_ko_rebased_v2r.v1.jsonl"
NOVEL_OUTPUT = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgev_semantic_quality_v2r_novel.v1.jsonl"

# ``3118`` remains unchanged in the existing CJK review.  The other three
# existing residual proposals are replaced by the stricter v2r PC-only review.
EXISTING_V2R_IDS = frozenset({3118, 10837, 10840, 10905})
SUPERSEDED_LEGACY_IDS = frozenset({10837, 10840, 10905})


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-16-le")).hexdigest().upper()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"review input is absent: {path}")
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"review row is not an object: {path}:{number}")
        identifier = row.get("id")
        if not isinstance(identifier, int):
            raise ValueError(f"review row has no integer id: {path}:{number}")
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


def safe_under(path: Path) -> Path:
    root = TMP_ROOT.resolve()
    resolved = path.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"output escapes tmp: {resolved}")
    return resolved


def atomic_write(path: Path, payload: str) -> None:
    path = safe_under(path)
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


def build() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    jp = load_table(PRISTINE_JP)
    ko = load_table(LIVE_KO)
    if len(jp) != 17916 or len(ko) != 17916:
        raise ValueError("MS GEV coordinate count changed")

    legacy = load_jsonl(LEGACY)
    v2r = load_jsonl(V2R)
    v2r_by_id = {row["id"]: row for row in v2r}
    if not EXISTING_V2R_IDS.issubset(v2r_by_id):
        raise ValueError("v2r does not contain every expected existing coordinate")
    legacy_ids = {row["id"] for row in legacy}
    if not SUPERSEDED_LEGACY_IDS.issubset(legacy_ids):
        raise ValueError("legacy review does not contain every superseded coordinate")

    for row in v2r:
        identifier = row["id"]
        if not 0 <= identifier < len(jp):
            raise ValueError(f"v2r ID is outside MS GEV: {identifier}")
        if row.get("jp_source") != jp[identifier] or row.get("ko") != ko[identifier]:
            raise ValueError(f"v2r source/current text gate differs: {identifier}")
        if row.get("jp_source_hash") != sha_text(jp[identifier]) or row.get("current_hash") != sha_text(ko[identifier]):
            raise ValueError(f"v2r source/current hash gate differs: {identifier}")
        if row.get("switch_korean_translation_used") is not False:
            raise ValueError(f"v2r Switch policy differs: {identifier}")
        if not isinstance(row.get("proposed_ko"), str) or not row["proposed_ko"]:
            raise ValueError(f"v2r Korean proposal is absent: {identifier}")

    rebased: list[dict[str, Any]] = []
    for row in legacy:
        identifier = row["id"]
        current_hash = row.get("source_hash")
        if not isinstance(current_hash, str) or current_hash.upper() != sha_text(ko[identifier]):
            raise ValueError(f"legacy current hash gate differs: {identifier}")
        if identifier in SUPERSEDED_LEGACY_IDS:
            replacement = v2r_by_id[identifier]
            linebreak = replacement.get("validation", {}).get("linebreak")
            if not isinstance(linebreak, dict) or linebreak.get("within_three_line_budget") is not True:
                raise ValueError(f"v2r layout proof is absent: {identifier}")
            rebased.append(
                {
                    "id": identifier,
                    "ko": replacement["proposed_ko"],
                    "reason": "Superseded by the later PC-only v2r semantic review.",
                    "source_hash": replacement["current_hash"],
                    "allowed_format_delta": replacement["allowed_format_delta"],
                    "validation": replacement["validation"],
                    "reference_basis": replacement["reference_basis"],
                    "switch_korean_translation_used": False,
                    "supersedes": "msgev_ko.jsonl",
                }
            )
        else:
            rebased.append(row)
    rebased.sort(key=lambda row: row["id"])
    novel = [row for row in v2r if row["id"] not in EXISTING_V2R_IDS]
    if len(novel) != len(v2r) - len(EXISTING_V2R_IDS):
        raise ValueError("v2r novel split is not exact")
    summary = {
        "legacy_row_count": len(legacy),
        "rebased_row_count": len(rebased),
        "v2r_row_count": len(v2r),
        "v2r_novel_row_count": len(novel),
        "superseded_legacy_ids": sorted(SUPERSEDED_LEGACY_IDS),
        "existing_v2r_ids": sorted(EXISTING_V2R_IDS),
        "source_current_hashes": "all_exact_utf16le",
        "switch_korean_translation_used": False,
        "game_files_written": False,
        "json_encoding": "ensure_ascii_true_utf8",
    }
    return rebased, novel, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rebased, novel, summary = build()
    if args.write:
        for path, rows in ((REBASING_OUTPUT, rebased), (NOVEL_OUTPUT, novel)):
            atomic_write(path, "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows))
        print(json.dumps({**summary, "outputs": [str(REBASING_OUTPUT), str(NOVEL_OUTPUT)]}, ensure_ascii=True, sort_keys=True))
        return 0
    if args.validate:
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
        return 0
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
