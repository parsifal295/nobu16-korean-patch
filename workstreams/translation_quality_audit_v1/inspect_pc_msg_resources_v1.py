#!/usr/bin/env python3
"""Inspect one PC message resource across pristine JP and live localizations.

This is a read-only audit helper.  It intentionally reads Korean only from the
current PC Steam installation and Japanese only from the declared pristine PC
source.  It does not access Switch files or historic Korean backups.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
STEAM = Path(r"F:\\SteamLibrary\\steamapps\\common\\NOBU16")
PRISTINE_ROOT = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
sys.path.insert(0, str(REPO / "tools"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


def load(path: Path) -> list[str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("resource", choices=("msgbre", "msgire", "msgstf"))
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--only-nonempty", action="store_true")
    parser.add_argument("--ascii", action="store_true")
    args = parser.parse_args()

    name = args.resource + ".bin"
    paths = {
        "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / name,
        "ko": STEAM / "MSG_PK" / "JP" / name,
        "en": STEAM / "MSG_PK" / "EN" / name,
        "sc": STEAM / "MSG_PK" / "SC" / name,
        "tc": STEAM / "MSG_PK" / "TC" / name,
    }
    texts = {language: load(path) for language, path in paths.items()}
    lengths = {language: len(rows) for language, rows in texts.items()}
    if len(set(lengths.values())) != 1:
        raise SystemExit(json.dumps({"length_mismatch": lengths}, ensure_ascii=True))
    stop = min(args.start + args.limit, lengths["jp"])
    for index in range(args.start, stop):
        row = {language: rows[index] for language, rows in texts.items()}
        if args.only_nonempty and not any(row.values()):
            continue
        row["id"] = index
        print(json.dumps(row, ensure_ascii=args.ascii, separators=(",", ":")))
    print(
        json.dumps(
            {
                "resource": args.resource,
                "counts": lengths,
                "pristine_jp_file_sha256": hashlib.sha256(paths["jp"].read_bytes()).hexdigest().upper(),
                "live_ko_file_sha256": hashlib.sha256(paths["ko"].read_bytes()).hexdigest().upper(),
                "switch_korean_translation_used": False,
                "historic_korean_backup_used": False,
            },
            ensure_ascii=args.ascii,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
