#!/usr/bin/env python3
"""Build the root-disjoint two-chunk assignment for PK selector 226."""

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
    / "build_pk_next_selector_family_ranking_post_selector1168_consolidated_v1.py"
)
RANKING_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector1168_consolidated.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector1168_consolidated.source_free.v1.json"
)
THOUGHT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_thought_predicate_family_exact_closure_v1.py"
)
THOUGHT_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_thought_predicate_family_exact_closure_evidence.private.v1.jsonl"
)
DEFAULT_PRIVATE_OUTPUT = DIALOGUE_TMP / "pk_selector226_assignment.private.v1.json"
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector226_assignment_coverage.v1.json"
)

SELECTOR = 226
TERMINALS = tuple(range(1538, 1545))
PRIVATE_SCHEMA = "nobu16.kr.pk-selector226-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector226-assignment-coverage.v1"
METHOD = (
    "selector1168_checkpoint_selector226_root_disjoint_two_chunk_"
    "template_atom_and_prior_caller_evidence_assignment"
)
EXPECTED_INPUT_SHA256 = {
    "ledger":
        "56FBAF8FB54CCFA7EAF10355F66FE6A730374804F48FB4CD9F8F15A99AEE9A91",
    "checkpoint_public":
        "9A04C999B850A1024BBB9AE57F509CA1C879A5DC4D59BF717873FD17E609545F",
    "ranking_builder":
        "9BE21F732628EB30ABA43D7BB8DAD1E14F25D9E7F011DBE680093CA7E25D4EC5",
    "ranking_private":
        "F0AC863B20850BD149344E2524A373C051325FE5BF4D0E010CD59F65CFB907F2",
    "ranking_public":
        "FD4A36F6F150FC4EAB929924CB1D5B0092923607D8418BE1D0B4E36154FAB836",
    "base_assignment":
        "AE1428FBF34BA042F1588E89DAA02623752D791BCD498687B9AD8595ED4BD7FF",
    "helper":
        "E39ED4738833FB56680E81E5B06A68F04472BABE7279D92CB608A40DB7D17CF5",
}
EXPECTED_WRAPPER_BASE_SHA256 = (
    "698AAEB85B9036ABBD4171E41E533EC9A2EDDCF511D9755BF0DD1BF7E60CB0EB"
)
EXPECTED_THOUGHT_BUILDER_SHA256 = (
    "D7801EE34E0FF39255E679C75D9E6EBD7A9FC4B9421818BC88B1CA3A18624868"
)
EXPECTED_THOUGHT_EVIDENCE_SHA256 = (
    "76722DBB632D9CBB78C5BE089C18BDA8AD66C79C8A302B79DBE7DA9C03F32399"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "EF84A8B8A18C1F2F1F72D3A650C01DC7B058F32A3536C130809C4FCB31C837C7"
)
EXPECTED_COVERAGE = (70, 70, 75, 5, 0, 33, 33, 46)
EXPECTED_SITE_ROW_SHA256: str | None = (
    "B4C257880F99C979E968A47D5EBD17BC3FD2D7A2F5F9C4FE43170A67B32D9715"
)
EXPECTED_TEMPLATE_SIZES: tuple[int, ...] | None = (2, 3, 5)
EXPECTED_CHUNK_METRICS: tuple[tuple[int, ...], ...] | None = (
    (35, 35, 15, 20, 4, 527),
    (35, 35, 18, 26, 5, 526),
)
EXPECTED_EVIDENCE_OVERLAP = (33, 33)
EXPECTED_OWNED_OVERLAP = (9, 10)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "223EBD7D1C0C0D6E78DCD97D0189C1E5099DBB917DD2498CC659BEDEBFAEE050"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "BFD1F9D8A813C2ADA7D8C065B4F7C1963F8704A7538C306C9EF6DE203F414215"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSIGNMENT = load_module(BASE_BUILDER_PATH, "pk_selector226_assignment_base_v1")
RANKING_WRAPPER = load_module(RANKING_BUILDER_PATH, "pk_selector226_ranking_v1")
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


def prior_evidence_coordinates() -> set[str]:
    rows = [
        json.loads(line)
        for line in THOUGHT_EVIDENCE_PATH.read_text(encoding="utf-8").splitlines()
        if line
    ]
    return {
        str(row["coordinate"])
        for row in rows
        if row.get("resource") == "pk_msggame"
    }


def prior_evidence_template_atoms(
    sites: Sequence[str],
    _record_sets: Sequence[Any],
) -> list[set[tuple[int, int]]]:
    """Keep repeated reviewed caller literals as indivisible assignment units."""
    site_roots = {RANKING.site_key(site)[:2] for site in sites}
    by_literal: dict[str, set[tuple[int, int]]] = {}
    for line in THOUGHT_EVIDENCE_PATH.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        coordinate = str(row.get("coordinate", ""))
        parts = coordinate.split(":")
        if len(parts) != 3 or row.get("resource") != "pk_msggame":
            continue
        root = (int(parts[0]), int(parts[1]))
        if root not in site_roots:
            continue
        digest = str(row["candidate_literal_utf16le_sha256"])
        by_literal.setdefault(digest, set()).add(root)
    result = [roots for roots in by_literal.values() if len(roots) >= 2]
    result.sort(key=lambda roots: (-len(roots), ASSIGNMENT.root_digest(roots)))
    return result


ASSIGNMENT.template_atoms = prior_evidence_template_atoms


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(BASE_BUILDER_PATH) == EXPECTED_WRAPPER_BASE_SHA256,
        "selector226 assignment base drift",
    )
    require(
        sha256_file(THOUGHT_BUILDER_PATH) == EXPECTED_THOUGHT_BUILDER_SHA256,
        "thought-predicate builder drift",
    )
    require(
        sha256_file(THOUGHT_EVIDENCE_PATH) == EXPECTED_THOUGHT_EVIDENCE_SHA256,
        "thought-predicate evidence drift",
    )
    original_loads = ASSIGNMENT.json.loads

    def adapted_loads(value: str, *args: Any, **kwargs: Any) -> Any:
        result = original_loads(value, *args, **kwargs)
        if not isinstance(result, dict):
            return result
        if "direct_targets" in result:
            for row in result["direct_targets"]:
                if row.get("target_coordinate") == "0:226":
                    row["target_coordinate"] = "0:1198"
                    break
        recommendation = result.get("recommendation")
        if (
            isinstance(recommendation, dict)
            and recommendation.get("selector_coordinate") == "0:226"
        ):
            recommendation["selector_coordinate"] = "0:1198"
        return result

    ASSIGNMENT.json.loads = adapted_loads
    try:
        _private_content, _public_content, private, public = (
            ASSIGNMENT.build_outputs()
        )
    finally:
        ASSIGNMENT.json.loads = original_loads

    evidence = prior_evidence_coordinates()
    evidence_roots = {
        ":".join(coordinate.split(":")[:2]) for coordinate in evidence
    }
    pending_roots = {
        ":".join(coordinate.split(":")[:2])
        for coordinate in private["scope"]["potential_current_pending_coordinates"]
    }
    overlap_roots = pending_roots & evidence_roots
    overlap_relations = {
        coordinate
        for coordinate in evidence
        if ":".join(coordinate.split(":")[:2]) in pending_roots
    }
    require(
        (len(overlap_roots), len(overlap_relations))
        == EXPECTED_EVIDENCE_OVERLAP,
        "prior caller evidence overlap drift",
    )

    candidate, _current, _source, _contexts, _pending = (
        ASSIGNMENT.RECORDS.load_records()
    )
    candidate_edges = RANKING.graph_edges(candidate)
    reachable_roots = {RANKING.parse_root(root) for root in pending_roots}
    owned_relations = {
        (RANKING.root_string(root), selector)
        for root in reachable_roots
        for selector in RANKING_WRAPPER.OWNED_SELECTORS
        if (0, selector) in RANKING.reachable_call_targets(
            candidate_edges, root
        )
    }
    owned_roots = {root for root, _selector in owned_relations}
    require(
        (len(owned_roots), len(owned_relations)) == EXPECTED_OWNED_OVERLAP,
        "completed-selector relation overlap drift",
    )

    private["scope"]["selector_coordinate"] = "0:226:0"
    private["shared_terminal_ownership"] = {
        "chunk_ids": [],
        "group_count": 1,
        "owner": "assignment_scope",
        "terminal_coordinates": private["scope"]["terminal_coordinates"],
    }
    private["prior_caller_evidence_overlap"] = {
        "builder_sha256": EXPECTED_THOUGHT_BUILDER_SHA256,
        "evidence_sha256": EXPECTED_THOUGHT_EVIDENCE_SHA256,
        "relation_coordinates": sorted(
            overlap_relations, key=RANKING.parse_coordinate
        ),
        "relation_count": len(overlap_relations),
        "root_count": len(overlap_roots),
        "root_sha256": ASSIGNMENT.root_digest(
            RANKING.parse_root(root) for root in overlap_roots
        ),
    }
    private["completed_selector_overlap"] = {
        "relation_count": len(owned_relations),
        "relations": [
            {"root": root, "selector": selector}
            for root, selector in sorted(
                owned_relations,
                key=lambda row: (*RANKING.parse_root(row[0]), row[1]),
            )
        ],
        "root_count": len(owned_roots),
        "root_sha256": ASSIGNMENT.root_digest(
            RANKING.parse_root(root) for root in owned_roots
        ),
    }

    for chunk in private["chunks"]:
        roots = set(chunk["roots"])
        chunk_evidence = roots & overlap_roots
        chunk_owned = {
            relation for relation in owned_relations if relation[0] in roots
        }
        chunk["prior_caller_evidence_overlap_root_count"] = len(chunk_evidence)
        chunk["prior_caller_evidence_overlap_root_sha256"] = (
            ASSIGNMENT.root_digest(
                RANKING.parse_root(root) for root in chunk_evidence
            )
        )
        chunk["completed_selector_overlap_relation_count"] = len(chunk_owned)

    public["scope"]["official_pending_rows"] = 6283
    public["assignment"]["shared_terminal_group_count"] = 1
    public["assignment"]["shared_terminal_group_split"] = False
    public["coverage"]["source_only_action_count"] = 0
    public["coverage"]["prior_caller_evidence_overlap_root_count"] = len(
        overlap_roots
    )
    public["coverage"]["prior_caller_evidence_overlap_relation_count"] = len(
        overlap_relations
    )
    public["coverage"]["completed_selector_overlap_relation_count"] = len(
        owned_relations
    )
    public["coverage"]["owned_overlap_root_count"] = len(owned_roots)
    private_chunks = {row["chunk_id"]: row for row in private["chunks"]}
    for chunk in public["assignment"]["chunks"]:
        private_chunk = private_chunks[chunk["chunk_id"]]
        chunk["prior_caller_evidence_overlap_root_count"] = private_chunk[
            "prior_caller_evidence_overlap_root_count"
        ]
        chunk["prior_caller_evidence_overlap_root_sha256"] = private_chunk[
            "prior_caller_evidence_overlap_root_sha256"
        ]
        chunk["completed_selector_overlap_relation_count"] = private_chunk[
            "completed_selector_overlap_relation_count"
        ]
    public["terminal_compatibility"] = {
        "caller_complete_form_review_required": True,
        "dispatch_source_candidate_identical": True,
        "terminal_registers_frozen": True,
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
    return (
        private_content,
        ASSIGNMENT.serialized_json(public),
        private,
        public,
    )


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
                row["prior_caller_evidence_overlap_root_count"],
                row["completed_selector_overlap_relation_count"],
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
