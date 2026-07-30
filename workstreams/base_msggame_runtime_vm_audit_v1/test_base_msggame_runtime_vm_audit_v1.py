#!/usr/bin/env python3
"""Regression checks for the Base msggame reversed-VM coverage report."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_base_msggame_runtime_vm_audit_v1.py"
SPEC = importlib.util.spec_from_file_location("base_msggame_runtime_vm_audit_v1", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def main() -> int:
    contract = MODULE.load_json(MODULE.GHIDRA_CONTRACT)
    rows = MODULE.load_pending_rows(MODULE.DEFAULT_DECISIONS)
    decision_rows = MODULE.load_base_decision_rows(MODULE.DEFAULT_DECISIONS)
    source_records = MODULE.archive_records(MODULE.DEFAULT_BASE_MSGGAME)
    current_records = MODULE.archive_records(MODULE.DEFAULT_CURRENT_BASE_MSGGAME)
    candidate_records, current_hash, candidate_hash = MODULE.build_candidate_records(
        MODULE.DEFAULT_CURRENT_BASE_MSGGAME,
        decision_rows,
    )
    report = MODULE.build_report(
        rows,
        source_records,
        current_records,
        candidate_records,
        contract,
        source_blob_sha256=MODULE.sha256_bytes(MODULE.DEFAULT_BASE_MSGGAME.read_bytes()),
        current_blob_sha256=current_hash,
        candidate_blob_sha256=candidate_hash,
    )

    assert report["status"] == "PASS"
    assert report["scope"]["runtime_automatically_verified_rows"] == 15_651
    assert report["scope"]["runtime_pending_records"] == 9_138
    assert report["scope"]["per_row_game_playback_required"] == 0
    assert report["opcode_coverage"]["0143_call_occurrences"] == 4_335
    assert report["opcode_coverage"]["02_dynamic_value_occurrences"] == 8_255
    assert report["opcode_coverage"]["02_selector_family_count"] == 31
    assert report["opcode_coverage"]["02_slot_form_count"] == 56
    assert report["opcode_coverage"]["exact_decoded_pending_record_count"] == 9_138
    assert report["opcode_coverage"]["unknown_pending_gap_byte_count"] == 0
    assert report["reachable_control_flow_graph"]["root_count"] == 160
    assert report["reachable_control_flow_graph"]["reachable_record_count"] == 1_864
    assert report["reachable_control_flow_graph"]["nested_0143_edge_occurrence_count"] == 2
    assert report["reachable_control_flow_graph"]["014a_edge_occurrence_count"] == 2_030
    assert report["reachable_control_flow_graph"]["edge_count"] == 1_951
    assert report["opcode_coverage"]["all_0143_targets_valid"] is True
    assert report["opcode_coverage"]["all_reachable_014a_targets_valid"] is True
    assert report["opcode_coverage"]["all_nested_0143_targets_valid"] is True
    assert len(report["guards"]["record_template_guards"]) == 9_138
    assert len(report["guards"]["row_verification_guards"]) == 15_651
    assert report["symbolic_boundaries"]["all_pending_rows_have_exact_translation_bound_guards"]
    assert report["korean_boundary_risks"]["empty_runtime_morpheme_count"] == 17
    assert report["korean_boundary_risks"]["neutral_particle_row_count"] == 4_062
    assert report["ghidra_contract"]["no_implicit_space_proved"] is True
    assert report["ghidra_contract"]["no_implicit_punctuation_proved"] is True
    assert report["ghidra_contract"]["base_msggame_route_proved"] is True
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
