#!/usr/bin/env python3
"""Promote the fully audited Base runtime decisions into one private decision set.

The source-bearing output stays below ``tmp/``.  The tracked promotion report
contains counts and hashes only.  Steam is read for the normal v0.15.0 input
guards but is never written.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
MAIN_WORKSTREAM = REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
DECISIONS_ROOT = REPO / "tmp" / MAIN_WORKSTREAM.name / "decisions"
DEFAULT_PRIVATE_OUTPUT = (
    REPO
    / "tmp"
    / MAIN_WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = WORKSTREAM / "public" / "base_msggame_runtime_vm_promotion.v1.json"
COVERAGE_PATH = WORKSTREAM / "public" / "base_msggame_runtime_vm_coverage.v1.json"
ENGINE_PATH = MAIN_WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
AUDIT_PATH = WORKSTREAM / "build_base_msggame_runtime_vm_audit_v1.py"
PROMOTION_SCHEMA = "nobu16.kr.base-msggame-runtime-vm-promotion.v1"
ROW_VERIFICATION_SCHEMA = "nobu16.kr.base-msggame-runtime-vm-row-verification.v1"


class PromotionError(ValueError):
    """Raised when a private decision or source-free guard has drifted."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PromotionError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module("base_runtime_vm_promotion_engine", ENGINE_PATH)
AUDIT = load_module("base_runtime_vm_promotion_audit", AUDIT_PATH)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def canonical_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )


def coordinate_key(row: dict[str, Any]) -> tuple[int, int, int]:
    return AUDIT.parse_coordinate(row.get("coordinate"))


def load_base_rows(
    decision_root: Path,
    *,
    engine_prepared: Any,
) -> tuple[list[dict[str, Any]], list[Path]]:
    paths = sorted(decision_root.glob("base_msggame_*.private.v1.jsonl"))
    require(paths, f"no Base private decision segments found below {decision_root}")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in paths:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line:
                continue
            row = json.loads(line)
            require(isinstance(row, dict), f"{path}:{line_number} is not an object")
            require(row.get("resource") == "base_msggame", f"{path}:{line_number} mixes resources")
            coordinate = row.get("coordinate")
            require(isinstance(coordinate, str), f"{path}:{line_number} has no coordinate")
            require(coordinate not in seen, f"duplicate Base coordinate: {coordinate}")
            seen.add(coordinate)
            rows.append(row)
    rows.sort(key=coordinate_key)
    expected = {
        f"{block_id}:{record_id}:{literal_id}"
        for resource, block_id, record_id, literal_id in engine_prepared.visible_targets
        if resource == "base_msggame"
    }
    require(seen == expected, f"Base decision coverage drifted: missing={len(expected - seen)}, extra={len(seen - expected)}")
    return rows, paths


def verified_coverage() -> tuple[dict[str, Any], str]:
    contract = AUDIT.load_json(AUDIT.GHIDRA_CONTRACT)
    pending_rows = AUDIT.load_pending_rows(AUDIT.DEFAULT_DECISIONS)
    decision_rows = AUDIT.load_base_decision_rows(AUDIT.DEFAULT_DECISIONS)
    source_records = AUDIT.archive_records(AUDIT.DEFAULT_BASE_MSGGAME)
    current_records = AUDIT.archive_records(AUDIT.DEFAULT_CURRENT_BASE_MSGGAME)
    candidate_records, current_blob_sha256, candidate_blob_sha256 = (
        AUDIT.build_candidate_records(
            AUDIT.DEFAULT_CURRENT_BASE_MSGGAME,
            decision_rows,
        )
    )
    rebuilt = AUDIT.build_report(
        pending_rows,
        source_records,
        current_records,
        candidate_records,
        contract,
        source_blob_sha256=sha256_bytes(AUDIT.DEFAULT_BASE_MSGGAME.read_bytes()),
        current_blob_sha256=current_blob_sha256,
        candidate_blob_sha256=candidate_blob_sha256,
    )
    rebuilt_text = AUDIT.canonical_json(rebuilt)
    require(COVERAGE_PATH.is_file(), f"tracked coverage report is absent: {COVERAGE_PATH}")
    tracked = COVERAGE_PATH.read_text(encoding="utf-8")
    require(tracked == rebuilt_text, "tracked runtime coverage report drifted")
    require(rebuilt.get("status") == "PASS", "runtime coverage status is not PASS")
    return rebuilt, sha256_bytes(tracked.encode("utf-8"))


def promote_rows(
    rows: list[dict[str, Any]],
    coverage: dict[str, Any],
    coverage_sha256: str,
) -> tuple[list[dict[str, Any]], int]:
    promoted: list[dict[str, Any]] = []
    promoted_count = 0
    universe_digest = coverage["guards"]["pending_universe_digest_sha256"]
    record_guards = coverage["guards"]["record_template_guards"]
    row_guards = coverage["guards"]["row_verification_guards"]
    for source in rows:
        row = dict(source)
        if (
            row.get("scope_classification") == AUDIT.PENDING_CLASS
            and row.get("runtime_review") == "pending"
        ):
            block_id, record_id, _literal_id = coordinate_key(row)
            coordinate = row["coordinate"]
            record_guard = record_guards.get(f"{block_id}:{record_id}")
            row_guard = row_guards.get(coordinate)
            require(isinstance(record_guard, dict), f"missing record guard for {coordinate}")
            require(isinstance(row_guard, str), f"missing row guard for {coordinate}")
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "verified"
            row["runtime_vm_verification"] = {
                "schema": ROW_VERIFICATION_SCHEMA,
                "coverage_report_sha256": coverage_sha256,
                "method": "reversed_vm_static_analysis",
                "pending_universe_digest_sha256": universe_digest,
                "record_template_sha256": record_guard["template_sha256"],
                "candidate_record_raw_sha256": record_guard[
                    "candidate_record_raw_sha256"
                ],
                "row_verification_sha256": row_guard,
                "per_row_game_playback_required": False,
                "result": "verified",
            }
            promoted_count += 1
        promoted.append(row)
    require(
        promoted_count == coverage["scope"]["runtime_automatically_verified_rows"],
        "promotion count differs from the audited pending universe",
    )
    require(
        not any(
            row.get("resource") == "base_msggame"
            and row.get("runtime_review") == "pending"
            for row in promoted
        ),
        "a Base runtime-pending decision survived promotion",
    )
    return promoted, promoted_count


def build_outputs() -> tuple[str, str, dict[str, Any], Any]:
    coverage, coverage_sha256 = verified_coverage()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows, paths = load_base_rows(DECISIONS_ROOT, engine_prepared=prepared)
    promoted, promoted_count = promote_rows(rows, coverage, coverage_sha256)
    private_content = canonical_jsonl(promoted)
    private_sha256 = sha256_bytes(private_content.encode("utf-8"))
    report = {
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG/JP/msggame.bin",
        "input": {
            "decision_segment_count": len(paths),
            "base_visible_decision_count": len(rows),
            "runtime_pending_before": promoted_count,
            "already_candidate_eligible_before": len(rows) - promoted_count,
        },
        "result": {
            "runtime_verified_promoted": promoted_count,
            "runtime_pending_after": 0,
            "base_candidate_eligible_after": len(promoted),
            "private_merged_decision_sha256": private_sha256,
        },
        "evidence": {
            "coverage_report": (
                "workstreams/base_msggame_runtime_vm_audit_v1/public/"
                "base_msggame_runtime_vm_coverage.v1.json"
            ),
            "coverage_report_sha256": coverage_sha256,
            "pending_universe_digest_sha256": (
                coverage["guards"]["pending_universe_digest_sha256"]
            ),
            "semantic_review_approved_reused": True,
            "source_record_hash_guards_rechecked": True,
            "normal_v0150_decision_validator_rechecked": True,
        },
        "qa_boundary": {
            "per_row_game_playback_required": False,
            "representative_game_smoke_test_required_before_release": True,
            "representative_game_smoke_test_status": "not_run",
            "pk_msggame_scope_untouched": True,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "private_merged_decision_stays_below_tmp": True,
        },
        "steam_write_performed": False,
    }
    return private_content, canonical_json(report), report, prepared


def validate_private_output(path: Path, prepared: Any, expected_count: int) -> None:
    replacements = ENGINE.validate_decisions(prepared, path, require_complete=False)
    require(len(replacements) == expected_count, "validated Base replacement count drifted")
    require(
        all(resource == "base_msggame" for resource, *_ in replacements),
        "validated private output contains a non-Base resource",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-output", type=Path, default=DEFAULT_PRIVATE_OUTPUT)
    parser.add_argument("--public-output", type=Path, default=DEFAULT_PUBLIC_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    private_content, public_content, report, prepared = build_outputs()
    if args.check:
        require(args.private_output.is_file(), f"private promoted decisions are absent: {args.private_output}")
        require(
            args.private_output.read_text(encoding="utf-8") == private_content,
            "private promoted decisions drifted",
        )
        require(args.public_output.is_file(), f"public promotion report is absent: {args.public_output}")
        require(args.public_output.read_text(encoding="utf-8") == public_content, "public promotion report drifted")
    else:
        ENGINE.atomic_write(args.private_output, private_content)
    validate_private_output(
        args.private_output,
        prepared,
        report["result"]["base_candidate_eligible_after"],
    )
    if not args.check:
        ENGINE.atomic_write(args.public_output, public_content)
    print(
        f"PASS promoted={report['result']['runtime_verified_promoted']} "
        f"base_eligible={report['result']['base_candidate_eligible_after']} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, PromotionError, ValueError, ENGINE.RetranslationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
