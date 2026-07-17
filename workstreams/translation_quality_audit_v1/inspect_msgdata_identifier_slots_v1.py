#!/usr/bin/env python3
"""Read-only inspector for msgdata localization identifiers with JP text.

Rows are selected from the v5 private inventory flag, then reloaded directly
from the pristine PC Japanese and live PC EN/SC/TC/KO message tables.  It
never reads Switch Korean/historic Korean data and never writes a file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_JP = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msgdata.bin"
)
LIVE_ROOT = STEAM / "MSG_PK"
INVENTORY = REPO / "tmp" / "translation_quality_audit_v1" / "semantic_inventory_v5" / "private_review_queue.jsonl"
EXISTING = REPO / "tmp" / "translation_quality_audit_v1" / "proposals" / "msgdata_ko.jsonl"

sys.path.insert(0, str(REPO / "tools"))
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


FLAG = "target_localization_identifier_for_nonempty_jp"
IDENTIFIER_RE = re.compile(r"^([A-Z]+(?:_[A-Z]+)*)(?:_\d+)?$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load(path: Path) -> list[str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def existing_ids() -> set[int]:
    if not EXISTING.is_file():
        raise SystemExit(f"existing msgdata proposal file is absent: {EXISTING}")
    values: set[int] = set()
    for number, line in enumerate(EXISTING.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        row = json.loads(line)
        identifier = row.get("id")
        if not isinstance(identifier, int) or identifier in values:
            raise SystemExit(f"existing proposal line {number}: invalid or duplicate ID")
        values.add(identifier)
    return values


def group(identifier: str) -> str:
    if identifier.startswith("POLICY_EFFECT_NAME"):
        return "policy"
    if identifier.startswith("LANDMARK_NAME"):
        return "landmark"
    if identifier.startswith("LANDMARKEFFECT_DESC"):
        return "description"
    return "other"


def inventory_rows() -> list[dict[str, object]]:
    if not INVENTORY.is_file():
        raise SystemExit(f"v5 private inventory is absent: {INVENTORY}")
    rows: list[dict[str, object]] = []
    seen: set[int] = set()
    for number, line in enumerate(INVENTORY.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        row = json.loads(line)
        if row.get("resource") != "msgdata" or FLAG not in row.get("flags", []):
            continue
        identifier = int(str(row["coordinate"]))
        if identifier in seen:
            raise SystemExit(f"inventory line {number}: duplicate msgdata ID {identifier}")
        seen.add(identifier)
        rows.append({"id": identifier, "inventory_ko": str(row["ko"])})
    return sorted(rows, key=lambda row: int(row["id"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=("policy", "landmark", "description", "other"))
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()
    if args.offset < 0 or args.limit is not None and args.limit < 0:
        raise SystemExit("offset and limit must be non-negative")

    selected = inventory_rows()
    jp = load(PRISTINE_JP)
    ko = load(LIVE_ROOT / "JP" / "msgdata.bin")
    en = load(LIVE_ROOT / "EN" / "msgdata.bin")
    sc = load(LIVE_ROOT / "SC" / "msgdata.bin")
    tc = load(LIVE_ROOT / "TC" / "msgdata.bin")
    if not (len(jp) == len(ko) == len(en) == len(sc) == len(tc)):
        raise SystemExit("msgdata table count mismatch across PC resources")
    existing = existing_ids()
    prepared: list[dict[str, object]] = []
    for row in selected:
        identifier = int(row["id"])
        if not 0 <= identifier < len(jp):
            raise SystemExit(f"inventory coordinate outside msgdata: {identifier}")
        current = ko[identifier]
        if current != row["inventory_ko"]:
            raise SystemExit(f"{identifier}: inventory KO value no longer matches live file")
        if not IDENTIFIER_RE.fullmatch(current):
            raise SystemExit(f"{identifier}: live KO is not an identifier: {current!r}")
        prepared.append(
            {
                "id": identifier,
                "identifier": current,
                "group": group(current),
                "already_existing_proposal": identifier in existing,
                "jp": jp[identifier],
                "ko": current,
                "en": en[identifier],
                "sc": sc[identifier],
                "tc": tc[identifier],
            }
        )
    summary = {
        "resource": "MSG_PK/JP/msgdata.bin",
        "flagged_id_count": len(prepared),
        "group_counts": dict(sorted(Counter(str(row["group"]) for row in prepared).items())),
        "existing_proposal_overlap_ids": [int(row["id"]) for row in prepared if row["already_existing_proposal"]],
        "all_contexts_same_identifier_count": sum(
            all(row[key] == row["ko"] for key in ("en", "sc", "tc")) for row in prepared
        ),
        "pristine_jp_pc_sha256": sha256_file(PRISTINE_JP),
        "live_steam_ko_sha256": sha256_file(LIVE_ROOT / "JP" / "msgdata.bin"),
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }
    print("@@SUMMARY@@" + json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    if args.summary_only:
        return 0
    output = [row for row in prepared if args.group is None or row["group"] == args.group]
    output = output[args.offset : None if args.limit is None else args.offset + args.limit]
    for row in output:
        print("@@ROW@@" + json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
