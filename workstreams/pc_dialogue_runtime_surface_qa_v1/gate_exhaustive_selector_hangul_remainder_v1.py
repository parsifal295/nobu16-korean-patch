#!/usr/bin/env python3
"""Gate a current direct-selector Hangul universe against exact review.

The classification contract is frozen from the exhaustive Base95/PK199
review.  Reviewed-false rows are accepted only by exact
resource/coordinate/group/property/literal-hash signature.  Reviewed actual
rows remain release-blocking until the no-space row disappears.  Any new or
changed signature is unresolved and also blocks release.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

import classify_exhaustive_selector_hangul_remainder_v1 as CLASSIFY


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
SCHEMA = "nobu16.kr.selector-hangul-remainder-exact-gate.v1"
DEFAULT_CONTRACT = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "selector-hangul-remainder-classification.source-free.v1.json"
)
DEFAULT_CURRENT = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "selector-hangul-remainder-current.private.v1.json"
)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def contract_rows(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for resource in contract["resources"].values()
        for row in resource["rows"]
    ]


def build_report(
    contract: dict[str, Any],
    current: dict[str, Any],
    *,
    contract_path: Path,
    current_path: Path,
) -> dict[str, Any]:
    reviewed = contract_rows(contract)
    exact_false = {
        row["signature"]
        for row in reviewed
        if row["decision"] == "reviewed_false"
    }
    exact_actual = {
        row["signature"]
        for row in reviewed
        if row["decision"] == "actual_missing_space_or_carrier"
    }
    resources: dict[str, Any] = {}
    all_rows: list[dict[str, Any]] = []
    for resource, value in current["resources"].items():
        rows: list[dict[str, Any]] = []
        for candidate in value["candidates"]:
            row_signature = CLASSIFY.signature(resource, candidate)
            if row_signature in exact_false:
                decision = "reviewed_false"
            elif row_signature in exact_actual:
                decision = "actual_residual"
            else:
                decision = "unresolved"
            row = {
                "resource": resource,
                "block_id": int(candidate["block_id"]),
                "record_id": int(candidate["record_id"]),
                "literal_id": int(candidate["literal_id"]),
                "selector_group": int(candidate["selector_group"]),
                "selector_property": candidate["selector_property"],
                "literal_utf16le_sha256": CLASSIFY.utf16le_sha256(
                    str(candidate["literal"])
                ),
                "signature": row_signature,
                "decision": decision,
            }
            rows.append(row)
        counts = Counter(row["decision"] for row in rows)
        resources[resource] = {
            "path": value["path"],
            "sha256": value["sha256"],
            "candidate_count": len(rows),
            "reviewed_false_count": counts["reviewed_false"],
            "actual_residual_count": counts["actual_residual"],
            "unresolved_count": counts["unresolved"],
            "rows": rows,
        }
        all_rows.extend(rows)
    counts = Counter(row["decision"] for row in all_rows)
    release_blocking_count = (
        counts["actual_residual"] + counts["unresolved"]
    )
    contract_valid = (
        contract["status"] == "PASS"
        and int(contract["unresolved_count"]) == 0
        and len(reviewed) == int(contract["universe_candidate_count"])
    )
    return {
        "schema": SCHEMA,
        "status": (
            "PASS"
            if contract_valid and release_blocking_count == 0
            else "FAIL"
        ),
        "release_target": "0.15.0",
        "classification_contract_valid": contract_valid,
        "classification_contract_path": str(contract_path.resolve()),
        "classification_contract_sha256": sha256_path(contract_path),
        "classification_coordinate_contract_sha256":
            contract["coordinate_contract_sha256"],
        "current_universe_path": str(current_path.resolve()),
        "current_universe_sha256": sha256_path(current_path),
        "baseline_universe_candidate_count":
            contract["universe_candidate_count"],
        "baseline_classified_actual_count":
            contract["classified_actual_count"],
        "baseline_classified_false_count":
            contract["classified_false_count"],
        "current_candidate_count": len(all_rows),
        "current_reviewed_false_count": counts["reviewed_false"],
        "actual_residual_count": counts["actual_residual"],
        "unresolved_count": counts["unresolved"],
        "release_blocking_count": release_blocking_count,
        "resources": resources,
        "contract": {
            "reviewed_false_exact_signature_only": True,
            "actual_row_must_disappear": True,
            "new_or_changed_signature_is_unresolved": True,
            "all_current_rows_classified": True,
            "reviewed_term_and_call_jump_gate_required_separately": True,
        },
        "source_or_translation_bodies_omitted": True,
        "steam_write_performed": False,
    }


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--classification-contract",
        type=Path,
        default=DEFAULT_CONTRACT,
    )
    parser.add_argument(
        "--current-universe",
        type=Path,
        default=DEFAULT_CURRENT,
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    contract = json.loads(
        args.classification_contract.read_text(encoding="utf-8")
    )
    current = json.loads(
        args.current_universe.read_text(encoding="utf-8")
    )
    report = build_report(
        contract,
        current,
        contract_path=args.classification_contract,
        current_path=args.current_universe,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        canonical_json(report),
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "current_candidate_count":
                    report["current_candidate_count"],
                "current_reviewed_false_count":
                    report["current_reviewed_false_count"],
                "actual_residual_count":
                    report["actual_residual_count"],
                "unresolved_count": report["unresolved_count"],
                "release_blocking_count":
                    report["release_blocking_count"],
            },
            sort_keys=True,
        )
    )
    return int(args.strict and report["status"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
