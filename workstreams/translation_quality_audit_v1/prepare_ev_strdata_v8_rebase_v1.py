#!/usr/bin/env python3
"""Replace three legacy ``陪臣`` rows with PC-only reviewed rows.

The older v7 aggregate remains untouched in ``tmp``.  This helper creates a
new aggregate for the correction builder: it retains the 31 unrelated legacy
rows and replaces IDs 3444, 4050, and 4487 with the PC-Japanese/PC-multilingual
review rows produced by ``prepare_haishin_false_friend_addendum_v1.py``.

It never opens a Switch path and only writes its private output below ``tmp``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_JP = Path(r"F:\Games\NOBU16\MSG\JP\ev_strdata.bin")
LIVE_KO = STEAM / "MSG" / "JP" / "ev_strdata.bin"
SEMANTIC = REPO / "tmp" / "translation_quality_audit_v1" / "semantic"
LEGACY = SEMANTIC / "ev_strdata_findings_rebased_v7.v1.jsonl"
PC_ONLY = SEMANTIC / "haishin_false_friend_addendum.v1.jsonl"
OUTPUT = SEMANTIC / "ev_strdata_findings_rebased_v8.v1.jsonl"
SUPERSEDED_IDS = frozenset({3444, 4050, 4487})
PRISTINE_SHA256 = "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB"


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-16-le")).hexdigest().upper()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"review input is absent: {path}")
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"invalid review row: {path}:{number}")
        rows.append(row)
    return rows


def load_table(path: Path) -> tuple[str, ...]:
    sys.path.insert(0, str(REPO / "tools"))
    from nobu16_lz4 import decompress_wrapper
    from nobu16_msg_table import parse_message_table

    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def atomic_write(path: Path, text: str) -> None:
    root = (REPO / "tmp").resolve()
    resolved = path.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"output must stay below tmp: {resolved}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if sha_file(PRISTINE_JP) != PRISTINE_SHA256:
        raise ValueError("pristine PC Japanese base-event hash differs")
    jp = load_table(PRISTINE_JP)
    ko = load_table(LIVE_KO)
    if len(jp) != 17868 or len(ko) != 17868:
        raise ValueError("base event coordinate count differs")

    legacy = load_jsonl(LEGACY)
    legacy_by_id = {row.get("id"): row for row in legacy if isinstance(row.get("id"), int)}
    if len(legacy_by_id) != len(legacy) or not SUPERSEDED_IDS.issubset(legacy_by_id):
        raise ValueError("legacy aggregate lacks exactly-addressable superseded IDs")
    for identifier, row in legacy_by_id.items():
        if not 0 <= identifier < len(ko) or row.get("ko") != ko[identifier] or row.get("current_hash") != sha_text(ko[identifier]):
            raise ValueError(f"legacy current-text gate differs at {identifier}")

    pc_rows = [
        row
        for row in load_jsonl(PC_ONLY)
        if row.get("resource") == "ev_strdata" and isinstance(row.get("id"), int)
    ]
    pc_by_id = {int(row["id"]): row for row in pc_rows}
    if set(pc_by_id) != SUPERSEDED_IDS or len(pc_by_id) != len(pc_rows):
        raise ValueError("PC-only false-friend input differs from the expected three IDs")
    for identifier, row in pc_by_id.items():
        if row.get("switch_korean_translation_used") is not False:
            raise ValueError(f"PC-only policy differs at {identifier}")
        if row.get("current_hash") != sha_text(ko[identifier]) or row.get("ko") != ko[identifier]:
            raise ValueError(f"PC-only current-text gate differs at {identifier}")
        if row.get("jp_source_hash") != sha_text(jp[identifier]) or "陪臣" not in jp[identifier]:
            raise ValueError(f"PC-only Japanese evidence differs at {identifier}")
        if not isinstance(row.get("proposed_ko"), str) or not row["proposed_ko"]:
            raise ValueError(f"PC-only replacement is absent at {identifier}")

    rebased = [pc_by_id.get(identifier, row) for identifier, row in sorted(legacy_by_id.items())]
    summary = {
        "legacy_row_count": len(legacy),
        "rebased_row_count": len(rebased),
        "superseded_ids": sorted(SUPERSEDED_IDS),
        "pc_only_override_count": len(pc_by_id),
        "source_current_hashes": "all_exact_utf16le",
        "switch_korean_translation_used": False,
        "game_files_written": False,
    }
    return rebased, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows, summary = build()
    if args.write:
        atomic_write(OUTPUT, "".join(json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n" for row in rows))
        summary["output"] = str(OUTPUT)
        summary["output_sha256"] = sha_file(OUTPUT)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
