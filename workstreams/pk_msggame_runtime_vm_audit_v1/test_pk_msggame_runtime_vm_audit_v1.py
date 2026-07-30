#!/usr/bin/env python3
"""Regression and tamper tests for the PK reversed-VM reuse audit."""

from __future__ import annotations

import copy
import importlib.util
import struct
import sys
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_pk_msggame_runtime_vm_audit_v1.py"
SPEC = importlib.util.spec_from_file_location(
    "pk_msggame_runtime_vm_audit_v1",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

from msggame_format import MsgGameRecord  # noqa: E402


LITERAL_START = b"\x07\x07\x01"
LITERAL_END = b"\x07\x07\x02"
RETURN = b"\x05\x05\x05"


def expect_audit_error(function: Callable[[], Any], label: str) -> None:
    try:
        function()
    except MODULE.AuditError:
        return
    raise AssertionError(f"tamper was accepted: {label}")


def packed(coordinate: tuple[int, int]) -> int:
    return coordinate[0] * 10_000 + coordinate[1]


def edge(kind: str, target: tuple[int, int]) -> bytes:
    subcode = 0x43 if kind == "call" else 0x4A
    return b"\x01" + bytes([subcode]) + struct.pack("<I", packed(target))


def record(
    coordinate: tuple[int, int],
    texts: tuple[str, ...],
    gaps: tuple[bytes, ...],
) -> MsgGameRecord:
    assert len(gaps) == len(texts) + 1
    data = bytearray()
    for gap, text in zip(gaps, texts):
        data.extend(gap)
        data.extend(LITERAL_START)
        data.extend(text.encode("utf-16-le"))
        data.extend(LITERAL_END)
    data.extend(gaps[-1])
    return MsgGameRecord(
        block_id=coordinate[0],
        record_id=coordinate[1],
        relative_offset=0,
        data=bytes(data),
    )


def valid_pair_maps() -> tuple[
    tuple[int, int],
    tuple[int, int],
    dict[tuple[int, int], MsgGameRecord],
    dict[tuple[int, int], MsgGameRecord],
]:
    base_root = (2, 1)
    pk_root = (2, 2)
    base_a, base_b = (0, 10), (0, 11)
    pk_a, pk_b = (0, 20), (0, 21)
    base = {
        base_root: record(
            base_root,
            ("ROOT",),
            (edge("call", base_a) + edge("call", base_b), RETURN),
        ),
        base_a: record(base_a, ("A",), (b"", RETURN)),
        base_b: record(base_b, ("B",), (b"", RETURN)),
    }
    pk = {
        pk_root: record(
            pk_root,
            ("ROOT",),
            (edge("call", pk_a) + edge("call", pk_b), RETURN),
        ),
        pk_a: record(pk_a, ("A",), (b"", RETURN)),
        pk_b: record(pk_b, ("B",), (b"", RETURN)),
    }
    return base_root, pk_root, base, pk


def pair_audit(
    base_root: tuple[int, int],
    pk_root: tuple[int, int],
    base: dict[tuple[int, int], MsgGameRecord],
    pk: dict[tuple[int, int], MsgGameRecord],
) -> Any:
    return MODULE.compare_record_pair(
        base_root,
        pk_root,
        base_source_records=base,
        base_candidate_records=base,
        pk_source_records=pk,
        pk_candidate_records=pk,
    )


def test_synthetic_pair_and_tampers() -> None:
    base_root, pk_root, base, pk = valid_pair_maps()
    clean = pair_audit(base_root, pk_root, base, pk)
    assert clean.eligible
    assert clean.call_occurrences == 2
    assert not clean.taints

    swapped = dict(pk)
    swapped[pk_root] = record(
        pk_root,
        ("ROOT",),
        (edge("call", (0, 21)) + edge("call", (0, 20)), RETURN),
    )
    swapped_result = pair_audit(base_root, pk_root, base, swapped)
    assert "closure_taint" in swapped_result.taints
    assert any("sibling" in value for value in swapped_result.reason_codes)

    kind_changed = dict(pk)
    kind_changed[pk_root] = record(
        pk_root,
        ("ROOT",),
        (edge("jump", (0, 20)) + edge("call", (0, 21)), RETURN),
    )
    kind_result = pair_audit(base_root, pk_root, base, kind_changed)
    assert "novel_taint" in kind_result.taints
    assert "control_edge_kind_or_order" in kind_result.reason_codes

    selector_base_root = (3, 1)
    selector_pk_root = (3, 2)
    selector_base = {
        selector_base_root: record(
            selector_base_root,
            ("S",),
            (b"\x02\x46\x32", RETURN),
        )
    }
    selector_pk = {
        selector_pk_root: record(
            selector_pk_root,
            ("S",),
            (b"\x02\x46\x33", RETURN),
        )
    }
    selector_result = pair_audit(
        selector_base_root,
        selector_pk_root,
        selector_base,
        selector_pk,
    )
    assert "novel_taint" in selector_result.taints
    assert "selector_property_or_slot" in selector_result.reason_codes

    boundary_pk = {
        selector_pk_root: record(
            selector_pk_root,
            ("S",),
            (b"", b"\x02\x46\x32" + RETURN),
        )
    }
    boundary_result = pair_audit(
        selector_base_root,
        selector_pk_root,
        selector_base,
        boundary_pk,
    )
    assert "novel_taint" in boundary_result.taints
    assert "literal_boundary" in boundary_result.reason_codes


def row_validation_kwargs(inputs: Any) -> dict[str, Any]:
    return {
        "prefill_report": inputs.prefill_report,
        "base_promoted_rows": inputs.base_promoted_rows,
        "base_coverage": inputs.base_coverage,
        "base_source_records": inputs.base_source_records,
        "base_candidate_records": inputs.base_candidate_records,
        "pk_source_records": inputs.pk_source_records,
        "pk_current_records": inputs.pk_current_records,
        "pk_candidate_records": inputs.pk_candidate_records,
    }


def test_real_inputs_and_report_tampers() -> None:
    inputs = MODULE.build_inputs()
    assert len(inputs.rows) == MODULE.EXPECTED_PENDING_ROWS
    kwargs = row_validation_kwargs(inputs)
    first = copy.deepcopy(inputs.rows[0])
    clean = MODULE.validate_row_binding(first, **kwargs)
    assert clean["coordinate"] == first["coordinate"]

    translation_tamper = copy.deepcopy(first)
    translation_tamper["translation"] += "X"
    expect_audit_error(
        lambda: MODULE.validate_row_binding(translation_tamper, **kwargs),
        "translation",
    )

    donor_tamper = copy.deepcopy(first)
    donor_tamper["base_exact_reuse_prefill"]["base_coordinate"] = "0:0:0"
    expect_audit_error(
        lambda: MODULE.validate_row_binding(donor_tamper, **kwargs),
        "donor",
    )

    report = MODULE.build_report(inputs)
    MODULE.validate_report(report)
    assert report["scope"]["runtime_pending_rows"] == MODULE.EXPECTED_PENDING_ROWS
    assert report["opcode_coverage"]["raw_regex_operand_masking_used"] is False
    assert report["opcode_coverage"]["unknown_gap_byte_count"] == 0
    assert report["blockers"]["prefill_global_operand_masked_novel_rows"] == 25
    assert (
        report["blockers"][
            "prefill_global_operand_masked_novel_rows_blocked_as_novel"
        ]
        == 25
    )
    assert report["blockers"]["exact_donor_operand_masked_mismatch_rows"] == 83
    assert (
        report["blockers"]["exact_donor_mismatch_rows_blocked_as_novel"]
        == 83
    )

    hash_tamper = copy.deepcopy(report)
    hash_tamper["scope"]["blocked_rows"] += 1
    expect_audit_error(
        lambda: MODULE.validate_report(hash_tamper),
        "report hash",
    )

    novel_coordinate = next(
        coordinate
        for coordinate, value in report["row_adjudications"].items()
        if "novel_taint" in value["taints"]
    )
    promotion_tamper = copy.deepcopy(report)
    promoted = promotion_tamper["row_adjudications"][novel_coordinate]
    promoted["status"] = "promotion_eligible"
    promoted["taints"] = []
    promoted["reason_codes"] = []
    promoted["layout_change_pending"] = False
    promoted["base_vm_row_guard_present"] = True
    promotion_tamper["scope"]["promotion_eligible_rows"] += 1
    promotion_tamper["scope"]["blocked_rows"] -= 1
    promotion_tamper = MODULE.seal_report(promotion_tamper)
    expect_audit_error(
        lambda: MODULE.validate_report(promotion_tamper),
        "novel promotion",
    )


def main() -> int:
    contract = MODULE.read_json(MODULE.GHIDRA_CONTRACT)
    MODULE.verify_contract(contract)
    assert contract["pk_message_route_proof"]["locale_directories"]["JP"] == {
        "string": "MSG_PK/JP",
        "address": "0x14154C908",
    }
    assert (
        contract["pk_message_route_proof"]["loaded_object_binding"]["vtable_slots"][
            "+0x18"
        ]
        == "0x1409F7490"
    )
    test_synthetic_pair_and_tampers()
    test_real_inputs_and_report_tampers()
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
