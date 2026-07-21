#!/usr/bin/env python3
"""Verify the read-only 3309–3484 PC ending-region event audit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILD = WORKSTREAM / "build_pc_event_ending_regions_audit_v1.py"
REPORT = WORKSTREAM / "public" / "pc_event_ending_regions_audit.v1.json"

EXPECTED_CORRECTION_IDS = [3331, 3413, 3446, 3475, 3477, 3479]
EXPECTED_W98_CHANGED_IDS = [3288, 3293, 3295, 3298, 3299, 3300, 3302, 3303, 3304, 3305, 3306, 3307]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    result = subprocess.run([sys.executable, str(BUILD), "verify"], check=False, text=True, capture_output=True)
    require(result.returncode == 0, result.stderr or result.stdout)
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    require(payload["schema"] == "nobu16.kr.pc-event-ending-regions-audit.v1", "schema drift")
    scope = payload["scope"]
    require(scope["resource"] == "MSG_PK/JP/msgev.bin", "resource drift")
    require(scope["start_id"] == 3309 and scope["end_id"] == 3484, "ID scope drift")
    require(scope["target_row_count"] == 176, "target count drift")
    require(scope["strict_input_rebased_to"] == "pc_event_gifu_quality_wave98_v1/candidate-final", "W98 rebase drift")
    require(scope["w98_allowed_change_start_id"] == 3287, "W98 allowed-start drift")
    require(scope["w98_allowed_change_end_id"] == 3307, "W98 allowed-end drift")
    require(scope["w98_changed_ids"] == EXPECTED_W98_CHANGED_IDS, "W98 changed-row drift")
    require(scope["w98_target_rows_identical_to_pre_w98"] is True, "W98 overlaps ending audit scope")
    require(scope["candidate_binary_created"] is False, "binary candidate must not exist")
    require(scope["steam_files_written"] is False, "Steam write recorded")
    require(scope["git_or_release_actions_performed"] is False, "Git/release action recorded")
    require(scope["network_operation_performed"] is False, "network action recorded")

    counts = payload["counts"]
    require(counts["classification"] == {
        "reviewed_preserve": 81,
        "runtime_or_ui_hold": 89,
        "static_high_confidence_correction": 6,
    }, "classification count drift")
    require(counts["static_high_confidence_correction_ids"] == EXPECTED_CORRECTION_IDS, "correction IDs drift")
    require(len(counts["runtime_token_hold_ids"]) == 71, "runtime hold count drift")
    require(len(counts["internal_event_key_hold_ids"]) == 18, "internal-key hold count drift")
    require(counts["static_or_proposed_lines_over_912px"] == 0, "static overflow recorded")
    require(counts["static_or_proposed_rows_over_four_lines"] == 0, "four-line overflow recorded")
    require(counts["sentence_shortened_or_deleted"] is False, "shortening recorded")
    sources = payload["sources"]
    require(set(sources) == {"current_ko_w98", "pre_w98_ko_for_nonoverlap_check", "jp", "en", "sc", "tc"}, "source profile drift")
    require(sources["current_ko_w98"]["packed_sha256"] == "62C7F55506DB59A43761DDCE07FB5DA4175AD0AC4B68C03507B37AD52E2AEBD3", "W98 packed pin drift")
    require(sources["pre_w98_ko_for_nonoverlap_check"]["packed_sha256"] == "CFF60029741A596F40EA19DF9F05A8FEC53E240EF09C750B732D052195A04D35", "pre-W98 packed pin drift")

    entries = payload["entries"]
    require(len(entries) == 176, "entry ledger incomplete")
    by_id = {entry["entry_id"]: entry for entry in entries}
    require(sorted(by_id) == list(range(3309, 3485)), "entry IDs are not continuous")
    for entry_id in EXPECTED_CORRECTION_IDS:
        entry = by_id[entry_id]
        require(entry["classification"] == "static_high_confidence_correction", f"{entry_id}: classification drift")
        correction = entry["correction"]
        require(correction["control_signature_preserved"] is True, f"{entry_id}: control drift")
        require(correction["sentence_shortened_or_deleted"] is False, f"{entry_id}: shortening allowed")
        require(correction["japanese_linebreaks_copied"] is False, f"{entry_id}: JP LF copied")
        require(correction["tag_internal_linebreak_inserted"] is False, f"{entry_id}: LF inside tag")
        require(set(correction["direct_pc_sources_for_meaning_review"]) == {"jp", "en", "sc", "tc"}, f"{entry_id}: source coverage")
        layout = correction["proposed_layout"]
        require(layout["line_count"] <= 4, f"{entry_id}: line count overflow")
        require(layout["all_lines_pass_static_patch_007"] is True, f"{entry_id}: Static Patch 007 failure")
        for line in layout["lines"]:
            for key in (
                "display_string",
                "raw_g1n_width_px",
                "effective_width_px",
                "full_width_character_count",
                "half_width_character_count",
                "exceeds_912px",
            ):
                require(key in line, f"{entry_id}: missing line field {key}")
            require(line["effective_width_px"] <= 912, f"{entry_id}: line exceeds 912px")
            require(line["exceeds_912px"] is False, f"{entry_id}: overflow flag")
    require("\x1bCA하루모토\x1bCZ와 결별하자" in by_id[3446]["correction"]["proposed_ko"], "3446 political-break correction missing")
    require("여러 외국과의 교역" in by_id[3413]["correction"]["proposed_ko"], "3413 foreign-trade correction missing")
    require("내가 노리는 것은" in by_id[3477]["correction"]["proposed_ko"], "3477 aspiration correction missing")
    require("\n 다른 누구도" not in by_id[3479]["correction"]["proposed_ko"], "3479 indent not removed")

    for entry in entries:
        if entry["classification"] == "runtime_or_ui_hold" and entry["layout"]["measurement_status"] != "not_applicable_internal_event_key":
            require(entry["layout"]["runtime_display_proven"] is False, f"{entry['entry_id']}: runtime proof overstated")
            require(entry["layout"]["all_lines_pass_static_patch_007"] is None, f"{entry['entry_id']}: literal-only width passed")

    safety = payload["safety"]
    require(safety["candidate_binary_written"] is False, "candidate binary write recorded")
    require(safety["steam_game_resource_written"] is False, "Steam write recorded")
    require(safety["git_operation_performed"] is False, "Git action recorded")
    require(safety["release_published"] is False, "release action recorded")
    require(safety["network_operation_performed"] is False, "network action recorded")
    print("PASS: all 176 ending-region rows are ledgered; six static corrections are source-backed and Static Patch 007-safe.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
