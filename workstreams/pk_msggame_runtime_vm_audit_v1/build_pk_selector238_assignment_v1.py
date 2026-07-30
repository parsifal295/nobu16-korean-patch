#!/usr/bin/env python3
"""Build the immutable two-chunk PK selector-238 assignment."""

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
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
BASE_BUILDER_PATH = WORKSTREAM / "build_pk_selector1198_assignment_v1.py"
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_selector730_consolidated_v1.py"
)
RANKING_PRIVATE_PATH = (
    TMP / "pk_next_selector_family_ranking.post_selector730_consolidated.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    WORKSTREAM / "public"
    / "pk_next_selector_family_ranking.post_selector730_consolidated.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = TMP / "pk_selector238_assignment.private.v1.json"
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector238_assignment_coverage.v1.json"
)

SELECTOR = 238
TERMINALS = tuple(range(1552, 1559))
PRIVATE_SCHEMA = "nobu16.kr.pk-selector238-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector238-assignment-coverage.v1"
METHOD = (
    "selector730_checkpoint_selector238_root_disjoint_two_chunk_"
    "minimal_structural_atom_assignment"
)
EXPECTED_INPUT_SHA256 = {
    "ledger":
        "9F6BD587F6EC92CD00A2E2AF9FD9E07A8B6A71405272F0D79A515C3405617C5C",
    "checkpoint_public":
        "311DD27E8C260B7438EDF90FFB944EAEC25C3462C2C8E6BDA196BCF89DEDF362",
    "ranking_builder":
        "3BCA1BFD3A6F4E87975EC46C15E8EEA460AF0EE348C3D3BD199668DF76C271AD",
    "ranking_private":
        "7ECBEFF5559CDE4AFAE5D3EA96F26BF25CCADCA8881CA588859AB693A437A2B8",
    "ranking_public":
        "58386A927032222AB951E4FB5170ADB587627528657D7617B14B5EA2B8B0A266",
    "base_assignment":
        "AE1428FBF34BA042F1588E89DAA02623752D791BCD498687B9AD8595ED4BD7FF",
    "helper":
        "E39ED4738833FB56680E81E5B06A68F04472BABE7279D92CB608A40DB7D17CF5",
}
EXPECTED_BASE_BUILDER_SHA256 = (
    "698AAEB85B9036ABBD4171E41E533EC9A2EDDCF511D9755BF0DD1BF7E60CB0EB"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "5D4CDF1CEB8C733B0E22C7AA6185D9FF6C5C4C500176E99A6AACB3D89F7E0140"
)
EXPECTED_COVERAGE = (27, 27, 28, 1, 0, 15, 15, 36)
EXPECTED_SITE_ROW_SHA256: str | None = (
    "0460BEDA1B60F22CC2B02B3EDCA3FE7D464BE2B6846A2C97DD08C19057F9B2EC"
)
EXPECTED_TEMPLATE_SIZES = ()
EXPECTED_CHUNK_METRICS: tuple[tuple[int, ...], ...] | None = (
    (14, 14, 7, 14, 4, 271),
    (13, 13, 8, 22, 4, 261),
)
EXPECTED_COMPLETED_OVERLAP = (8, 8, 18)
EXPECTED_PRIOR_ASSEMBLY_EVIDENCE = (14, 26)
EXPECTED_SAME_GAP = (0, 0, 0, 0, 0, 0)
EXPECTED_ATOMIC_SENSITIVE_ROOTS = 14
EXPECTED_FLAG_COUNTS = (15, 25, 408)
EXPECTED_TERMINAL_EVIDENCE = 7
EXPECTED_TERMINAL_COMPARISON = (6, 1)
EXPECTED_ORDINARY_BRANCHES = 105
EXPECTED_WIDTH_PRECHECK = (4, 1, 10)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "464E10C8A1DCFEF1B73492494A92601C01AC45FADE7F9D63D9691A931208F706"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "EED5D974C2CCA3E2C2186AEDC0DF3A480C95062942D55ECC3E966B8B94207B5E"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "E7D01ED5F17258F69B7A74858EC5D442FF39E9F2551426F903AAF83E1D6AA8ED"
)
EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_SOURCE_ONLY_SHA256 = (
    "52B8160BA78B19CEB6727EDC82F1D93599D79C0D3777EA849456B52397A51CFE"
)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "3B8629AC3DF5E18FEA92D82EB97D0E6D87870509E1C986BEFC3069050FF6D0C8"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "B44358FE6CC6EAD85972255F8D360EF5B6A0B1AB2D935DBCA4CC7F4D490ACE30"
)


def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSIGNMENT = load(BASE_BUILDER_PATH, "selector238_assignment_base")
RANKING_WRAPPER = load(RANKING_BUILDER_PATH, "selector238_ranking")
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
    ledger = {
        str(row["coordinate"]): row
        for row in (
            ORIGINAL_JSON_LOADS(line)
            for line in RANKING_WRAPPER.DEFAULT_LEDGER.read_text(
                encoding="utf-8"
            ).splitlines()
            if line
        )
        if row.get("resource") == "pk_msggame"
    }
    prior_roots = {
        RANKING.parse_root(":".join(coordinate.split(":")[:2]))
        for coordinate in target["current_pending_coordinates"]
        if ledger[coordinate].get("runtime_assembly_evidence")
    }
    template_union = set().union(*repeated) if repeated else set()
    sensitive = same_gap_roots | owned | prior_roots
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


def terminal_digest(records: Any) -> str:
    values = []
    for terminal in TERMINALS:
        literals = ENGINE.parse_record_literals(records[(0, terminal)])
        require(len(literals) == 1, "terminal literal shape drifted")
        values.append(literals[0].text)
    return ASSIGNMENT.sha256_bytes("\0".join(values).encode("utf-8"))


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector238 assignment base drifted",
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
            elif target == "0:238":
                row["target_coordinate"] = "0:1198"
        recommendation = result.get("recommendation")
        if (
            isinstance(recommendation, dict)
            and recommendation.get("selector_coordinate") == "0:238"
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
        if row["target_coordinate"] == "0:238"
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
    template_union = set().union(*templates) if templates else set()

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
        siblings = [
            int(edge["target"][1])
            for edge in controls
            if int(edge["target"][1]) != SELECTOR
        ]
        root = (block, record)
        same_gap_sites.append(site)
        same_gap_roots.add(root)
        same_gap_relations.append({
            "control_count": len(controls),
            "ordered_targets": [
                {
                    "offset": int(edge["offset"]),
                    "selector": int(edge["target"][1]),
                }
                for edge in controls
            ],
            "root": RANKING.root_string(root),
            "site": site,
            "sibling_selectors": siblings,
        })
        sibling_selectors.update(siblings)
    same_gap_pending = {
        coordinate
        for root in same_gap_roots
        for coordinate in pending.get(root, set())
    }
    same_gap_pending_roots = same_gap_roots & set(pending)
    require(
        (
            len(same_gap_sites), len(same_gap_roots),
            len(same_gap_relations), len(same_gap_pending_roots),
            len(same_gap_pending), sum(
                7 ** int(row["control_count"])
                for row in same_gap_relations
            ),
        ) == EXPECTED_SAME_GAP
        and not sibling_selectors,
        "same-gap or multi-control scope drifted",
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

    terminal_manifest = []
    for terminal in TERMINALS:
        coordinate = f"0:{terminal}:0"
        root = (0, terminal)
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
    require(
        terminal_digest(candidate) == EXPECTED_TERMINAL_CANDIDATE_SHA256
        and terminal_digest(current) == EXPECTED_TERMINAL_CURRENT_SHA256
        and terminal_digest(source) == EXPECTED_TERMINAL_SOURCE_SHA256
        and all(
            terminal_digest(contexts[language])
                == EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256
            for language in ("en", "sc", "tc")
        ),
        "terminal family digest drifted",
    )

    source_sites = set(
        RANKING.candidate_call_sites(RANKING.graph_edges(source))[(0, SELECTOR)]
    )
    source_only = source_sites - set(candidate_sites)
    require(
        len(source_only) == 1
        and ASSIGNMENT.site_digest(source_only)
            == EXPECTED_SOURCE_ONLY_SHA256,
        "source-only scope drifted",
    )
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

    atomic_sensitive = (
        template_union
        | same_gap_roots
        | {RANKING.parse_root(root) for root in owned_roots}
        | {RANKING.parse_root(root) for root in assembly_roots}
    )
    require(
        len(atomic_sensitive) == EXPECTED_ATOMIC_SENSITIVE_ROOTS,
        "atomic-sensitive union drifted: "
        f"{len(atomic_sensitive)} != {EXPECTED_ATOMIC_SENSITIVE_ROOTS}",
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
    private["scope"]["selector_coordinate"] = "0:238:0"
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
        root_strings = {RANKING.root_string(root) for root in roots}
        chunk["atomic_sensitive_root_count"] = len(roots & atomic_sensitive)
        chunk["completed_selector_overlap_relation_count"] = sum(
            root in root_strings for root, _selector in owned_relations
        )
        chunk["prior_assembly_evidence_pending_row_count"] = len(
            set(chunk["pending_coordinates"]) & assembly_coordinates
        )
        chunk["prior_assembly_evidence_root_count"] = len(
            root_strings & assembly_roots
        )
        chunk["same_gap_atom_count"] = len(roots & same_gap_roots)
        chunk["same_gap_cartesian_branch_count"] = sum(
            7 ** int(row["control_count"])
            for row in same_gap_relations
            if RANKING.parse_root(row["root"]) in roots
        )
        chunk["template_root_count"] = len(roots & template_union)
        chunk["template_root_sha256"] = ASSIGNMENT.root_digest(
            roots & template_union
        )

    public["schema"] = PUBLIC_SCHEMA
    public["method"] = METHOD
    public["scope"]["selector"] = SELECTOR
    public["scope"]["official_pending_rows"] = 6_178
    public["assignment"].update({
        "atomic_sensitive_root_count": len(atomic_sensitive),
        "giant_atom_created": False,
        "identical_template_atom_count": len(templates),
        "identical_template_root_count": len(template_union),
        "maximum_assignment_atom_root_count": 1,
        "multi_control_atom_count": len(same_gap_roots),
        "same_gap_atom_count": len(same_gap_roots),
        "same_gap_atom_split": False,
        "same_gap_cartesian_branch_count": EXPECTED_SAME_GAP[-1],
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
    pins_resolved = (
        EXPECTED_SITE_ROW_SHA256 is not None
        and EXPECTED_CHUNK_METRICS is not None
        and EXPECTED_PRIVATE_FILE_SHA256 is not None
        and EXPECTED_PUBLIC_FILE_SHA256 is not None
    )
    if args.bootstrap:
        require(not pins_resolved, "bootstrap forbidden after assignment freeze")
    else:
        require(pins_resolved, "assignment bootstrap pins unresolved")
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
