#!/usr/bin/env python3
"""Build the immutable two-chunk PK selector-730 assignment."""

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
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
BASE_BUILDER_PATH = WORKSTREAM / "build_pk_selector1198_assignment_v1.py"
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_selector562_consolidated_v1.py"
)
RANKING_PRIVATE_PATH = (
    TMP / "pk_next_selector_family_ranking.post_selector562_consolidated.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    WORKSTREAM / "public"
    / "pk_next_selector_family_ranking.post_selector562_consolidated.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = TMP / "pk_selector730_assignment.private.v1.json"
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector730_assignment_coverage.v1.json"
)

SELECTOR = 730
TERMINALS = tuple(range(2140, 2147))
PRIVATE_SCHEMA = "nobu16.kr.pk-selector730-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector730-assignment-coverage.v1"
METHOD = (
    "selector562_checkpoint_selector730_root_disjoint_two_chunk_"
    "per_root_same_gap_and_template_atom_assignment"
)
EXPECTED_INPUT_SHA256 = {
    "ledger":
        "8E31995689359D5F8DD1F23FC7A894C07AC8BBB3C08EF2B87651E6E3E8B1086A",
    "checkpoint_public":
        "5445CD4A9C9515A8732446DA397D0FF0BB66E657A17C14BEDC374CCC745CDF76",
    "ranking_builder":
        "09FD073859C3D75B2C4343D722A0498B6B20B0B8C5AD289A95C657CF052C92B8",
    "ranking_private":
        "1A8479D8CE3EEFE52E853B1B8F1AE0D194FF63D9E7CB1C27D4B0936D32041056",
    "ranking_public":
        "85E6DED228DF9771A973BE907C0B1973D15E5EFF59BDADEE4C64BED6B84CDA66",
    "base_assignment":
        "AE1428FBF34BA042F1588E89DAA02623752D791BCD498687B9AD8595ED4BD7FF",
    "helper":
        "E39ED4738833FB56680E81E5B06A68F04472BABE7279D92CB608A40DB7D17CF5",
}
EXPECTED_BASE_BUILDER_SHA256 = (
    "698AAEB85B9036ABBD4171E41E533EC9A2EDDCF511D9755BF0DD1BF7E60CB0EB"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "B7CBFA388BDD50F60CD5EEF88A63B62D357475925A0A3AA6D7DCA1A191607815"
)
EXPECTED_COVERAGE = (41, 41, 46, 5, 0, 18, 18, 37)
EXPECTED_SITE_ROW_SHA256: str | None = (
    "996F75ACDDB0E5EA9AE14F189D7D55F6966AAB3B29D50A6E49D0B66770188C3E"
)
EXPECTED_TEMPLATE_SIZES = (2,)
EXPECTED_CHUNK_METRICS: tuple[tuple[int, ...], ...] | None = (
    (21, 21, 8, 12, 3, 503),
    (20, 20, 10, 25, 7, 504),
)
EXPECTED_COMPLETED_OVERLAP = (10, 10, 23)
EXPECTED_PRIOR_ASSEMBLY_EVIDENCE = (15, 32)
EXPECTED_SAME_GAP = (37, 37, 37, 17, 34, 1_813)
EXPECTED_ATOMIC_SENSITIVE_ROOTS = 38
EXPECTED_FLAG_COUNTS = (27, 21, 480)
EXPECTED_TERMINAL_EVIDENCE = 7
EXPECTED_TERMINAL_COMPARISON = (4, 3)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "D9554CC8E6BED91EB9141CFC11F142E389868565AFC7B82B230FC9F931DB4781"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "07EA6FE891F17C7E4CF22C6C42625D1E224FF606524A2683ED0CA58C767CD454"
)


def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSIGNMENT = load(BASE_BUILDER_PATH, "selector730_assignment_base")
RANKING_WRAPPER = load(RANKING_BUILDER_PATH, "selector730_ranking")
RANKING = RANKING_WRAPPER.RANKING
ENGINE = RANKING.ENGINE
RANKING.CONTROL_RE = RANKING.LEGACY.CONTROL_RE
ORIGINAL_TEMPLATE_ATOMS = ASSIGNMENT.BASE.template_atoms
ORIGINAL_JSON_LOADS = json.loads


def structural_atoms(
    sites: Sequence[str],
    record_sets: Sequence[Any],
) -> list[set[tuple[int, int]]]:
    repeated = ORIGINAL_TEMPLATE_ATOMS(sites, record_sets)
    candidate = record_sets[0]
    edges = RANKING.graph_edges(candidate)
    same_gap_roots = {
        RANKING.site_key(site)[:2]
        for site in sites
        if sum(
            int(edge["gap_id"]) == RANKING.site_key(site)[2]
            for edge in edges[RANKING.site_key(site)[:2]]
        ) > 1
    }
    ranking = ORIGINAL_JSON_LOADS(
        RANKING_PRIVATE_PATH.read_text(encoding="utf-8")
    )
    target = next(
        row for row in ranking["direct_targets"]
        if row["target_coordinate"] == f"0:{SELECTOR}"
    )
    reachable = {
        RANKING.parse_root(root)
        for root in target["reachable_pending_roots"]
    }
    owned = {
        root
        for root in reachable
        if any(
            (0, selector) in RANKING.reachable_call_targets(edges, root)
            for selector in RANKING_WRAPPER.OWNED_SELECTORS
        )
    }
    template_union = set().union(*repeated) if repeated else set()
    sensitive = same_gap_roots | owned
    return repeated + [
        {root} for root in sorted(sensitive - template_union)
    ]


def configure() -> None:
    for name in (
        "RANKING_BUILDER_PATH", "RANKING_PRIVATE_PATH", "RANKING_PUBLIC_PATH",
        "DEFAULT_PRIVATE_OUTPUT", "DEFAULT_PUBLIC_OUTPUT", "SELECTOR",
        "TERMINALS", "PRIVATE_SCHEMA", "PUBLIC_SCHEMA", "METHOD",
        "EXPECTED_INPUT_SHA256", "EXPECTED_PK_CANDIDATE_SHA256",
        "EXPECTED_COVERAGE", "EXPECTED_SITE_ROW_SHA256",
        "EXPECTED_CHUNK_METRICS", "EXPECTED_PRIVATE_FILE_SHA256",
        "EXPECTED_PUBLIC_FILE_SHA256",
    ):
        setattr(ASSIGNMENT, name, globals()[name])
    ASSIGNMENT.EXPECTED_TEMPLATE_SIZES = None
    ASSIGNMENT.template_atoms = structural_atoms
    ASSIGNMENT.balanced_chunks = ASSIGNMENT.BASE.balanced_chunks
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
    ASSIGNMENT.HELPER.CHUNK_COUNT = 2
    ASSIGNMENT.HELPER.LEGACY.RANKING = RANKING
    ASSIGNMENT.HELPER.LEGACY.ENGINE = ENGINE
    ASSIGNMENT.HELPER.LEGACY.SELECTOR = SELECTOR
    ASSIGNMENT.HELPER.LEGACY.TERMINALS = TERMINALS


configure()
AssignmentError = ASSIGNMENT.AssignmentError
require = ASSIGNMENT.require
sha256_file = ASSIGNMENT.sha256_file
assert_source_free = ASSIGNMENT.assert_source_free


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector730 assignment base drifted",
    )
    original_loads = ASSIGNMENT.json.loads

    def adapted_loads(value: str, *args: Any, **kwargs: Any) -> Any:
        result = original_loads(value, *args, **kwargs)
        if not isinstance(result, dict):
            return result
        for row in result.get("direct_targets", []):
            target = row.get("target_coordinate")
            if target == "0:1198":
                row["target_coordinate"] = "0:-1198"
            elif target == "0:730":
                row["target_coordinate"] = "0:1198"
        recommendation = result.get("recommendation")
        if (
            isinstance(recommendation, dict)
            and recommendation.get("selector_coordinate") == "0:730"
        ):
            recommendation["selector_coordinate"] = "0:1198"
        return result

    ASSIGNMENT.json.loads = adapted_loads
    try:
        _a, _b, private, public = ASSIGNMENT.build_outputs()
    finally:
        ASSIGNMENT.json.loads = original_loads

    candidate, current, source, contexts, pending = (
        ASSIGNMENT.RECORDS.load_records()
    )
    edges = RANKING.graph_edges(candidate)
    ranking = ORIGINAL_JSON_LOADS(
        RANKING_PRIVATE_PATH.read_text(encoding="utf-8")
    )
    target = next(
        row for row in ranking["direct_targets"]
        if row["target_coordinate"] == "0:730"
    )
    reachable = {
        RANKING.parse_root(root)
        for root in target["reachable_pending_roots"]
    }
    potential = {
        coordinate for root in reachable for coordinate in pending[root]
    }
    candidate_sites = [str(row["site"]) for row in private["site_assignments"]]
    record_sets = [
        candidate, current, source,
        contexts["en"], contexts["sc"], contexts["tc"],
    ]
    templates = ORIGINAL_TEMPLATE_ATOMS(candidate_sites, record_sets)
    require(
        tuple(sorted(len(group) for group in templates))
        == EXPECTED_TEMPLATE_SIZES,
        "template atom drifted",
    )
    template_union = set().union(*templates)

    owned_relations = {
        (RANKING.root_string(root), selector)
        for root in reachable
        for selector in RANKING_WRAPPER.OWNED_SELECTORS
        if (0, selector) in RANKING.reachable_call_targets(edges, root)
    }
    owned_roots = {root for root, _selector in owned_relations}
    owned_pending = {
        coordinate
        for root in owned_roots
        for coordinate in pending[RANKING.parse_root(root)]
    }
    require(
        (len(owned_roots), len(owned_relations), len(owned_pending))
        == EXPECTED_COMPLETED_OVERLAP,
        "completed-owned overlap drifted",
    )

    same_gap_sites = []
    same_gap_roots = set()
    same_gap_relations = []
    sibling_selectors = set()
    for site in candidate_sites:
        block, record, gap, _offset = RANKING.site_key(site)
        controls = sorted(
            (
                edge for edge in edges[(block, record)]
                if int(edge["gap_id"]) == gap
            ),
            key=lambda edge: int(edge["offset"]),
        )
        if len(controls) <= 1:
            continue
        require(len(controls) == 2, "same-gap control count drifted")
        siblings = [
            int(edge["target"][1])
            for edge in controls
            if int(edge["target"][1]) != SELECTOR
        ]
        require(len(siblings) == 1, "same-gap sibling drifted")
        root = (block, record)
        same_gap_sites.append(site)
        same_gap_roots.add(root)
        same_gap_relations.append({
            "ordered_targets": [
                {
                    "offset": int(edge["offset"]),
                    "selector": int(edge["target"][1]),
                }
                for edge in controls
            ],
            "root": RANKING.root_string(root),
            "site": site,
            "sibling_selector": siblings[0],
        })
        sibling_selectors.add(siblings[0])
    same_gap_pending = {
        coordinate
        for root in same_gap_roots
        for coordinate in pending.get(root, set())
    }
    same_gap_pending_roots = {
        root for root in same_gap_roots if root in pending
    }
    require(
        (
            len(same_gap_sites), len(same_gap_roots),
            len(same_gap_relations), len(same_gap_pending_roots),
            len(same_gap_pending), len(same_gap_sites) * 49,
        ) == EXPECTED_SAME_GAP
        and len(sibling_selectors) == 17,
        "same-gap scope drifted",
    )

    ledger_rows = [
        ORIGINAL_JSON_LOADS(line)
        for line in RANKING_WRAPPER.DEFAULT_LEDGER.read_text(
            encoding="utf-8"
        ).splitlines()
        if line
    ]
    pk_ledger = {
        str(row["coordinate"]): row
        for row in ledger_rows
        if row.get("resource") == "pk_msggame"
    }
    assembly_coordinates = {
        coordinate
        for coordinate in potential
        if pk_ledger[coordinate].get("runtime_assembly_evidence")
    }
    assembly_roots = {
        ":".join(coordinate.split(":")[:2])
        for coordinate in assembly_coordinates
    }
    require(
        (len(assembly_roots), len(assembly_coordinates))
        == EXPECTED_PRIOR_ASSEMBLY_EVIDENCE,
        "prior assembly evidence drifted",
    )

    terminal_coordinates = [
        f"0:{terminal}:0" for terminal in TERMINALS
    ]
    terminal_manifest = []
    for coordinate in terminal_coordinates:
        root = RANKING.parse_root(":".join(coordinate.split(":")[:2]))
        terminal_manifest.append({
            "candidate_current_identical":
                candidate[root].data == current[root].data,
            "coordinate": coordinate,
            "runtime_review": pk_ledger[coordinate]["runtime_review"],
        })
    require(
        len(terminal_manifest) == EXPECTED_TERMINAL_EVIDENCE
        and all(row["runtime_review"] == "pending" for row in terminal_manifest)
        and (
            sum(row["candidate_current_identical"] for row in terminal_manifest),
            sum(not row["candidate_current_identical"] for row in terminal_manifest),
        ) == EXPECTED_TERMINAL_COMPARISON,
        "terminal read-only evidence drifted",
    )

    source_sites = set(
        RANKING.candidate_call_sites(RANKING.graph_edges(source))[(0, SELECTOR)]
    )
    source_only = source_sites - set(candidate_sites)
    require(len(source_only) == 5, "source-only scope drifted")
    expansion_count = sum(
        bool(row["flags"]["layout_relative_expansion"])
        for row in private["site_assignments"]
    )
    grammar_count = sum(
        bool(row["flags"]["grammar_right_boundary"])
        for row in private["site_assignments"]
    )
    maximum_expansion = max(
        int(row["maximum_positive_raw_g1n_delta_px"])
        for row in private["site_assignments"]
    )
    require(
        (expansion_count, grammar_count, maximum_expansion)
        == EXPECTED_FLAG_COUNTS,
        "risk flags drifted",
    )

    atomic_sensitive = template_union | same_gap_roots | {
        RANKING.parse_root(root) for root in owned_roots
    }
    require(
        len(atomic_sensitive) == EXPECTED_ATOMIC_SENSITIVE_ROOTS,
        "atomic-sensitive union drifted",
    )
    root_to_chunk = {
        RANKING.parse_root(root): int(chunk["chunk_id"])
        for chunk in private["chunks"]
        for root in chunk["roots"]
    }
    require(
        all(
            len({root_to_chunk[root] for root in group}) == 1
            for group in templates
        ),
        "template atom split",
    )

    private["schema"] = PRIVATE_SCHEMA
    private["method"] = METHOD
    private["scope"]["selector_coordinate"] = "0:730:0"
    private["identical_template_atoms"] = [
        [RANKING.root_string(root) for root in sorted(group)]
        for group in templates
    ]
    private["same_gap_root_atoms"] = same_gap_relations
    private["completed_selector_overlap"] = {
        "pending_row_count": len(owned_pending),
        "relation_count": len(owned_relations),
        "relations": [
            {"root": root, "selector": selector}
            for root, selector in sorted(owned_relations)
        ],
        "root_count": len(owned_roots),
    }
    private["prior_pending_evidence"] = {
        "automatic_status_promotion_authorized": False,
        "potential_pending_assembly_coordinates": sorted(
            assembly_coordinates, key=RANKING.parse_coordinate
        ),
        "potential_pending_assembly_root_count": len(assembly_roots),
    }
    private["shared_terminal_ownership"] = {
        "automatic_status_promotion_authorized": False,
        "terminal_manifest": terminal_manifest,
    }
    private["source_only_repair"] = {
        "action_count": 0,
        "sites": sorted(source_only, key=RANKING.site_key),
    }
    private_chunks = {int(row["chunk_id"]): row for row in private["chunks"]}
    for chunk in private["chunks"]:
        roots = {RANKING.parse_root(root) for root in chunk["roots"]}
        chunk["atomic_sensitive_root_count"] = len(roots & atomic_sensitive)
        chunk["completed_selector_overlap_relation_count"] = sum(
            root in {RANKING.root_string(value) for value in roots}
            for root, _selector in owned_relations
        )
        chunk["prior_assembly_evidence_pending_row_count"] = len(
            set(chunk["pending_coordinates"]) & assembly_coordinates
        )
        chunk["prior_assembly_evidence_root_count"] = len(
            {RANKING.root_string(root) for root in roots} & assembly_roots
        )
        chunk["same_gap_atom_count"] = len(roots & same_gap_roots)
        chunk["same_gap_cartesian_branch_count"] = (
            len(roots & same_gap_roots) * 49
        )
        chunk["template_root_count"] = len(roots & template_union)
        chunk["template_root_sha256"] = ASSIGNMENT.root_digest(
            roots & template_union
        )

    public["schema"] = PUBLIC_SCHEMA
    public["method"] = METHOD
    public["scope"]["selector"] = SELECTOR
    public["scope"]["official_pending_rows"] = 6_181
    public["assignment"].update({
        "atomic_sensitive_root_count": len(atomic_sensitive),
        "giant_atom_created": False,
        "identical_template_atom_count": len(templates),
        "identical_template_root_count": len(template_union),
        "maximum_assignment_atom_root_count": 2,
        "same_gap_atom_count": len(same_gap_roots),
        "same_gap_atom_split": False,
        "same_gap_cartesian_branch_count": len(same_gap_sites) * 49,
        "same_gap_sibling_family_count": len(sibling_selectors),
        "shared_terminal_group_count": 1,
        "shared_terminal_group_split": False,
        "terminal_manifest_sha256":
            ASSIGNMENT.canonical_sha256(terminal_manifest),
    })
    public["coverage"].update({
        "candidate_non_display_root_count": 0,
        "completed_selector_overlap_relation_count": len(owned_relations),
        "direct_pending_non_display_root_count": 0,
        "prior_assembly_evidence_pending_root_count": len(assembly_roots),
        "prior_assembly_evidence_pending_row_count": len(assembly_coordinates),
        "same_gap_pending_root_count": len(same_gap_pending_roots),
        "same_gap_pending_row_count": len(same_gap_pending),
        "source_only_action_count": 0,
        "source_only_repair_site_count": len(source_only),
        "source_only_repair_site_sha256": ASSIGNMENT.site_digest(source_only),
    })
    public["terminal_compatibility"] = {
        "automatic_status_promotion_authorized": False,
        "candidate_current_different_terminal_count":
            EXPECTED_TERMINAL_COMPARISON[1],
        "candidate_current_identical_terminal_count":
            EXPECTED_TERMINAL_COMPARISON[0],
        "context_terminals_authoritative": False,
        "read_only_pending_terminal_count": 7,
    }
    for chunk in public["assignment"]["chunks"]:
        source_chunk = private_chunks[int(chunk["chunk_id"])]
        for key in (
            "atomic_sensitive_root_count",
            "completed_selector_overlap_relation_count",
            "prior_assembly_evidence_pending_row_count",
            "prior_assembly_evidence_root_count",
            "same_gap_atom_count",
            "same_gap_cartesian_branch_count",
            "template_root_count",
            "template_root_sha256",
        ):
            chunk[key] = source_chunk[key]

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
    parser.add_argument("--bootstrap", action="store_true")
    args = parser.parse_args(argv)
    private_content, public_content, _private, public = build_outputs()
    private_sha = ASSIGNMENT.sha256_bytes(private_content.encode("utf-8"))
    public_sha = ASSIGNMENT.sha256_bytes(public_content.encode("utf-8"))
    if not args.bootstrap:
        require(
            EXPECTED_SITE_ROW_SHA256 is not None
            and EXPECTED_CHUNK_METRICS is not None
            and EXPECTED_PRIVATE_FILE_SHA256 is not None
            and EXPECTED_PUBLIC_FILE_SHA256 is not None,
            "assignment bootstrap pins unresolved",
        )
        require(
            private_sha == EXPECTED_PRIVATE_FILE_SHA256
            and public_sha == EXPECTED_PUBLIC_FILE_SHA256,
            "assignment output drifted",
        )
    if args.check:
        require(
            DEFAULT_PRIVATE_OUTPUT.read_text(encoding="utf-8")
            == private_content,
            "private artifact drifted",
        )
        require(
            DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii")
            == public_content,
            "public artifact drifted",
        )
    else:
        DEFAULT_PRIVATE_OUTPUT.write_text(
            private_content, encoding="utf-8", newline=""
        )
        DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
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
        "same_gap_cartesian_branches":
            public["assignment"]["same_gap_cartesian_branch_count"],
        "steam_write_performed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
