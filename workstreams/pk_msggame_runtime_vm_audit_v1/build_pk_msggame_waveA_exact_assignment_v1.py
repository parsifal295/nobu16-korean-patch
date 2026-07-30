#!/usr/bin/env python3
"""Build the exact post-Wave7 inline-selector/incoming-J WaveA assignment.

This tracked builder reconstructs the frozen Wave7 candidate, derives
the residual classes from the exact reversed VM, groups incoming-J terminal
leaves by their complete reverse-J top-root tuple, and assigns the resulting
root-atomic units to three deterministic LPT bundles.  It writes ignored
private review packets plus a source-free public assignment; it never rebuilds
the full integration or writes to Steam.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
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
DIALOGUE = REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
CHECKPOINT = (
    TMP
    / "runtime_vm_integrated."
    "post_selector292_wave7_root_sharded_consolidated_checkpoint."
    "private.v1.jsonl"
)
VM_BUILDER = WORKSTREAM / "build_pk_msggame_runtime_vm_audit_v1.py"
RANKING_BUILDER = WORKSTREAM / "build_pk_next_selector_family_ranking_v1.py"
ENGINE_BUILDER = DIALOGUE / "build_pc_dialogue_full_retranslation_v0150.py"
DEV_ROOT = TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
CURRENT = DEV_ROOT / "MSG_PK" / "JP" / "msggame.bin"
JP_SOURCE = (
    DEV_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
CONTEXT_PATHS = {
    language: DEV_ROOT / "MSG_PK" / language.upper() / "msggame.bin"
    for language in ("en", "sc", "tc")
}
DEFAULT_ASSIGNMENT = TMP / "pk_msggame_waveA_exact_assignment.private.v1.json"
DEFAULT_PUBLIC = (
    WORKSTREAM
    / "public"
    / "pk_msggame_waveA_exact_assignment.source_free.v1.json"
)
PACKET_DIR = TMP / "pk_msggame_waveA_exact_packets"
DEFAULT_PACKETS = tuple(
    PACKET_DIR / f"A{index}.private.v1.json" for index in range(3)
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
    "current":
        "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
    "jp_source":
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "en":
        "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "sc":
        "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "tc":
        "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}
EXPECTED_CANDIDATE_SHA256 = (
    "DAB40F2AA8095E67550B69213A53CC777B96B17071FFF5B860CFAEE1A868D7E0"
)
EXPECTED_CHECKPOINT_ROWS = 52_803
EXPECTED_PENDING_ROWS = 5_901
EXPECTED_STATIC = (1_254, 674)
EXPECTED_INLINE = (1_679, 925)
EXPECTED_TERMINAL = (1_754, 1_617)
EXPECTED_TERMINAL_GROUPS = 367
EXPECTED_WAVEA = (3_433, 2_542)
EXPECTED_BUNDLES = (
    (1_144, 852, 430),
    (1_144, 853, 431),
    (1_145, 837, 431),
)
EXPECTED_BUNDLE_ROOT_SHA256 = (
    "B7CC5F469D9DAE5195AED291C07CF42C3E7C08936443B0E9E695BA55A38EA516",
    "A12E2BB93DD5DA25A465DAD31ECAC4B09D66DB2A0A3BB2C2E9F74F94E9CB5961",
    "CED2A1511B00542EE959C963CFBCA626F43E74D8D21781227964DF26298B81CE",
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "assignment":
        "352BA44152920A269D092237DA70F5278FADB295D3AEB4B8F52BD8B7DA78448F",
    "public":
        "B6F5D4A92A9968D10D449633AE8D3A4940560F849AC8F9AEEF7FAD7ECDABC341",
    "A0":
        "E45B355C4606E8BA56E34CFD89D48668E5ACF25889C4562B44388F7FA69AB4A2",
    "A1":
        "EE59AF760C9940C259A27B0813A7777B2B63A7E9DDE3C18F2DDF53EA6DAB41B7",
    "A2":
        "EB87B46196D03354E7E6B22658F929D9CF7CD961FDC5A76ACAD29A1C09924823",
}

ALLOWED_LOCAL = frozenset(
    {"literal_boundary", "block_token", "control_tag", "output_control"}
)
ASSIGNMENT_SCHEMA = "nobu16.kr.pk-msggame-waveA-exact-assignment.private.v1"
PACKET_SCHEMA = "nobu16.kr.pk-msggame-waveA-exact-packet.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-msggame-waveA-exact-assignment.source-free.v1"
METHOD = (
    "wave7_exact_reversed_vm_inline_selector_and_reverse_incoming_jump_"
    "top_root_grouped_root_atomic_three_way_lpt"
)


class WaveAError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WaveAError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


VM = load_module(VM_BUILDER, "pk_waveA_vm")
RANKING = load_module(RANKING_BUILDER, "pk_waveA_ranking")
ENGINE = load_module(ENGINE_BUILDER, "pk_waveA_engine")


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


def private_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return parts


def root_string(root: tuple[int, int]) -> str:
    return f"{root[0]}:{root[1]}"


def root_from_string(value: str) -> tuple[int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 2, f"invalid root: {value}")
    return parts


def root_digest(roots: Iterable[tuple[int, int]]) -> str:
    # Frozen contract: roots are serialized as lexically sorted "block:record".
    values = sorted(root_string(root) for root in set(roots))
    return sha256_bytes("".join(f"{value}\n" for value in values).encode("ascii"))


def coordinate_digest(values: Iterable[str]) -> str:
    ordered = sorted(set(values), key=parse_coordinate)
    return sha256_bytes("".join(f"{value}\n" for value in ordered).encode("ascii"))


def relative(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


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


def archive(path: Path) -> dict[tuple[int, int], Any]:
    return ENGINE.archive_records(ENGINE.parse_packed_msggame(path.read_bytes()).archive)


def record_payload(
    records: Mapping[tuple[int, int], Any],
    root: tuple[int, int],
) -> dict[str, Any]:
    record = records.get(root)
    if record is None:
        return {"available": False, "boundaries": [], "gaps_raw_hex": [], "literals": []}
    literals = [row.text for row in ENGINE.parse_record_literals(record)]
    gaps = list(ENGINE.record_gap_bytes(record))
    return {
        "available": True,
        "boundaries": [
            {
                "boundary_index": index,
                "left": "" if index == 0 else literals[index - 1],
                "right": "" if index == len(literals) else literals[index],
            }
            for index in range(len(literals) + 1)
        ],
        "gaps_raw_hex": [gap.hex().upper() for gap in gaps],
        "literals": literals,
        "record_data_sha256": sha256_bytes(record.data),
    }


def matrix(
    root: tuple[int, int],
    *,
    records_by_language: Mapping[str, Mapping[tuple[int, int], Any]],
) -> dict[str, Any]:
    payloads = {
        language: record_payload(records, root)
        for language, records in records_by_language.items()
    }
    max_boundaries = max(
        (len(value["boundaries"]) for value in payloads.values()), default=0
    )
    columns = []
    for index in range(max_boundaries):
        column: dict[str, Any] = {"boundary_index": index}
        for language, payload in payloads.items():
            if index < len(payload["boundaries"]):
                column[language] = payload["boundaries"][index]
            else:
                column[language] = {"available": False}
        columns.append(column)
    return {
        "columns": columns,
        "language_order": ["jp", "candidate", "current", "en", "sc", "tc"],
        "languages": payloads,
        "matrix_sha256": canonical_sha256(columns),
    }


def reverse_j_proof(
    terminal: tuple[int, int],
    incoming_j: Mapping[tuple[int, int], Sequence[Mapping[str, Any]]],
) -> tuple[tuple[tuple[int, int], ...], tuple[dict[str, Any], ...]]:
    stack = [terminal]
    visited: set[tuple[int, int]] = set()
    tops: set[tuple[int, int]] = set()
    proof_edges: dict[tuple[Any, ...], dict[str, Any]] = {}
    while stack:
        target = stack.pop()
        if target in visited:
            continue
        visited.add(target)
        parents = incoming_j.get(target, ())
        if not parents:
            tops.add(target)
            continue
        for row in parents:
            source = tuple(row["source"])
            key = (source, target, int(row["gap_id"]), int(row["offset"]))
            proof_edges[key] = {
                "gap_id": int(row["gap_id"]),
                "kind": "J",
                "offset": int(row["offset"]),
                "source": root_string(source),
                "target": root_string(target),
            }
            stack.append(source)
    require(tops, f"reverse-J closure has no top root: {root_string(terminal)}")
    edges = tuple(
        proof_edges[key]
        for key in sorted(
            proof_edges,
            key=lambda value: (value[0], value[1], value[2], value[3]),
        )
    )
    return tuple(sorted(tops)), edges


def build_outputs() -> tuple[bytes, tuple[bytes, ...], dict[str, Any]]:
    input_paths = {
        "checkpoint": CHECKPOINT,
        "vm_builder": VM_BUILDER,
        "ranking_builder": RANKING_BUILDER,
        "engine_builder": ENGINE_BUILDER,
        "current": CURRENT,
        "jp_source": JP_SOURCE,
        **CONTEXT_PATHS,
    }
    observed_inputs = {name: sha256_file(path) for name, path in input_paths.items()}
    require(observed_inputs == EXPECTED_INPUT_SHA256, f"input hash drift: {observed_inputs}")

    rows: dict[str, dict[str, Any]] = {}
    replacements: dict[tuple[int, int, int], str] = {}
    pending: defaultdict[tuple[int, int], list[str]] = defaultdict(list)
    checkpoint_rows = 0
    with CHECKPOINT.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            checkpoint_rows += 1
            row = json.loads(line)
            if row.get("resource") != "pk_msggame":
                continue
            coordinate = str(row["coordinate"])
            key = parse_coordinate(coordinate)
            rows[coordinate] = row
            if "translation" in row:
                replacements[key] = str(row["translation"])
            if row.get("runtime_review") == "pending":
                pending[key[:2]].append(coordinate)
    require(checkpoint_rows == EXPECTED_CHECKPOINT_ROWS, "checkpoint row count drift")
    require(sum(map(len, pending.values())) == EXPECTED_PENDING_ROWS, "pending row drift")

    candidate_blob = ENGINE.rebuild_packed_with_literals(
        CURRENT.read_bytes(), replacements
    )
    candidate_sha256 = sha256_bytes(candidate_blob)
    require(candidate_sha256 == EXPECTED_CANDIDATE_SHA256, "candidate drift")
    candidate = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate_blob).archive
    )
    current = archive(CURRENT)
    source = archive(JP_SOURCE)
    contexts = {language: archive(path) for language, path in CONTEXT_PATHS.items()}
    records_by_language = {
        "jp": source,
        "candidate": candidate,
        "current": current,
        **contexts,
    }

    edges = RANKING.graph_edges(candidate)
    incoming_all: defaultdict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    incoming_j: defaultdict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for source_root, values in edges.items():
        for value in values:
            target = tuple(value["target"])
            row = {
                "gap_id": int(value["gap_id"]),
                "kind": str(value["kind"]),
                "offset": int(value["offset"]),
                "source": [source_root[0], source_root[1]],
                "target": [target[0], target[1]],
            }
            incoming_all[target].append(row)
            if value["kind"] == "J":
                incoming_j[target].append(row)
    for values in incoming_all.values():
        values.sort(
            key=lambda row: (
                tuple(row["source"]), row["gap_id"], row["offset"], row["kind"]
            )
        )
    for values in incoming_j.values():
        values.sort(
            key=lambda row: (tuple(row["source"]), row["gap_id"], row["offset"])
        )

    static_roots: list[tuple[int, int]] = []
    inline_roots: list[tuple[int, int]] = []
    terminal_roots: list[tuple[int, int]] = []
    components_by_root: dict[tuple[int, int], tuple[dict[str, Any], ...]] = {}
    for root in sorted(pending):
        components = VM.decode_record(candidate[root])
        components_by_root[root] = components
        dynamic = tuple(
            component
            for component in components
            if component["kind"] not in ALLOWED_LOCAL
        )
        outgoing = edges[root]
        if not outgoing and not incoming_j[root] and not dynamic:
            static_roots.append(root)
        if (
            not outgoing
            and not incoming_j[root]
            and 1 <= len(dynamic) <= 7
            and {component["kind"] for component in dynamic} == {"selector"}
        ):
            inline_roots.append(root)
        if not outgoing and incoming_j[root]:
            terminal_roots.append(root)

    def class_count(roots: Sequence[tuple[int, int]]) -> tuple[int, int]:
        return sum(len(pending[root]) for root in roots), len(roots)

    require(class_count(static_roots) == EXPECTED_STATIC, "static exclusion drift")
    require(class_count(inline_roots) == EXPECTED_INLINE, "inline class drift")
    require(class_count(terminal_roots) == EXPECTED_TERMINAL, "terminal class drift")
    require(
        not (set(static_roots) & set(inline_roots))
        and not (set(static_roots) & set(terminal_roots))
        and not (set(inline_roots) & set(terminal_roots)),
        "class roots overlap",
    )

    terminal_groups: defaultdict[
        tuple[tuple[int, int], ...], list[tuple[int, int]]
    ] = defaultdict(list)
    terminal_proofs: dict[
        tuple[int, int], tuple[tuple[tuple[int, int], ...], tuple[dict[str, Any], ...]]
    ] = {}
    for root in terminal_roots:
        proof = reverse_j_proof(root, incoming_j)
        terminal_proofs[root] = proof
        terminal_groups[proof[0]].append(root)
    require(len(terminal_groups) == EXPECTED_TERMINAL_GROUPS, "terminal group drift")

    units: list[dict[str, Any]] = []
    for root in inline_roots:
        units.append(
            {
                "class": "inline-selector",
                "coordinates": tuple(sorted(pending[root], key=parse_coordinate)),
                "roots": (root,),
                "top_roots": (root,),
            }
        )
    for tops, group_roots in terminal_groups.items():
        ordered_roots = tuple(sorted(group_roots))
        units.append(
            {
                "class": "incoming-J-terminal",
                "coordinates": tuple(
                    coordinate
                    for root in ordered_roots
                    for coordinate in sorted(pending[root], key=parse_coordinate)
                ),
                "roots": ordered_roots,
                "top_roots": tops,
            }
        )
    units.sort(
        key=lambda unit: (
            -len(unit["coordinates"]),
            -len(unit["roots"]),
            unit["class"],
            unit["roots"],
        )
    )
    require(
        (
            sum(len(unit["coordinates"]) for unit in units),
            sum(len(unit["roots"]) for unit in units),
        )
        == EXPECTED_WAVEA,
        "WaveA coverage drift",
    )

    bundles = [
        {"coordinate_count": 0, "root_count": 0, "units": []}
        for _ in range(3)
    ]
    for unit in units:
        target = min(
            range(3),
            key=lambda index: (
                bundles[index]["coordinate_count"],
                bundles[index]["root_count"],
                len(bundles[index]["units"]),
            ),
        )
        bundles[target]["units"].append(unit)
        bundles[target]["coordinate_count"] += len(unit["coordinates"])
        bundles[target]["root_count"] += len(unit["roots"])

    packet_values: list[dict[str, Any]] = []
    all_owned_roots: set[tuple[int, int]] = set()
    all_owned_coordinates: set[str] = set()
    for bundle_id, bundle in enumerate(bundles):
        bundle_units = bundle["units"]
        owned_roots = {
            root for unit in bundle_units for root in unit["roots"]
        }
        owned_coordinates = {
            coordinate
            for unit in bundle_units
            for coordinate in unit["coordinates"]
        }
        require(not (all_owned_roots & owned_roots), "root has multiple owners")
        require(
            not (all_owned_coordinates & owned_coordinates),
            "coordinate has multiple owners",
        )
        all_owned_roots.update(owned_roots)
        all_owned_coordinates.update(owned_coordinates)

        unit_rows = []
        for unit_id, unit in enumerate(bundle_units):
            reverse_edges: dict[tuple[Any, ...], dict[str, Any]] = {}
            if unit["class"] == "incoming-J-terminal":
                for root in unit["roots"]:
                    for edge in terminal_proofs[root][1]:
                        key = (
                            root_from_string(edge["source"]),
                            root_from_string(edge["target"]),
                            edge["gap_id"],
                            edge["offset"],
                        )
                        reverse_edges[key] = edge
            unit_rows.append(
                {
                    "class": unit["class"],
                    "coordinate_count": len(unit["coordinates"]),
                    "coordinate_sha256": coordinate_digest(unit["coordinates"]),
                    "coordinates": list(unit["coordinates"]),
                    "root_count": len(unit["roots"]),
                    "root_sha256": root_digest(unit["roots"]),
                    "roots": [root_string(root) for root in unit["roots"]],
                    "reverse_j_edges": [
                        reverse_edges[key] for key in sorted(reverse_edges)
                    ],
                    "top_root_count": len(unit["top_roots"]),
                    "top_roots": [
                        root_string(root) for root in unit["top_roots"]
                    ],
                    "unit_id": unit_id,
                }
            )

        root_rows = []
        for root in sorted(owned_roots):
            components = components_by_root[root]
            component_rows = [
                {"component_index": index, **component}
                for index, component in enumerate(components)
            ]
            incoming_rows = [
                {
                    **row,
                    "source": root_string(tuple(row["source"])),
                    "target": root_string(tuple(row["target"])),
                }
                for row in incoming_all[root]
            ]
            root_rows.append(
                {
                    "candidate_outgoing_edges": [
                        {
                            "gap_id": int(row["gap_id"]),
                            "kind": str(row["kind"]),
                            "offset": int(row["offset"]),
                            "target": root_string(tuple(row["target"])),
                        }
                        for row in edges[root]
                    ],
                    "incoming_control_call_edges": incoming_rows,
                    "pending_coordinate_count": len(pending[root]),
                    "pending_coordinates": sorted(
                        pending[root], key=parse_coordinate
                    ),
                    "root": root_string(root),
                    "terminal_boundary_matrix": matrix(
                        root, records_by_language=records_by_language
                    ),
                    "vm_component_count": len(component_rows),
                    "vm_component_sha256": canonical_sha256(component_rows),
                    "vm_components": component_rows,
                }
            )

        packet = {
            "agent_contract": {
                "exact_vm_topology_required": True,
                "full_integration_rebuild_authorized": False,
                "jp_authoritative": True,
                "nonpending_root_actions_authorized": False,
                "source_only_action_count": 0,
                "steam_write_authorized": False,
                "terminal_boundary_matrix_required": True,
            },
            "assignment_id": f"WaveA-A{bundle_id}",
            "candidate_sha256": candidate_sha256,
            "method": METHOD,
            "packet_id": bundle_id,
            "root_contexts": root_rows,
            "schema": PACKET_SCHEMA,
            "scope": {
                "coordinate_count": len(owned_coordinates),
                "coordinate_sha256": coordinate_digest(owned_coordinates),
                "incoming_j_terminal_root_count": sum(
                    len(unit["roots"])
                    for unit in bundle_units
                    if unit["class"] == "incoming-J-terminal"
                ),
                "inline_selector_root_count": sum(
                    len(unit["roots"])
                    for unit in bundle_units
                    if unit["class"] == "inline-selector"
                ),
                "root_count": len(owned_roots),
                "root_sha256": root_digest(owned_roots),
                "unit_count": len(bundle_units),
            },
            "units": unit_rows,
        }
        packet_values.append(packet)

    require(
        all_owned_roots == set(inline_roots) | set(terminal_roots),
        "root coverage is not exact",
    )
    require(
        all_owned_coordinates
        == {
            coordinate
            for root in set(inline_roots) | set(terminal_roots)
            for coordinate in pending[root]
        },
        "coordinate coverage is not exact",
    )
    bundle_counts = tuple(
        (
            int(packet["scope"]["coordinate_count"]),
            int(packet["scope"]["root_count"]),
            int(packet["scope"]["unit_count"]),
        )
        for packet in packet_values
    )
    require(bundle_counts == EXPECTED_BUNDLES, f"bundle count drift: {bundle_counts}")
    bundle_root_hashes = tuple(
        str(packet["scope"]["root_sha256"]) for packet in packet_values
    )
    require(
        bundle_root_hashes == EXPECTED_BUNDLE_ROOT_SHA256,
        f"bundle root digest drift: {bundle_root_hashes}",
    )

    packet_payloads = tuple(private_bytes(packet) for packet in packet_values)
    packet_hashes = tuple(map(sha256_bytes, packet_payloads))
    assignment = {
        "agent_contract": {
            "full_integration_rebuild_authorized": False,
            "nonpending_root_actions_authorized": False,
            "source_only_action_count": 0,
            "steam_write_authorized": False,
        },
        "bindings": {
            "candidate_sha256": candidate_sha256,
            "checkpoint_sha256": observed_inputs["checkpoint"],
            "input_sha256": observed_inputs,
        },
        "classification": {
            "incoming_j_terminal": {
                "coordinate_count": EXPECTED_TERMINAL[0],
                "root_count": EXPECTED_TERMINAL[1],
                "top_root_group_count": EXPECTED_TERMINAL_GROUPS,
            },
            "inline_selector": {
                "coordinate_count": EXPECTED_INLINE[0],
                "root_count": EXPECTED_INLINE[1],
                "selector_count_range": [1, 7],
            },
            "local_static_excluded": {
                "coordinate_count": EXPECTED_STATIC[0],
                "root_count": EXPECTED_STATIC[1],
            },
        },
        "method": METHOD,
        "packet_artifacts": [
            {
                "packet_id": index,
                "path": relative(DEFAULT_PACKETS[index]),
                "sha256": packet_hashes[index],
                "scope": packet_values[index]["scope"],
            }
            for index in range(3)
        ],
        "result": {
            "bundle_count": 3,
            "exact_coordinate_coverage": True,
            "exact_root_coverage": True,
            "pairwise_coordinate_overlap_count": 0,
            "pairwise_root_overlap_count": 0,
            "waveA_coordinate_count": len(all_owned_coordinates),
            "waveA_root_count": len(all_owned_roots),
            "waveA_unit_count": len(units),
        },
        "root_digest_serialization": (
            "sha256_ascii_of_lexically_sorted_block_colon_record_plus_lf"
        ),
        "schema": ASSIGNMENT_SCHEMA,
    }
    return private_bytes(assignment), packet_payloads, assignment


def build_public(assignment: Mapping[str, Any]) -> dict[str, Any]:
    """Return the source-free audit summary for the frozen private packets."""
    return {
        "bundles": [
            {
                "coordinate_count": int(artifact["scope"]["coordinate_count"]),
                "coordinate_sha256": str(artifact["scope"]["coordinate_sha256"]),
                "packet_id": int(artifact["packet_id"]),
                "packet_sha256": str(artifact["sha256"]),
                "root_count": int(artifact["scope"]["root_count"]),
                "root_sha256": str(artifact["scope"]["root_sha256"]),
                "unit_count": int(artifact["scope"]["unit_count"]),
            }
            for artifact in assignment["packet_artifacts"]
        ],
        "classification": assignment["classification"],
        "inputs": {
            "candidate_sha256": assignment["bindings"]["candidate_sha256"],
            "checkpoint_sha256": assignment["bindings"]["checkpoint_sha256"],
            "engine_builder_sha256":
                assignment["bindings"]["input_sha256"]["engine_builder"],
            "jp_source_sha256":
                assignment["bindings"]["input_sha256"]["jp_source"],
            "runtime_vm_builder_sha256":
                assignment["bindings"]["input_sha256"]["vm_builder"],
        },
        "method": assignment["method"],
        "proof": {
            "exact_coordinate_coverage": True,
            "exact_root_coverage": True,
            "full_integration_rebuild_performed": False,
            "owned_coordinates_pairwise_disjoint": True,
            "owned_roots_pairwise_disjoint": True,
            "source_only_action_count": 0,
            "steam_write_performed": False,
        },
        "result": assignment["result"],
        "schema": PUBLIC_SCHEMA,
        "status": "ASSIGNED_REVIEW_IN_PROGRESS",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--bootstrap-output-pins", action="store_true")
    args = parser.parse_args(argv)

    assignment_payload, packet_payloads, assignment = build_outputs()
    public_payload = private_bytes(build_public(assignment))
    outputs = {
        "assignment": (DEFAULT_ASSIGNMENT, assignment_payload),
        "public": (DEFAULT_PUBLIC, public_payload),
        **{
            f"A{index}": (DEFAULT_PACKETS[index], packet_payloads[index])
            for index in range(3)
        },
    }
    observed = {name: sha256_bytes(payload) for name, (_path, payload) in outputs.items()}
    if not args.bootstrap_output_pins:
        require(
            all(EXPECTED_OUTPUT_SHA256.values()),
            "output pins unresolved; bootstrap first",
        )
        require(observed == EXPECTED_OUTPUT_SHA256, f"output hash drift: {observed}")
    if args.write:
        for path, payload in outputs.values():
            atomic_write(path, payload)
    else:
        for name, (path, payload) in outputs.items():
            require(path.is_file(), f"missing output: {path}")
            require(path.read_bytes() == payload, f"output differs: {name}")
    print(
        json.dumps(
            {
                "assignment_path": relative(DEFAULT_ASSIGNMENT),
                "bundle_counts": EXPECTED_BUNDLES,
                "candidate_sha256": assignment["bindings"]["candidate_sha256"],
                "full_integration_rebuild": False,
                "output_sha256": observed,
                "packet_paths": [relative(path) for path in DEFAULT_PACKETS],
                "source_only_actions": 0,
                "steam_write": False,
                "waveA_coordinates": assignment["result"]["waveA_coordinate_count"],
                "waveA_roots": assignment["result"]["waveA_root_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
