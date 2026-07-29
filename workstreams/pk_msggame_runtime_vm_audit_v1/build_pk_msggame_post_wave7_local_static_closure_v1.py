#!/usr/bin/env python3
"""Close post-wave7 PK rows whose final VM records are entirely local/static.

This generator starts directly from the frozen wave-7
checkpoint and uses the exact reversed-VM component decoder.  A pending
record is eligible only when:

* its final candidate contains no selector, call, jump, random-select,
  arithmetic, comparison, logical, or other data-dependent VM component;
* no final-candidate call or jump targets the record; and
* every row remains semantically approved with its predecessor translation
  and layout judgement unchanged.

The generated delta changes classification only.  It never carries
translation text and cannot alter the packed candidate.
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
WORKSTREAM = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)

CHECKPOINT = (
    TMP
    / "runtime_vm_integrated."
    "post_selector292_wave7_root_sharded_consolidated_checkpoint."
    "private.v1.jsonl"
)
VM_BUILDER = WORKSTREAM / "build_pk_msggame_runtime_vm_audit_v1.py"
RANKING_BUILDER = (
    WORKSTREAM / "build_pk_next_selector_family_ranking_v1.py"
)
ENGINE_BUILDER = (
    DIALOGUE_WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
)
SHADOW_CURRENT = (
    TMP
    / "development_steam_root_pre_base_runtime_apply_13a404f"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)

DEFAULT_DECISIONS = (
    TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_msggame_post_wave7_local_static_runtime_verified_decisions."
    "private.v1.jsonl"
)
DEFAULT_EVIDENCE = (
    TMP
    / "pk_msggame_post_wave7_local_static_runtime_verified_evidence."
    "private.v1.json"
)
DEFAULT_PUBLIC = (
    WORKSTREAM
    / "public"
    / "pk_msggame_post_wave7_local_static_runtime_verified."
    "source_free.v1.json"
)

EXPECTED_INPUT_SHA256 = {
    "checkpoint":
        "B1CF7F4523DE9411BA5172E7C9DEA946C7646085C83A1480C51807E2DD0C90E7",
    "vm_builder":
        "B9769DED8D55AB8B73ECF54AB44A1F5C41E693E4681A647910067941DC81DFF0",
    "ranking_builder":
        "19D8F10FC3995AD05A39AD12CD554292A47BF4A1AB572D28359130326FA69391",
    "engine_builder":
        "CF32112EB7B0BA578DF9EF2E9D2A5C92818E25AC2217FE867BE7968F92D8372E",
    "shadow_current":
        "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
}
EXPECTED_WAVE7_CANDIDATE_SHA256 = (
    "DAB40F2AA8095E67550B69213A53CC777B96B17071FFF5B860CFAEE1A868D7E0"
)
EXPECTED_CHECKPOINT_ROWS = 52_803
EXPECTED_WAVE7_PENDING = 5_901
EXPECTED_STATIC_ROWS = 1_254
EXPECTED_STATIC_ROOTS = 674
EXPECTED_PENDING_AFTER = 4_647

# Frozen after the first reproducible bootstrap.
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "decisions":
        "1F026C793D9B8E0A8D5139B5B1B1EFFC7B23899244AE6C38F7C37911E7D423FE",
    "evidence":
        "CFC6ADCCE55D3374AF69D4B3D6002DE6E013E6BFD0E9685915E2F7457713C7A2",
    "public":
        "82B3A5E1C2B8E7558E1992BA65D0B001EC6778B60C9BC12EB2A5483F887E60F4",
}

ALLOWED_LOCAL_COMPONENT_KINDS = frozenset(
    {
        "literal_boundary",
        "block_token",
        "control_tag",
        "output_control",
    }
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-msggame-post-wave7-local-static-closure.private.v1"
)
DECISION_SCHEMA = (
    "nobu16.kr.pk-msggame-post-wave7-local-static-runtime-verified-"
    "decision.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-msggame-post-wave7-local-static-closure-"
    "source-free.v1"
)
METHOD = (
    "wave7_checkpoint_exact_reversed_vm_decoder_"
    "no_data_dependent_components_no_incoming_call_or_jump"
)


class LocalStaticClosureError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LocalStaticClosureError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


VM = load_module(VM_BUILDER, "pk_post_wave7_local_static_vm")
RANKING = load_module(
    RANKING_BUILDER, "pk_post_wave7_local_static_ranking"
)
ENGINE = load_module(
    ENGINE_BUILDER, "pk_post_wave7_local_static_dialogue_engine"
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def serialized_json(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("ascii")


def serialized_jsonl(values: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(canonical_bytes(value) + b"\n" for value in values)


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return parts


def parse_root(value: str) -> tuple[int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 2, f"invalid root: {value}")
    return parts


def coordinate_digest(values: Iterable[str]) -> str:
    payload = "".join(
        f"{value}\n"
        for value in sorted(set(values), key=parse_coordinate)
    ).encode("ascii")
    return sha256_bytes(payload)


def root_digest(values: Iterable[str]) -> str:
    payload = "".join(
        f"{value}\n" for value in sorted(set(values), key=parse_root)
    ).encode("ascii")
    return sha256_bytes(payload)


def text_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
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


def relative(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


def build_outputs() -> tuple[bytes, bytes, bytes, dict[str, Any]]:
    inputs = {
        "checkpoint": sha256_file(CHECKPOINT),
        "vm_builder": sha256_file(VM_BUILDER),
        "ranking_builder": sha256_file(RANKING_BUILDER),
        "engine_builder": sha256_file(ENGINE_BUILDER),
        "shadow_current": sha256_file(SHADOW_CURRENT),
    }
    require(inputs == EXPECTED_INPUT_SHA256, f"input hash drift: {inputs}")

    rows: dict[str, dict[str, Any]] = {}
    replacements: dict[tuple[int, int, int], str] = {}
    pending_by_root: dict[tuple[int, int], set[str]] = {}
    row_count = 0
    checkpoint_pk_pending = 0
    with CHECKPOINT.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row_count += 1
            row = json.loads(line)
            if row.get("resource") != "pk_msggame":
                continue
            coordinate = str(row["coordinate"])
            key = parse_coordinate(coordinate)
            require(coordinate not in rows, f"duplicate checkpoint row: {coordinate}")
            rows[coordinate] = row
            if "translation" in row:
                replacements[key] = str(row["translation"])
            if row.get("runtime_review") == "pending":
                checkpoint_pk_pending += 1
                pending_by_root.setdefault(key[:2], set()).add(coordinate)
    require(row_count == EXPECTED_CHECKPOINT_ROWS, "checkpoint row count drift")
    require(
        checkpoint_pk_pending == EXPECTED_WAVE7_PENDING,
        "wave7 checkpoint pending count drift",
    )

    remaining_pending = sum(len(values) for values in pending_by_root.values())
    require(remaining_pending == EXPECTED_WAVE7_PENDING, "wave7 pending drift")

    current_blob = SHADOW_CURRENT.read_bytes()
    candidate_blob = ENGINE.rebuild_packed_with_literals(
        current_blob, replacements
    )
    candidate_sha256 = sha256_bytes(candidate_blob)
    require(
        candidate_sha256 == EXPECTED_WAVE7_CANDIDATE_SHA256,
        f"wave7 candidate drift: {candidate_sha256}",
    )
    records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate_blob).archive
    )

    # Discover every actual 0143/014A edge over nonliteral gaps without
    # requiring unrelated records to pass the stricter full component decoder.
    # Each selected root itself must still pass VM.decode_record() exactly.
    candidate_edges = RANKING.graph_edges(records)
    incoming: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for source, edges in candidate_edges.items():
        for edge in edges:
            target = tuple(edge["target"])
            incoming.setdefault(target, []).append(
                {
                    "kind": edge["kind"],
                    "source": [source[0], source[1]],
                }
            )

    selected_roots: list[tuple[int, int]] = []
    root_evidence: list[dict[str, Any]] = []
    selected_coordinates: list[str] = []
    component_kind_counts: dict[str, int] = {}
    pending_root_decode_failures = 0
    for root in sorted(pending_by_root):
        try:
            components = VM.decode_record(records[root])
        except VM.AuditError:
            pending_root_decode_failures += 1
            continue
        disallowed = [
            component
            for component in components
            if component["kind"] not in ALLOWED_LOCAL_COMPONENT_KINDS
        ]
        if disallowed or candidate_edges[root] or incoming.get(root):
            continue
        coordinates = sorted(
            pending_by_root[root], key=parse_coordinate
        )
        selected_roots.append(root)
        selected_coordinates.extend(coordinates)
        local_counts: dict[str, int] = {}
        for component in components:
            kind = str(component["kind"])
            local_counts[kind] = local_counts.get(kind, 0) + 1
            component_kind_counts[kind] = (
                component_kind_counts.get(kind, 0) + 1
            )
        root_evidence.append(
            {
                "root": f"{root[0]}:{root[1]}",
                "pending_coordinate_count": len(coordinates),
                "pending_coordinate_sha256": coordinate_digest(coordinates),
                "candidate_record_data_sha256": sha256_bytes(
                    records[root].data
                ),
                "decoded_component_count": len(components),
                "decoded_component_kind_counts": dict(
                    sorted(local_counts.items())
                ),
                "decoded_component_sha256": canonical_sha256(components),
                "incoming_call_count": 0,
                "incoming_jump_count": 0,
                "outgoing_call_count": 0,
                "outgoing_jump_count": 0,
                "data_dependent_component_count": 0,
            }
        )

    selected_root_strings = [
        f"{root[0]}:{root[1]}" for root in selected_roots
    ]
    require(
        len(selected_coordinates) == EXPECTED_STATIC_ROWS,
        f"static row count drift: {len(selected_coordinates)}",
    )
    require(
        len(selected_roots) == EXPECTED_STATIC_ROOTS,
        f"static root count drift: {len(selected_roots)}",
    )

    decisions: list[dict[str, Any]] = []
    for coordinate in sorted(selected_coordinates, key=parse_coordinate):
        predecessor = rows[coordinate]
        key = parse_coordinate(coordinate)
        translation = replacements[key]
        require(
            predecessor.get("runtime_review") == "pending"
            and predecessor.get("scope_classification")
            == "runtime_fragment_pending"
            and predecessor.get("semantic_review") == "approved",
            f"invalid static predecessor state: {coordinate}",
        )
        decisions.append(
            {
                "schema": DECISION_SCHEMA,
                "method": METHOD,
                "action": "runtime_promotion",
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "root": f"{key[0]}:{key[1]}",
                "predecessor_row_sha256": canonical_sha256(predecessor),
                "translation_utf16le_sha256": text_sha256(translation),
                "candidate_record_data_sha256": sha256_bytes(
                    records[key[:2]].data
                ),
                "semantic_review": "approved",
                "layout_review": predecessor["layout_review"],
                "runtime_review": "verified",
                "scope_classification": "retranslated",
                "runtime_vm_verification": {
                    "method": METHOD,
                    "candidate_record_data_sha256": sha256_bytes(
                        records[key[:2]].data
                    ),
                    "decoded_component_kinds_subset_proven": sorted(
                        ALLOWED_LOCAL_COMPONENT_KINDS
                    ),
                    "data_dependent_component_count": 0,
                    "incoming_call_count": 0,
                    "incoming_jump_count": 0,
                    "status": "PASS",
                },
                "translation_changed": False,
                "layout_changed": False,
                "control_or_token_changed": False,
                "steam_write_performed": False,
            }
        )

    # Classification-only decisions cannot feed the literal rebuild.
    post_candidate_blob = ENGINE.rebuild_packed_with_literals(
        current_blob, replacements
    )
    require(
        post_candidate_blob == candidate_blob,
        "classification delta changed the packed candidate",
    )

    decision_payload = serialized_jsonl(decisions)
    coordinate_sha256 = coordinate_digest(selected_coordinates)
    root_sha256 = root_digest(selected_root_strings)
    evidence: dict[str, Any] = {
        "schema": PRIVATE_SCHEMA,
        "method": METHOD,
        "inputs": {
            **inputs,
            "checkpoint_path": relative(CHECKPOINT),
            "shadow_current_path": relative(SHADOW_CURRENT),
        },
        "proof": {
            "exact_reversed_vm_decoder_used": True,
            "allowed_local_component_kinds": sorted(
                ALLOWED_LOCAL_COMPONENT_KINDS
            ),
            "all_selected_data_dependent_component_counts_zero": True,
            "all_selected_incoming_call_counts_zero": True,
            "all_selected_incoming_jump_counts_zero": True,
            "all_selected_outgoing_call_counts_zero": True,
            "all_selected_outgoing_jump_counts_zero": True,
            "all_selected_predecessor_semantic_reviews_approved": True,
            "translation_changes": 0,
            "layout_changes": 0,
            "control_or_token_changes": 0,
            "candidate_byte_changes": 0,
            "event_dialogue_912px_rule_applied": False,
            "full_rebuild_performed": False,
            "steam_write_performed": False,
        },
        "counts": {
            "checkpoint_rows": row_count,
            "wave7_checkpoint_pk_pending_rows": checkpoint_pk_pending,
            "wave7_pending_rows": remaining_pending,
            "local_static_roots": len(selected_roots),
            "local_static_rows": len(selected_coordinates),
            "pending_after": remaining_pending - len(selected_coordinates),
            "decision_rows": len(decisions),
            "translation_overrides": 0,
            "pending_root_decode_failures": pending_root_decode_failures,
        },
        "digests": {
            "local_static_coordinate_sha256": coordinate_sha256,
            "local_static_root_sha256": root_sha256,
            "decision_payload_sha256": sha256_bytes(decision_payload),
            "wave7_candidate_before_sha256": candidate_sha256,
            "candidate_after_sha256": sha256_bytes(post_candidate_blob),
            "decoded_component_kind_counts_sha256": canonical_sha256(
                component_kind_counts
            ),
        },
        "decoded_component_kind_counts": dict(
            sorted(component_kind_counts.items())
        ),
        "root_evidence": root_evidence,
        "status": "PASS",
    }
    require(
        evidence["counts"]["pending_after"] == EXPECTED_PENDING_AFTER,
        "post-static pending count drift",
    )

    public: dict[str, Any] = {
        "schema": PUBLIC_SCHEMA,
        "method": METHOD,
        "inputs": {
            "checkpoint_sha256": inputs["checkpoint"],
            "vm_builder_sha256": inputs["vm_builder"],
            "ranking_builder_sha256": inputs["ranking_builder"],
            "engine_builder_sha256": inputs["engine_builder"],
            "shadow_current_sha256": inputs["shadow_current"],
        },
        "scope": {
            "resource": "MSG_PK/JP/msggame.bin",
            "wave7_pending_rows": remaining_pending,
            "local_static_roots": len(selected_roots),
            "local_static_rows": len(selected_coordinates),
            "pending_after": remaining_pending - len(selected_coordinates),
        },
        "proof": {
            "exact_reversed_vm_decoder_used": True,
            "allowed_local_component_kinds": sorted(
                ALLOWED_LOCAL_COMPONENT_KINDS
            ),
            "data_dependent_components": 0,
            "incoming_calls": 0,
            "incoming_jumps": 0,
            "outgoing_calls": 0,
            "outgoing_jumps": 0,
            "translation_changes": 0,
            "layout_changes": 0,
            "control_or_token_changes": 0,
            "candidate_byte_changes": 0,
            "candidate_before_sha256": candidate_sha256,
            "candidate_after_sha256": sha256_bytes(post_candidate_blob),
            "full_rebuild_performed": False,
            "steam_write_performed": False,
        },
        "digests": {
            "local_static_coordinate_sha256": coordinate_sha256,
            "local_static_root_sha256": root_sha256,
            "decision_payload_sha256": sha256_bytes(decision_payload),
            "decoded_component_kind_counts_sha256": canonical_sha256(
                component_kind_counts
            ),
        },
        "status": "PASS",
    }
    public_payload = serialized_json(public)
    evidence["digests"]["public_payload_sha256"] = sha256_bytes(
        public_payload
    )
    evidence_payload = serialized_json(evidence)
    return decision_payload, evidence_payload, public_payload, evidence


def verify_expected(
    decisions: bytes,
    evidence: bytes,
    public: bytes,
) -> None:
    actual = {
        "decisions": sha256_bytes(decisions),
        "evidence": sha256_bytes(evidence),
        "public": sha256_bytes(public),
    }
    missing = [
        name
        for name, expected in EXPECTED_OUTPUT_SHA256.items()
        if expected is None
    ]
    require(not missing, f"unfrozen output hashes: {missing}")
    require(actual == EXPECTED_OUTPUT_SHA256, f"output hash drift: {actual}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--bootstrap", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--public", type=Path, default=DEFAULT_PUBLIC)
    args = parser.parse_args(argv)

    decisions, evidence, public, report = build_outputs()
    if not args.bootstrap:
        verify_expected(decisions, evidence, public)

    if args.bootstrap or args.write:
        atomic_write(args.decisions, decisions)
        atomic_write(args.evidence, evidence)
        atomic_write(args.public, public)
    else:
        require(args.decisions.read_bytes() == decisions, "decision file drift")
        require(args.evidence.read_bytes() == evidence, "evidence file drift")
        require(args.public.read_bytes() == public, "public file drift")

    print(
        json.dumps(
            {
                "status": report["status"],
                "local_static_rows": report["counts"]["local_static_rows"],
                "local_static_roots": report["counts"]["local_static_roots"],
                "pending_after": report["counts"]["pending_after"],
                "coordinate_sha256":
                    report["digests"]["local_static_coordinate_sha256"],
                "root_sha256": report["digests"]["local_static_root_sha256"],
                "candidate_sha256":
                    report["digests"]["candidate_after_sha256"],
                "decisions_sha256": sha256_bytes(decisions),
                "evidence_sha256": sha256_bytes(evidence),
                "public_sha256": sha256_bytes(public),
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
