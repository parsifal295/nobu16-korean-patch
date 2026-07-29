#!/usr/bin/env python3
"""Finalize the Wave-B caller packets against a post-Wave-A candidate.

The tracked Wave-B assignment is intentionally provisional.  This tracked
builder reconstructs the frozen post-Wave-A candidate from its checkpoint,
proves that the entire control graph and every owned caller/closure topology
are identical to that provisional baseline, retains its three root-disjoint
balanced bundles, and replaces all terminal-byte snapshots.

The frozen input and output hashes authorize Wave-B review only; they never
authorize a full rebuild or a Steam write.  Dialogue-bearing assignment and
packets stay below ``tmp/``; only the source-free summary is tracked.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import importlib.util
import itertools
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

PROVISIONAL_BUILDER = (
    AUDIT / "build_pk_msggame_post_wave7_waveB_caller_assignment_v1.py"
)
WAVE_A_CHECKPOINT = (
    TMP
    / "runtime_vm_integrated."
    "post_waveA_consolidated_checkpoint.private.v1.jsonl"
)
WAVE_A_CANDIDATE = TMP / "pk_msggame_waveA_union_candidate.private.v1.bin"

DEFAULT_ASSIGNMENT = (
    TMP / "pk_msggame_post_waveA_waveB_caller_assignment.final.private.v1.json"
)
DEFAULT_PUBLIC = (
    AUDIT
    / "public"
    / "pk_msggame_post_waveA_waveB_caller_assignment."
    "final.source_free.v1.json"
)
DEFAULT_PACKET_DIR = TMP / "pk_msggame_post_waveA_waveB_caller_final_packets"

EXPECTED_PROVISIONAL_BUILDER_SHA256 = (
    "778C53339CF43F9D0916644553048D5523411E16E239CB444E874D2FD299FA1E"
)
EXPECTED_PROVISIONAL_OUTPUT_SHA256 = {
    "assignment": "10484CE4CD3D4413C770CE1F23FF165B658762C3B4FB022D1F4CE711A2F915BA",
    "public": "2C817E6DE4C8BAF20006415AC46E046B757FC8F131577D77E81E32472649FA04",
    "packet0": "20E6B287428B5985D96147CB1EC23CBA2BC9ACE76BC1F178433A395145AB5819",
    "packet1": "78739654A8F1C6285A7ACA889349FDDE4368A515E38632D74E4804378C5B9492",
    "packet2": "722FF0417657330EF77C4834C3FF4FFEB891B4A855A131857C910C3AA245C292",
}
EXPECTED_CALLER_ROWS = 1_214
EXPECTED_CALLER_ROOTS = 717
EXPECTED_BRANCHES = 606_902
EXPECTED_FREEZE_CHECKPOINT_SHA256 = (
    "F7B2AA9642E6FDC80920B091991C41F7EC08590E5DE778326EB72E3C8BA67E1A"
)
EXPECTED_FREEZE_CANDIDATE_SHA256 = (
    "A2811CA8B9A53C84678727737FDA1729520FB4AB16F19AAB537C51292D1EEE78"
)
EXPECTED_OUTPUT_SHA256 = {
    "assignment": "37180F050DDAC42D322E8B7EA58F30B4B736443794AB46DEBDF0BFD83E458775",
    "public": "D753E99EA3037F6741E1255BC8E786AC907410670AF43CDBCA687BA266BE42B9",
    "packet0": "00CBDA5E313291F3DF6CE9A5CECEF43843E54B108B7875B015F09B0E6F3C47A1",
    "packet1": "12A125F5891F1C4DEF3934F0E635649DDB2B71C31D88FF276D0743B35AA536CF",
    "packet2": "9BEBF0FD1ED359925DD5C5B99A3B002C6D83B06893ECFCB74A66CBFD27899EC9",
}

ASSIGNMENT_SCHEMA = (
    "nobu16.kr.pk-msggame-post-waveA-waveB-caller-assignment."
    "final.private.v1"
)
PACKET_SCHEMA = (
    "nobu16.kr.pk-msggame-post-waveA-waveB-caller-packet."
    "final.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-msggame-post-waveA-waveB-caller-assignment."
    "final.source-free.v1"
)
METHOD = (
    "frozen_post_waveA_candidate_exact_0143_caller_cross_product_"
    "provisional_topology_identity_terminal_snapshot_refreeze"
)


class WaveBFinalizerError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WaveBFinalizerError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


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
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("ascii")


def parse_coordinate(value: str) -> tuple[int, ...]:
    return tuple(map(int, value.split(":")))


def parse_root(value: str) -> tuple[int, int]:
    parts = parse_coordinate(value)
    require(len(parts) == 2, f"bad root: {value}")
    return parts


def root_string(root: tuple[int, int]) -> str:
    return f"{root[0]}:{root[1]}"


def coordinate_digest(values: Iterable[str]) -> str:
    payload = "".join(
        f"{value}\n"
        for value in sorted(set(values), key=parse_coordinate)
    ).encode("ascii")
    return sha256_bytes(payload)


def root_digest(values: Iterable[tuple[int, int]]) -> str:
    payload = "".join(
        f"{root_string(root)}\n" for root in sorted(set(values))
    ).encode("ascii")
    return sha256_bytes(payload)


def graph_serializable(
    edges_by_root: Mapping[
        tuple[int, int], Sequence[Mapping[str, Any]]
    ],
) -> list[dict[str, Any]]:
    return [
        {
            "root": root_string(root),
            "edges": [
                {
                    "kind": str(edge["kind"]),
                    "target": root_string(tuple(edge["target"])),
                    "gap_id": int(edge["gap_id"]),
                    "offset": int(edge["offset"]),
                }
                for edge in edges_by_root[root]
            ],
        }
        for root in sorted(edges_by_root)
    ]


def closure_topology(
    ranking: Any,
    edges_by_root: Mapping[
        tuple[int, int], Sequence[Mapping[str, Any]]
    ],
    target: tuple[int, int],
) -> dict[str, Any]:
    nodes, dispatch, leaves = ranking.jump_closure(edges_by_root, target)
    rows = [
        {
            "root": root_string(root),
            "edges": [
                {
                    "kind": str(edge["kind"]),
                    "target": root_string(tuple(edge["target"])),
                    "gap_id": int(edge["gap_id"]),
                    "offset": int(edge["offset"]),
                }
                for edge in edges_by_root[root]
            ],
        }
        for root in sorted(nodes)
    ]
    return {
        "nodes": sorted(nodes),
        "dispatch": sorted(dispatch),
        "leaves": sorted(leaves),
        "full_control_sha256": canonical_sha256(rows),
    }


def record_snapshot(
    engine: Any,
    records: Mapping[tuple[int, int], Any],
    root: tuple[int, int],
) -> dict[str, Any]:
    record = records[root]
    literals = list(engine.parse_record_literals(record))
    return {
        "root": root_string(root),
        "record_data_sha256": sha256_bytes(record.data),
        "literal_count": len(literals),
        "literal_utf16le_sha256": [
            sha256_bytes(literal.text.encode("utf-16le"))
            for literal in literals
        ],
    }


def branch_cross_product_digest(
    root: tuple[int, int],
    factors: Sequence[Sequence[tuple[int, int]]],
) -> tuple[int, str]:
    digest = hashlib.sha256()
    count = 0
    for branch in itertools.product(*factors):
        digest.update(root_string(root).encode("ascii"))
        for occurrence, terminal in enumerate(branch):
            digest.update(
                f"|{occurrence}={root_string(terminal)}".encode("ascii")
            )
        digest.update(b"\n")
        count += 1
    return count, digest.hexdigest().upper()


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


def load_checkpoint(
    checkpoint_bytes: bytes,
) -> tuple[
    dict[tuple[int, int, int], str],
    dict[tuple[int, int], set[str]],
    int,
]:
    replacements: dict[tuple[int, int, int], str] = {}
    pending: defaultdict[tuple[int, int], set[str]] = defaultdict(set)
    row_count = 0
    for raw_line in checkpoint_bytes.splitlines():
        if not raw_line:
            continue
        row_count += 1
        row = json.loads(raw_line)
        if row.get("resource") != "pk_msggame":
            continue
        coordinate = str(row["coordinate"])
        key = parse_coordinate(coordinate)
        require(len(key) == 3, f"bad checkpoint coordinate: {coordinate}")
        if "translation" in row:
            replacements[key] = str(row["translation"])
        if row.get("runtime_review") == "pending":
            pending[key[:2]].add(coordinate)
    return replacements, dict(pending), row_count


def build_outputs(
    freeze_checkpoint_sha256: str | None,
    freeze_candidate_sha256: str | None,
) -> tuple[dict[Path, bytes], dict[str, Any]]:
    require(
        (freeze_checkpoint_sha256 is None)
        == (freeze_candidate_sha256 is None),
        "both frozen hashes must be supplied together",
    )
    frozen = freeze_checkpoint_sha256 is not None
    if frozen:
        freeze_checkpoint_sha256 = freeze_checkpoint_sha256.upper()
        freeze_candidate_sha256 = freeze_candidate_sha256.upper()
        require(
            len(freeze_checkpoint_sha256) == 64
            and len(freeze_candidate_sha256) == 64,
            "frozen hashes must be SHA-256 hex",
        )

    provisional_builder_sha256 = sha256_file(PROVISIONAL_BUILDER)
    require(
        provisional_builder_sha256
        == EXPECTED_PROVISIONAL_BUILDER_SHA256,
        f"provisional builder drift: {provisional_builder_sha256}",
    )
    provisional = load_module(
        PROVISIONAL_BUILDER, "pk_waveB_provisional_for_finalizer"
    )
    provisional_outputs, provisional_assignment = (
        provisional.build_outputs()
    )
    require(
        provisional.output_hashes(provisional_outputs)
        == EXPECTED_PROVISIONAL_OUTPUT_SHA256,
        "provisional output hash drift",
    )
    provisional_packets = [
        json.loads(
            provisional_outputs[
                provisional.DEFAULT_PACKET_DIR
                / f"bundle{bundle_id}.private.v1.json"
            ]
        )
        for bundle_id in range(3)
    ]

    checkpoint_bytes = WAVE_A_CHECKPOINT.read_bytes()
    candidate_bytes = WAVE_A_CANDIDATE.read_bytes()
    checkpoint_sha256 = sha256_bytes(checkpoint_bytes)
    candidate_sha256 = sha256_bytes(candidate_bytes)
    if frozen:
        require(
            checkpoint_sha256 == freeze_checkpoint_sha256,
            f"frozen checkpoint mismatch: {checkpoint_sha256}",
        )
        require(
            candidate_sha256 == freeze_candidate_sha256,
            f"frozen candidate mismatch: {candidate_sha256}",
        )

    replacements, pending, checkpoint_row_count = load_checkpoint(
        checkpoint_bytes
    )
    require(checkpoint_row_count == 52_803, "checkpoint row count drift")
    rebuilt_candidate = provisional.ENGINE.rebuild_packed_with_literals(
        provisional.SHADOW_CURRENT.read_bytes(), replacements
    )
    require(
        rebuilt_candidate == candidate_bytes,
        "staged Wave-A candidate does not reconstruct from checkpoint",
    )

    old_replacements, _, old_checkpoint_rows = load_checkpoint(
        provisional.CHECKPOINT.read_bytes()
    )
    require(old_checkpoint_rows == 52_803, "provisional checkpoint row drift")
    old_candidate = provisional.ENGINE.rebuild_packed_with_literals(
        provisional.SHADOW_CURRENT.read_bytes(), old_replacements
    )
    require(
        sha256_bytes(old_candidate)
        == provisional.EXPECTED_CANDIDATE_SHA256,
        "provisional candidate reconstruction drift",
    )

    old_records = provisional.ENGINE.archive_records(
        provisional.ENGINE.parse_packed_msggame(old_candidate).archive
    )
    new_records = provisional.ENGINE.archive_records(
        provisional.ENGINE.parse_packed_msggame(candidate_bytes).archive
    )
    source_records = provisional.ENGINE.archive_records(
        provisional.ENGINE.parse_packed_msggame(
            provisional.PRISTINE.read_bytes()
        ).archive
    )
    require(
        set(old_records) == set(new_records),
        "post-Wave-A archive root set changed",
    )
    old_edges = provisional.RANKING.graph_edges(old_records)
    new_edges = provisional.RANKING.graph_edges(new_records)
    source_edges = provisional.RANKING.graph_edges(source_records)
    old_graph = graph_serializable(old_edges)
    new_graph = graph_serializable(new_edges)
    old_graph_sha256 = canonical_sha256(old_graph)
    new_graph_sha256 = canonical_sha256(new_graph)
    require(
        old_graph == new_graph,
        "post-Wave-A control graph differs from provisional candidate",
    )

    old_snapshot_by_root: dict[tuple[int, int], dict[str, Any]] = {}
    owned_roots: set[tuple[int, int]] = set()
    owned_coordinates: set[str] = set()
    bundle_roots: list[list[dict[str, Any]]] = []
    for packet in provisional_packets:
        rows = list(packet["owned_roots"])
        bundle_roots.append(rows)
        for row in rows:
            root = parse_root(row["root"])
            require(root not in owned_roots, f"duplicate owned root: {root}")
            owned_roots.add(root)
            for coordinate in row["pending_coordinates"]:
                require(
                    coordinate not in owned_coordinates,
                    f"duplicate owned coordinate: {coordinate}",
                )
                require(
                    parse_coordinate(coordinate)[:2] == root,
                    f"coordinate/root mismatch: {coordinate}",
                )
                owned_coordinates.add(coordinate)
        for snapshot in packet["pre_waveA_terminal_snapshot"]:
            root = parse_root(snapshot["root"])
            existing = old_snapshot_by_root.get(root)
            require(
                existing is None or existing == snapshot,
                f"conflicting provisional terminal snapshot: {root}",
            )
            old_snapshot_by_root[root] = snapshot

    require(len(owned_roots) == EXPECTED_CALLER_ROOTS, "owned root drift")
    require(
        len(owned_coordinates) == EXPECTED_CALLER_ROWS,
        "owned coordinate drift",
    )
    provisional_result = provisional_assignment["result"]
    require(
        root_digest(owned_roots)
        == provisional_result["caller_root_sha256"],
        "provisional root digest drift",
    )
    require(
        coordinate_digest(owned_coordinates)
        == provisional_result["caller_pending_coordinate_sha256"],
        "provisional coordinate digest drift",
    )

    current_direct_call_roots = {
        root
        for root in pending
        if any(edge["kind"] == "C" for edge in new_edges[root])
    }
    require(
        current_direct_call_roots == owned_roots,
        "current pending direct-call root universe differs from provisional",
    )
    current_direct_call_coordinates = {
        coordinate
        for root in current_direct_call_roots
        for coordinate in pending[root]
    }
    require(
        current_direct_call_coordinates == owned_coordinates,
        "current pending caller coordinate universe differs from provisional",
    )

    packet_payloads: list[bytes] = []
    bundle_manifest: list[dict[str, Any]] = []
    global_branch_count = 0
    global_cross_product_digest = hashlib.sha256()
    changed_terminals_global: set[tuple[int, int]] = set()
    all_terminals_global: set[tuple[int, int]] = set()
    all_closure_targets: set[tuple[int, int]] = set()

    for bundle_id, (old_packet, old_rows) in enumerate(
        zip(provisional_packets, bundle_roots, strict=True)
    ):
        final_rows: list[dict[str, Any]] = []
        bundle_terminals: set[tuple[int, int]] = set()
        bundle_changed_terminals: set[tuple[int, int]] = set()
        bundle_branch_count = 0
        bundle_branch_digest = hashlib.sha256()
        bundle_owned_roots = {
            parse_root(row["root"]) for row in old_rows
        }
        bundle_owned_coordinates = {
            coordinate
            for row in old_rows
            for coordinate in row["pending_coordinates"]
        }

        for old_row in old_rows:
            root = parse_root(old_row["root"])
            require(
                old_edges[root] == new_edges[root],
                f"caller control topology changed: {root}",
            )
            calls = [
                edge
                for edge in new_edges[root]
                if edge["kind"] == "C"
            ]
            require(
                len(calls) == old_row["direct_call_count"],
                f"direct call count drift: {root}",
            )
            call_rows: list[dict[str, Any]] = []
            factors: list[list[tuple[int, int]]] = []
            for occurrence, (edge, old_call) in enumerate(
                zip(calls, old_row["calls"], strict=True)
            ):
                target = tuple(edge["target"])
                all_closure_targets.add(target)
                old_closure = closure_topology(
                    provisional.RANKING, old_edges, target
                )
                new_closure = closure_topology(
                    provisional.RANKING, new_edges, target
                )
                source_closure = closure_topology(
                    provisional.RANKING, source_edges, target
                )
                require(
                    old_closure == new_closure,
                    f"call closure topology changed: {root}->{target}",
                )
                terminals = list(new_closure["leaves"])
                require(terminals, f"empty terminal set: {root}->{target}")
                expected_call = {
                    "occurrence": occurrence,
                    "gap_id": int(edge["gap_id"]),
                    "offset": int(edge["offset"]),
                    "target": root_string(target),
                    "terminal_count": len(terminals),
                    "terminal_root_sha256": root_digest(terminals),
                    "source_candidate_control_identical": (
                        new_closure["nodes"] == source_closure["nodes"]
                        and new_closure["dispatch"]
                        == source_closure["dispatch"]
                        and new_closure["leaves"]
                        == source_closure["leaves"]
                    ),
                }
                require(
                    expected_call == old_call,
                    f"provisional call summary drift: {root} occurrence "
                    f"{occurrence}",
                )
                call_rows.append(
                    {
                        **expected_call,
                        "closure_full_control_sha256":
                            new_closure["full_control_sha256"],
                        "terminal_roots": [
                            root_string(value) for value in terminals
                        ],
                    }
                )
                factors.append(terminals)
                bundle_terminals.update(terminals)

            branch_count, branch_sha256 = branch_cross_product_digest(
                root, factors
            )
            require(
                branch_count == old_row["branch_count"],
                f"branch count drift: {root}",
            )
            branch_line = (
                f"{root_string(root)}|{branch_count}|{branch_sha256}\n"
            ).encode("ascii")
            bundle_branch_digest.update(branch_line)
            global_cross_product_digest.update(branch_line)
            bundle_branch_count += branch_count
            global_branch_count += branch_count
            final_rows.append(
                {
                    "root": root_string(root),
                    "pending_coordinates":
                        list(old_row["pending_coordinates"]),
                    "pending_coordinate_count":
                        int(old_row["pending_coordinate_count"]),
                    "pending_coordinate_sha256":
                        str(old_row["pending_coordinate_sha256"]),
                    "direct_call_count": len(calls),
                    "branch_count": branch_count,
                    "actual_branch_cross_product_sha256": branch_sha256,
                    "calls": call_rows,
                }
            )

        terminal_snapshot = [
            record_snapshot(provisional.ENGINE, new_records, root)
            for root in sorted(bundle_terminals)
        ]
        for snapshot in terminal_snapshot:
            root = parse_root(snapshot["root"])
            old_snapshot = old_snapshot_by_root[root]
            if snapshot != old_snapshot:
                bundle_changed_terminals.add(root)
                changed_terminals_global.add(root)
        all_terminals_global.update(bundle_terminals)

        old_scope = old_packet["scope"]
        require(
            len(bundle_owned_roots) == old_scope["root_count"],
            f"bundle {bundle_id} root count drift",
        )
        require(
            len(bundle_owned_coordinates)
            == old_scope["pending_coordinate_count"],
            f"bundle {bundle_id} coordinate count drift",
        )
        require(
            bundle_branch_count == old_scope["branch_count"],
            f"bundle {bundle_id} branch count drift",
        )
        require(
            root_digest(bundle_owned_roots) == old_scope["root_sha256"],
            f"bundle {bundle_id} root digest drift",
        )
        require(
            coordinate_digest(bundle_owned_coordinates)
            == old_scope["pending_coordinate_sha256"],
            f"bundle {bundle_id} coordinate digest drift",
        )
        require(
            root_digest(bundle_terminals)
            == old_scope["unique_terminal_root_sha256"],
            f"bundle {bundle_id} terminal universe drift",
        )

        status = (
            "PASS_FROZEN_WAVE_A_BOUND_REVIEW_AUTHORIZED"
            if frozen
            else "DRAFT_UNFROZEN_WAVE_A_INPUTS_REVIEW_UNAUTHORIZED"
        )
        packet = {
            "schema": PACKET_SCHEMA,
            "method": METHOD,
            "status": status,
            "bundle_id": bundle_id,
            "candidate_binding": {
                "binding_mode":
                    "explicit_sha256_freeze" if frozen else "draft_observed",
                "post_waveA_checkpoint_sha256": checkpoint_sha256,
                "post_waveA_candidate_sha256": candidate_sha256,
                "provisional_candidate_sha256":
                    provisional.EXPECTED_CANDIDATE_SHA256,
            },
            "scope": {
                "root_count": len(bundle_owned_roots),
                "root_sha256": root_digest(bundle_owned_roots),
                "pending_coordinate_count": len(bundle_owned_coordinates),
                "pending_coordinate_sha256":
                    coordinate_digest(bundle_owned_coordinates),
                "branch_count": bundle_branch_count,
                "actual_branch_cross_product_sha256":
                    bundle_branch_digest.hexdigest().upper(),
                "unique_terminal_root_count": len(bundle_terminals),
                "unique_terminal_root_sha256":
                    root_digest(bundle_terminals),
                "changed_terminal_root_count":
                    len(bundle_changed_terminals),
                "changed_terminal_root_sha256":
                    root_digest(bundle_changed_terminals),
            },
            "contract": {
                "actions_authorized": frozen,
                "review_start_authorized": frozen,
                "decision_rows_authorized":
                    len(bundle_owned_coordinates) if frozen else 0,
                "owned_caller_records_writable": frozen,
                "terminal_records_read_only": True,
                "translation_changes_require_full_branch_proof": True,
                "root_atomic_decisions_required": True,
                "current_relative_raw_g1n_nonexpansion_required": True,
                "source_only_actions_required": True,
                "full_rebuild_authorized": False,
                "steam_write_authorized": False,
            },
            "proof": {
                "candidate_rebuilt_from_checkpoint": True,
                "full_control_graph_identical_to_provisional": True,
                "caller_root_set_identical_to_provisional": True,
                "caller_coordinate_set_identical_to_provisional": True,
                "all_owned_coordinates_still_pending": True,
                "all_actual_branch_cross_products_recomputed": True,
                "terminal_universe_identical_to_provisional": True,
                "terminal_snapshots_refrozen": frozen,
            },
            "owned_roots": final_rows,
            "post_waveA_terminal_snapshot": terminal_snapshot,
            "post_waveA_terminal_snapshot_sha256":
                canonical_sha256(terminal_snapshot),
        }
        payload = serialized_json(packet)
        packet_payloads.append(payload)
        bundle_manifest.append(
            {
                "bundle_id": bundle_id,
                **packet["scope"],
                "post_waveA_terminal_snapshot_sha256":
                    packet["post_waveA_terminal_snapshot_sha256"],
                "packet_sha256": sha256_bytes(payload),
                "actions_authorized": frozen,
            }
        )

    require(
        global_branch_count == EXPECTED_BRANCHES,
        "global branch count drift",
    )
    require(
        global_branch_count
        == provisional_result["actual_branch_count"],
        "global/provisional branch count mismatch",
    )

    status = (
        "PASS_FROZEN_WAVE_A_BOUND_REVIEW_AUTHORIZED"
        if frozen
        else "DRAFT_UNFROZEN_WAVE_A_INPUTS_REVIEW_UNAUTHORIZED"
    )
    result = {
        "bundle_count": 3,
        "caller_root_count": len(owned_roots),
        "caller_root_sha256": root_digest(owned_roots),
        "caller_pending_coordinate_count": len(owned_coordinates),
        "caller_pending_coordinate_sha256":
            coordinate_digest(owned_coordinates),
        "actual_branch_count": global_branch_count,
        "actual_branch_cross_product_sha256":
            global_cross_product_digest.hexdigest().upper(),
        "unique_closure_target_count": len(all_closure_targets),
        "unique_closure_target_sha256":
            root_digest(all_closure_targets),
        "unique_terminal_root_count": len(all_terminals_global),
        "unique_terminal_root_sha256":
            root_digest(all_terminals_global),
        "changed_terminal_root_count": len(changed_terminals_global),
        "changed_terminal_root_sha256":
            root_digest(changed_terminals_global),
        "pending_checkpoint_row_count":
            sum(len(values) for values in pending.values()),
    }
    assignment = {
        "schema": ASSIGNMENT_SCHEMA,
        "method": METHOD,
        "status": status,
        "inputs": {
            "provisional_builder_sha256": provisional_builder_sha256,
            "provisional_assignment_sha256":
                EXPECTED_PROVISIONAL_OUTPUT_SHA256["assignment"],
            "provisional_packet_sha256": [
                EXPECTED_PROVISIONAL_OUTPUT_SHA256[f"packet{bundle_id}"]
                for bundle_id in range(3)
            ],
            "post_waveA_checkpoint_path":
                str(WAVE_A_CHECKPOINT.relative_to(REPO)).replace("\\", "/"),
            "post_waveA_checkpoint_sha256": checkpoint_sha256,
            "post_waveA_candidate_path":
                str(WAVE_A_CANDIDATE.relative_to(REPO)).replace("\\", "/"),
            "post_waveA_candidate_sha256": candidate_sha256,
            "shadow_current_sha256":
                sha256_file(provisional.SHADOW_CURRENT),
            "pristine_sha256": sha256_file(provisional.PRISTINE),
        },
        "freeze": {
            "binding_mode":
                "explicit_sha256_freeze" if frozen else "draft_observed",
            "expected_checkpoint_sha256": freeze_checkpoint_sha256,
            "expected_candidate_sha256": freeze_candidate_sha256,
            "review_start_authorized": frozen,
        },
        "result": result,
        "bundle_manifest": bundle_manifest,
        "proof": {
            "candidate_rebuilt_from_checkpoint": True,
            "archive_root_set_identical_to_provisional": True,
            "full_control_graph_identical_to_provisional": True,
            "provisional_control_graph_sha256": old_graph_sha256,
            "post_waveA_control_graph_sha256": new_graph_sha256,
            "pending_direct_call_root_universe_exact": True,
            "pending_direct_call_coordinate_universe_exact": True,
            "bundle_roots_pairwise_disjoint": True,
            "bundle_coordinates_pairwise_disjoint": True,
            "bundle_branch_balance_max_minus_min":
                max(row["branch_count"] for row in bundle_manifest)
                - min(row["branch_count"] for row in bundle_manifest),
            "actual_branch_cross_products_recomputed": True,
            "terminal_snapshots_replaced": True,
            "source_only_action_count": 0,
            "full_rebuild_performed": False,
            "steam_write_performed": False,
        },
    }
    assignment_payload = serialized_json(assignment)
    public = {
        "schema": PUBLIC_SCHEMA,
        "method": METHOD,
        "status": status,
        "inputs": {
            "provisional_builder_sha256": provisional_builder_sha256,
            "provisional_assignment_sha256":
                EXPECTED_PROVISIONAL_OUTPUT_SHA256["assignment"],
            "post_waveA_checkpoint_sha256": checkpoint_sha256,
            "post_waveA_candidate_sha256": candidate_sha256,
        },
        "freeze": assignment["freeze"],
        "result": result,
        "bundles": [
            {
                key: value
                for key, value in row.items()
                if key not in {
                    "pending_coordinate_sha256",
                    "root_sha256",
                    "unique_terminal_root_sha256",
                    "changed_terminal_root_sha256",
                }
            }
            for row in bundle_manifest
        ],
        "proof": assignment["proof"],
        "privacy": {
            "source_free": True,
            "contains_dialogue_bodies": False,
            "contains_translations": False,
            "private_packets_stay_below_tmp": True,
        },
    }
    public_payload = serialized_json(public)
    outputs = {
        DEFAULT_ASSIGNMENT: assignment_payload,
        DEFAULT_PUBLIC: public_payload,
        DEFAULT_PACKET_DIR / "bundle0.final.private.v1.json":
            packet_payloads[0],
        DEFAULT_PACKET_DIR / "bundle1.final.private.v1.json":
            packet_payloads[1],
        DEFAULT_PACKET_DIR / "bundle2.final.private.v1.json":
            packet_payloads[2],
    }
    return outputs, assignment


def output_hashes(outputs: Mapping[Path, bytes]) -> dict[str, str]:
    result = {
        "assignment": sha256_bytes(outputs[DEFAULT_ASSIGNMENT]),
        "public": sha256_bytes(outputs[DEFAULT_PUBLIC]),
    }
    for bundle_id in range(3):
        result[f"packet{bundle_id}"] = sha256_bytes(
            outputs[
                DEFAULT_PACKET_DIR
                / f"bundle{bundle_id}.final.private.v1.json"
            ]
        )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument(
        "--freeze-checkpoint-sha256",
        default=EXPECTED_FREEZE_CHECKPOINT_SHA256,
    )
    parser.add_argument(
        "--freeze-candidate-sha256",
        default=EXPECTED_FREEZE_CANDIDATE_SHA256,
    )
    args = parser.parse_args(argv)

    outputs, assignment = build_outputs(
        args.freeze_checkpoint_sha256,
        args.freeze_candidate_sha256,
    )
    observed = output_hashes(outputs)
    require(
        observed == EXPECTED_OUTPUT_SHA256,
        f"frozen WaveB output drift: {observed}",
    )
    if args.write:
        for path, payload in outputs.items():
            atomic_write(path, payload)
    else:
        for path, payload in outputs.items():
            require(path.read_bytes() == payload, f"file drift: {path}")

    print(
        json.dumps(
            {
                "status": assignment["status"],
                **assignment["result"],
                "output_sha256": observed,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
