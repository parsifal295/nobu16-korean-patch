#!/usr/bin/env python3
"""Regression checks for the Base runtime-verified decision promotion."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_base_msggame_runtime_verified_decisions_v1.py"
SPEC = importlib.util.spec_from_file_location("base_msggame_runtime_verified_decisions_v1", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def main() -> int:
    private_content, public_content, report, prepared = MODULE.build_outputs()
    rows = [
        json.loads(line)
        for line in private_content.splitlines()
        if line
    ]
    assert report["status"] == "PASS"
    assert report["input"]["base_visible_decision_count"] == 23_765
    assert report["input"]["runtime_pending_before"] == 15_651
    assert report["result"]["runtime_verified_promoted"] == 15_651
    assert report["result"]["runtime_pending_after"] == 0
    assert report["result"]["base_candidate_eligible_after"] == 23_765
    assert len(rows) == 23_765
    assert all(row["resource"] == "base_msggame" for row in rows)
    assert not any(row["runtime_review"] == "pending" for row in rows)
    assert sum(row["runtime_review"] == "verified" for row in rows) == 15_651
    verified = [
        row["runtime_vm_verification"]
        for row in rows
        if row["runtime_review"] == "verified"
    ]
    assert all(
        evidence["schema"]
        == "nobu16.kr.base-msggame-runtime-vm-row-verification.v1"
        for evidence in verified
    )
    assert all(evidence["method"] == "reversed_vm_static_analysis" for evidence in verified)
    assert all(len(evidence["record_template_sha256"]) == 64 for evidence in verified)
    assert all(len(evidence["candidate_record_raw_sha256"]) == 64 for evidence in verified)
    assert all(len(evidence["row_verification_sha256"]) == 64 for evidence in verified)
    assert (
        hashlib.sha256(private_content.encode("utf-8")).hexdigest().upper()
        == report["result"]["private_merged_decision_sha256"]
    )
    assert json.loads(public_content) == report
    assert report["steam_write_performed"] is False

    tampered = [dict(row) for row in rows]
    tampered_index = next(
        index
        for index, row in enumerate(tampered)
        if row["runtime_review"] == "verified"
    )
    tampered[tampered_index] = dict(tampered[tampered_index])
    tampered[tampered_index]["runtime_vm_verification"] = dict(
        tampered[tampered_index]["runtime_vm_verification"]
    )
    tampered[tampered_index]["runtime_vm_verification"][
        "row_verification_sha256"
    ] = "0" * 64
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "tampered.jsonl"
        path.write_text(MODULE.canonical_jsonl(tampered), encoding="utf-8", newline="\n")
        try:
            MODULE.ENGINE.validate_decisions(prepared, path, require_complete=False)
        except MODULE.ENGINE.RetranslationError:
            pass
        else:
            raise AssertionError("tampered runtime VM row proof was accepted")
        missing_evidence = [dict(row) for row in rows]
        missing_evidence[tampered_index] = dict(missing_evidence[tampered_index])
        missing_evidence[tampered_index].pop("runtime_vm_verification")
        path.write_text(
            MODULE.canonical_jsonl(missing_evidence),
            encoding="utf-8",
            newline="\n",
        )
        try:
            MODULE.ENGINE.validate_decisions(prepared, path, require_complete=False)
        except MODULE.ENGINE.RetranslationError:
            pass
        else:
            raise AssertionError("audited Base row without runtime VM evidence was accepted")
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
