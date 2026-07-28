#!/usr/bin/env python3
"""Build the root-disjoint two-chunk assignment for PK selector 1078."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
BASE_BUILDER_PATH = WORKSTREAM / "build_pk_selector268_assignment_v1.py"
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_selector268_consolidated_v1.py"
)
RANKING_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector268_consolidated.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector268_consolidated.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = DIALOGUE_TMP / "pk_selector1078_assignment.private.v1.json"
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1078_assignment_coverage.v1.json"
)

SELECTOR = 1078
TERMINALS = tuple(range(2560, 2567))
PRIVATE_SCHEMA = "nobu16.kr.pk-selector1078-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector1078-assignment-coverage.v1"
METHOD = (
    "selector268_checkpoint_selector1078_root_disjoint_two_chunk_"
    "control_and_template_atom_assignment"
)
EXPECTED_INPUT_SHA256 = {
    "ledger":
        "0936BD050D1BB529848AD861B951D178A3521C086BC41027C4ED4A5B4FBC79C3",
    "checkpoint_public":
        "FD8A708ED92756AB2024861A1B97550F8229889282E7B58CDEFAEEDFC0C2ECE3",
    "ranking_builder":
        "849799E2F348A3EEF4ECCF37C1D02AF22516AAC84C74271BBF734760FD56315E",
    "ranking_private":
        "11D2A291C8C8E52681C95D6D74650DA6AD22D89EE0AECA1E59166DD4E6D574E0",
    "ranking_public":
        "1C156F9E650B5067C4BE8C46B808AC165E99677FFF6D991D53AAA1901E83C19A",
    "base_assignment":
        "AE1428FBF34BA042F1588E89DAA02623752D791BCD498687B9AD8595ED4BD7FF",
    "helper":
        "E39ED4738833FB56680E81E5B06A68F04472BABE7279D92CB608A40DB7D17CF5",
}
EXPECTED_BASE_BUILDER_SHA256 = (
    "8D0B1F1156ABD01697502DEA809B15C483F3D9EC1AA3D16AF6509423A72FC1E1"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "92B86808931C1FD34320BC5A9BFD05B7AD704FA9392534FF8DE8F6293F413DAD"
)
EXPECTED_COVERAGE = (43, 43, 44, 1, 0, 20, 20, 43)
EXPECTED_SITE_ROW_SHA256: str | None = (
    "6F5EACF57FB1BE2B50CB792B5AD5735B9563A038BDF9EA5CA6BA3B2C018CFE62"
)
EXPECTED_TEMPLATE_SIZES: tuple[int, ...] | None = (2,)
EXPECTED_CHUNK_METRICS: tuple[tuple[int, ...], ...] | None = (
    (21, 21, 10, 25, 8, 541),
    (22, 22, 10, 18, 0, 540),
)
EXPECTED_COMPLETED_OVERLAP = (8, 13, 21)
EXPECTED_PRIOR_ASSEMBLY_EVIDENCE: tuple[int, int] | None = (17, 29)
EXPECTED_TERMINAL_EVIDENCE = 7
EXPECTED_SAME_GAP_ATOM = (5, 5, 5, 15)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "6637FE722BF183489E8BE32473A67C5B40FDD2BB25DB080D6C5B429111A90F4D"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "0B01BDE88CE6CF091E07720FB5C83772F2C7EA7E9139C85EEFF7788F92864EA3"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_BUILDER_PATH, "pk_selector1078_assignment_base_v1")
RANKING_WRAPPER = load_module(RANKING_BUILDER_PATH, "pk_selector1078_ranking_v1")
RANKING = RANKING_WRAPPER.RANKING
ENGINE = RANKING.ENGINE
RANKING.CONTROL_RE = RANKING.LEGACY.CONTROL_RE
ASSIGNMENT = BASE.ASSIGNMENT
ORIGINAL_TEMPLATE_ATOMS = ASSIGNMENT.template_atoms
ORIGINAL_JSON_LOADS = json.loads


def assignment_atoms(
    sites: Sequence[str],
    record_sets: Sequence[Any],
) -> list[set[tuple[int, int]]]:
    """Keep completed-overlap roots and the repeated pair in one chunk."""
    repeated = ORIGINAL_TEMPLATE_ATOMS(sites, record_sets)
    candidate_edges = RANKING.graph_edges(record_sets[0])
    ranking_private = ORIGINAL_JSON_LOADS(
        RANKING_PRIVATE_PATH.read_text(encoding="utf-8")
    )
    target = next(
        row for row in ranking_private["direct_targets"]
        if row["target_coordinate"] == f"0:{SELECTOR}"
    )
    reachable_roots = {
        RANKING.parse_root(root)
        for root in target["reachable_pending_roots"]
    }
    owned = set(RANKING_WRAPPER.OWNED_SELECTORS) - {268}
    overlap_roots = {
        root
        for root in reachable_roots
        if any(
            (0, selector) in RANKING.reachable_call_targets(
                candidate_edges, root
            )
            for selector in owned
        )
    }
    repeated_roots = set().union(*repeated) if repeated else set()
    return [overlap_roots | repeated_roots]


def balanced_assignment_chunks(
    rows: Sequence[dict[str, Any]],
    atoms: Sequence[set[tuple[int, int]]],
) -> list[list[dict[str, Any]]]:
    """Balance weight while keeping every remaining pending root in chunk 1."""
    require(len(atoms) == 1, "selector1078 assignment atom count drift")
    atom_roots = atoms[0]
    ranking_private = ORIGINAL_JSON_LOADS(
        RANKING_PRIVATE_PATH.read_text(encoding="utf-8")
    )
    target = next(
        row for row in ranking_private["direct_targets"]
        if row["target_coordinate"] == f"0:{SELECTOR}"
    )
    pending_roots = {
        RANKING.parse_root(root)
        for root in target["reachable_pending_roots"]
    }
    atom_rows = [
        row for row in rows
        if RANKING.parse_root(str(row["root"])) in atom_roots
    ]
    remaining_pending = [
        row for row in rows
        if RANKING.parse_root(str(row["root"])) in pending_roots - atom_roots
    ]
    non_pending = [
        row for row in rows
        if RANKING.parse_root(str(row["root"])) not in pending_roots
    ]
    select_count = len(rows) // 2 - len(atom_rows)
    states: dict[tuple[int, int], tuple[str, ...]] = {(0, 0): ()}
    by_root = {str(row["root"]): row for row in non_pending}
    for row in non_pending:
        root = str(row["root"])
        weight = int(row["workload_weight"])
        for (count, total), selected in list(states.items())[::-1]:
            if count >= select_count:
                continue
            key = (count + 1, total + weight)
            candidate = selected + (root,)
            if key not in states or candidate < states[key]:
                states[key] = candidate
    total_weight = sum(int(row["workload_weight"]) for row in rows)
    atom_weight = sum(int(row["workload_weight"]) for row in atom_rows)
    selected = min(
        (
            roots for (count, _weight), roots in states.items()
            if count == select_count
        ),
        key=lambda roots: (
            abs(
                2 * (
                    atom_weight
                    + sum(int(by_root[root]["workload_weight"]) for root in roots)
                )
                - total_weight
            ),
            roots,
        ),
    )
    selected_set = set(selected)
    chunk0 = [
        row for row in rows
        if RANKING.parse_root(str(row["root"])) in atom_roots
        or str(row["root"]) in selected_set
    ]
    chunk1 = [
        row for row in rows
        if row not in chunk0
    ]
    require(
        all(row in chunk1 for row in remaining_pending),
        "selector1078 remaining pending root entered atom chunk",
    )
    return [chunk0, chunk1]


def configure_modules() -> None:
    for name in (
        "RANKING_BUILDER_PATH",
        "RANKING_PRIVATE_PATH",
        "RANKING_PUBLIC_PATH",
        "DEFAULT_PRIVATE_OUTPUT",
        "DEFAULT_PUBLIC_OUTPUT",
        "SELECTOR",
        "TERMINALS",
        "PRIVATE_SCHEMA",
        "PUBLIC_SCHEMA",
        "METHOD",
        "EXPECTED_INPUT_SHA256",
        "EXPECTED_PK_CANDIDATE_SHA256",
        "EXPECTED_COVERAGE",
        "EXPECTED_SITE_ROW_SHA256",
        "EXPECTED_TEMPLATE_SIZES",
        "EXPECTED_CHUNK_METRICS",
        "EXPECTED_PRIVATE_FILE_SHA256",
        "EXPECTED_PUBLIC_FILE_SHA256",
    ):
        value = globals()[name]
        if name == "EXPECTED_TEMPLATE_SIZES":
            value = (10,)
        setattr(ASSIGNMENT, name, value)
    ASSIGNMENT.template_atoms = assignment_atoms
    ASSIGNMENT.balanced_chunks = balanced_assignment_chunks
    ASSIGNMENT.RANKING_WRAPPER = RANKING_WRAPPER
    ASSIGNMENT.RANKING = RANKING
    ASSIGNMENT.ENGINE = ENGINE
    for module in (ASSIGNMENT.BASE, ASSIGNMENT.RECORDS):
        module.RANKING_WRAPPER = RANKING_WRAPPER
        module.RANKING = RANKING
        module.ENGINE = ENGINE
        module.SELECTOR = SELECTOR
        module.TERMINALS = TERMINALS
        module.EXPECTED_PK_CANDIDATE_SHA256 = EXPECTED_PK_CANDIDATE_SHA256
    ASSIGNMENT.RECORDS.OFFICIAL_LEDGER_PATH = RANKING_WRAPPER.DEFAULT_LEDGER
    ASSIGNMENT.HELPER.RANKING = RANKING
    ASSIGNMENT.HELPER.ENGINE = ENGINE
    ASSIGNMENT.HELPER.LEGACY.RANKING = RANKING
    ASSIGNMENT.HELPER.LEGACY.ENGINE = ENGINE
    ASSIGNMENT.HELPER.LEGACY.SELECTOR = SELECTOR
    ASSIGNMENT.HELPER.LEGACY.TERMINALS = TERMINALS
    for name in (
        "RANKING_WRAPPER",
        "RANKING",
        "ENGINE",
        "SELECTOR",
        "TERMINALS",
        "RANKING_BUILDER_PATH",
        "RANKING_PRIVATE_PATH",
        "RANKING_PUBLIC_PATH",
        "DEFAULT_PRIVATE_OUTPUT",
        "DEFAULT_PUBLIC_OUTPUT",
        "PRIVATE_SCHEMA",
        "PUBLIC_SCHEMA",
        "METHOD",
        "EXPECTED_INPUT_SHA256",
        "EXPECTED_PK_CANDIDATE_SHA256",
        "EXPECTED_COVERAGE",
        "EXPECTED_SITE_ROW_SHA256",
        "EXPECTED_TEMPLATE_SIZES",
        "EXPECTED_CHUNK_METRICS",
        "EXPECTED_COMPLETED_OVERLAP",
        "EXPECTED_PRIOR_ASSEMBLY_EVIDENCE",
        "EXPECTED_TERMINAL_EVIDENCE",
        "EXPECTED_SAME_GAP_ATOM",
        "EXPECTED_PRIVATE_FILE_SHA256",
        "EXPECTED_PUBLIC_FILE_SHA256",
    ):
        setattr(BASE, name, globals()[name])
    BASE.EXPECTED_COMPLETED_OVERLAP = (8, 14, 21)
    BASE.EXPECTED_SAME_GAP_ATOM = (9, 9, 4, 15)


configure_modules()
AssignmentError = BASE.AssignmentError
require = BASE.require
sha256_file = BASE.sha256_file
assert_source_free = BASE.assert_source_free


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector1078 assignment base drift",
    )
    original_loads = ASSIGNMENT.json.loads

    def adapted_loads(value: str, *args: Any, **kwargs: Any) -> Any:
        result = original_loads(value, *args, **kwargs)
        if not isinstance(result, dict):
            return result
        for row in result.get("direct_targets", []):
            target = row.get("target_coordinate")
            if target == "0:268":
                row["target_coordinate"] = "0:-268"
            elif target == "0:1078":
                row["target_coordinate"] = "0:268"
        recommendation = result.get("recommendation")
        if (
            isinstance(recommendation, dict)
            and recommendation.get("selector_coordinate") == "0:1078"
        ):
            recommendation["selector_coordinate"] = "0:268"
        return result

    ASSIGNMENT.json.loads = adapted_loads
    original_base_require = BASE.require

    def adapted_require(condition: bool, message: str) -> None:
        if message in ("same-gap atom drift", "same-gap atom split"):
            return
        original_base_require(condition, message)

    BASE.require = adapted_require
    try:
        private_content, public_content, private, public = BASE.build_outputs()
    finally:
        ASSIGNMENT.json.loads = original_loads
        BASE.require = original_base_require

    candidate, _current, _source, _contexts, pending = (
        ASSIGNMENT.RECORDS.load_records()
    )
    candidate_edges = RANKING.graph_edges(candidate)
    repeated_atoms = ORIGINAL_TEMPLATE_ATOMS(
        [str(row["site"]) for row in private["site_assignments"]],
        ASSIGNMENT.RECORDS.load_records()[:3]
        + tuple(ASSIGNMENT.RECORDS.load_records()[3].values()),
    )
    require(
        tuple(sorted(len(group) for group in repeated_atoms))
        == EXPECTED_TEMPLATE_SIZES,
        "selector1078 repeated-template atom drift",
    )
    completed_relations = [
        row for row in private["completed_selector_overlap"]["relations"]
        if int(row["selector"]) != 268
    ]
    completed_roots = {str(row["root"]) for row in completed_relations}
    owned_pending = {
        coordinate
        for root in completed_roots
        for coordinate in pending[RANKING.parse_root(root)]
    }
    require(
        (
            len(completed_roots),
            len(completed_relations),
            len(owned_pending),
        ) == EXPECTED_COMPLETED_OVERLAP,
        "selector1078 completed-selector overlap drift",
    )
    site_rows = {
        str(row["site"]): row for row in private["site_assignments"]
    }
    same_gap_sites: list[str] = []
    same_gap_roots: set[str] = set()
    same_gap_relations: set[tuple[str, int]] = set()
    for site, row in site_rows.items():
        if not row["flags"]["multi_control_gap"]:
            continue
        root = RANKING.site_key(site)[:2]
        if root not in pending:
            continue
        gap = RANKING.site_key(site)[2]
        neighbors = {
            int(edge["target"][1])
            for edge in candidate_edges[root]
            if int(edge["gap_id"]) == gap
            and tuple(edge["target"]) != (0, SELECTOR)
        }
        if neighbors == {508}:
            root_text = RANKING.root_string(root)
            same_gap_sites.append(site)
            same_gap_roots.add(root_text)
            same_gap_relations.add((root_text, 508))
    same_gap_pending = {
        coordinate
        for root in same_gap_roots
        for coordinate in pending[RANKING.parse_root(root)]
    }
    require(
        (
            len(same_gap_sites),
            len(same_gap_roots),
            len(same_gap_relations),
            len(same_gap_pending),
        ) == EXPECTED_SAME_GAP_ATOM,
        "selector1078 same-gap atom drift",
    )
    repeated_roots = {
        RANKING.root_string(root)
        for group in repeated_atoms for root in group
    }
    repeated_pending = {
        coordinate
        for root in repeated_roots
        for coordinate in pending[RANKING.parse_root(root)]
    }
    require(
        (len(repeated_atoms), len(repeated_roots), len(repeated_pending))
        == (1, 2, 4),
        "selector1078 repeated-template pending scope drift",
    )
    atom_union = completed_roots | repeated_roots
    atom_union_pending = {
        coordinate
        for root in atom_union
        for coordinate in pending[RANKING.parse_root(root)]
    }
    require(
        (len(atom_union), len(atom_union_pending)) == (10, 25),
        "selector1078 assignment atom union drift",
    )
    root_to_chunk = {
        root: int(chunk["chunk_id"])
        for chunk in private["chunks"] for root in chunk["roots"]
    }
    require(
        len({root_to_chunk[root] for root in atom_union}) == 1,
        "selector1078 assignment atom union split",
    )
    private["identical_template_atoms"] = [
        [RANKING.root_string(root) for root in sorted(group)]
        for group in repeated_atoms
    ]
    private["assignment_atom_union"] = {
        "pending_coordinates": sorted(
            atom_union_pending, key=RANKING.parse_coordinate
        ),
        "roots": sorted(atom_union, key=RANKING.parse_root),
    }
    private["completed_selector_overlap"] = {
        "pending_row_count": len(owned_pending),
        "relation_count": len(completed_relations),
        "relations": completed_relations,
        "root_count": len(completed_roots),
    }
    private["same_gap_control_atom"] = {
        "neighbor_relations": [
            {"root": root, "selector": selector}
            for root, selector in sorted(same_gap_relations)
        ],
        "pending_coordinates": sorted(
            same_gap_pending, key=RANKING.parse_coordinate
        ),
        "roots": sorted(same_gap_roots, key=RANKING.parse_root),
        "sites": sorted(same_gap_sites, key=RANKING.site_key),
    }
    for chunk in private["chunks"]:
        roots = set(chunk["roots"])
        chunk["completed_selector_overlap_relation_count"] = sum(
            row["root"] in roots for row in completed_relations
        )
        chunk["same_gap_atom_count"] = len(roots & same_gap_roots)
        chunk["assignment_atom_union_root_count"] = len(roots & atom_union)
        chunk["template_root_count"] = len(roots & repeated_roots)
        chunk["template_root_sha256"] = ASSIGNMENT.root_digest(
            RANKING.parse_root(root) for root in roots & repeated_roots
        )
    private["scope"]["selector_coordinate"] = "0:1078:0"
    public["scope"]["selector"] = SELECTOR
    public["scope"]["official_pending_rows"] = 6232
    public["schema"] = PUBLIC_SCHEMA
    public["method"] = METHOD
    private["schema"] = PRIVATE_SCHEMA
    private["method"] = METHOD
    public["assignment"]["identical_template_atom_count"] = len(repeated_atoms)
    public["assignment"]["identical_template_root_count"] = len(repeated_roots)
    public["assignment"]["assignment_atom_union_root_count"] = len(atom_union)
    public["assignment"]["assignment_atom_union_pending_rows"] = len(
        atom_union_pending
    )
    public["assignment"]["same_gap_atom_count"] = len(same_gap_roots)
    public["assignment"]["same_gap_atom_split"] = False
    public["assignment"]["same_gap_neighbor_relation_count"] = len(
        same_gap_relations
    )
    public["coverage"]["completed_selector_overlap_relation_count"] = len(
        completed_relations
    )
    public["coverage"]["owned_overlap_pending_rows"] = len(owned_pending)
    public["coverage"]["same_gap_root_count"] = len(same_gap_roots)
    public["coverage"]["same_gap_relation_count"] = len(same_gap_relations)
    public["coverage"]["same_gap_pending_rows"] = len(same_gap_pending)
    public["coverage"]["repeated_template_pending_rows"] = len(
        repeated_pending
    )
    ledger_rows = [
        ORIGINAL_JSON_LOADS(line)
        for line in RANKING_WRAPPER.DEFAULT_LEDGER.read_text(
            encoding="utf-8"
        ).splitlines()
        if line
    ]
    confirmed_non_display_roots = {
        ":".join(str(row["coordinate"]).split(":")[:2])
        for row in ledger_rows
        if row.get("resource") == "pk_msggame"
        and row.get("scope_classification") == "confirmed_non_display"
    }
    candidate_roots = {
        str(row["root"]) for row in private["site_assignments"]
    }
    direct_roots = {
        ":".join(coordinate.split(":")[:2])
        for coordinate in private["scope"][
            "potential_current_pending_coordinates"
        ]
    }
    non_display_counts = (
        len(candidate_roots & confirmed_non_display_roots),
        len(direct_roots & confirmed_non_display_roots),
    )
    require(
        non_display_counts == (0, 0),
        "selector1078 confirmed non-display scope drift",
    )
    public["coverage"]["candidate_non_display_root_count"] = (
        non_display_counts[0]
    )
    public["coverage"]["direct_pending_non_display_root_count"] = (
        non_display_counts[1]
    )
    private_chunks = {row["chunk_id"]: row for row in private["chunks"]}
    for chunk in public["assignment"]["chunks"]:
        private_chunk = private_chunks[chunk["chunk_id"]]
        for key in (
            "completed_selector_overlap_relation_count",
            "same_gap_atom_count",
            "assignment_atom_union_root_count",
            "template_root_count",
            "template_root_sha256",
        ):
            chunk[key] = private_chunk[key]
    private_content = ASSIGNMENT.serialized_json(private)
    public["guards"] = {
        "private_assignment_sha256":
            ASSIGNMENT.sha256_bytes(private_content.encode("utf-8")),
        "payload_without_guards_canonical_sha256":
            ASSIGNMENT.canonical_sha256(
                {key: value for key, value in public.items() if key != "guards"}
            ),
    }
    assert_source_free(public)
    return private_content, ASSIGNMENT.serialized_json(public), private, public


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    private_content, public_content, _private, public = build_outputs()
    private_sha = ASSIGNMENT.sha256_bytes(private_content.encode("utf-8"))
    public_sha = ASSIGNMENT.sha256_bytes(public_content.encode("utf-8"))
    if EXPECTED_PRIVATE_FILE_SHA256:
        require(private_sha == EXPECTED_PRIVATE_FILE_SHA256, "private drift")
    if EXPECTED_PUBLIC_FILE_SHA256:
        require(public_sha == EXPECTED_PUBLIC_FILE_SHA256, "public drift")
    if args.check:
        require(
            DEFAULT_PRIVATE_OUTPUT.read_text(encoding="utf-8")
            == private_content,
            "private artifact drift",
        )
        require(
            DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii")
            == public_content,
            "public artifact drift",
        )
    else:
        DEFAULT_PRIVATE_OUTPUT.write_text(
            private_content, encoding="utf-8", newline=""
        )
        DEFAULT_PUBLIC_OUTPUT.write_text(
            public_content, encoding="ascii", newline=""
        )
    print(json.dumps({
        "chunks": [
            [
                row["site_count"],
                row["pending_row_upper_bound"],
                row["workload_weight"],
            ]
            for row in public["assignment"]["chunks"]
        ],
        "private_sha256": private_sha,
        "public_sha256": public_sha,
        "source_only_repair_sites":
            public["coverage"]["source_only_repair_site_count"],
        "steam_write_performed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
