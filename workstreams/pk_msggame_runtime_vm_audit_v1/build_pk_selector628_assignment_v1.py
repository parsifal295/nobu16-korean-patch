#!/usr/bin/env python3
"""Build the root-disjoint two-chunk assignment for PK selector 628."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_selector514_consolidated_v1.py"
)
BASE_ASSIGNMENT_PATH = WORKSTREAM / "build_pk_selector142_assignment_v1.py"
HELPER_PATH = WORKSTREAM / "build_pk_selector748_assignment_v1.py"
RANKING_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector514_consolidated.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector514_consolidated.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector628_assignment.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector628_assignment_coverage.v1.json"
)

SELECTOR = 628
TERMINALS = tuple(range(2021, 2028))
CHUNK_COUNT = 2
PRIVATE_SCHEMA = "nobu16.kr.pk-selector628-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector628-assignment-coverage.v1"
METHOD = (
    "selector514_checkpoint_selector628_root_disjoint_two_chunk_"
    "template_atom_assignment"
)

EXPECTED_INPUT_SHA256 = {
    "ledger": "FCAB3A5CACEEAE4C610BD284D8C0631E65DA14562DB7B78A66655554EED07A79",
    "checkpoint_public": "49BB13AF414DA7A751F7B9CA9830386A3832FF99411B4FC39DC96F94FE649100",
    "ranking_builder": "3DD646E132E4CB37E573072595FDA7EF0A58CA3CC5CC2C1B6ADC0583DE2BEC9A",
    "ranking_private": "C66F51470642FE61BFE56953ACD972846D2A0D78C7CB3656137EA4FEF02DA3B3",
    "ranking_public": "5BD03ED691569744AE3D3192EEF313372A8BC047ECC88E4310115FEB18BD26D5",
    "base_assignment": "AE1428FBF34BA042F1588E89DAA02623752D791BCD498687B9AD8595ED4BD7FF",
    "helper": "E39ED4738833FB56680E81E5B06A68F04472BABE7279D92CB608A40DB7D17CF5",
}
EXPECTED_PK_CANDIDATE_SHA256 = (
    "623C6EE2BDC25B13680C353C97847C3AC646C4B2B222A51F0F242B7A1CC2E093"
)
EXPECTED_COVERAGE = (145, 145, 166, 21, 0, 34, 34, 90)
EXPECTED_SITE_ROW_SHA256: str | None = (
    "C8DB1AD9966019FED6AE9B09AF14414F2708F1DF0D8DE9747A1967EBF10F79DE"
)
EXPECTED_TEMPLATE_SIZES: tuple[int, ...] | None = (2, 6, 8, 8, 24)
EXPECTED_CHUNK_METRICS: tuple[tuple[int, ...], ...] | None = (
    (73, 73, 19, 50, 1, 1523),
    (72, 72, 15, 40, 3, 1531),
)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "14578A2713C45C4E3088E7B9547ED48CFA4BC0B2CCF8795EE522EF614691F87B"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "82CE0CA3BBC6579125AF1D0C20BFBF6A508B1F51594B53EC23103842CCF3B476"
)


class AssignmentError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssignmentError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RANKING_WRAPPER = load_module(RANKING_BUILDER_PATH, "pk_selector628_ranking_v1")
RANKING = RANKING_WRAPPER.RANKING
RANKING.CONTROL_RE = RANKING.LEGACY.CONTROL_RE
BASE = load_module(BASE_ASSIGNMENT_PATH, "pk_selector628_base_assignment_v1")
HELPER = BASE.HELPER
RECORDS = BASE.BASE
ENGINE = RANKING.ENGINE

BASE.RANKING_WRAPPER = RANKING_WRAPPER
BASE.RANKING = RANKING
BASE.ENGINE = ENGINE
BASE.SELECTOR = SELECTOR
BASE.TERMINALS = TERMINALS
BASE.EXPECTED_PK_CANDIDATE_SHA256 = EXPECTED_PK_CANDIDATE_SHA256
RECORDS.RANKING_WRAPPER = RANKING_WRAPPER
RECORDS.RANKING = RANKING
RECORDS.ENGINE = ENGINE
RECORDS.SELECTOR = SELECTOR
RECORDS.TERMINALS = TERMINALS
RECORDS.EXPECTED_PK_CANDIDATE_SHA256 = EXPECTED_PK_CANDIDATE_SHA256
HELPER.RANKING = RANKING
HELPER.ENGINE = ENGINE
HELPER.CHUNK_COUNT = CHUNK_COUNT
HELPER.LEGACY.RANKING = RANKING
HELPER.LEGACY.ENGINE = ENGINE
HELPER.LEGACY.SELECTOR = SELECTOR
HELPER.LEGACY.TERMINALS = TERMINALS

sha256_bytes = BASE.sha256_bytes
sha256_file = BASE.sha256_file
canonical_sha256 = BASE.canonical_sha256
serialized_json = BASE.serialized_json
coordinate_digest = BASE.coordinate_digest
root_digest = BASE.root_digest
site_digest = BASE.site_digest
template_atoms = BASE.template_atoms
balanced_chunks = BASE.balanced_chunks
assert_source_free = BASE.assert_source_free


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    immutable = {
        RANKING_WRAPPER.DEFAULT_LEDGER: EXPECTED_INPUT_SHA256["ledger"],
        RANKING_WRAPPER.CHECKPOINT_PUBLIC:
            EXPECTED_INPUT_SHA256["checkpoint_public"],
        RANKING_BUILDER_PATH: EXPECTED_INPUT_SHA256["ranking_builder"],
        RANKING_PRIVATE_PATH: EXPECTED_INPUT_SHA256["ranking_private"],
        RANKING_PUBLIC_PATH: EXPECTED_INPUT_SHA256["ranking_public"],
        BASE_ASSIGNMENT_PATH: EXPECTED_INPUT_SHA256["base_assignment"],
        HELPER_PATH: EXPECTED_INPUT_SHA256["helper"],
    }
    for path, expected in immutable.items():
        require(
            path.is_file() and sha256_file(path) == expected,
            f"input drift: {path}",
        )
    ranking_private = json.loads(RANKING_PRIVATE_PATH.read_text(encoding="utf-8"))
    ranking_public = json.loads(RANKING_PUBLIC_PATH.read_text(encoding="ascii"))
    require(
        ranking_public["recommendation"]["selector_coordinate"] == "0:628",
        "ranking handoff drift",
    )
    target = next(
        row for row in ranking_private["direct_targets"]
        if row["target_coordinate"] == "0:628"
    )
    candidate, current, source, contexts, pending = RECORDS.load_records()
    candidate_edges = RANKING.graph_edges(candidate)
    source_edges = RANKING.graph_edges(source)
    candidate_sites = RANKING.candidate_call_sites(candidate_edges)[(0, SELECTOR)]
    source_sites = RANKING.candidate_call_sites(source_edges)[(0, SELECTOR)]
    candidate_roots = {RANKING.site_key(site)[:2] for site in candidate_sites}
    source_only = set(source_sites) - set(candidate_sites)
    candidate_only = set(candidate_sites) - set(source_sites)
    direct_pending_sites = [
        site for site in candidate_sites
        if RANKING.site_key(site)[:2] in pending
    ]
    reachable_roots = {
        RANKING.parse_root(root) for root in target["reachable_pending_roots"]
    }
    potential = {
        coordinate for root in reachable_roots for coordinate in pending[root]
    }
    observed_coverage = (
        len(candidate_sites),
        len(candidate_roots),
        len(source_sites),
        len(source_only),
        len(candidate_only),
        len(direct_pending_sites),
        len(reachable_roots),
        len(potential),
    )
    require(
        observed_coverage == EXPECTED_COVERAGE,
        f"selector628 coverage drift: {observed_coverage}",
    )

    owned_by_selector = {
        selector: set() for selector in RANKING_WRAPPER.OWNED_SELECTORS
    }
    for root in reachable_roots:
        calls = RANKING.reachable_call_targets(candidate_edges, root)
        for selector in owned_by_selector:
            if (0, selector) in calls:
                owned_by_selector[selector].add(root)
    owned_roots = set().union(*owned_by_selector.values())
    owned_coordinates = {
        coordinate for root in owned_roots for coordinate in pending[root]
    }
    site_rows = HELPER.LEGACY.build_site_rows(
        sites=candidate_sites,
        candidate=candidate,
        current=current,
        source=source,
        contexts=contexts,
    )
    site_row_sha = canonical_sha256(site_rows)
    if EXPECTED_SITE_ROW_SHA256 is not None:
        require(site_row_sha == EXPECTED_SITE_ROW_SHA256, "site matrix drift")
    templates = template_atoms(
        candidate_sites,
        [
            candidate,
            current,
            source,
            contexts["en"],
            contexts["sc"],
            contexts["tc"],
        ],
    )
    template_sizes = tuple(sorted(len(group) for group in templates))
    if EXPECTED_TEMPLATE_SIZES is not None:
        require(template_sizes == EXPECTED_TEMPLATE_SIZES, "template atom drift")
    template_union = set().union(*templates) if templates else set()

    chunks: list[dict[str, Any]] = []
    for chunk_id, members in enumerate(balanced_chunks(site_rows, templates)):
        roots = {RANKING.parse_root(str(row["root"])) for row in members}
        chunk_pending = {
            coordinate
            for root in roots
            for coordinate in pending.get(root, set())
        }
        flags: Counter[str] = Counter()
        for row in members:
            flags.update(key for key, value in row["flags"].items() if value)
        chunks.append({
            "chunk_id": chunk_id,
            "flag_counts": dict(sorted(flags.items())),
            "pending_coordinates": sorted(
                chunk_pending, key=RANKING.parse_coordinate
            ),
            "pending_row_upper_bound": len(chunk_pending),
            "pending_sha256": coordinate_digest(chunk_pending),
            "owned_overlap_root_count": len(roots & owned_roots),
            "owned_overlap_root_sha256": root_digest(roots & owned_roots),
            "pending_root_count": len(roots & reachable_roots),
            "pending_root_sha256": root_digest(roots & reachable_roots),
            "root_count": len(roots),
            "root_sha256": root_digest(roots),
            "roots": [RANKING.root_string(root) for root in sorted(roots)],
            "site_count": len(members),
            "site_sha256": site_digest(str(row["site"]) for row in members),
            "sites": [str(row["site"]) for row in members],
            "template_root_count": len(roots & template_union),
            "template_root_sha256": root_digest(roots & template_union),
            "workload_weight": sum(
                int(row["workload_weight"]) for row in members
            ),
        })
    observed_chunks = tuple(
        (
            row["site_count"],
            row["root_count"],
            row["pending_root_count"],
            row["pending_row_upper_bound"],
            row["owned_overlap_root_count"],
            row["workload_weight"],
        )
        for row in chunks
    )
    if EXPECTED_CHUNK_METRICS is not None:
        require(
            observed_chunks == EXPECTED_CHUNK_METRICS,
            f"chunk drift: {observed_chunks}",
        )
    require(len(chunks) == CHUNK_COUNT, "chunk count drift")
    require(
        not any(
            set(chunks[left]["roots"]) & set(chunks[right]["roots"])
            for left in range(CHUNK_COUNT)
            for right in range(left + 1, CHUNK_COUNT)
        ),
        "root split",
    )
    root_to_chunk = {
        RANKING.parse_root(root): row["chunk_id"]
        for row in chunks for root in row["roots"]
    }
    require(
        all(
            len({root_to_chunk[root] for root in group}) == 1
            for group in templates
        ),
        "template split",
    )
    require(
        set(source_only).isdisjoint(candidate_sites),
        "source-only sites entered candidate assignment",
    )

    inputs = {
        "official_integrated_ledger_sha256": EXPECTED_INPUT_SHA256["ledger"],
        "official_public_checkpoint_sha256":
            EXPECTED_INPUT_SHA256["checkpoint_public"],
        "ranking_builder_sha256": EXPECTED_INPUT_SHA256["ranking_builder"],
        "ranking_private_sha256": EXPECTED_INPUT_SHA256["ranking_private"],
        "ranking_public_sha256": EXPECTED_INPUT_SHA256["ranking_public"],
        "pk_rebuilt_candidate_sha256": EXPECTED_PK_CANDIDATE_SHA256,
    }
    private = {
        "schema": PRIVATE_SCHEMA,
        "method": METHOD,
        "inputs": inputs,
        "scope": {
            "selector_coordinate": "0:628:0",
            "terminal_coordinates": [
                f"0:{value}:0" for value in TERMINALS
            ],
            "candidate_call_sites": candidate_sites,
            "source_only_repair_sites": sorted(
                source_only, key=RANKING.site_key
            ),
            "potential_current_pending_coordinates": sorted(
                potential, key=RANKING.parse_coordinate
            ),
        },
        "identical_template_atoms": [
            [RANKING.root_string(root) for root in sorted(group)]
            for group in templates
        ],
        "site_assignments": site_rows,
        "chunks": chunks,
        "steam_write_performed": False,
    }
    private_content = serialized_json(private)
    public_chunks = [
        {
            key: row[key]
            for key in (
                "chunk_id",
                "pending_row_upper_bound",
                "pending_sha256",
                "owned_overlap_root_count",
                "owned_overlap_root_sha256",
                "pending_root_count",
                "pending_root_sha256",
                "root_count",
                "root_sha256",
                "site_count",
                "site_sha256",
                "template_root_count",
                "template_root_sha256",
                "workload_weight",
            )
        }
        for row in chunks
    ]
    public = {
        "schema": PUBLIC_SCHEMA,
        "method": METHOD,
        "inputs": inputs,
        "scope": {
            "resource": "MSG_PK/JP/msggame.bin",
            "selector": SELECTOR,
            "terminal_count": 7,
            "official_pending_rows": 6547,
        },
        "coverage": {
            "candidate_call_site_count": len(candidate_sites),
            "candidate_call_root_count": len(candidate_roots),
            "source_call_site_count": len(source_sites),
            "source_only_repair_site_count": len(source_only),
            "direct_pending_call_site_count": len(direct_pending_sites),
            "potential_current_pending_rows": len(potential),
            "owned_overlap_root_count": len(owned_roots),
            "owned_overlap_pending_rows": len(owned_coordinates),
        },
        "assignment": {
            "chunk_count": CHUNK_COUNT,
            "root_split_permitted": False,
            "identical_template_atom_count": len(templates),
            "identical_template_root_count": len(template_union),
            "identical_template_atoms_split": False,
            "source_only_calls_separate_from_candidate_chunks": True,
            "site_risk_matrix_sha256": site_row_sha,
            "chunks": public_chunks,
        },
        "privacy": {
            "contains_commercial_source_text": False,
            "contains_exact_coordinates": False,
            "contains_translations": False,
            "private_assignment_stays_below_tmp": True,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    public["guards"] = {
        "private_assignment_sha256":
            sha256_bytes(private_content.encode("utf-8")),
        "payload_without_guards_canonical_sha256": canonical_sha256(public),
    }
    assert_source_free(public)
    return private_content, serialized_json(public), private, public


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    private_content, public_content, _private, public = build_outputs()
    private_sha = sha256_bytes(private_content.encode("utf-8"))
    public_sha = sha256_bytes(public_content.encode("utf-8"))
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
