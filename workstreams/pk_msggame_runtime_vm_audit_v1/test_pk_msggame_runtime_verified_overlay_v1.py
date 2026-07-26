#!/usr/bin/env python3
"""Tamper, completeness, reproduction, and Steam guards for PK promotion."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_pk_msggame_runtime_verified_overlay_v1.py"
SPEC = importlib.util.spec_from_file_location(
    "pk_msggame_runtime_verified_overlay_v1",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def expect_rejection(function: Callable[[], Any], label: str) -> None:
    try:
        function()
    except (MODULE.PromotionError, MODULE.AUDIT.AuditError):
        return
    raise AssertionError(f"promotion tamper was accepted: {label}")


def validate_rows(
    rows: list[dict[str, Any]],
    context: dict[str, Any],
) -> None:
    MODULE.validate_overlay_rows(
        rows,
        inputs=context["inputs"],
        report=context["coverage"],
        report_file_sha256=context["coverage_file_sha256"],
    )


def main() -> int:
    steam_before = MODULE.live_steam_hash()
    first = MODULE.build_outputs()
    second = MODULE.build_outputs()
    private_content, public_content, report, _inputs, context = first
    assert private_content == second[0]
    assert public_content == second[1]
    assert report == second[2]
    assert report["status"] == "PASS"
    assert report["result"]["private_overlay_rows"] == 4_717
    assert report["input"]["promotion_eligible_rows"] == 4_717
    assert report["input"]["blocked_rows_excluded"] == 5_053
    assert report["exclusion_policy"]["blocked_rows_included"] == 0
    assert report["steam_write_performed"] is False
    assert report["steam_read_guard"]["unchanged"] is True
    assert MODULE.live_steam_hash() == steam_before

    rows = [
        json.loads(line)
        for line in private_content.splitlines()
        if line
    ]
    assert len(rows) == 4_717
    assert len({row["coordinate"] for row in rows}) == 4_717
    assert all(row["status"] == "verified" for row in rows)
    assert all(row["resource"] == "pk_msggame" for row in rows)
    assert all("translation" not in row for row in rows)
    assert all(
        len(row["translation_utf16le_sha256"]) == 64
        for row in rows
    )
    assert all(ord(character) < 128 for character in private_content)
    assert all(ord(character) < 128 for character in public_content)
    validate_rows(rows, context)

    missing = copy.deepcopy(rows[:-1])
    expect_rejection(lambda: validate_rows(missing, context), "completeness")

    coordinate_tamper = copy.deepcopy(rows)
    coordinate_tamper[0]["coordinate"] = coordinate_tamper[1]["coordinate"]
    expect_rejection(
        lambda: validate_rows(coordinate_tamper, context),
        "coordinate",
    )

    translation_hash_tamper = copy.deepcopy(rows)
    translation_hash_tamper[0]["translation_utf16le_sha256"] = "0" * 64
    expect_rejection(
        lambda: validate_rows(translation_hash_tamper, context),
        "translation hash",
    )

    audit_row_tamper = copy.deepcopy(rows)
    audit_row_tamper[0]["audit_binding"]["row_adjudication_sha256"] = "0" * 64
    expect_rejection(
        lambda: validate_rows(audit_row_tamper, context),
        "audit row",
    )

    pair_proof_tamper = copy.deepcopy(rows)
    pair_proof_tamper[0]["audit_binding"]["pair_proof_sha256"] = "0" * 64
    expect_rejection(
        lambda: validate_rows(pair_proof_tamper, context),
        "pair proof",
    )

    report_hash_tamper = copy.deepcopy(rows)
    report_hash_tamper[0]["audit_binding"]["coverage_report_payload_sha256"] = (
        "0" * 64
    )
    expect_rejection(
        lambda: validate_rows(report_hash_tamper, context),
        "coverage report hash",
    )

    donor_guard_tamper = copy.deepcopy(rows)
    donor_guard_tamper[0]["base_donor_binding"]["base_vm_row_guard_sha256"] = (
        "0" * 64
    )
    expect_rejection(
        lambda: validate_rows(donor_guard_tamper, context),
        "Base donor VM guard",
    )

    coverage_tamper = copy.deepcopy(context["coverage"])
    blocked_coordinate = next(
        coordinate
        for coordinate, adjudication in coverage_tamper[
            "row_adjudications"
        ].items()
        if "novel_taint" in adjudication["taints"]
    )
    blocked = coverage_tamper["row_adjudications"][blocked_coordinate]
    blocked["status"] = "promotion_eligible"
    blocked["taints"] = []
    blocked["reason_codes"] = []
    blocked["layout_change_pending"] = False
    blocked["base_vm_row_guard_present"] = True
    coverage_tamper["scope"]["promotion_eligible_rows"] += 1
    coverage_tamper["scope"]["blocked_rows"] -= 1
    coverage_tamper = MODULE.AUDIT.seal_report(coverage_tamper)
    expect_rejection(
        lambda: MODULE.build_overlay_rows(
            inputs=context["inputs"],
            report=coverage_tamper,
            report_file_sha256=context["coverage_file_sha256"],
        ),
        "blocked novel promotion",
    )

    assert MODULE.live_steam_hash() == steam_before
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
