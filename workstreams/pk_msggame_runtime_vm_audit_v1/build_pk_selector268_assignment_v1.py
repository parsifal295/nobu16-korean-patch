#!/usr/bin/env python3
"""Build the root-disjoint two-chunk assignment for PK selector 268."""

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
BASE_BUILDER_PATH = WORKSTREAM / "build_pk_selector1198_assignment_v1.py"
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_selector226_consolidated_v1.py"
)
RANKING_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector226_consolidated.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector226_consolidated.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = DIALOGUE_TMP / "pk_selector268_assignment.private.v1.json"
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector268_assignment_coverage.v1.json"
)

SELECTOR = 268
TERMINALS = tuple(range(1587, 1594))
PRIVATE_SCHEMA = "nobu16.kr.pk-selector268-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector268-assignment-coverage.v1"
METHOD = (
    "selector226_checkpoint_selector268_root_disjoint_two_chunk_"
    "template_atom_and_pending_evidence_assignment"
)
EXPECTED_INPUT_SHA256 = {
    "ledger":
        "33B635E1409B290202A98719A9CD58F356551BB54703B7F287FC45250134623D",
    "checkpoint_public":
        "8526C4C53B87ED529D6C9EC44FF00FC9B77703EB6D4369DB83F4B916BAE37337",
    "ranking_builder":
        "5BFE586A4BA3B5D989E25BF444A1F7451C1798C6FAD45F7E9A331DD46265FDF9",
    "ranking_private":
        "C4A954E2B236CC2E5A04F23D3DE90F25806A76BEF087CDC3F3D6A1A5B5E8964A",
    "ranking_public":
        "2A8BFE0FBCFEBBDAF146C268D5DF7B4AFDC46CCB342ED7EDFF4E47C8A26CA6AA",
    "base_assignment":
        "AE1428FBF34BA042F1588E89DAA02623752D791BCD498687B9AD8595ED4BD7FF",
    "helper":
        "E39ED4738833FB56680E81E5B06A68F04472BABE7279D92CB608A40DB7D17CF5",
}
EXPECTED_WRAPPER_BASE_SHA256 = (
    "698AAEB85B9036ABBD4171E41E533EC9A2EDDCF511D9755BF0DD1BF7E60CB0EB"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "FEE99844339C291F6950BEB2193AB5FDD8D25B6F6117AD52F81DCBF7F0CC9B66"
)
EXPECTED_COVERAGE = (26, 25, 27, 1, 0, 16, 15, 44)
EXPECTED_SITE_ROW_SHA256: str | None = (
    "4D8D87A4E994526456BD54B91B5C882BDDFCC95DC41CF88282DE3C1E1673C3E4"
)
EXPECTED_TEMPLATE_SIZES: tuple[int, ...] | None = ()
EXPECTED_CHUNK_METRICS: tuple[tuple[int, ...], ...] | None = (
    (13, 12, 5, 16, 3, 242),
    (13, 13, 10, 28, 4, 255),
)
EXPECTED_COMPLETED_OVERLAP = (7, 10, 25)
EXPECTED_PRIOR_ASSEMBLY_EVIDENCE = (15, 41)
EXPECTED_TERMINAL_EVIDENCE = 7
EXPECTED_SAME_GAP_ATOM = (1, 1, 2, 1)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "91ED0510E5783DDA7B6894CA8A5144FB4D2FA9300A71BD2EC1B2F4699022C315"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "5F0C6B1935B7EC8568DC7C52EFB67D90BEF96398A8977DFEA70B23B3FA71053B"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSIGNMENT = load_module(BASE_BUILDER_PATH, "pk_selector268_assignment_base_v1")
RANKING_WRAPPER = load_module(RANKING_BUILDER_PATH, "pk_selector268_ranking_v1")
RANKING = RANKING_WRAPPER.RANKING
ENGINE = RANKING.ENGINE
RANKING.CONTROL_RE = RANKING.LEGACY.CONTROL_RE

for _name in (
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
    setattr(ASSIGNMENT, _name, globals()[_name])

ASSIGNMENT.RANKING_WRAPPER = RANKING_WRAPPER
ASSIGNMENT.RANKING = RANKING
ASSIGNMENT.ENGINE = ENGINE
for _module in (ASSIGNMENT.BASE, ASSIGNMENT.RECORDS):
    _module.RANKING_WRAPPER = RANKING_WRAPPER
    _module.RANKING = RANKING
    _module.ENGINE = ENGINE
    _module.SELECTOR = SELECTOR
    _module.TERMINALS = TERMINALS
    _module.EXPECTED_PK_CANDIDATE_SHA256 = EXPECTED_PK_CANDIDATE_SHA256
ASSIGNMENT.RECORDS.OFFICIAL_LEDGER_PATH = RANKING_WRAPPER.DEFAULT_LEDGER
ASSIGNMENT.HELPER.RANKING = RANKING
ASSIGNMENT.HELPER.ENGINE = ENGINE
ASSIGNMENT.HELPER.LEGACY.RANKING = RANKING
ASSIGNMENT.HELPER.LEGACY.ENGINE = ENGINE
ASSIGNMENT.HELPER.LEGACY.SELECTOR = SELECTOR
ASSIGNMENT.HELPER.LEGACY.TERMINALS = TERMINALS

AssignmentError = ASSIGNMENT.AssignmentError
require = ASSIGNMENT.require
sha256_file = ASSIGNMENT.sha256_file
assert_source_free = ASSIGNMENT.assert_source_free


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(BASE_BUILDER_PATH) == EXPECTED_WRAPPER_BASE_SHA256,
        "selector268 assignment base drift",
    )
    original_loads = ASSIGNMENT.json.loads

    def adapted_loads(value: str, *args: Any, **kwargs: Any) -> Any:
        result = original_loads(value, *args, **kwargs)
        if not isinstance(result, dict):
            return result
        if "direct_targets" in result:
            for row in result["direct_targets"]:
                if row.get("target_coordinate") == "0:268":
                    row["target_coordinate"] = "0:1198"
                    break
        recommendation = result.get("recommendation")
        if (
            isinstance(recommendation, dict)
            and recommendation.get("selector_coordinate") == "0:268"
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

    candidate, _current, _source, _contexts, pending = (
        ASSIGNMENT.RECORDS.load_records()
    )
    candidate_edges = RANKING.graph_edges(candidate)
    potential = set(private["scope"]["potential_current_pending_coordinates"])
    pending_roots = {
        RANKING.parse_root(":".join(coordinate.split(":")[:2]))
        for coordinate in potential
    }
    owned_relations = {
        (RANKING.root_string(root), selector)
        for root in pending_roots
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
        json.loads(line)
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
    terminal_coordinates = [
        f"0:{terminal}:0" for terminal in TERMINALS
    ]
    terminal_evidence = [
        pk_ledger[coordinate] for coordinate in terminal_coordinates
    ]
    require(
        len(terminal_evidence) == EXPECTED_TERMINAL_EVIDENCE
        and all(
            row.get("runtime_assembly_evidence")
            and row.get("runtime_review") == "pending"
            and row.get("scope_classification")
                == "runtime_fragment_pending"
            for row in terminal_evidence
        ),
        "terminal prior-evidence/pending-state drift",
    )

    same_gap_rows = [
        row for row in private["site_assignments"]
        if row["flags"]["multi_control_gap"]
    ]
    same_gap_roots = {
        RANKING.parse_root(str(row["root"])) for row in same_gap_rows
    }
    same_gap_neighbors = {
        (
            RANKING.root_string(root),
            int(edge["target"][1]),
        )
        for root in same_gap_roots
        for edge in candidate_edges[root]
        if edge["gap_id"]
            == RANKING.site_key(str(same_gap_rows[0]["site"]))[2]
        and tuple(edge["target"]) != (0, SELECTOR)
    }
    same_gap_pending = {
        coordinate
        for root in same_gap_roots
        for coordinate in pending.get(root, set())
    }
    require(
        (
            len(same_gap_rows),
            len(same_gap_roots),
            len(same_gap_neighbors),
            len(same_gap_pending),
        ) == EXPECTED_SAME_GAP_ATOM,
        "same-gap atom drift",
    )

    private["scope"]["selector_coordinate"] = "0:268:0"
    private["shared_terminal_ownership"] = {
        "chunk_ids": [],
        "group_count": 1,
        "owner": "assignment_scope",
        "terminal_coordinates": private["scope"]["terminal_coordinates"],
    }
    private["prior_pending_evidence"] = {
        "automatic_status_promotion_authorized": False,
        "potential_pending_assembly_coordinates": sorted(
            assembly_coordinates, key=RANKING.parse_coordinate
        ),
        "potential_pending_assembly_root_count": len(assembly_roots),
        "terminal_evidence_coordinates": terminal_coordinates,
        "terminal_evidence_count": len(terminal_evidence),
        "terminal_runtime_review": "pending",
    }
    private["completed_selector_overlap"] = {
        "pending_row_count": len(owned_pending),
        "relation_count": len(owned_relations),
        "relations": [
            {"root": root, "selector": selector}
            for root, selector in sorted(
                owned_relations,
                key=lambda row: (*RANKING.parse_root(row[0]), row[1]),
            )
        ],
        "root_count": len(owned_roots),
    }
    private["same_gap_control_atom"] = {
        "neighbor_relations": [
            {"root": root, "selector": selector}
            for root, selector in sorted(same_gap_neighbors)
        ],
        "pending_coordinates": sorted(
            same_gap_pending, key=RANKING.parse_coordinate
        ),
        "roots": [
            RANKING.root_string(root) for root in sorted(same_gap_roots)
        ],
        "sites": [str(row["site"]) for row in same_gap_rows],
    }
    site_to_chunk = {
        site: chunk["chunk_id"]
        for chunk in private["chunks"]
        for site in chunk["sites"]
    }
    require(
        len({site_to_chunk[str(row["site"])] for row in same_gap_rows}) == 1,
        "same-gap atom split",
    )
    for chunk in private["chunks"]:
        roots = set(chunk["roots"])
        chunk_owned = {
            relation for relation in owned_relations
            if relation[0] in roots
        }
        chunk_assembly = set(chunk["pending_coordinates"]) & assembly_coordinates
        chunk["completed_selector_overlap_relation_count"] = len(chunk_owned)
        chunk["prior_assembly_evidence_pending_row_count"] = len(
            chunk_assembly
        )
        chunk["same_gap_atom_count"] = sum(
            str(row["site"]) in set(chunk["sites"])
            for row in same_gap_rows
        )

    public["scope"]["official_pending_rows"] = 6246
    public["assignment"]["shared_terminal_group_count"] = 1
    public["assignment"]["shared_terminal_group_split"] = False
    public["assignment"]["same_gap_atom_count"] = len(same_gap_rows)
    public["assignment"]["same_gap_atom_split"] = False
    public["assignment"]["same_gap_neighbor_relation_count"] = len(
        same_gap_neighbors
    )
    public["coverage"]["source_only_action_count"] = 0
    public["coverage"]["completed_selector_overlap_relation_count"] = len(
        owned_relations
    )
    public["coverage"]["owned_overlap_pending_rows"] = len(owned_pending)
    public["coverage"]["prior_assembly_evidence_pending_root_count"] = len(
        assembly_roots
    )
    public["coverage"]["prior_assembly_evidence_pending_row_count"] = len(
        assembly_coordinates
    )
    public["coverage"]["terminal_prior_evidence_pending_count"] = len(
        terminal_evidence
    )
    private_chunks = {row["chunk_id"]: row for row in private["chunks"]}
    for chunk in public["assignment"]["chunks"]:
        private_chunk = private_chunks[chunk["chunk_id"]]
        for key in (
            "completed_selector_overlap_relation_count",
            "prior_assembly_evidence_pending_row_count",
            "same_gap_atom_count",
        ):
            chunk[key] = private_chunk[key]
    public["terminal_compatibility"] = {
        "automatic_status_promotion_authorized": False,
        "candidate_terminal_multiplicity_sorted": [1, 2, 4],
        "candidate_terminal_nonempty_count": 7,
        "context_terminal_nonempty_counts": {"en": 0, "sc": 0, "tc": 0},
        "context_terminals_authoritative": False,
        "dispatch_source_candidate_identical": True,
        "register_review_required": True,
    }
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
