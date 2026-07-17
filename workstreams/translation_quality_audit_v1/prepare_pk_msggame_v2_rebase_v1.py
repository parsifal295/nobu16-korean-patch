#!/usr/bin/env python3
"""Replace one legacy PK-event false-friend row with a PC-only review row.

The v1 aggregate already identifies ``陪臣`` as a false friend.  This rebase
keeps its other rows intact but replaces literal ``17:393:2`` with the newer
PC-only review wording, which avoids needlessly widening the rendered line.
No Switch data is read; output remains a private JSONL artifact under ``tmp``.
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
PRISTINE = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
LIVE_KO = STEAM / "MSG_PK" / "JP" / "msggame.bin"
SEMANTIC = REPO / "tmp" / "translation_quality_audit_v1" / "semantic"
LEGACY = SEMANTIC / "pk_msggame_quality_findings.v1.jsonl"
PC_ONLY = SEMANTIC / "haishin_false_friend_addendum.v1.jsonl"
OUTPUT = SEMANTIC / "pk_msggame_quality_findings_rebased_v2.v1.jsonl"
SUPERSEDED = "17:393:2"
PRISTINE_SHA256 = "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"


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


def load_literals(path: Path) -> dict[str, str]:
    sys.path.insert(0, str(REPO / "workstreams" / "msggame"))
    from msggame_format import iter_literals, parse_packed_msggame

    archive = parse_packed_msggame(path.read_bytes()).archive
    return {f"{item.block_id}:{item.record_id}:{item.literal_id}": item.text for item in iter_literals(archive)}


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


def sort_key(row: dict[str, Any]) -> tuple[int, ...]:
    coordinate = row.get("coordinate")
    if not isinstance(coordinate, str):
        raise ValueError("PK review row lacks a coordinate")
    return tuple(int(part) for part in coordinate.split(":"))


def build() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if sha_file(PRISTINE) != PRISTINE_SHA256:
        raise ValueError("pristine PC Japanese PK msggame hash differs")
    jp = load_literals(PRISTINE)
    ko = load_literals(LIVE_KO)
    if set(jp) != set(ko):
        raise ValueError("PC JP and current Korean literal coordinates differ")

    legacy = load_jsonl(LEGACY)
    legacy_by_coordinate = {row.get("coordinate"): row for row in legacy if isinstance(row.get("coordinate"), str)}
    if len(legacy_by_coordinate) != len(legacy) or SUPERSEDED not in legacy_by_coordinate:
        raise ValueError("legacy PK aggregate lacks exactly-addressable target coordinate")
    for coordinate, row in legacy_by_coordinate.items():
        if coordinate not in ko or row.get("ko") != ko[coordinate] or row.get("current_hash") != sha_text(ko[coordinate]):
            raise ValueError(f"legacy current-text gate differs at {coordinate}")

    matches = [
        row
        for row in load_jsonl(PC_ONLY)
        if row.get("resource") == "pk_msggame" and row.get("coordinate") == SUPERSEDED
    ]
    if len(matches) != 1:
        raise ValueError("PC-only false-friend input differs from the expected PK literal")
    replacement = matches[0]
    if replacement.get("switch_korean_translation_used") is not False:
        raise ValueError("PC-only policy differs")
    if replacement.get("ko") != ko[SUPERSEDED] or replacement.get("current_hash") != sha_text(ko[SUPERSEDED]):
        raise ValueError("PC-only current-text gate differs")
    if replacement.get("jp_source_hash") != sha_text(jp[SUPERSEDED]) or "陪臣" not in jp[SUPERSEDED]:
        raise ValueError("PC-only Japanese evidence differs")
    if not isinstance(replacement.get("proposed_ko"), str) or not replacement["proposed_ko"]:
        raise ValueError("PC-only replacement is absent")

    rebased = [replacement if coordinate == SUPERSEDED else row for coordinate, row in legacy_by_coordinate.items()]
    rebased.sort(key=sort_key)
    summary = {
        "legacy_row_count": len(legacy),
        "rebased_row_count": len(rebased),
        "superseded_coordinate": SUPERSEDED,
        "pc_only_override_count": 1,
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
