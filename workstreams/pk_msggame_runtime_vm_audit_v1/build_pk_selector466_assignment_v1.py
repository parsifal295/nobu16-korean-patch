#!/usr/bin/env python3
"""Build the immutable two-chunk PK selector-466 assignment."""

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
BASE_BUILDER_PATH = WORKSTREAM / "build_pk_selector1198_assignment_v1.py"
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_selector1078_consolidated_v1.py"
)
RANKING_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector1078_consolidated.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector1078_consolidated.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = DIALOGUE_TMP / "pk_selector466_assignment.private.v1.json"
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector466_assignment_coverage.v1.json"
)

SELECTOR = 466
TERMINALS = tuple(range(1839, 1846))
PRIVATE_SCHEMA = "nobu16.kr.pk-selector466-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector466-assignment-coverage.v1"
METHOD = (
    "selector1078_checkpoint_selector466_root_disjoint_two_chunk_"
    "template_and_same_gap_control_atom_assignment"
)
EXPECTED_INPUT_SHA256 = {
    "ledger":
        "71ADE7F33FC40A817E60F429DE0A0B329E05BF37BD1E03E1671A019783E800F6",
    "checkpoint_public":
        "395C8B600B1AED634FA199602CBBB9F2DCA5691D9E5850688E2107966A8A77E3",
    "ranking_builder":
        "E7FBD842B47A583AA0DF3A3EC0C084BE5DDAC1D5CBE159A2DE4C8323154C183B",
    "ranking_private":
        "1FBA5D0ACAFAF1E4194DD8B11A955C7C4380E3A742E74F202243CE30FCA22D2E",
    "ranking_public":
        "B2083C98020074910116226E7EA0B798A40A6760EF1F9D68609770317DD36203",
    "base_assignment":
        "AE1428FBF34BA042F1588E89DAA02623752D791BCD498687B9AD8595ED4BD7FF",
    "helper":
        "E39ED4738833FB56680E81E5B06A68F04472BABE7279D92CB608A40DB7D17CF5",
}
EXPECTED_BASE_BUILDER_SHA256 = (
    "698AAEB85B9036ABBD4171E41E533EC9A2EDDCF511D9755BF0DD1BF7E60CB0EB"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "1A931E023A5248626AE90094772657D91B4270D0F530B48ABC613FDA84BB508D"
)
EXPECTED_COVERAGE = (79, 79, 94, 15, 0, 20, 20, 41)
EXPECTED_SITE_ROW_SHA256: str | None = (
    "509E8B764B4D98FC2295B0BF303105CC637531CC73BD3EE0800DEF08C0A4368A"
)
EXPECTED_TEMPLATE_SIZES: tuple[int, ...] | None = (2, 3, 4, 8, 8)
EXPECTED_CHUNK_METRICS: tuple[tuple[int, ...], ...] | None = (
    (38, 38, 8, 16, 1, 836),
    (41, 41, 12, 25, 2, 831),
)
EXPECTED_COMPLETED_OVERLAP = (3, 4, 5)
EXPECTED_PRIOR_ASSEMBLY_EVIDENCE = (18, 35)
EXPECTED_TERMINAL_EVIDENCE = 7
EXPECTED_SAME_GAP_ATOM = (2, 2, 2, 4)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "8C7350F94A08894C5B88A4E6BD335DA96877EEE55902B4E9110186FE0E8C7507"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "457C7C0D368269F69C391E6A981CF6AA5D4FB905C99B327C2DAEE9C4F137BA5E"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSIGNMENT = load_module(BASE_BUILDER_PATH, "pk_selector466_assignment_base_v1")
RANKING_WRAPPER = load_module(RANKING_BUILDER_PATH, "pk_selector466_ranking_v1")
RANKING = RANKING_WRAPPER.RANKING
ENGINE = RANKING.ENGINE
RANKING.CONTROL_RE = RANKING.LEGACY.CONTROL_RE
ORIGINAL_TEMPLATE_ATOMS = ASSIGNMENT.BASE.template_atoms
ORIGINAL_JSON_LOADS = json.loads


def assignment_atoms(
    sites: Sequence[str],
    record_sets: Sequence[Any],
) -> list[set[tuple[int, int]]]:
    """Preserve repeated templates and all ambiguous same-gap roots."""
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
    if same_gap_roots:
        repeated.append(same_gap_roots)
    return repeated


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
        "EXPECTED_CHUNK_METRICS",
        "EXPECTED_PRIVATE_FILE_SHA256",
        "EXPECTED_PUBLIC_FILE_SHA256",
    ):
        setattr(ASSIGNMENT, name, globals()[name])
    # The generic field counts all balancing atoms, including the dedicated
    # same-gap block. Repeated-template sizes are pinned independently below.
    ASSIGNMENT.EXPECTED_TEMPLATE_SIZES = None
    ASSIGNMENT.template_atoms = assignment_atoms
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


configure_modules()
AssignmentError = ASSIGNMENT.AssignmentError
require = ASSIGNMENT.require
sha256_file = ASSIGNMENT.sha256_file
assert_source_free = ASSIGNMENT.assert_source_free


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector466 assignment base drift",
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
            elif target == "0:466":
                row["target_coordinate"] = "0:1198"
        recommendation = result.get("recommendation")
        if (
            isinstance(recommendation, dict)
            and recommendation.get("selector_coordinate") == "0:466"
        ):
            recommendation["selector_coordinate"] = "0:1198"
        return result

    ASSIGNMENT.json.loads = adapted_loads
    try:
        private_content, public_content, private, public = (
            ASSIGNMENT.build_outputs()
        )
    finally:
        ASSIGNMENT.json.loads = original_loads

    candidate, _current, source, _contexts, pending = (
        ASSIGNMENT.RECORDS.load_records()
    )
    candidate_edges = RANKING.graph_edges(candidate)
    source_edges = RANKING.graph_edges(source)
    ranking_private = ORIGINAL_JSON_LOADS(
        RANKING_PRIVATE_PATH.read_text(encoding="utf-8")
    )
    target = next(
        row for row in ranking_private["direct_targets"]
        if row["target_coordinate"] == "0:466"
    )
    reachable_roots = {
        RANKING.parse_root(root) for root in target["reachable_pending_roots"]
    }
    potential = {
        coordinate for root in reachable_roots for coordinate in pending[root]
    }

    owned_relations = {
        (RANKING.root_string(root), selector)
        for root in reachable_roots
        for selector in RANKING_WRAPPER.OWNED_SELECTORS
        if (0, selector) in RANKING.reachable_call_targets(
            candidate_edges, root
        )
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
        "completed-selector overlap drift",
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
        "prior assembly evidence overlap drift",
    )

    closure_terminals = [
        f"{coordinate}:0"
        for coordinate in target["jump_closure"]["terminal_coordinates"]
    ]
    terminal_evidence = [pk_ledger[coordinate] for coordinate in closure_terminals]
    require(
        closure_terminals == [f"0:{terminal}:0" for terminal in TERMINALS]
        and len(terminal_evidence) == EXPECTED_TERMINAL_EVIDENCE
        and all(
            row.get("runtime_assembly_evidence")
            and row.get("runtime_review") == "verified"
            for row in terminal_evidence
        ),
        "terminal closure/evidence/read-only drift",
    )
    terminal_manifest = []
    for coordinate in closure_terminals:
        root = RANKING.parse_root(":".join(coordinate.split(":")[:2]))
        record = candidate[root]
        literals = ENGINE.parse_record_literals(record)
        controls = RANKING.LEGACY.record_edges(record)
        terminal_manifest.append({
            "component_signature_sha256": ASSIGNMENT.canonical_sha256([
                ASSIGNMENT.sha256_bytes(item.text.encode("utf-8"))
                for item in literals
            ]),
            "control_signature_sha256": ASSIGNMENT.canonical_sha256(controls),
            "coordinate": coordinate,
            "raw_record_sha256": ASSIGNMENT.sha256_bytes(record.data),
            "runtime_review": pk_ledger[coordinate]["runtime_review"],
        })

    same_gap_rows = [
        row for row in private["site_assignments"]
        if row["flags"]["multi_control_gap"]
    ]
    same_gap_roots = {
        RANKING.parse_root(str(row["root"])) for row in same_gap_rows
    }
    same_gap_relations: set[tuple[str, int]] = set()
    same_gap_manifest = []
    for row in same_gap_rows:
        site = str(row["site"])
        block_id, record_id, gap_id, site_offset = RANKING.site_key(site)
        root = (block_id, record_id)
        siblings = sorted(
            (
                {
                    "gap_id": int(edge["gap_id"]),
                    "kind": str(edge["kind"]),
                    "offset": int(edge["offset"]),
                    "target": RANKING.root_string(tuple(edge["target"])),
                }
                for edge in candidate_edges[root]
                if int(edge["gap_id"]) == gap_id
            ),
            key=lambda item: (item["offset"], item["kind"], item["target"]),
        )
        for sibling in siblings:
            if sibling["target"] != f"0:{SELECTOR}":
                same_gap_relations.add((RANKING.root_string(root), int(
                    sibling["target"].split(":")[1]
                )))
        literals = ENGINE.parse_record_literals(candidate[root])
        left = literals[gap_id - 1].text if gap_id else ""
        right = literals[gap_id].text if gap_id < len(literals) else ""
        same_gap_manifest.append({
            "assignment_mode": "block_all_ordered_sibling_controls",
            "cartesian_runtime_validation_complete": False,
            "gap_id": gap_id,
            "left_right_digest_sha256": ASSIGNMENT.canonical_sha256({
                "left": ASSIGNMENT.sha256_bytes(left.encode("utf-8")),
                "right": ASSIGNMENT.sha256_bytes(right.encode("utf-8")),
            }),
            "ordered_siblings": siblings,
            "root": RANKING.root_string(root),
            "site": site,
            "site_offset": site_offset,
        })
    same_gap_pending = {
        coordinate
        for root in same_gap_roots
        for coordinate in pending.get(root, set())
    }
    require(
        (
            len(same_gap_rows),
            len(same_gap_roots),
            len(same_gap_relations),
            len(same_gap_pending),
        ) == EXPECTED_SAME_GAP_ATOM,
        "same-gap control atom drift",
    )

    repeated_atoms = ORIGINAL_TEMPLATE_ATOMS(
        [str(row["site"]) for row in private["site_assignments"]],
        [
            candidate,
            _current,
            source,
            *_contexts.values(),
        ],
    )
    require(
        tuple(sorted(len(group) for group in repeated_atoms))
        == EXPECTED_TEMPLATE_SIZES,
        "repeated-template atom drift",
    )
    root_to_chunk = {
        root: int(chunk["chunk_id"])
        for chunk in private["chunks"] for root in chunk["roots"]
    }
    require(
        len({root_to_chunk[RANKING.root_string(root)] for root in same_gap_roots})
        == 1,
        "same-gap atom split",
    )

    source_sites = set(
        RANKING.candidate_call_sites(source_edges)[(0, SELECTOR)]
    )
    candidate_sites = set(private["scope"]["candidate_call_sites"])
    source_only = source_sites - candidate_sites
    require(
        len(source_only) == 15 and not (candidate_sites - source_sites),
        "source-only scope drift",
    )
    non_display_roots = {
        ":".join(str(row["coordinate"]).split(":")[:2])
        for row in ledger_rows
        if row.get("resource") == "pk_msggame"
        and row.get("scope_classification") == "confirmed_non_display"
    }
    candidate_roots = {str(row["root"]) for row in private["site_assignments"]}
    direct_roots = {
        ":".join(coordinate.split(":")[:2])
        for coordinate in private["scope"]["potential_current_pending_coordinates"]
    }
    require(
        (len(candidate_roots & non_display_roots),
         len(direct_roots & non_display_roots)) == (0, 0),
        "confirmed non-display scope drift",
    )

    private["schema"] = PRIVATE_SCHEMA
    private["method"] = METHOD
    private["scope"]["selector_coordinate"] = "0:466:0"
    private["identical_template_atoms"] = [
        [RANKING.root_string(root) for root in sorted(group)]
        for group in repeated_atoms
    ]
    private["shared_terminal_ownership"] = {
        "automatic_status_promotion_authorized": False,
        "chunk_ids": [],
        "group_count": 1,
        "owner": "assignment_scope",
        "terminal_coordinates": closure_terminals,
        "terminal_manifest": terminal_manifest,
    }
    private["prior_pending_evidence"] = {
        "automatic_status_promotion_authorized": False,
        "potential_pending_assembly_coordinates": sorted(
            assembly_coordinates, key=RANKING.parse_coordinate
        ),
        "potential_pending_assembly_root_count": len(assembly_roots),
        "terminal_evidence_coordinates": closure_terminals,
        "terminal_evidence_count": len(terminal_evidence),
        "terminal_runtime_review": "verified_read_only",
    }
    private["completed_selector_overlap"] = {
        "pending_row_count": len(owned_pending),
        "relation_count": len(owned_relations),
        "relations": [
            {"root": root, "selector": selector}
            for root, selector in sorted(
                owned_relations,
                key=lambda item: (*RANKING.parse_root(item[0]), item[1]),
            )
        ],
        "root_count": len(owned_roots),
    }
    private["same_gap_control_atom"] = {
        "atom_roots": [
            RANKING.root_string(root) for root in sorted(same_gap_roots)
        ],
        "manifest": same_gap_manifest,
        "neighbor_relations": [
            {"root": root, "selector": selector}
            for root, selector in sorted(same_gap_relations)
        ],
        "pending_coordinates": sorted(
            same_gap_pending, key=RANKING.parse_coordinate
        ),
    }
    private["source_only_repair"] = {
        "action_count": 0,
        "sites": sorted(source_only, key=RANKING.site_key),
    }
    for chunk in private["chunks"]:
        roots = set(chunk["roots"])
        chunk["completed_selector_overlap_relation_count"] = sum(
            root in roots for root, _selector in owned_relations
        )
        chunk["prior_assembly_evidence_pending_row_count"] = len(
            set(chunk["pending_coordinates"]) & assembly_coordinates
        )
        chunk["prior_assembly_evidence_root_count"] = len(
            roots & assembly_roots
        )
        chunk["same_gap_atom_root_count"] = len(
            roots & {RANKING.root_string(root) for root in same_gap_roots}
        )

    public["schema"] = PUBLIC_SCHEMA
    public["method"] = METHOD
    public["scope"]["selector"] = SELECTOR
    public["scope"]["official_pending_rows"] = 6215
    public["assignment"]["identical_template_atom_count"] = len(repeated_atoms)
    public["assignment"]["identical_template_root_count"] = sum(
        len(group) for group in repeated_atoms
    )
    public["assignment"]["same_gap_atom_count"] = len(same_gap_roots)
    public["assignment"]["same_gap_atom_split"] = False
    public["assignment"]["same_gap_block_manifest_sha256"] = (
        ASSIGNMENT.canonical_sha256(same_gap_manifest)
    )
    public["assignment"]["shared_terminal_group_count"] = 1
    public["assignment"]["shared_terminal_group_split"] = False
    public["assignment"]["terminal_manifest_sha256"] = (
        ASSIGNMENT.canonical_sha256(terminal_manifest)
    )
    public["coverage"].update({
        "candidate_non_display_root_count": 0,
        "completed_selector_overlap_relation_count": len(owned_relations),
        "direct_pending_non_display_root_count": 0,
        "owned_overlap_pending_rows": len(owned_pending),
        "prior_assembly_evidence_pending_root_count": len(assembly_roots),
        "prior_assembly_evidence_pending_row_count": len(assembly_coordinates),
        "same_gap_pending_rows": len(same_gap_pending),
        "same_gap_relation_count": len(same_gap_relations),
        "same_gap_root_count": len(same_gap_roots),
        "source_only_action_count": 0,
        "source_only_repair_site_sha256": ASSIGNMENT.site_digest(source_only),
        "terminal_prior_evidence_pending_count": len(terminal_evidence),
    })
    public["terminal_compatibility"] = {
        "automatic_status_promotion_authorized": False,
        "candidate_terminal_nonempty_count": 7,
        "dispatch_source_candidate_identical": True,
        "read_only_verified_terminal_count": 7,
        "register_review_required": True,
    }
    private_chunks = {row["chunk_id"]: row for row in private["chunks"]}
    for chunk in public["assignment"]["chunks"]:
        private_chunk = private_chunks[chunk["chunk_id"]]
        for key in (
            "completed_selector_overlap_relation_count",
            "prior_assembly_evidence_pending_row_count",
            "prior_assembly_evidence_root_count",
            "same_gap_atom_root_count",
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
