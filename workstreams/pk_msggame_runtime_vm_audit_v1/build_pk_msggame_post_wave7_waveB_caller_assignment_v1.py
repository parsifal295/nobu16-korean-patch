#!/usr/bin/env python3
"""Build the provisional post-wave7 Wave-B caller-root assignment.

Wave B owns every still-pending PK record that directly executes 0143.  The
assignment is root-disjoint and exactly balances the actual current dispatch
cross-product across three bundles.

This artifact is deliberately *provisional*.  Wave A owns inline selectors
and jump terminals, so it can change the literal bytes read by these callers.
The packets therefore authorize zero actions and zero review decisions.  A
later finalizer must rebuild from the frozen post-Wave-A checkpoint, prove
control-topology identity, replace every terminal-byte snapshot, and freeze
the resulting candidate before review may begin.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
import math
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
    TMP
    / "runtime_vm_integrated."
    "post_selector292_wave7_root_sharded_consolidated_checkpoint.private.v1.jsonl"
)
ENGINE_BUILDER = DIALOGUE / "build_pc_dialogue_full_retranslation_v0150.py"
RANKING_BUILDER = AUDIT / "build_pk_next_selector_family_ranking_v1.py"
SHADOW_ROOT = (
    TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
SHADOW_CURRENT = SHADOW_ROOT / "MSG_PK" / "JP" / "msggame.bin"
PRISTINE = (
    SHADOW_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)

DEFAULT_ASSIGNMENT = (
    TMP / "pk_msggame_post_wave7_waveB_caller_assignment.private.v1.json"
)
DEFAULT_PUBLIC = (
    AUDIT
    / "public"
    / "pk_msggame_post_wave7_waveB_caller_assignment."
    "source_free.v1.json"
)
DEFAULT_PACKET_DIR = (
    TMP / "pk_msggame_post_wave7_waveB_caller_packets"
)

EXPECTED_INPUT_SHA256 = {
    "checkpoint":
        "B1CF7F4523DE9411BA5172E7C9DEA946C7646085C83A1480C51807E2DD0C90E7",
    "engine_builder":
        "CF32112EB7B0BA578DF9EF2E9D2A5C92818E25AC2217FE867BE7968F92D8372E",
    "ranking_builder": "19D8F10FC3995AD05A39AD12CD554292A47BF4A1AB572D28359130326FA69391",
    "shadow_current":
        "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
    "pristine":
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
}
EXPECTED_CANDIDATE_SHA256 = (
    "DAB40F2AA8095E67550B69213A53CC777B96B17071FFF5B860CFAEE1A868D7E0"
)
EXPECTED_PENDING_ROWS = 5_901
EXPECTED_CALLER_ROWS = 1_214
EXPECTED_CALLER_ROOTS = 717
EXPECTED_BRANCHES = 606_902
EXPECTED_BUNDLES = (
    {
        "branch_count": 202_301,
        "pending_coordinate_count": 396,
        "root_count": 238,
        "root_sha256":
            "A43E89308BE98B59AFA8BB933D452F6A2F6F0F430BCD2A59877E679CB62409AE",
    },
    {
        "branch_count": 202_300,
        "pending_coordinate_count": 411,
        "root_count": 240,
        "root_sha256":
            "1D021F3C7E080DF8E59C6E008F64E24FA15F68CFBFA56BA29AD1617DDF4C3FD6",
    },
    {
        "branch_count": 202_301,
        "pending_coordinate_count": 407,
        "root_count": 239,
        "root_sha256":
            "1EA4E7521B7468D82C0ECC543B5469A5F9088FCC6794EF891928B6C1BD455CF9",
    },
)

# Frozen after a reproducible bootstrap.
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "assignment": "10484CE4CD3D4413C770CE1F23FF165B658762C3B4FB022D1F4CE711A2F915BA",
    "public": "2C817E6DE4C8BAF20006415AC46E046B757FC8F131577D77E81E32472649FA04",
    "packet0": "20E6B287428B5985D96147CB1EC23CBA2BC9ACE76BC1F178433A395145AB5819",
    "packet1": "78739654A8F1C6285A7ACA889349FDDE4368A515E38632D74E4804378C5B9492",
    "packet2": "722FF0417657330EF77C4834C3FF4FFEB891B4A855A131857C910C3AA245C292",
}

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-msggame-post-wave7-waveB-caller-assignment."
    "private.v1"
)
PACKET_SCHEMA = (
    "nobu16.kr.pk-msggame-post-wave7-waveB-caller-packet.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-msggame-post-wave7-waveB-caller-assignment."
    "source-free.v1"
)
METHOD = (
    "post_wave7_all_pending_direct_0143_caller_roots_actual_jump_leaf_"
    "cross_product_lpt_three_way_provisional_pre_waveA"
)


class WaveBAssignmentError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WaveBAssignmentError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module(ENGINE_BUILDER, "pk_post_wave7_waveB_engine")
RANKING = load_module(RANKING_BUILDER, "pk_post_wave7_waveB_ranking")


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


def parse_coordinate(value: str) -> tuple[int, ...]:
    return tuple(map(int, value.split(":")))


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


def record_snapshot(
    records: Mapping[tuple[int, int], Any],
    root: tuple[int, int],
) -> dict[str, Any]:
    record = records[root]
    literals = list(ENGINE.parse_record_literals(record))
    return {
        "root": root_string(root),
        "record_data_sha256": sha256_bytes(record.data),
        "literal_count": len(literals),
        "literal_utf16le_sha256": [
            sha256_bytes(literal.text.encode("utf-16le"))
            for literal in literals
        ],
    }


def build_outputs() -> tuple[dict[Path, bytes], dict[str, Any]]:
    inputs = {
        "checkpoint": sha256_file(CHECKPOINT),
        "engine_builder": sha256_file(ENGINE_BUILDER),
        "ranking_builder": sha256_file(RANKING_BUILDER),
        "shadow_current": sha256_file(SHADOW_CURRENT),
        "pristine": sha256_file(PRISTINE),
    }
    require(inputs == EXPECTED_INPUT_SHA256, f"input hash drift: {inputs}")

    replacements: dict[tuple[int, int, int], str] = {}
    pending: defaultdict[tuple[int, int], set[str]] = defaultdict(set)
    for line in CHECKPOINT.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        if row.get("resource") != "pk_msggame":
            continue
        coordinate = str(row["coordinate"])
        key = parse_coordinate(coordinate)
        require(len(key) == 3, f"bad ledger coordinate: {coordinate}")
        if "translation" in row:
            replacements[key] = str(row["translation"])
        if row.get("runtime_review") == "pending":
            pending[key[:2]].add(coordinate)
    require(
        sum(len(values) for values in pending.values())
        == EXPECTED_PENDING_ROWS,
        "pending row count drift",
    )

    current_blob = SHADOW_CURRENT.read_bytes()
    candidate_blob = ENGINE.rebuild_packed_with_literals(
        current_blob, replacements
    )
    candidate_sha256 = sha256_bytes(candidate_blob)
    require(
        candidate_sha256 == EXPECTED_CANDIDATE_SHA256,
        f"candidate drift: {candidate_sha256}",
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate_blob).archive
    )
    source_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(PRISTINE.read_bytes()).archive
    )
    candidate_edges = RANKING.graph_edges(candidate_records)
    source_edges = RANKING.graph_edges(source_records)

    closure_cache: dict[tuple[int, int], dict[str, Any]] = {}

    def closure(target: tuple[int, int]) -> dict[str, Any]:
        if target not in closure_cache:
            nodes, edges, leaves = RANKING.jump_closure(
                candidate_edges, target
            )
            source_nodes, source_dispatch, source_leaves = (
                RANKING.jump_closure(source_edges, target)
            )
            closure_cache[target] = {
                "target": root_string(target),
                "candidate_nodes": nodes,
                "candidate_edges": edges,
                "candidate_leaves": leaves,
                "source_candidate_control_identical": (
                    nodes == source_nodes
                    and edges == source_dispatch
                    and leaves == source_leaves
                ),
            }
        return closure_cache[target]

    items: list[dict[str, Any]] = []
    for root in sorted(pending):
        calls = [
            edge
            for edge in candidate_edges[root]
            if edge["kind"] == "C"
        ]
        if not calls:
            continue
        call_rows: list[dict[str, Any]] = []
        branch_count = 1
        all_terminals: set[tuple[int, int]] = set()
        for occurrence, edge in enumerate(calls):
            target = tuple(edge["target"])
            profile = closure(target)
            terminals = set(profile["candidate_leaves"])
            terminal_count = len(terminals)
            require(terminal_count > 0, f"empty call closure: {target}")
            branch_count *= terminal_count
            all_terminals.update(terminals)
            call_rows.append(
                {
                    "occurrence": occurrence,
                    "gap_id": int(edge["gap_id"]),
                    "offset": int(edge["offset"]),
                    "target": root_string(target),
                    "terminal_count": terminal_count,
                    "terminal_root_sha256": root_digest(terminals),
                    "source_candidate_control_identical":
                        profile["source_candidate_control_identical"],
                }
            )
        coordinates = sorted(pending[root], key=parse_coordinate)
        items.append(
            {
                "root_tuple": root,
                "root": root_string(root),
                "pending_coordinates": coordinates,
                "pending_coordinate_count": len(coordinates),
                "pending_coordinate_sha256": coordinate_digest(coordinates),
                "direct_call_count": len(calls),
                "branch_count": branch_count,
                "calls": call_rows,
                "terminal_roots": sorted(all_terminals),
            }
        )

    require(len(items) == EXPECTED_CALLER_ROOTS, "caller root count drift")
    require(
        sum(row["pending_coordinate_count"] for row in items)
        == EXPECTED_CALLER_ROWS,
        "caller pending row count drift",
    )
    require(
        sum(row["branch_count"] for row in items)
        == EXPECTED_BRANCHES,
        "caller branch total drift",
    )

    bins: list[dict[str, Any]] = [
        {
            "branch_count": 0,
            "pending_coordinate_count": 0,
            "roots": [],
        }
        for _ in range(3)
    ]
    for item in sorted(
        items,
        key=lambda row: (
            -int(row["branch_count"]),
            -int(row["pending_coordinate_count"]),
            row["root_tuple"],
        ),
    ):
        bundle = min(
            bins,
            key=lambda row: (
                int(row["branch_count"]),
                int(row["pending_coordinate_count"]),
                len(row["roots"]),
            ),
        )
        bundle["branch_count"] += item["branch_count"]
        bundle["pending_coordinate_count"] += (
            item["pending_coordinate_count"]
        )
        bundle["roots"].append(item)

    packet_payloads: list[bytes] = []
    bundle_manifest: list[dict[str, Any]] = []
    global_owned_roots: set[tuple[int, int]] = set()
    global_owned_coordinates: set[str] = set()
    for bundle_id, bundle in enumerate(bins):
        roots = {row["root_tuple"] for row in bundle["roots"]}
        coordinates = {
            coordinate
            for row in bundle["roots"]
            for coordinate in row["pending_coordinates"]
        }
        terminals = {
            terminal
            for row in bundle["roots"]
            for terminal in row["terminal_roots"]
        }
        require(
            not global_owned_roots.intersection(roots),
            "bundle root ownership overlap",
        )
        require(
            not global_owned_coordinates.intersection(coordinates),
            "bundle coordinate ownership overlap",
        )
        global_owned_roots.update(roots)
        global_owned_coordinates.update(coordinates)

        expected = EXPECTED_BUNDLES[bundle_id]
        actual = {
            "branch_count": int(bundle["branch_count"]),
            "pending_coordinate_count": len(coordinates),
            "root_count": len(roots),
            "root_sha256": root_digest(roots),
        }
        require(actual == expected, f"bundle {bundle_id} drift: {actual}")

        terminal_snapshot = [
            record_snapshot(candidate_records, root)
            for root in sorted(terminals)
        ]
        packet_roots = []
        for row in sorted(
            bundle["roots"], key=lambda value: value["root_tuple"]
        ):
            packet_roots.append(
                {
                    key: value
                    for key, value in row.items()
                    if key not in {"root_tuple", "terminal_roots"}
                }
            )
        packet = {
            "schema": PACKET_SCHEMA,
            "method": METHOD,
            "status": "BLOCKED_PENDING_WAVE_A_FINAL_TERMINAL_SNAPSHOT",
            "bundle_id": bundle_id,
            "candidate_binding": {
                "pre_waveA_candidate_sha256": candidate_sha256,
                "checkpoint_sha256": inputs["checkpoint"],
            },
            "scope": {
                **actual,
                "pending_coordinate_sha256":
                    coordinate_digest(coordinates),
                "unique_terminal_root_count": len(terminals),
                "unique_terminal_root_sha256": root_digest(terminals),
            },
            "contract": {
                "actions_authorized": False,
                "review_start_authorized": False,
                "decision_rows_authorized": 0,
                "translation_changes_authorized": 0,
                "runtime_promotions_authorized": 0,
                "terminal_records_read_only": True,
                "full_rebuild_authorized": False,
                "steam_write_authorized": False,
                "waveA_checkpoint_required_before_review": True,
                "waveA_candidate_rebuild_required_before_review": True,
                "all_terminal_bytes_must_be_recomputed_after_waveA": True,
                "control_topology_must_match_this_assignment": True,
                "owned_root_set_must_match_this_assignment": True,
                "owned_coordinate_set_must_match_this_assignment": True,
                "branch_counts_must_be_recomputed_after_waveA": True,
                "packet_must_be_rewritten_and_refrozen_after_waveA": True,
            },
            "owned_roots": packet_roots,
            "pre_waveA_terminal_snapshot": terminal_snapshot,
            "pre_waveA_terminal_snapshot_sha256":
                canonical_sha256(terminal_snapshot),
        }
        packet_payload = serialized_json(packet)
        packet_payloads.append(packet_payload)
        bundle_manifest.append(
            {
                "bundle_id": bundle_id,
                **actual,
                "pending_coordinate_sha256":
                    coordinate_digest(coordinates),
                "unique_terminal_root_count": len(terminals),
                "unique_terminal_root_sha256": root_digest(terminals),
                "pre_waveA_terminal_snapshot_sha256":
                    packet["pre_waveA_terminal_snapshot_sha256"],
                "packet_sha256": sha256_bytes(packet_payload),
                "actions_authorized": False,
            }
        )

    require(
        len(global_owned_roots) == EXPECTED_CALLER_ROOTS,
        "global caller root union drift",
    )
    require(
        len(global_owned_coordinates) == EXPECTED_CALLER_ROWS,
        "global caller coordinate union drift",
    )

    assignment = {
        "schema": PRIVATE_SCHEMA,
        "method": METHOD,
        "status": "BLOCKED_PENDING_WAVE_A_FINAL_TERMINAL_SNAPSHOT",
        "inputs": {
            **inputs,
            "checkpoint_path":
                str(CHECKPOINT.relative_to(REPO)).replace("\\", "/"),
            "shadow_current_path":
                str(SHADOW_CURRENT.relative_to(REPO)).replace("\\", "/"),
            "pristine_path":
                str(PRISTINE.relative_to(REPO)).replace("\\", "/"),
        },
        "candidate_binding": {
            "pre_waveA_candidate_sha256": candidate_sha256,
        },
        "result": {
            "bundle_count": len(bins),
            "caller_root_count": len(global_owned_roots),
            "caller_pending_coordinate_count":
                len(global_owned_coordinates),
            "actual_branch_count": sum(
                row["branch_count"] for row in items
            ),
            "caller_root_sha256": root_digest(global_owned_roots),
            "caller_pending_coordinate_sha256":
                coordinate_digest(global_owned_coordinates),
        },
        "bundle_manifest": bundle_manifest,
        "global_disjointness": {
            "owned_root_intersections": 0,
            "owned_coordinate_intersections": 0,
            "bundle_pair_count": 3,
        },
        "finalization_gate": {
            "actions_authorized": False,
            "review_start_authorized": False,
            "waveA_checkpoint_sha256": None,
            "post_waveA_candidate_sha256": None,
            "terminal_snapshot_refrozen": False,
            "control_topology_reverified": False,
            "branch_counts_reverified": False,
            "Steam_write_performed": False,
        },
    }
    assignment_payload = serialized_json(assignment)

    public = {
        "schema": PUBLIC_SCHEMA,
        "method": METHOD,
        "status": assignment["status"],
        "inputs": {
            "checkpoint_sha256": inputs["checkpoint"],
            "engine_builder_sha256": inputs["engine_builder"],
            "ranking_builder_sha256": inputs["ranking_builder"],
            "shadow_current_sha256": inputs["shadow_current"],
            "pristine_sha256": inputs["pristine"],
            "pre_waveA_candidate_sha256": candidate_sha256,
        },
        "result": assignment["result"],
        "bundles": [
            {
                key: value
                for key, value in row.items()
                if key
                not in {
                    "pending_coordinate_sha256",
                    "unique_terminal_root_sha256",
                }
            }
            for row in bundle_manifest
        ],
        "proof": {
            "all_pending_direct_call_roots_owned": True,
            "owned_roots_pairwise_disjoint": True,
            "owned_coordinates_pairwise_disjoint": True,
            "actual_dispatch_cross_product_used": True,
            "actions_authorized": False,
            "review_start_authorized": False,
            "waveA_final_terminal_recalculation_required": True,
            "full_rebuild_performed": False,
            "steam_write_performed": False,
        },
    }
    public_payload = serialized_json(public)
    outputs = {
        DEFAULT_ASSIGNMENT: assignment_payload,
        DEFAULT_PUBLIC: public_payload,
        DEFAULT_PACKET_DIR / "bundle0.private.v1.json":
            packet_payloads[0],
        DEFAULT_PACKET_DIR / "bundle1.private.v1.json":
            packet_payloads[1],
        DEFAULT_PACKET_DIR / "bundle2.private.v1.json":
            packet_payloads[2],
    }
    return outputs, assignment


def output_hashes(outputs: Mapping[Path, bytes]) -> dict[str, str]:
    return {
        "assignment": sha256_bytes(outputs[DEFAULT_ASSIGNMENT]),
        "public": sha256_bytes(outputs[DEFAULT_PUBLIC]),
        "packet0": sha256_bytes(
            outputs[DEFAULT_PACKET_DIR / "bundle0.private.v1.json"]
        ),
        "packet1": sha256_bytes(
            outputs[DEFAULT_PACKET_DIR / "bundle1.private.v1.json"]
        ),
        "packet2": sha256_bytes(
            outputs[DEFAULT_PACKET_DIR / "bundle2.private.v1.json"]
        ),
    }


def verify_expected(outputs: Mapping[Path, bytes]) -> None:
    missing = [
        key
        for key, value in EXPECTED_OUTPUT_SHA256.items()
        if value is None
    ]
    require(not missing, f"unfrozen output hashes: {missing}")
    actual = output_hashes(outputs)
    require(
        actual == EXPECTED_OUTPUT_SHA256,
        f"output hash drift: {actual}",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--bootstrap", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    outputs, assignment = build_outputs()
    if not args.bootstrap:
        verify_expected(outputs)
    if args.bootstrap or args.write:
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
                "output_sha256": output_hashes(outputs),
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
