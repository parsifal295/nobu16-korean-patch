#!/usr/bin/env python3
"""Rank the next PK seven-way selector family on the official 81B4 ledger.

This is a read-only planning audit.  It reconstructs the final PK candidate
in memory, walks every 0143/014A closure reachable from a currently pending
record, identifies the fixed 13-node / 13-edge / seven-terminal selector
shape, and removes the already owned 538, 568, and 1096 closures.

No translation is proposed here.  Coordinate-bearing detail stays below
``tmp``; the tracked report contains only source-free coordinates, counts,
and cryptographic guards.  There is no Steam write path.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
ENGINE_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "build_pc_dialogue_full_retranslation_v0150.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP
    / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = DIALOGUE_TMP / "runtime_vm_integrated.private.v1.jsonl"
SELECTOR568_DECISIONS = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector568_family_consolidated_closure_decisions.private.v1.jsonl"
)
SELECTOR1096_DECISIONS = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1096_family_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP / "pk_next_selector_family_ranking.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking.source_free.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-next-selector-family-ranking.private.v1"
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-source-free.v1"
)
METHOD = "official81b4_pending_reachable_0143_seven_way_selector_ranking"

CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
CONTROL_RE = re.compile(b"\x01([CJ])(.{4})", re.DOTALL)
OWNED_SELECTORS = (538, 568, 1096)

EXPECTED_LEDGER_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_PK_CURRENT_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PK_PRISTINE_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "DCB19B0D85422F7C0EA5888F9A0C47667D75A88D100BABAE11DDAF4A8DD2000E"
)
EXPECTED_SELECTOR568_DECISION_SHA256 = (
    "500A3E36AA434819D75917E35AD60D8576C1B8CE8B2E4F408DDBAF2E2D800CCE"
)
EXPECTED_SELECTOR1096_DECISION_SHA256 = (
    "DCE8F3441EA8852BAACB222D1A122864208EA191354B0C73F1609EB33A8F6A4B"
)
EXPECTED_LEDGER_ROWS = 52_803
EXPECTED_PK_PENDING_ROWS = 7_896
EXPECTED_SELECTOR568_PROMOTIONS = 225
EXPECTED_SELECTOR1096_PROMOTIONS = 206
EXPECTED_REACHABLE_CALL_TARGETS = 170
EXPECTED_OWNED_CALL_TARGETS = 4
EXPECTED_NON_SEVEN_WAY_TARGETS = 26
EXPECTED_ELIGIBLE_FAMILIES = 140
EXPECTED_ELIGIBLE_UNION_ROWS = 2_525
EXPECTED_RECOMMENDED_SELECTOR = "0:1174"
EXPECTED_RECOMMENDED_TERMINALS = tuple(
    f"0:{record_id}" for record_id in range(2644, 2651)
)
EXPECTED_RECOMMENDED_POTENTIAL = 242
EXPECTED_RECOMMENDED_OVERLAP_568 = 0
EXPECTED_RECOMMENDED_OVERLAP_1096 = 18
EXPECTED_RECOMMENDED_DISJOINT = 224
EXPECTED_RECOMMENDED_PENDING_ROOTS = 80
EXPECTED_RECOMMENDED_PENDING_SITES = 82
EXPECTED_RECOMMENDED_CANDIDATE_SITES = 115
EXPECTED_RECOMMENDED_SOURCE_SITES = 121
EXPECTED_POINT_ESTIMATE = 167
EXPECTED_ESTIMATE_RANGE = (152, 187)

# Frozen after the first reproducible write/check cycle.
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "DBEAF9685FAF9F2987DF0267DA40139FF6520F20A02CD1748CCD4280FC591DDE"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "395BEC89F4D37D1F2272145DA8E250B4FF973DBE49818A133242C493A0354541"
)


class RankingError(ValueError):
    """Raised when the next-selector ranking inputs or result drift."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RankingError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Bind the existing full-retranslation engine rather than duplicating the
# packed MSG parser and literal-preserving candidate rebuild.
ENGINE = load_module(ENGINE_PATH, "pk_next_selector_ranking_engine_v1")


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


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return parts


def parse_root(value: str) -> tuple[int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 2, f"invalid root: {value}")
    return parts


def root_string(root: tuple[int, int]) -> str:
    return f"{root[0]}:{root[1]}"


def coordinate_digest(values: Iterable[str]) -> str:
    payload = "".join(
        f"{value}\n"
        for value in sorted(set(values), key=parse_coordinate)
    )
    return sha256_bytes(payload.encode("ascii"))


def root_digest(values: Iterable[tuple[int, int]]) -> str:
    payload = "".join(
        f"{root_string(value)}\n" for value in sorted(set(values))
    )
    return sha256_bytes(payload.encode("ascii"))


def site_key(value: str) -> tuple[int, int, int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 4, f"invalid site: {value}")
    return parts


def site_digest(values: Iterable[str]) -> str:
    payload = "".join(
        f"{value}\n" for value in sorted(set(values), key=site_key)
    )
    return sha256_bytes(payload.encode("ascii"))


def edge_digest(
    values: Iterable[tuple[tuple[int, int], tuple[int, int]]],
) -> str:
    payload = "".join(
        f"{root_string(source)}>{root_string(target)}\n"
        for source, target in sorted(set(values))
    )
    return sha256_bytes(payload.encode("ascii"))


def packed_target(operand: bytes) -> tuple[int, int]:
    value = int.from_bytes(operand, "little")
    return value // 10_000, value % 10_000


def record_edges(record: Any) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for gap_id, gap in enumerate(ENGINE.record_gap_bytes(record)):
        for match in CONTROL_RE.finditer(gap):
            result.append(
                {
                    "kind": match.group(1).decode("ascii"),
                    "target": packed_target(match.group(2)),
                    "gap_id": gap_id,
                    "offset": match.start(),
                }
            )
    return result


def graph_edges(
    records: Mapping[tuple[int, int], Any],
) -> dict[tuple[int, int], list[dict[str, Any]]]:
    return {
        root: record_edges(record)
        for root, record in records.items()
    }


def jump_closure(
    edges_by_root: Mapping[tuple[int, int], Sequence[Mapping[str, Any]]],
    start: tuple[int, int],
) -> tuple[
    set[tuple[int, int]],
    set[tuple[tuple[int, int], tuple[int, int]]],
    set[tuple[int, int]],
]:
    pending = [start]
    visited: set[tuple[int, int]] = set()
    edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    while pending:
        root = pending.pop()
        if root in visited:
            continue
        require(root in edges_by_root, f"missing jump target record: {root}")
        visited.add(root)
        for row in edges_by_root[root]:
            if row["kind"] != "J":
                continue
            target = tuple(row["target"])
            edges.add((root, target))
            pending.append(target)
    leaves = {
        root
        for root in visited
        if not any(
            row["kind"] == "J" for row in edges_by_root[root]
        )
    }
    return visited, edges, leaves


def candidate_call_sites(
    edges_by_root: Mapping[tuple[int, int], Sequence[Mapping[str, Any]]],
) -> dict[tuple[int, int], list[str]]:
    result: defaultdict[tuple[int, int], list[str]] = defaultdict(list)
    for root, rows in edges_by_root.items():
        for row in rows:
            if row["kind"] != "C":
                continue
            target = tuple(row["target"])
            result[target].append(
                f"{root[0]}:{root[1]}:{row['gap_id']}:{row['offset']}"
            )
    return {
        target: sorted(sites, key=site_key)
        for target, sites in result.items()
    }


def reachable_call_targets(
    edges_by_root: Mapping[tuple[int, int], Sequence[Mapping[str, Any]]],
    start: tuple[int, int],
) -> set[tuple[int, int]]:
    pending = [start]
    visited: set[tuple[int, int]] = set()
    calls: set[tuple[int, int]] = set()
    while pending:
        root = pending.pop()
        if root in visited:
            continue
        require(root in edges_by_root, f"missing control target record: {root}")
        visited.add(root)
        for row in edges_by_root[root]:
            target = tuple(row["target"])
            if row["kind"] == "C":
                calls.add(target)
            pending.append(target)
    return calls


def load_official_ledger(
    path: Path,
) -> tuple[
    dict[tuple[int, int, int], str],
    dict[tuple[int, int], set[str]],
    dict[str, Mapping[str, Any]],
]:
    replacements: dict[tuple[int, int, int], str] = {}
    pending: defaultdict[tuple[int, int], set[str]] = defaultdict(set)
    rows: dict[str, Mapping[str, Any]] = {}
    row_count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row_count += 1
        row = json.loads(line)
        if row.get("resource") != "pk_msggame":
            continue
        coordinate = str(row["coordinate"])
        key = parse_coordinate(coordinate)
        require(coordinate not in rows, f"duplicate ledger coordinate: {coordinate}")
        rows[coordinate] = row
        if "translation" in row:
            replacements[key] = str(row["translation"])
        if row.get("runtime_review") == "pending":
            pending[key[:2]].add(coordinate)
    require(row_count == EXPECTED_LEDGER_ROWS, f"ledger row count drifted: {row_count}")
    require(
        sum(len(values) for values in pending.values())
        == EXPECTED_PK_PENDING_ROWS,
        "official PK pending count drifted",
    )
    return replacements, dict(pending), rows


def current_pending_promotions(
    decision_path: Path,
    pending_by_root: Mapping[tuple[int, int], set[str]],
) -> set[str]:
    result: set[str] = set()
    for line in decision_path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        coordinate = str(row["coordinate"])
        root = parse_coordinate(coordinate)[:2]
        if coordinate in pending_by_root.get(root, set()):
            result.add(coordinate)
    return result


def family_shape(
    candidate_edges: Mapping[
        tuple[int, int], Sequence[Mapping[str, Any]]
    ],
    source_edges: Mapping[
        tuple[int, int], Sequence[Mapping[str, Any]]
    ],
    target: tuple[int, int],
) -> dict[str, Any]:
    candidate_nodes, candidate_dispatch, candidate_leaves = jump_closure(
        candidate_edges, target
    )
    source_nodes, source_dispatch, source_leaves = jump_closure(
        source_edges, target
    )
    identical = (
        candidate_nodes == source_nodes
        and candidate_dispatch == source_dispatch
        and candidate_leaves == source_leaves
    )
    seven_way = (
        identical
        and len(candidate_nodes) == 13
        and len(candidate_dispatch) == 13
        and len(candidate_leaves) == 7
    )
    return {
        "candidate_nodes": candidate_nodes,
        "candidate_dispatch": candidate_dispatch,
        "candidate_leaves": candidate_leaves,
        "source_candidate_identical": identical,
        "seven_way": seven_way,
    }


def build_outputs(
    *,
    steam_root: Path = DEFAULT_STEAM_ROOT,
    ledger_path: Path = DEFAULT_LEDGER,
) -> tuple[dict[str, Any], dict[str, Any]]:
    current_path = steam_root / "MSG_PK" / "JP" / "msggame.bin"
    pristine_path = (
        steam_root
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msggame.bin"
    )
    inputs = {
        "ledger": sha256_file(ledger_path),
        "pk_current": sha256_file(current_path),
        "pk_pristine": sha256_file(pristine_path),
        "selector568_decisions": sha256_file(SELECTOR568_DECISIONS),
        "selector1096_decisions": sha256_file(SELECTOR1096_DECISIONS),
    }
    require(
        inputs["ledger"] == EXPECTED_LEDGER_SHA256,
        "official integrated ledger drifted",
    )
    require(
        inputs["pk_current"] == EXPECTED_PK_CURRENT_SHA256,
        "shadow current PK input drifted",
    )
    require(
        inputs["pk_pristine"] == EXPECTED_PK_PRISTINE_SHA256,
        "pristine PK input drifted",
    )
    require(
        inputs["selector568_decisions"]
        == EXPECTED_SELECTOR568_DECISION_SHA256,
        "selector-568 consolidated decisions drifted",
    )
    require(
        inputs["selector1096_decisions"]
        == EXPECTED_SELECTOR1096_DECISION_SHA256,
        "selector-1096 consolidated decisions drifted",
    )

    replacements, pending_by_root, _rows = load_official_ledger(ledger_path)
    current_blob = current_path.read_bytes()
    candidate_blob = ENGINE.rebuild_packed_with_literals(
        current_blob, replacements
    )
    candidate_sha256 = sha256_bytes(candidate_blob)
    require(
        candidate_sha256 == EXPECTED_PK_CANDIDATE_SHA256,
        f"official PK candidate drifted: {candidate_sha256}",
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate_blob).archive
    )
    source_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(pristine_path.read_bytes()).archive
    )
    require(
        set(candidate_records) == set(source_records),
        "candidate/source PK record universe drifted",
    )

    candidate_edges = graph_edges(candidate_records)
    source_edges = graph_edges(source_records)
    candidate_sites = candidate_call_sites(candidate_edges)
    source_sites = candidate_call_sites(source_edges)

    promotion568 = current_pending_promotions(
        SELECTOR568_DECISIONS, pending_by_root
    )
    promotion1096 = current_pending_promotions(
        SELECTOR1096_DECISIONS, pending_by_root
    )
    require(
        len(promotion568) == EXPECTED_SELECTOR568_PROMOTIONS
        and len(promotion1096) == EXPECTED_SELECTOR1096_PROMOTIONS
        and not promotion568.intersection(promotion1096),
        "568/1096 current-pending promotion unions drifted",
    )

    reachable_roots: defaultdict[
        tuple[int, int], set[tuple[int, int]]
    ] = defaultdict(set)
    for pending_root in sorted(pending_by_root):
        for target in reachable_call_targets(candidate_edges, pending_root):
            reachable_roots[target].add(pending_root)
    require(
        len(reachable_roots) == EXPECTED_REACHABLE_CALL_TARGETS,
        "reachable 0143 target count drifted",
    )

    owned_closure: set[tuple[int, int]] = set()
    owned_summary: list[dict[str, Any]] = []
    for selector in OWNED_SELECTORS:
        target = (0, selector)
        shape = family_shape(candidate_edges, source_edges, target)
        require(shape["seven_way"], f"owned selector {selector} shape drifted")
        owned_closure.update(shape["candidate_nodes"])
        owned_summary.append(
            {
                "selector_coordinate": root_string(target),
                "closure_node_count": len(shape["candidate_nodes"]),
                "closure_node_sha256": root_digest(shape["candidate_nodes"]),
                "dispatch_edge_count": len(shape["candidate_dispatch"]),
                "dispatch_edge_sha256": edge_digest(
                    shape["candidate_dispatch"]
                ),
                "terminal_count": len(shape["candidate_leaves"]),
                "terminal_coordinate_sha256": root_digest(
                    shape["candidate_leaves"]
                ),
            }
        )

    private_targets: list[dict[str, Any]] = []
    public_ranking: list[dict[str, Any]] = []
    classification_counts: defaultdict[str, int] = defaultdict(int)
    eligible_union: set[str] = set()
    for target in sorted(reachable_roots):
        roots = reachable_roots[target]
        potential = {
            coordinate
            for root in roots
            for coordinate in pending_by_root[root]
        }
        shape = family_shape(candidate_edges, source_edges, target)
        if target in owned_closure:
            classification = "already_owned_selector_or_dispatch_closure"
        elif shape["seven_way"]:
            classification = "eligible_fixed_seven_way_selector"
        else:
            classification = "non_seven_way_call_target"
        classification_counts[classification] += 1

        all_candidate_sites = candidate_sites.get(target, [])
        all_source_sites = source_sites.get(target, [])
        pending_direct_sites = [
            site
            for site in all_candidate_sites
            if site_key(site)[:2] in pending_by_root
        ]
        direct_pending_roots = {
            site_key(site)[:2] for site in pending_direct_sites
        }
        overlap568 = potential.intersection(promotion568)
        overlap1096 = potential.intersection(promotion1096)
        overlap = overlap568.union(overlap1096)
        disjoint = potential.difference(overlap)

        private_targets.append(
            {
                "classification": classification,
                "target_coordinate": root_string(target),
                "reachable_pending_roots": [
                    root_string(root) for root in sorted(roots)
                ],
                "reachable_pending_root_count": len(roots),
                "reachable_pending_root_sha256": root_digest(roots),
                "potential_current_pending_coordinates": sorted(
                    potential, key=parse_coordinate
                ),
                "potential_current_pending_row_count": len(potential),
                "potential_current_pending_coordinate_sha256":
                    coordinate_digest(potential),
                "candidate_call_sites": all_candidate_sites,
                "candidate_call_site_count": len(all_candidate_sites),
                "candidate_call_site_sha256": site_digest(
                    all_candidate_sites
                ),
                "source_call_sites": all_source_sites,
                "source_call_site_count": len(all_source_sites),
                "source_call_site_sha256": site_digest(all_source_sites),
                "direct_pending_call_sites": pending_direct_sites,
                "direct_pending_call_site_count": len(
                    pending_direct_sites
                ),
                "direct_pending_root_count": len(direct_pending_roots),
                "direct_pending_root_sha256": root_digest(
                    direct_pending_roots
                ),
                "overlap_selector568_coordinates": sorted(
                    overlap568, key=parse_coordinate
                ),
                "overlap_selector1096_coordinates": sorted(
                    overlap1096, key=parse_coordinate
                ),
                "disjoint_current_pending_coordinates": sorted(
                    disjoint, key=parse_coordinate
                ),
                "jump_closure": {
                    "source_candidate_identical":
                        shape["source_candidate_identical"],
                    "node_coordinates": [
                        root_string(root)
                        for root in sorted(shape["candidate_nodes"])
                    ],
                    "dispatch_edges": [
                        [root_string(source), root_string(destination)]
                        for source, destination
                        in sorted(shape["candidate_dispatch"])
                    ],
                    "terminal_coordinates": [
                        root_string(root)
                        for root in sorted(shape["candidate_leaves"])
                    ],
                },
            }
        )

        if classification != "eligible_fixed_seven_way_selector":
            continue
        eligible_union.update(potential)
        source_only_sites = set(all_source_sites).difference(
            all_candidate_sites
        )
        candidate_only_sites = set(all_candidate_sites).difference(
            all_source_sites
        )
        public_ranking.append(
            {
                "selector_coordinate": root_string(target),
                "potential_current_pending_rows": len(potential),
                "potential_current_pending_coordinate_sha256":
                    coordinate_digest(potential),
                "overlap_selector568_promotion_rows": len(overlap568),
                "overlap_selector568_coordinate_sha256":
                    coordinate_digest(overlap568),
                "overlap_selector1096_promotion_rows": len(overlap1096),
                "overlap_selector1096_coordinate_sha256":
                    coordinate_digest(overlap1096),
                "disjoint_current_pending_rows": len(disjoint),
                "disjoint_current_pending_coordinate_sha256":
                    coordinate_digest(disjoint),
                "reachable_pending_root_count": len(roots),
                "reachable_pending_root_sha256": root_digest(roots),
                "direct_pending_root_count": len(direct_pending_roots),
                "direct_pending_call_site_count": len(
                    pending_direct_sites
                ),
                "candidate_call_site_count": len(all_candidate_sites),
                "source_call_site_count": len(all_source_sites),
                "source_only_call_site_count": len(source_only_sites),
                "source_only_call_site_sha256": site_digest(
                    source_only_sites
                ),
                "candidate_only_call_site_count": len(
                    candidate_only_sites
                ),
                "candidate_only_call_site_sha256": site_digest(
                    candidate_only_sites
                ),
                "dispatch_contract": {
                    "source_candidate_identical": True,
                    "node_count": len(shape["candidate_nodes"]),
                    "node_sha256": root_digest(shape["candidate_nodes"]),
                    "edge_count": len(shape["candidate_dispatch"]),
                    "edge_sha256": edge_digest(
                        shape["candidate_dispatch"]
                    ),
                    "terminal_count": len(shape["candidate_leaves"]),
                    "terminal_coordinate_sha256": root_digest(
                        shape["candidate_leaves"]
                    ),
                },
            }
        )

    public_ranking.sort(
        key=lambda row: (
            -int(row["disjoint_current_pending_rows"]),
            -int(row["potential_current_pending_rows"]),
            parse_root(str(row["selector_coordinate"])),
        )
    )
    require(
        classification_counts[
            "already_owned_selector_or_dispatch_closure"
        ]
        == EXPECTED_OWNED_CALL_TARGETS,
        (
            "owned reachable call-target count drifted: "
            f"{dict(classification_counts)}"
        ),
    )
    require(
        classification_counts["non_seven_way_call_target"]
        == EXPECTED_NON_SEVEN_WAY_TARGETS,
        "non-seven-way call-target count drifted",
    )
    require(
        len(public_ranking) == EXPECTED_ELIGIBLE_FAMILIES,
        "eligible selector-family count drifted",
    )
    require(
        len(eligible_union) == EXPECTED_ELIGIBLE_UNION_ROWS,
        (
            "eligible family pending union drifted: "
            f"{len(eligible_union)}"
        ),
    )

    top = public_ranking[0]
    top_private = next(
        row
        for row in private_targets
        if row["target_coordinate"] == top["selector_coordinate"]
    )
    top_terminals = tuple(top_private["jump_closure"]["terminal_coordinates"])
    require(
        top["selector_coordinate"] == EXPECTED_RECOMMENDED_SELECTOR
        and top_terminals == EXPECTED_RECOMMENDED_TERMINALS
        and top["potential_current_pending_rows"]
        == EXPECTED_RECOMMENDED_POTENTIAL
        and top["overlap_selector568_promotion_rows"]
        == EXPECTED_RECOMMENDED_OVERLAP_568
        and top["overlap_selector1096_promotion_rows"]
        == EXPECTED_RECOMMENDED_OVERLAP_1096
        and top["disjoint_current_pending_rows"]
        == EXPECTED_RECOMMENDED_DISJOINT
        and top["reachable_pending_root_count"]
        == EXPECTED_RECOMMENDED_PENDING_ROOTS
        and top["direct_pending_call_site_count"]
        == EXPECTED_RECOMMENDED_PENDING_SITES
        and top["candidate_call_site_count"]
        == EXPECTED_RECOMMENDED_CANDIDATE_SITES
        and top["source_call_site_count"]
        == EXPECTED_RECOMMENDED_SOURCE_SITES,
        "recommended selector-1174 metrics drifted",
    )

    # The point/range estimate is explicitly heuristic.  Its exact inputs are
    # the two completed comparable families; the 224-row disjoint ceiling is
    # the auditable planning number.
    comparable_potential = {568: 331, 1096: 247}
    comparable_actual = {
        568: len(promotion568),
        1096: len(promotion1096),
    }
    disjoint = int(top["disjoint_current_pending_rows"])
    point_estimate = round(
        disjoint
        * sum(comparable_actual.values())
        / sum(comparable_potential.values())
    )
    estimate_range = (
        round(
            disjoint
            * min(
                comparable_actual[key] / comparable_potential[key]
                for key in comparable_actual
            )
        ),
        round(
            disjoint
            * max(
                comparable_actual[key] / comparable_potential[key]
                for key in comparable_actual
            )
        ),
    )
    require(
        point_estimate == EXPECTED_POINT_ESTIMATE
        and estimate_range == EXPECTED_ESTIMATE_RANGE,
        "comparable-family yield estimate drifted",
    )

    common_inputs = {
        "official_integrated_ledger_sha256": inputs["ledger"],
        "pk_current_sha256": inputs["pk_current"],
        "pk_pristine_sha256": inputs["pk_pristine"],
        "pk_rebuilt_candidate_sha256": candidate_sha256,
        "selector568_consolidated_decision_sha256":
            inputs["selector568_decisions"],
        "selector1096_consolidated_decision_sha256":
            inputs["selector1096_decisions"],
    }
    scope = {
        "resource": "pk_msggame",
        "official_pending_rows": EXPECTED_PK_PENDING_ROWS,
        "official_pending_root_count": len(pending_by_root),
        "official_pending_root_sha256": root_digest(pending_by_root),
        "reachable_0143_call_target_count": len(reachable_roots),
        "eligible_fixed_seven_way_family_count": len(public_ranking),
        "eligible_family_current_pending_union_rows": len(eligible_union),
        "eligible_family_current_pending_union_coordinate_sha256":
            coordinate_digest(eligible_union),
        "selector568_current_pending_promotion_rows": len(promotion568),
        "selector568_current_pending_promotion_coordinate_sha256":
            coordinate_digest(promotion568),
        "selector1096_current_pending_promotion_rows": len(promotion1096),
        "selector1096_current_pending_promotion_coordinate_sha256":
            coordinate_digest(promotion1096),
    }
    recommendation = {
        "selector_coordinate": top["selector_coordinate"],
        "terminal_count": top["dispatch_contract"]["terminal_count"],
        "terminal_coordinate_sha256":
            top["dispatch_contract"]["terminal_coordinate_sha256"],
        "exact_current_pending_upper_bound":
            top["potential_current_pending_rows"],
        "exact_overlap_with_selector568_promotions":
            top["overlap_selector568_promotion_rows"],
        "exact_overlap_with_selector1096_promotions":
            top["overlap_selector1096_promotion_rows"],
        "exact_disjoint_current_pending_upper_bound":
            top["disjoint_current_pending_rows"],
        "estimated_actual_promotion_rows": point_estimate,
        "estimated_actual_promotion_range": list(estimate_range),
        "estimate_basis": {
            "completed_comparable_family_actual_promotions":
                {
                    str(key): value
                    for key, value in comparable_actual.items()
                },
            "completed_comparable_family_pending_upper_bounds":
                {
                    str(key): value
                    for key, value in comparable_potential.items()
                },
            "heuristic_only": True,
        },
        "tractability": {
            "fixed_seven_way_dispatch": True,
            "source_candidate_dispatch_identical": True,
            "dispatch_node_count": top["dispatch_contract"]["node_count"],
            "dispatch_edge_count": top["dispatch_contract"]["edge_count"],
            "direct_pending_call_site_count":
                top["direct_pending_call_site_count"],
            "candidate_call_site_count": top["candidate_call_site_count"],
            "source_only_call_site_count":
                top["source_only_call_site_count"],
        },
    }

    private: dict[str, Any] = {
        "schema": PRIVATE_SCHEMA,
        "method": METHOD,
        "inputs": {
            **common_inputs,
            "official_integrated_ledger_path": str(
                ledger_path.relative_to(REPO)
            ).replace("\\", "/"),
            "pk_current_path": str(current_path.relative_to(REPO)).replace(
                "\\", "/"
            ),
            "pk_pristine_path": str(
                pristine_path.relative_to(REPO)
            ).replace("\\", "/"),
        },
        "scope": scope,
        "owned_selector_closures": owned_summary,
        "classification_counts": dict(sorted(classification_counts.items())),
        "direct_targets": private_targets,
        "eligible_family_ranking": public_ranking,
        "recommendation": {
            **recommendation,
            "terminal_coordinates": list(top_terminals),
        },
        "privacy": {
            "classification": "private_coordinate_graph",
            "contains_dialogue_bodies": False,
            "contains_translations": False,
            "shared_integration_mutated": False,
            "steam_write_performed": False,
        },
    }
    private["guards"] = {
        "direct_targets_canonical_sha256": canonical_sha256(private_targets),
        "eligible_ranking_canonical_sha256": canonical_sha256(public_ranking),
        "payload_without_guards_canonical_sha256": canonical_sha256(private),
    }

    public: dict[str, Any] = {
        "schema": PUBLIC_SCHEMA,
        "method": METHOD,
        "inputs": common_inputs,
        "scope": scope,
        "exclusions": {
            "already_owned_selectors": list(OWNED_SELECTORS),
            "already_owned_reachable_call_targets":
                classification_counts[
                    "already_owned_selector_or_dispatch_closure"
                ],
            "non_seven_way_reachable_call_targets":
                classification_counts["non_seven_way_call_target"],
            "owned_selector_closures": owned_summary,
        },
        "ranking": public_ranking,
        "recommendation": recommendation,
        "guards": {
            "eligible_ranking_canonical_sha256":
                canonical_sha256(public_ranking),
            "private_direct_targets_canonical_sha256":
                canonical_sha256(private_targets),
            "owned_closures_canonical_sha256":
                canonical_sha256(owned_summary),
        },
        "privacy": {
            "source_free": True,
            "contains_dialogue_bodies": False,
            "contains_translations": False,
            "coordinate_lists_kept_private": True,
            "shared_integration_mutated": False,
            "steam_write_performed": False,
        },
    }
    public["guards"]["payload_without_final_guard_canonical_sha256"] = (
        canonical_sha256(public)
    )
    return private, public


def assert_source_free(value: Any, path: str = "$") -> None:
    forbidden_keys = {
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
        r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff"
        r"\uac00-\ud7a3]"
    )
    if isinstance(value, dict):
        for key, child in value.items():
            require(
                str(key) not in forbidden_keys,
                f"source-bearing key in public report at {path}.{key}",
            )
            assert_source_free(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_source_free(child, f"{path}[{index}]")
    elif isinstance(value, str):
        require(
            cjk.search(value) is None,
            f"CJK dialogue leaked into public report at {path}",
        )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument(
        "--private-output", type=Path, default=DEFAULT_PRIVATE_OUTPUT
    )
    parser.add_argument(
        "--public-output", type=Path, default=DEFAULT_PUBLIC_OUTPUT
    )
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    private, public = build_outputs(
        steam_root=args.steam_root,
        ledger_path=args.ledger,
    )
    assert_source_free(public)
    private_content = serialized_json(private)
    public_content = serialized_json(public)
    private_sha256 = sha256_bytes(private_content)
    public_sha256 = sha256_bytes(public_content)
    if EXPECTED_PRIVATE_FILE_SHA256 is not None:
        require(
            private_sha256 == EXPECTED_PRIVATE_FILE_SHA256,
            f"private ranking digest drifted: {private_sha256}",
        )
    if EXPECTED_PUBLIC_FILE_SHA256 is not None:
        require(
            public_sha256 == EXPECTED_PUBLIC_FILE_SHA256,
            f"public ranking digest drifted: {public_sha256}",
        )
    if args.check:
        require(
            args.private_output.is_file()
            and args.private_output.read_bytes() == private_content,
            "private ranking artifact drifted",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_bytes() == public_content,
            "public ranking report drifted",
        )
    else:
        require(
            DEFAULT_PRIVATE_OUTPUT.resolve().parent
            in args.private_output.resolve().parents
            or args.private_output.resolve().parent
            == DEFAULT_PRIVATE_OUTPUT.resolve().parent,
            "private output must remain below the dialogue tmp directory",
        )
        args.private_output.parent.mkdir(parents=True, exist_ok=True)
        args.public_output.parent.mkdir(parents=True, exist_ok=True)
        args.private_output.write_bytes(private_content)
        args.public_output.write_bytes(public_content)
    print(
        json.dumps(
            {
                "eligible_families": len(public["ranking"]),
                "estimated_actual_promotions":
                    public["recommendation"][
                        "estimated_actual_promotion_rows"
                    ],
                "exact_disjoint_upper_bound":
                    public["recommendation"][
                        "exact_disjoint_current_pending_upper_bound"
                    ],
                "private_sha256": private_sha256,
                "public_sha256": public_sha256,
                "recommended_selector":
                    public["recommendation"]["selector_coordinate"],
                "status": "PASS",
                "steam_write_performed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
