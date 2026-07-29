#!/usr/bin/env python3
"""Apply the 1,254 post-wave7 local-static runtime promotions as a targeted delta."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
REPO = next(
    parent
    for parent in SCRIPT.parents
    if (parent / "workstreams" / "pc_dialogue_full_retranslation_v0150").is_dir()
)
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
DIALOGUE = REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
PK_AUDIT = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"

PREDECESSOR_BUILDER = (
    DIALOGUE
    / "build_runtime_vm_post_selector292_wave7_root_sharded_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE = (
    TMP
    / "runtime_vm_integrated.post_selector292_wave7_root_sharded_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC = (
    DIALOGUE
    / "runtime_vm_integration.post_selector292_wave7_root_sharded_consolidated_checkpoint.source_free.v1.json"
)
STATIC_BUILDER = (
    PK_AUDIT / "build_pk_msggame_post_wave7_local_static_closure_v1.py"
)
STATIC_DECISIONS = (
    TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_msggame_post_wave7_local_static_runtime_verified_decisions.private.v1.jsonl"
)
STATIC_EVIDENCE = (
    TMP / "pk_msggame_post_wave7_local_static_runtime_verified_evidence.private.v1.json"
)
STATIC_PUBLIC = (
    PK_AUDIT
    / "public"
    / "pk_msggame_post_wave7_local_static_runtime_verified.source_free.v1.json"
)
DEFAULT_PRIVATE = (
    TMP / "runtime_vm_integrated.post_wave7_local_static_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC = (
    DIALOGUE
    / "runtime_vm_integration.post_wave7_local_static_checkpoint."
    "source_free.v1.json"
)

EXPECTED_INPUT_SHA256 = {
    "predecessor_builder": "825D7AA13B5750697CB7A0A548CBE5C90D2F2A5BD7762985F1F17B1FEB556DFF",
    "predecessor_private": "B1CF7F4523DE9411BA5172E7C9DEA946C7646085C83A1480C51807E2DD0C90E7",
    "predecessor_public": "96E03D3EA32FAB5E6701DB75060038A5E967F9617EB0E22E5C91352944626930",
    "static_builder": "372146CEDED272C1D4B00EA9B647EDA54973087103BACDA279225F9CB32B0ABC",
    "static_decisions": "1F026C793D9B8E0A8D5139B5B1B1EFFC7B23899244AE6C38F7C37911E7D423FE",
    "static_evidence": "CFC6ADCCE55D3374AF69D4B3D6002DE6E013E6BFD0E9685915E2F7457713C7A2",
    "static_public": "82B3A5E1C2B8E7558E1992BA65D0B001EC6778B60C9BC12EB2A5483F887E60F4",
}
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private": "502C274DB571359D6C028381F1E77CE70A0AA191CAEC39FD41499044537964ED",
    "public": "CB33295B6416CC3F76041D502C0DA868773CCED8AC6337B60F3D45A30EFBDD84",
}

EXPECTED_ROWS = 52_803
EXPECTED_AFFECTED = 1_254
EXPECTED_UNAFFECTED = 51_549
EXPECTED_PENDING_BEFORE = 5_901
EXPECTED_PENDING_AFTER = 4_647
EXPECTED_ELIGIBLE_AFTER = 48_156
EXPECTED_PK_PROMOTIONS_AFTER = 16_036
EXPECTED_PROMOTED_TOTAL_AFTER = 31_687
EXPECTED_RETRANSLATED_AFTER = 47_811
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_CANDIDATE_SHA256 = (
    "DAB40F2AA8095E67550B69213A53CC777B96B17071FFF5B860CFAEE1A868D7E0"
)
EXPECTED_COORDINATE_SHA256 = (
    "7AD1E0AE524392364726462241867FBFA16A937826B016EA3C719AAB7DA3F7C5"
)
EXPECTED_ROOT_SHA256 = (
    "956C1695A6FDBD2F355F3BACC2E76DD28B15C7DE51E40DC8C8963D2BF58CEE73"
)
ACTION_FIELD = "post_wave7_local_static_update_action"
METHOD = (
    "post_wave7_local_static_1254_classification_only_targeted_ledger_delta"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pc-dialogue-runtime-vm-post-wave7-local-static-"
    "delta-checkpoint.source-free.v1"
)
ROW_VERIFICATION_SCHEMA = (
    "nobu16.kr.pk-msggame-post-wave7-local-static-row-verification.v1"
)


class CheckpointError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckpointError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def text_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("ascii")


def atomic_write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def assert_source_free(value: Any, path: str = "$") -> None:
    forbidden = {
        "translation",
        "translations",
        "dialogue",
        "dialogue_body",
        "source_text",
        "current_text",
        "candidate_text",
        "japanese",
        "korean",
    }
    cjk = re.compile(
        r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7a3]"
    )
    if isinstance(value, dict):
        for key, child in value.items():
            require(str(key) not in forbidden, f"source-bearing key: {path}.{key}")
            assert_source_free(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_source_free(child, f"{path}[{index}]")
    elif isinstance(value, str):
        require(cjk.search(value) is None, f"CJK leaked: {path}")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"not an object: {path}")
    return value


def load_decisions() -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for line in STATIC_DECISIONS.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        key = (str(row["resource"]), str(row["coordinate"]))
        require(key not in result, f"duplicate decision: {key}")
        require(
            row.get("action") == "runtime_promotion"
            and row.get("runtime_review") == "verified"
            and row.get("scope_classification") == "retranslated"
            and row.get("semantic_review") == "approved"
            and row.get("translation_changed") is False
            and row.get("layout_changed") is False
            and row.get("control_or_token_changed") is False
            and row.get("steam_write_performed") is False,
            f"invalid classification-only decision: {key}",
        )
        result[key] = row
    require(len(result) == EXPECTED_AFFECTED, "decision count drift")
    require(
        sha256_bytes(
            "".join(
                f"{coordinate}\n"
                for resource, coordinate in sorted(
                    result,
                    key=lambda item: tuple(map(int, item[1].split(":"))),
                )
                if resource == "pk_msggame"
            ).encode("ascii")
        )
        == EXPECTED_COORDINATE_SHA256,
        "decision coordinate digest drift",
    )
    return result


def validate_static_proof() -> None:
    evidence = load_json(STATIC_EVIDENCE)
    public = load_json(STATIC_PUBLIC)
    require(evidence.get("status") == public.get("status") == "PASS", "proof failed")
    require(
        evidence["counts"]["local_static_rows"] == EXPECTED_AFFECTED
        and evidence["counts"]["local_static_roots"] == 674
        and evidence["counts"]["pending_after"] == EXPECTED_PENDING_AFTER
        and evidence["digests"]["local_static_coordinate_sha256"]
        == EXPECTED_COORDINATE_SHA256
        and evidence["digests"]["local_static_root_sha256"]
        == EXPECTED_ROOT_SHA256,
        "static private proof drift",
    )
    require(
        evidence["proof"]["translation_changes"] == 0
        and evidence["proof"]["layout_changes"] == 0
        and evidence["proof"]["control_or_token_changes"] == 0
        and evidence["proof"]["candidate_byte_changes"] == 0
        and evidence["proof"]["full_rebuild_performed"] is False
        and evidence["proof"]["steam_write_performed"] is False,
        "static mutation proof drift",
    )
    require(
        public["proof"]["candidate_before_sha256"] == EXPECTED_CANDIDATE_SHA256
        and public["proof"]["candidate_after_sha256"] == EXPECTED_CANDIDATE_SHA256
        and public["proof"]["candidate_byte_changes"] == 0,
        "static public candidate proof drift",
    )


def patch_row(
    predecessor: dict[str, Any], decision: Mapping[str, Any]
) -> dict[str, Any]:
    require(
        predecessor.get("resource") == decision["resource"]
        and predecessor.get("coordinate") == decision["coordinate"],
        "decision/predecessor coordinate mismatch",
    )
    require(
        canonical_sha256(predecessor) == decision["predecessor_row_sha256"],
        f"predecessor row drift: {decision['coordinate']}",
    )
    require(
        predecessor.get("runtime_review") == "pending"
        and predecessor.get("scope_classification") == "runtime_fragment_pending"
        and predecessor.get("semantic_review") == "approved",
        f"invalid predecessor state: {decision['coordinate']}",
    )
    translation = str(predecessor["translation"])
    require(
        text_sha256(translation) == decision["translation_utf16le_sha256"],
        f"translation drift: {decision['coordinate']}",
    )
    changed = dict(predecessor)
    changed["runtime_review"] = "verified"
    changed["scope_classification"] = "retranslated"
    changed[ACTION_FIELD] = "runtime_promotion"
    verification = dict(decision["runtime_vm_verification"])
    verification.update(
        {
            "schema": ROW_VERIFICATION_SCHEMA,
            "result": "verified",
            "per_row_game_playback_required": False,
            "outgoing_call_count": 0,
            "outgoing_jump_count": 0,
            "closure_builder_sha256": EXPECTED_INPUT_SHA256["static_builder"],
            "closure_evidence_sha256": EXPECTED_INPUT_SHA256["static_evidence"],
            "closure_public_sha256": EXPECTED_INPUT_SHA256["static_public"],
        }
    )
    changed["runtime_vm_verification"] = verification
    require(changed["translation"] == predecessor["translation"], "translation changed")
    require(changed["layout_review"] == predecessor["layout_review"], "layout changed")
    return changed


def build_outputs() -> tuple[bytes, bytes, dict[str, Any]]:
    inputs = {
        "predecessor_builder": sha256_file(PREDECESSOR_BUILDER),
        "predecessor_private": sha256_file(PREDECESSOR_PRIVATE),
        "predecessor_public": sha256_file(PREDECESSOR_PUBLIC),
        "static_builder": sha256_file(STATIC_BUILDER),
        "static_decisions": sha256_file(STATIC_DECISIONS),
        "static_evidence": sha256_file(STATIC_EVIDENCE),
        "static_public": sha256_file(STATIC_PUBLIC),
    }
    require(inputs == EXPECTED_INPUT_SHA256, f"input drift: {inputs}")
    validate_static_proof()
    decisions = load_decisions()

    output_lines: list[bytes] = []
    seen: set[tuple[str, str]] = set()
    counts: dict[str, int] = {
        "rows": 0,
        "semantic_approved": 0,
        "pending": 0,
        "verified": 0,
        "not_required": 0,
        "retranslated": 0,
        "runtime_fragment_pending": 0,
        "confirmed_non_display": 0,
        "pk_verified": 0,
    }
    with PREDECESSOR_PRIVATE.open("rb") as handle:
        for raw_line in handle:
            require(raw_line.endswith(b"\n"), "unterminated predecessor line")
            predecessor = json.loads(raw_line)
            key = (
                str(predecessor["resource"]),
                str(predecessor["coordinate"]),
            )
            decision = decisions.get(key)
            if decision is None:
                output_lines.append(raw_line)
                row = predecessor
            else:
                require(key not in seen, f"duplicate predecessor key: {key}")
                seen.add(key)
                row = patch_row(predecessor, decision)
                output_lines.append(canonical_bytes(row) + b"\n")
            counts["rows"] += 1
            counts["semantic_approved"] += row.get("semantic_review") == "approved"
            runtime_review = str(row.get("runtime_review"))
            scope = str(row.get("scope_classification"))
            if runtime_review in {"pending", "verified", "not_required"}:
                counts[runtime_review] += 1
            if scope in {
                "retranslated",
                "runtime_fragment_pending",
                "confirmed_non_display",
            }:
                counts[scope] += 1
            counts["pk_verified"] += (
                row.get("resource") == "pk_msggame"
                and runtime_review == "verified"
            )
    require(seen == set(decisions), "not all decisions were applied")
    require(
        counts
        == {
            "rows": EXPECTED_ROWS,
            "semantic_approved": EXPECTED_ROWS,
            "pending": EXPECTED_PENDING_AFTER,
            "verified": EXPECTED_PROMOTED_TOTAL_AFTER,
            "not_required": 16_469,
            "retranslated": EXPECTED_RETRANSLATED_AFTER,
            "runtime_fragment_pending": EXPECTED_PENDING_AFTER,
            "confirmed_non_display": EXPECTED_CONFIRMED_NON_DISPLAY,
            "pk_verified": EXPECTED_PK_PROMOTIONS_AFTER,
        },
        f"result count drift: {counts}",
    )
    private = b"".join(output_lines)
    public: dict[str, Any] = {
        "schema": PUBLIC_SCHEMA,
        "method": METHOD,
        "release_target": "0.15.0",
        "inputs": {f"{key}_sha256": value for key, value in inputs.items()},
        "result": {
            "row_count": EXPECTED_ROWS,
            "affected_row_count": EXPECTED_AFFECTED,
            "unaffected_raw_line_copy_count": EXPECTED_UNAFFECTED,
            "semantic_review_approved": EXPECTED_ROWS,
            "runtime_review_pending": EXPECTED_PENDING_AFTER,
            "fully_candidate_eligible": EXPECTED_ELIGIBLE_AFTER,
            "pk_msggame_promotion_count": EXPECTED_PK_PROMOTIONS_AFTER,
            "promoted_total": EXPECTED_PROMOTED_TOTAL_AFTER,
            "retranslated": EXPECTED_RETRANSLATED_AFTER,
            "confirmed_non_display": EXPECTED_CONFIRMED_NON_DISPLAY,
            "private_integrated_decision_sha256": sha256_bytes(private),
        },
        "targeted_delta": {
            "action": "runtime_promotion",
            "decision_count": EXPECTED_AFFECTED,
            "promotion_count": EXPECTED_AFFECTED,
            "semantic_override_count": 0,
            "translation_change_count": 0,
            "layout_change_count": 0,
            "control_or_token_change_count": 0,
            "coordinate_sha256": EXPECTED_COORDINATE_SHA256,
            "root_count": 674,
            "root_sha256": EXPECTED_ROOT_SHA256,
        },
        "candidate": {
            "before_sha256": EXPECTED_CANDIDATE_SHA256,
            "after_sha256": EXPECTED_CANDIDATE_SHA256,
            "byte_change_count": 0,
        },
        "validation": {
            "targeted_affected_rows_rechecked": EXPECTED_AFFECTED,
            "unaffected_rows_byte_copied": EXPECTED_UNAFFECTED,
            "translation_hashes_matched": EXPECTED_AFFECTED,
            "predecessor_row_hashes_matched": EXPECTED_AFFECTED,
            "full_integration_engine_invoked": False,
            "full_dialogue_rebuild_performed": False,
            "steam_archives_read_only": True,
        },
        "privacy": {
            "source_free": True,
            "contains_dialogue_bodies": False,
            "contains_translations": False,
            "coordinate_lists_kept_private": True,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    assert_source_free(public)
    return private, json_bytes(public), public


def verify_frozen(private: bytes, public: bytes) -> None:
    actual = {
        "private": sha256_bytes(private),
        "public": sha256_bytes(public),
    }
    missing = [key for key, value in EXPECTED_OUTPUT_SHA256.items() if value is None]
    require(not missing, f"unfrozen outputs: {missing}")
    require(actual == EXPECTED_OUTPUT_SHA256, f"output drift: {actual}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--bootstrap", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--private", type=Path, default=DEFAULT_PRIVATE)
    parser.add_argument("--public", type=Path, default=DEFAULT_PUBLIC)
    args = parser.parse_args(argv)

    private, public, report = build_outputs()
    if not args.bootstrap:
        verify_frozen(private, public)
    if args.bootstrap or args.write:
        atomic_write(args.private, private)
        atomic_write(args.public, public)
    else:
        require(args.private.read_bytes() == private, "private output drift")
        require(args.public.read_bytes() == public, "public output drift")
    print(
        json.dumps(
            {
                "status": report["status"],
                "affected": report["result"]["affected_row_count"],
                "pending": report["result"]["runtime_review_pending"],
                "eligible": report["result"]["fully_candidate_eligible"],
                "private_sha256": sha256_bytes(private),
                "public_sha256": sha256_bytes(public),
                "candidate_sha256": report["candidate"]["after_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
