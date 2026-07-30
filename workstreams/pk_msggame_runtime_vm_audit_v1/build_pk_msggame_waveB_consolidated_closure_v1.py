#!/usr/bin/env python3
"""Union the three frozen WaveB caller reviews and rebuild the PK candidate.

Dialogue-bearing reviewer artifacts and the candidate stay below ``tmp/``.
This tracked verifier emits only a source-free public closure.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
REPO = next(
    parent
    for parent in SCRIPT.parents
    if (parent / "workstreams" / "pk_msggame_runtime_vm_audit_v1").is_dir()
)
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
AUDIT = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"
DIALOGUE = REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
CHECKPOINT = (
    TMP / "runtime_vm_integrated.post_waveA_consolidated_checkpoint.private.v1.jsonl"
)
ASSIGNMENT = (
    TMP / "pk_msggame_post_waveA_waveB_caller_assignment.final.private.v1.json"
)
PACKETS = tuple(
    TMP
    / "pk_msggame_post_waveA_waveB_caller_final_packets"
    / f"bundle{index}.final.private.v1.json"
    for index in range(3)
)
ENGINE_BUILDER = DIALOGUE / "build_pc_dialogue_full_retranslation_v0150.py"
SHADOW_CURRENT = (
    TMP
    / "development_steam_root_pre_base_runtime_apply_13a404f"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
DEFAULT_DECISIONS = TMP / "pk_msggame_waveB_union_decisions.private.v1.jsonl"
DEFAULT_EVIDENCE = TMP / "pk_msggame_waveB_union_evidence.private.v1.json"
DEFAULT_CANDIDATE = TMP / "pk_msggame_waveB_union_candidate.private.v1.bin"
DEFAULT_PUBLIC = (
    AUDIT
    / "public"
    / "pk_msggame_waveB_consolidated_closure.source_free.v1.json"
)
REVIEW_INPUTS = {
    "b0_builder":
        TMP / "build_pk_msggame_waveB_bundle0_review.private.v1.py",
    "b0_proposals":
        TMP / "pk_msggame_waveB_bundle0_proposals.private.v1.jsonl",
    "b0_decisions":
        TMP
        / "decisions"
        / "runtime_verification_overlays"
        / "pk_msggame_waveB_bundle0_runtime_verified_decisions.private.v1.jsonl",
    "b0_evidence":
        TMP / "pk_msggame_waveB_bundle0_review_evidence.private.v1.json",
    "b0_public":
        TMP / "pk_msggame_waveB_bundle0_review.source_free.v1.json",
    "b1_builder":
        TMP / "build_pk_msggame_waveB_bundle1_final_review.private.v1.py",
    "b1_proposals":
        TMP / "pk_msggame_waveB_bundle1_final_proposals.private.v1.jsonl",
    "b1_decisions":
        TMP
        / "decisions"
        / "runtime_verification_overlays"
        / "pk_msggame_waveB_bundle1_final_runtime_verified_decisions.private.v1.jsonl",
    "b1_evidence":
        TMP / "pk_msggame_waveB_bundle1_final_review_evidence.private.v1.json",
    "b1_public":
        TMP / "pk_msggame_waveB_bundle1_final_review.source_free.v1.json",
    "b2_builder":
        TMP / "build_pk_msggame_waveB_bundle2_review.private.v1.py",
    "b2_proposals":
        TMP / "pk_msggame_waveB_bundle2_proposals.private.v1.jsonl",
    "b2_decisions":
        TMP
        / "decisions"
        / "runtime_verification_overlays"
        / "pk_msggame_waveB_bundle2_runtime_verified_decisions.private.v1.jsonl",
    "b2_evidence":
        TMP / "pk_msggame_waveB_bundle2_review_evidence.private.v1.json",
    "b2_public":
        TMP / "pk_msggame_waveB_bundle2_review.source_free.v1.json",
}
DEFAULT_DECISION_PATHS = (
    REVIEW_INPUTS["b0_decisions"],
    REVIEW_INPUTS["b1_decisions"],
    REVIEW_INPUTS["b2_decisions"],
)
EXPECTED_REVIEW_INPUT_SHA256 = {
    "b0_builder": "DB93A240A16B71A936596897B7B2EFB2139C462114397F85BCABFABD902537E2",
    "b0_proposals": "CA207B8A461949067F3893CBC1991C5A3751E2D97778B5B7B99A620BDCE1B283",
    "b0_decisions": "F506594E9D9DD37BB255B7F97159B472662CE6B7079245A6604BD44AA02E8EDD",
    "b0_evidence": "93939123055328CA970D64844F56287663322BBB6338A954F04E68A95A053E16",
    "b0_public": "63017E2416A28ECB8E3133872CBBEBFA945C7BC6D098416803A1A24AF7FBD5AF",
    "b1_builder": "80D4833922678BB7C01764E3395A983CD76B13A73A78E5A0A8E20FCB6FECE8DE",
    "b1_proposals": "690863E280B618017B22CC8EEE8C6944DE0CAFD96C29432647A1F66B0A92CBD3",
    "b1_decisions": "3B1DB79361182BB2ACED88663AB6BAB25066C4698B6024506DAB9E9C733730B9",
    "b1_evidence": "72DD6235F27A3839CB2878065FBAF8543E23CFAAE03FF480441EA001121064F4",
    "b1_public": "F4686C0508C53F749584892752C5B6721A7C0D755AF8B57999924052BA8DEFC1",
    "b2_builder": "9FD386E0F2BE57566FDC2B606CEF1447D066356010E24D661B569FEE74F60B67",
    "b2_proposals": "8C3EAAE90C9D5F69B6FC1118AE08CF87DBE96D1A3E6F41FC3FF97CFB8F68C6BF",
    "b2_decisions": "23A921230B88253DFC2B4AAEB81154FB75C757D018AD93C4B13351E71345B465",
    "b2_evidence": "D7366C208695AE7F9FC39F55648E72144CFFB89B0F9E8C99C4FDE4BBC36C2587",
    "b2_public": "6804C4047C5CB3110069960000FA08A3F877877DC220653E949540D13793338A",
}
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "decisions": "FC0EDD1AF8F4EA67E98C16724526503BA1DCED18D69347DC9DFB1E74DF931E44",
    "evidence": "E0991999F909AC7630C510118241D204385ABBD08B096E31BF0EB58DB9783430",
    "candidate": "8EB28B349E704643B633CAF69640F4BAA1BC90B4E3F3505035069B9301C6008B",
    "public": "8A4856502B3743CB72E716BC40CDE1DA14F8AEC1A23842AAD7FB0AFD3D2B4267",
}

EXPECTED_INPUT_SHA256 = {
    "checkpoint": "F7B2AA9642E6FDC80920B091991C41F7EC08590E5DE778326EB72E3C8BA67E1A",
    "assignment": "37180F050DDAC42D322E8B7EA58F30B4B736443794AB46DEBDF0BFD83E458775",
    "packet0": "00CBDA5E313291F3DF6CE9A5CECEF43843E54B108B7875B015F09B0E6F3C47A1",
    "packet1": "12A125F5891F1C4DEF3934F0E635649DDB2B71C31D88FF276D0743B35AA536CF",
    "packet2": "9BEBF0FD1ED359925DD5C5B99A3B002C6D83B06893ECFCB74A66CBFD27899EC9",
    "engine_builder": "CF32112EB7B0BA578DF9EF2E9D2A5C92818E25AC2217FE867BE7968F92D8372E",
    "shadow_current": "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
}
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "A2811CA8B9A53C84678727737FDA1729520FB4AB16F19AAB537C51292D1EEE78"
)
EXPECTED_CALLER_COORDINATES = 1_214
EXPECTED_CALLER_ROOTS = 717
EXPECTED_ACTUAL_BRANCHES = 606_902


class UnionError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise UnionError(message)


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


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return parts


def parse_root(value: str) -> tuple[int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 2, f"invalid root: {value}")
    return parts


def digest_lines(values: Iterable[str], parser: Any) -> str:
    return sha256_bytes(
        "".join(f"{value}\n" for value in sorted(set(values), key=parser)).encode(
            "ascii"
        )
    )


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            require(
                isinstance(row, dict),
                f"non-object decision: {path}:{line_number}",
            )
            rows.append(row)
    return rows


def build_outputs(
    decision_paths: Sequence[Path],
) -> tuple[bytes, bytes, bytes, bytes, dict[str, Any]]:
    inputs = {
        "checkpoint": sha256_file(CHECKPOINT),
        "assignment": sha256_file(ASSIGNMENT),
        "packet0": sha256_file(PACKETS[0]),
        "packet1": sha256_file(PACKETS[1]),
        "packet2": sha256_file(PACKETS[2]),
        "engine_builder": sha256_file(ENGINE_BUILDER),
        "shadow_current": sha256_file(SHADOW_CURRENT),
    }
    require(inputs == EXPECTED_INPUT_SHA256, f"frozen input drift: {inputs}")
    review_inputs = {
        key: sha256_file(path) for key, path in REVIEW_INPUTS.items()
    }
    require(
        review_inputs == EXPECTED_REVIEW_INPUT_SHA256,
        f"frozen reviewer input drift: {review_inputs}",
    )
    require(decision_paths, "no WaveB decisions supplied")
    require(
        len({path.resolve() for path in decision_paths}) == len(decision_paths),
        "duplicate decision paths",
    )

    assignment = json.loads(ASSIGNMENT.read_text(encoding="utf-8"))
    require(
        assignment["status"] == "PASS_FROZEN_WAVE_A_BOUND_REVIEW_AUTHORIZED"
        and assignment["result"]["caller_pending_coordinate_count"]
        == EXPECTED_CALLER_COORDINATES
        and assignment["result"]["caller_root_count"] == EXPECTED_CALLER_ROOTS
        and assignment["result"]["actual_branch_count"]
        == EXPECTED_ACTUAL_BRANCHES,
        "WaveB assignment scope drift",
    )
    root_to_bundle: dict[str, int] = {}
    pending_by_root: dict[str, frozenset[str]] = {}
    coordinate_to_bundle: dict[str, int] = {}
    branch_count = 0
    terminal_roots: set[str] = set()
    for bundle_id, path in enumerate(PACKETS):
        packet = json.loads(path.read_text(encoding="utf-8"))
        require(
            packet["bundle_id"] == bundle_id
            and packet["contract"]["review_start_authorized"] is True
            and packet["contract"]["terminal_records_read_only"] is True,
            f"packet contract drift: B{bundle_id}",
        )
        for owned in packet["owned_roots"]:
            root = str(owned["root"])
            require(root not in root_to_bundle, f"caller root overlap: {root}")
            root_to_bundle[root] = bundle_id
            coordinates = frozenset(map(str, owned["pending_coordinates"]))
            require(coordinates, f"empty caller root: {root}")
            pending_by_root[root] = coordinates
            for coordinate in coordinates:
                require(
                    coordinate not in coordinate_to_bundle,
                    f"caller coordinate overlap: {coordinate}",
                )
                coordinate_to_bundle[coordinate] = bundle_id
            branch_count += int(owned["branch_count"])
            for call in owned["calls"]:
                terminal_roots.update(map(str, call["terminal_roots"]))
    require(
        len(root_to_bundle) == EXPECTED_CALLER_ROOTS
        and len(coordinate_to_bundle) == EXPECTED_CALLER_COORDINATES
        and branch_count == EXPECTED_ACTUAL_BRANCHES,
        "packet union drift",
    )
    require(
        not set(root_to_bundle) & terminal_roots,
        "caller/terminal root ownership overlap",
    )

    checkpoint_rows: dict[str, dict[str, Any]] = {}
    checkpoint_raw_sha256: dict[str, str] = {}
    replacements: dict[tuple[int, int, int], str] = {}
    row_count = 0
    pending_count = 0
    with CHECKPOINT.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row_count += 1
            row = json.loads(line)
            if row.get("resource") != "pk_msggame":
                continue
            coordinate = str(row["coordinate"])
            checkpoint_rows[coordinate] = row
            checkpoint_raw_sha256[coordinate] = sha256_bytes(
                line.encode("utf-8")
            )
            if "translation" in row:
                replacements[parse_coordinate(coordinate)] = str(
                    row["translation"]
                )
            pending_count += row.get("runtime_review") == "pending"
    require(row_count == 52_803 and pending_count == 3_293, "checkpoint drift")

    ENGINE = load_module(ENGINE_BUILDER, "pk_waveB_union_dialogue_engine")
    current_blob = SHADOW_CURRENT.read_bytes()
    predecessor_candidate = ENGINE.rebuild_packed_with_literals(
        current_blob, replacements
    )
    require(
        sha256_bytes(predecessor_candidate)
        == EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
        "predecessor candidate drift",
    )

    accepted: dict[str, dict[str, Any]] = {}
    promotions: dict[str, dict[str, Any]] = {}
    renewals: dict[str, dict[str, Any]] = {}
    blocked_rows = 0
    for path in decision_paths:
        require(path.is_file(), f"missing decisions: {path}")
        for original in load_jsonl(path):
            row = dict(original)
            coordinate = str(row.get("coordinate", ""))
            action = str(row.get("action", ""))
            if action == "runtime_verification_renewal":
                action = "verification_renewal"
                row["action"] = action
            root = ":".join(coordinate.split(":")[:2])
            is_pending = coordinate in coordinate_to_bundle
            is_renewal = not is_pending and root in root_to_bundle
            require(
                row.get("resource") == "pk_msggame"
                and (is_pending or is_renewal),
                f"non-owned decision: {path}:{coordinate}",
            )
            require(root not in terminal_roots, f"terminal write attempted: {root}")
            if action == "blocked":
                require(is_pending, f"blocked renewal: {coordinate}")
                blocked_rows += 1
                continue
            if is_pending:
                require(
                    action.endswith("runtime_promotion"),
                    f"bad promotion action: {coordinate}:{action}",
                )
            else:
                require(
                    action.endswith("verification_renewal"),
                    f"bad renewal action: {coordinate}:{action}",
                )
            require(
                coordinate not in accepted,
                f"accepted coordinate overlap: {coordinate}",
            )
            predecessor = checkpoint_rows[coordinate]
            if is_pending:
                require(
                    predecessor.get("runtime_review") == "pending"
                    and predecessor.get("scope_classification")
                    == "runtime_fragment_pending",
                    f"bad pending predecessor: {coordinate}",
                )
            else:
                require(
                    predecessor.get("runtime_review") == "verified"
                    and predecessor.get("scope_classification") == "retranslated",
                    f"bad renewal predecessor: {coordinate}",
                )
            require(
                row.get("predecessor_row_sha256")
                in {
                    canonical_sha256(predecessor),
                    checkpoint_raw_sha256[coordinate],
                },
                f"predecessor hash drift: {coordinate}",
            )
            translation_value = row.get("translation")
            if translation_value is None:
                require(
                    row.get("translation_changed") is False,
                    f"missing override: {coordinate}",
                )
                translation = str(predecessor["translation"])
                row["translation"] = translation
            else:
                translation = str(translation_value)
            translation_hash = (
                row.get("translation_utf16le_sha256")
                or row.get("after_translation_utf16le_sha256")
            )
            require(
                translation_hash == utf16le_sha256(translation),
                f"translation hash drift: {coordinate}",
            )
            row["translation_utf16le_sha256"] = utf16le_sha256(translation)
            require(
                row.get("runtime_review") == "verified"
                and row.get("semantic_review") == "approved"
                and row.get("layout_review")
                in {
                    "current_relative_raw_g1n_nonexpanding",
                    "all_actual_branches_current_relative_raw_g1n_nonexpanding",
                }
                and row.get("steam_write_performed") is False,
                f"review contract failed: {coordinate}",
            )
            row["layout_review"] = (
                "current_relative_raw_g1n_nonexpanding"
            )
            accepted[coordinate] = row
            (promotions if is_pending else renewals)[coordinate] = row

    for root, coordinates in pending_by_root.items():
        overlap = set(promotions) & coordinates
        require(
            not overlap or overlap == set(coordinates),
            f"partial caller-root promotion: {root}",
        )

    override_coordinates: set[str] = set()
    for coordinate, row in accepted.items():
        translation = str(row["translation"])
        changed = translation != str(checkpoint_rows[coordinate]["translation"])
        require(
            bool(row.get("translation_changed")) == changed,
            f"translation_changed drift: {coordinate}",
        )
        expected_action = (
            "translation_override_and_runtime_promotion"
            if coordinate in promotions and changed
            else "runtime_promotion"
            if coordinate in promotions
            else "translation_override_and_verification_renewal"
            if changed
            else "verification_renewal"
        )
        require(row["action"] == expected_action, f"action drift: {coordinate}")
        if changed:
            replacements[parse_coordinate(coordinate)] = translation
            override_coordinates.add(coordinate)

    candidate = ENGINE.rebuild_packed_with_literals(current_blob, replacements)
    decisions = b"".join(
        canonical_bytes(accepted[coordinate]) + b"\n"
        for coordinate in sorted(accepted, key=parse_coordinate)
    )
    promotion_roots = {
        ":".join(coordinate.split(":")[:2]) for coordinate in promotions
    }
    renewal_roots = {
        ":".join(coordinate.split(":")[:2]) for coordinate in renewals
    }
    report = {
        "schema": "nobu16.kr.pk-msggame-waveB-union-evidence.private.v1",
        "method": "three_bundle_caller_root_atomic_review_union_and_candidate_rebuild",
        "inputs": {
            **inputs,
            "review_artifacts": review_inputs,
            "decision_files": [
                {
                    "path": str(path.resolve().relative_to(REPO)).replace("\\", "/"),
                    "sha256": sha256_file(path),
                }
                for path in decision_paths
            ],
        },
        "counts": {
            "promoted_coordinates": len(promotions),
            "promoted_roots": len(promotion_roots),
            "renewal_coordinates": len(renewals),
            "renewal_roots": len(renewal_roots),
            "translation_overrides": len(override_coordinates),
            "classification_only_actions":
                len(accepted) - len(override_coordinates),
            "observed_block_rows": blocked_rows,
            "pending_before": pending_count,
            "pending_after": pending_count - len(promotions),
        },
        "digests": {
            "promotion_coordinate_sha256":
                digest_lines(promotions, parse_coordinate),
            "promotion_root_sha256":
                digest_lines(promotion_roots, parse_root),
            "renewal_coordinate_sha256":
                digest_lines(renewals, parse_coordinate),
            "renewal_root_sha256":
                digest_lines(renewal_roots, parse_root),
            "override_coordinate_sha256":
                digest_lines(override_coordinates, parse_coordinate),
            "decision_payload_sha256": sha256_bytes(decisions),
            "candidate_before_sha256":
                EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "candidate_after_sha256": sha256_bytes(candidate),
        },
        "proof": {
            "actual_branch_count": EXPECTED_ACTUAL_BRANCHES,
            "all_predecessor_rows_bound": True,
            "all_translation_hashes_bound": True,
            "accepted_coordinate_overlap_count": 0,
            "partial_caller_root_promotion_count": 0,
            "terminal_write_count": 0,
            "full_integration_rebuild_performed": False,
            "steam_write_performed": False,
        },
        "status": "PASS",
    }
    evidence = (
        json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("ascii")
    public = {
        "schema":
            "nobu16.kr.pk-msggame-waveB-consolidated-closure.source-free.v1",
        "method": report["method"],
        "release_target": "0.15.0",
        "inputs": {
            "checkpoint_sha256": inputs["checkpoint"],
            "assignment_sha256": inputs["assignment"],
            "packet_sha256": [
                inputs["packet0"],
                inputs["packet1"],
                inputs["packet2"],
            ],
            "review_artifact_sha256": review_inputs,
            "engine_builder_sha256": inputs["engine_builder"],
        },
        "result": report["counts"],
        "digests": report["digests"],
        "proof": report["proof"],
        "privacy": {
            "source_free": True,
            "contains_dialogue_bodies": False,
            "contains_translations": False,
            "private_reviews_stay_below_tmp": True,
        },
        "status": report["status"],
        "steam_write_performed": False,
    }
    public_payload = (
        json.dumps(public, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("ascii")
    return decisions, evidence, candidate, public_payload, report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--bootstrap-output-pins", action="store_true")
    parser.add_argument("--decision", action="append", type=Path)
    parser.add_argument("--decisions-output", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument("--evidence-output", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--candidate-output", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--public-output", type=Path, default=DEFAULT_PUBLIC)
    args = parser.parse_args(argv)

    decision_paths = tuple(args.decision or DEFAULT_DECISION_PATHS)
    decisions, evidence, candidate, public, report = build_outputs(
        decision_paths
    )
    outputs = (
        ("decisions", args.decisions_output, decisions),
        ("evidence", args.evidence_output, evidence),
        ("candidate", args.candidate_output, candidate),
        ("public", args.public_output, public),
    )
    observed = {
        key: sha256_bytes(payload) for key, _, payload in outputs
    }
    if args.bootstrap_output_pins:
        require(args.write, "pins may only be bootstrapped with --write")
    else:
        require(
            all(EXPECTED_OUTPUT_SHA256.values()),
            "unfrozen WaveB output pins",
        )
        require(
            observed == EXPECTED_OUTPUT_SHA256,
            f"WaveB output drift: {observed}",
        )
    if args.write:
        for _, path, payload in outputs:
            atomic_write(path, payload)
    else:
        for _, path, payload in outputs:
            require(path.is_file(), f"missing output: {path}")
            require(path.read_bytes() == payload, f"output drift: {path}")
    print(
        json.dumps(
            {
                "status": report["status"],
                **report["counts"],
                "candidate_sha256": report["digests"]["candidate_after_sha256"],
                "decisions_sha256": report["digests"]["decision_payload_sha256"],
                "output_sha256": observed,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
