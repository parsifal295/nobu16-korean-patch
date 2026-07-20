#!/usr/bin/env python3
"""Focused invariants for the private 6000-7999 restoration candidate."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name(
    "build_pc_event_manual_compact_static007_6000_7999_restore_v1.py"
)
spec = importlib.util.spec_from_file_location("restore_6000_7999", BUILDER)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def main() -> int:
    module.source_whitespace_check()
    bundle = module.prepare(require_output_profile=True)
    audit = bundle.audit
    assert audit["actual_changed_row_count"] == module.EXPECTED_CHANGED_COUNT
    assert (
        audit["actual_changed_row_ids_sha256"]
        == module.EXPECTED_CHANGED_IDS_SHA256
    )
    assert len(audit["rows"]) == module.EXPECTED_CHANGED_COUNT
    assert all(row["target_line_count"] <= module.MAX_LINES for row in audit["rows"])
    assert not any(row["any_line_exceeds_912px"] for row in audit["rows"])
    assert all(
        row["target_ko_utf16le_sha256"]
        == row["review_source_reference"]["artifact_proposed_ko_utf16le_sha256"]
        for row in audit["rows"]
    )
    assert all(
        set(row["direct_pc_sources"]) == {"jp", "en", "sc", "tc"}
        and row["review_source_reference"]["artifact"]["entry_id"]
        == row["entry_id"]
        for row in audit["rows"]
    )
    for row in audit["rows"]:
        assert row["target_line_count"] == len(row["target_lines"])
        for line in row["target_lines"]:
            assert set(
                (
                    "display_string",
                    "raw_g1n_width_px",
                    "effective_width_px",
                    "full_width_character_count",
                    "half_width_character_count",
                    "line_count",
                    "exceeds_912px",
                )
            ).issubset(line)
            assert line["effective_width_px"] == math.ceil(
                line["raw_g1n_width_px"] * module.DRAW_FONT_PX
                / module.RAW_FULL_WIDTH_PX
            )
            assert line["effective_width_px"] <= module.MAX_EFFECTIVE_LINE_PX
    assert all(
        sentinel["unchanged"]
        for sentinel in audit["coverage"]["protected_nonreviewed_sentinels"]
    )
    assert audit["source_policy"]["japanese_source_line_breaks_used"] is False
    assert audit["source_policy"]["korean_sentence_shortened_or_deleted"] is False
    assert not any(
        audit["source_policy"][key]
        for key in (
            "steam_game_resource_written",
            "git_operation_performed",
            "network_operation_performed",
            "release_published",
        )
    )
    verification = module.verify_private_candidate(bundle)
    assert verification["status"] == "PASS"
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
