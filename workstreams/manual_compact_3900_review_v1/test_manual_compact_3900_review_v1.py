#!/usr/bin/env python3
"""Verify the read-only 3900-series manual-compaction review artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILD = WORKSTREAM / "build_manual_compact_3900_review_v1.py"
OUTPUT = WORKSTREAM / "public" / "manual_compact_3900_review.v1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    result = subprocess.run([sys.executable, str(BUILD), "verify"], check=False, text=True, capture_output=True)
    require(result.returncode == 0, result.stderr or result.stdout)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    require(payload["schema"] == "nobu16.kr.manual-compact-3900-review.v1", "schema drift")
    require(payload["scope"]["manual_compact_target_count"] == 32, "target count drift")
    require(payload["scope"]["candidate_binary_created"] is False, "candidate must not exist")
    require(payload["safety"]["steam_game_resource_written"] is False, "Steam write recorded")
    require(payload["scope"]["git_or_release_actions_performed"] is False, "Git/release action recorded")
    require(payload["scope"]["network_operation_performed"] is False, "network action recorded")
    entries = payload["entries"]
    require(len(entries) == 32, "entry count drift")
    for entry in entries:
        layout = entry["layout"]
        require(1 <= layout["line_count"] <= 4, f"{entry['entry_id']}: invalid line count")
        require(layout["any_line_exceeds_912px"] is False, f"{entry['entry_id']}: width failure")
        for line in layout["lines"]:
            for key in (
                "display_string",
                "raw_g1n_width_px",
                "effective_width_px",
                "full_width_character_count",
                "half_width_character_count",
                "exceeds_912px",
            ):
                require(key in line, f"{entry['entry_id']}: missing line field {key}")
            require(line["effective_width_px"] <= 912, f"{entry['entry_id']}: effective width overflow")
            require(line["exceeds_912px"] is False, f"{entry['entry_id']}: overflow flag")
        policy = entry["review_policy"]
        require(policy["sentence_shortening_or_deletion_allowed"] is False, f"{entry['entry_id']}: shortening allowed")
        require(policy["japanese_source_linebreaks_used_as_layout_authority"] is False, f"{entry['entry_id']}: JP LF used")
    print("PASS: 3900-series manual compact review is deterministic, source-backed, and Static Patch 007-safe.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
