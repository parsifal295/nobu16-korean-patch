#!/usr/bin/env python3
"""Verify the held runtime-token 3442–3611 review artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILD = WORKSTREAM / "build_manual_compact_runtime_3442_3611_review_v1.py"
OUTPUT = WORKSTREAM / "public" / "manual_compact_runtime_3442_3611_review.v1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    result = subprocess.run([sys.executable, str(BUILD), "verify"], check=False, text=True, capture_output=True)
    require(result.returncode == 0, result.stderr or result.stdout)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    require(payload["schema"] == "nobu16.kr.manual-compact-runtime-3442-3611-review.v1", "schema drift")
    require(payload["scope"]["manual_compact_runtime_target_count"] == 17, "target count drift")
    require(payload["scope"]["batch07_nonoverlap_text_asserted"] is True, "batch07 text overlap not asserted")
    require(payload["scope"]["batch07_nonoverlap_name_table_asserted"] is True, "batch07 name overlap not asserted")
    require(payload["scope"]["source_complete_preserve_ids"] == [3442, 3443], "source-complete preserve scope drift")
    require(payload["scope"]["quality_correction_ids"] == [3524, 3579], "quality correction scope drift")
    require(payload["scope"]["candidate_binary_created"] is False, "candidate binary must not exist")
    require(payload["safety"]["steam_game_resource_written"] is False, "Steam write recorded")
    require(payload["safety"]["git_operation_performed"] is False, "Git operation recorded")
    require(payload["safety"]["network_operation_performed"] is False, "network operation recorded")
    entries = payload["entries"]
    require(len(entries) == 17, "entry count drift")
    by_id = {entry["entry_id"]: entry for entry in entries}
    require("또한" in by_id[3442]["proposed_ko"], "3442: source connective shortened")
    require("또한" in by_id[3443]["proposed_ko"], "3443: source connective shortened")
    require("일행" not in by_id[3524]["proposed_ko"], "3524: singular runtime name was pluralized")
    require("[b790]" in by_id[3524]["proposed_ko"], "3524: runtime token drift")
    require("지방 호족들의 원성도 컸습니다" in by_id[3579]["proposed_ko"], "3579: 国衆 meaning correction missing")
    for entry in entries:
        signature = entry["control_signature"]["proposed"]
        require(signature["runtime_tokens"], f"{entry['entry_id']}: runtime token absent")
        policy = entry["review_policy"]
        require(policy["runtime_prefix_semantics_inferred"] is False, f"{entry['entry_id']}: prefix semantics inferred")
        require(policy["sentence_shortening_or_deletion_allowed"] is False, f"{entry['entry_id']}: shortening allowed")
        layout = entry["layout"]
        require(1 <= layout["line_count"] <= 4, f"{entry['entry_id']}: line count invalid")
        for line in layout["lines"]:
            for key in (
                "display_string_template",
                "display_string",
                "display_string_with_strict_name_table_substitution",
                "raw_g1n_width_px",
                "effective_width_px",
                "full_width_character_count",
                "half_width_character_count",
                "exceeds_912px",
            ):
                require(key in line, f"{entry['entry_id']}: line field missing: {key}")
            require(line["effective_width_px"] <= 912, f"{entry['entry_id']}: effective width overflow")
            require(line["exceeds_912px"] is False, f"{entry['entry_id']}: overflow flag")
            for reservation in line["runtime_reservations"]:
                require(reservation["runtime_proven"] is False, f"{entry['entry_id']}: runtime proof overstated")
    print("PASS: 17 held runtime-token rows are source-backed and Static Patch 007-safe without a binary/Steam/Git action.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
