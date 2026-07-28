#!/usr/bin/env python3
"""Build the immutable two-chunk PK selector-562 assignment."""

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
    / "build_pk_next_selector_family_ranking_post_selector466_consolidated_v1.py"
)
RANKING_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector466_consolidated.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector466_consolidated.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = DIALOGUE_TMP / "pk_selector562_assignment.private.v1.json"
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector562_assignment_coverage.v1.json"
)

SELECTOR = 562
TERMINALS = tuple(range(1944, 1951))
PRIVATE_SCHEMA = "nobu16.kr.pk-selector562-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector562-assignment-coverage.v1"
METHOD = (
    "selector466_checkpoint_selector562_root_disjoint_two_chunk_"
    "completed_owned_and_template_atomic_union_assignment"
)
EXPECTED_INPUT_SHA256 = {
    "ledger":
        "99450F568D8EDED40C7A7332F52DADA184EE6F11FB129CFDBCC758C7880DC197",
    "checkpoint_public":
        "D3824B5CF7A8DE02626FF06CE40816086F7DFB8EF6A0A9E06686756A9B69EA5E",
    "ranking_builder":
        "ACF1EE6BD84482678CA0C64E882C65BF33E1048FF9E4CAEDA6DE3CEA22727E63",
    "ranking_private":
        "65F3BE24C8889641B2BF5193418ECD4D39FF069D486C005F4E88C00388AD1661",
    "ranking_public":
        "B0F0ED90FB11ED00EAAC1608583DA23C5F2F04A54CDFF4DFA5F57EEC624A258B",
    "base_assignment":
        "AE1428FBF34BA042F1588E89DAA02623752D791BCD498687B9AD8595ED4BD7FF",
    "helper":
        "E39ED4738833FB56680E81E5B06A68F04472BABE7279D92CB608A40DB7D17CF5",
}
EXPECTED_BASE_BUILDER_SHA256 = (
    "698AAEB85B9036ABBD4171E41E533EC9A2EDDCF511D9755BF0DD1BF7E60CB0EB"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "E2283160520383E455C9C26112E80E5DB5EDB89161A9842FF3BD8F4C7FFCAD45"
)
EXPECTED_COVERAGE = (54, 54, 60, 6, 0, 25, 25, 38)
EXPECTED_SITE_ROW_SHA256: str | None = (
    "037D3E2F8A5C234302CA6162D3A252721087DF775094DED0D0EE21934BBBCA66"
)
EXPECTED_TEMPLATE_SIZES: tuple[int, ...] = (2, 2, 3, 4, 8)
EXPECTED_CHUNK_METRICS: tuple[tuple[int, ...], ...] | None = (
    (28, 28, 9, 13, 3, 589),
    (26, 26, 16, 25, 0, 592),
)
EXPECTED_COMPLETED_OVERLAP = (3, 3, 6)
EXPECTED_PRIOR_ASSEMBLY_EVIDENCE = (25, 36)
EXPECTED_ATOMIC_UNION = (22, 7, 10)
EXPECTED_TEMPLATE_PENDING = (4, 4)
EXPECTED_TERMINAL_EVIDENCE = 7
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "9F0DF230231732B1345B80FC6F159F9D18DAD56F87D707971193658C895B1067"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "42AC1603E4F599BC36BF9B58BB766390388660050650101EC22DF41C043EED3A"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSIGNMENT = load_module(BASE_BUILDER_PATH, "pk_selector562_assignment_base_v1")
RANKING_WRAPPER = load_module(RANKING_BUILDER_PATH, "pk_selector562_ranking_v1")
RANKING = RANKING_WRAPPER.RANKING
ENGINE = RANKING.ENGINE
RANKING.CONTROL_RE = RANKING.LEGACY.CONTROL_RE
ORIGINAL_TEMPLATE_ATOMS = ASSIGNMENT.BASE.template_atoms
ORIGINAL_JSON_LOADS = json.loads


def assignment_atoms(
    sites: Sequence[str],
    record_sets: Sequence[Any],
) -> list[set[tuple[int, int]]]:
    """Keep every repeated template and completed-owned root in one chunk."""
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
    owned_roots = {
        root
        for root in reachable_roots
        if any(
            (0, selector) in RANKING.reachable_call_targets(
                candidate_edges, root
            )
            for selector in RANKING_WRAPPER.OWNED_SELECTORS
        )
    }
    template_roots = set().union(*repeated) if repeated else set()
    return [template_roots | owned_roots]


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
        "selector562 assignment base drift",
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
            elif target == "0:562":
                row["target_coordinate"] = "0:1198"
        recommendation = result.get("recommendation")
        if (
            isinstance(recommendation, dict)
            and recommendation.get("selector_coordinate") == "0:562"
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

    candidate, current, source, contexts, pending = (
        ASSIGNMENT.RECORDS.load_records()
    )
    candidate_edges = RANKING.graph_edges(candidate)
    source_edges = RANKING.graph_edges(source)
    ranking_private = ORIGINAL_JSON_LOADS(
        RANKING_PRIVATE_PATH.read_text(encoding="utf-8")
    )
    target = next(
        row for row in ranking_private["direct_targets"]
        if row["target_coordinate"] == "0:562"
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

    record_sets = [
        candidate, current, source,
        contexts["en"], contexts["sc"], contexts["tc"],
    ]
    repeated_atoms = ORIGINAL_TEMPLATE_ATOMS(
        [str(row["site"]) for row in private["site_assignments"]],
        record_sets,
    )
    require(
        tuple(sorted(len(group) for group in repeated_atoms))
        == EXPECTED_TEMPLATE_SIZES,
        "repeated-template atom drift",
    )
    template_roots = set().union(*repeated_atoms)
    require(
        not template_roots & {
            RANKING.parse_root(root) for root in owned_roots
        },
        "template/completed-owned atom overlap drift",
    )
    template_pending = {
        coordinate
        for root in template_roots
        for coordinate in pending.get(root, set())
    }
    template_pending_roots = {
        root for root in template_roots if root in pending
    }
    require(
        (len(template_pending_roots), len(template_pending))
        == EXPECTED_TEMPLATE_PENDING,
        "template pending overlap drift",
    )
    atom_union = template_roots | {
        RANKING.parse_root(root) for root in owned_roots
    }
    atom_pending = {
        coordinate
        for root in atom_union
        for coordinate in pending.get(root, set())
    }
    atom_pending_roots = {root for root in atom_union if root in pending}
    require(
        (len(atom_union), len(atom_pending_roots), len(atom_pending))
        == EXPECTED_ATOMIC_UNION,
        "assignment atomic union drift",
    )
    root_to_chunk = {
        RANKING.parse_root(root): int(chunk["chunk_id"])
        for chunk in private["chunks"] for root in chunk["roots"]
    }
    require(
        len({root_to_chunk[root] for root in atom_union}) == 1,
        "assignment atomic union split",
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
    terminal_manifest = []
    for coordinate in closure_terminals:
        root = RANKING.parse_root(":".join(coordinate.split(":")[:2]))
        candidate_record = candidate[root]
        current_record = current[root]
        terminal_manifest.append({
            "candidate_current_identical":
                candidate_record.data == current_record.data,
            "coordinate": coordinate,
            "raw_record_sha256":
                ASSIGNMENT.sha256_bytes(candidate_record.data),
            "runtime_review": pk_ledger[coordinate]["runtime_review"],
        })
    require(
        closure_terminals == [f"0:{terminal}:0" for terminal in TERMINALS]
        and len(terminal_evidence) == EXPECTED_TERMINAL_EVIDENCE
        and all(
            row.get("runtime_assembly_evidence")
            and row.get("runtime_review") == "verified"
            for row in terminal_evidence
        )
        and all(row["candidate_current_identical"] for row in terminal_manifest),
        "terminal closure/read-only/current identity drift",
    )
    terminal_values = [
        ENGINE.parse_record_literals(candidate[(0, terminal)])[0].text
        for terminal in TERMINALS
    ]
    require(
        sorted(
            __import__("collections").Counter(terminal_values).values()
        ) == [1, 2, 2, 2],
        "terminal register multiplicity drift",
    )
    empty_terminal_digest = ASSIGNMENT.sha256_bytes(
        "\0".join("" for _ in TERMINALS).encode("utf-8")
    )
    require(
        all(
            ASSIGNMENT.sha256_bytes(
                "\0".join(
                    ENGINE.parse_record_literals(
                        contexts[language][(0, terminal)]
                    )[0].text
                    for terminal in TERMINALS
                ).encode("utf-8")
            ) == empty_terminal_digest
            for language in ("en", "sc", "tc")
        ),
        "context terminals unexpectedly authoritative",
    )

    source_sites = set(
        RANKING.candidate_call_sites(source_edges)[(0, SELECTOR)]
    )
    candidate_sites = set(private["scope"]["candidate_call_sites"])
    source_only = source_sites - candidate_sites
    require(
        len(source_only) == 6 and not (candidate_sites - source_sites),
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
    require(
        not any(
            row["flags"]["multi_control_gap"]
            for row in private["site_assignments"]
        ),
        "same-gap candidate site drift",
    )

    private["schema"] = PRIVATE_SCHEMA
    private["method"] = METHOD
    private["scope"]["selector_coordinate"] = "0:562:0"
    private["identical_template_atoms"] = [
        [RANKING.root_string(root) for root in sorted(group)]
        for group in repeated_atoms
    ]
    private["assignment_atom_union"] = {
        "pending_coordinates": sorted(
            atom_pending, key=RANKING.parse_coordinate
        ),
        "roots": [
            RANKING.root_string(root) for root in sorted(atom_union)
        ],
    }
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
    private["source_only_repair"] = {
        "action_count": 0,
        "sites": sorted(source_only, key=RANKING.site_key),
    }
    for chunk in private["chunks"]:
        roots = set(chunk["roots"])
        parsed_roots = {RANKING.parse_root(root) for root in roots}
        chunk["assignment_atom_union_root_count"] = len(
            parsed_roots & atom_union
        )
        chunk["completed_selector_overlap_relation_count"] = sum(
            root in roots for root, _selector in owned_relations
        )
        chunk["prior_assembly_evidence_pending_row_count"] = len(
            set(chunk["pending_coordinates"]) & assembly_coordinates
        )
        chunk["prior_assembly_evidence_root_count"] = len(
            roots & assembly_roots
        )
        chunk["template_atom_root_count"] = len(
            parsed_roots & template_roots
        )
        chunk["template_root_count"] = len(parsed_roots & template_roots)
        chunk["template_root_sha256"] = ASSIGNMENT.root_digest(
            parsed_roots & template_roots
        )

    public["schema"] = PUBLIC_SCHEMA
    public["method"] = METHOD
    public["scope"]["selector"] = SELECTOR
    public["scope"]["official_pending_rows"] = 6191
    public["assignment"].update({
        "assignment_atom_union_pending_rows": len(atom_pending),
        "assignment_atom_union_root_count": len(atom_union),
        "assignment_atom_union_split": False,
        "identical_template_atom_count": len(repeated_atoms),
        "identical_template_root_count": len(template_roots),
        "same_gap_atom_count": 0,
        "same_gap_atom_split": False,
        "shared_terminal_group_count": 1,
        "shared_terminal_group_split": False,
        "terminal_manifest_sha256":
            ASSIGNMENT.canonical_sha256(terminal_manifest),
    })
    public["coverage"].update({
        "candidate_non_display_root_count": 0,
        "completed_selector_overlap_relation_count": len(owned_relations),
        "direct_pending_non_display_root_count": 0,
        "owned_overlap_pending_rows": len(owned_pending),
        "prior_assembly_evidence_pending_root_count": len(assembly_roots),
        "prior_assembly_evidence_pending_row_count": len(assembly_coordinates),
        "source_only_action_count": 0,
        "source_only_repair_site_sha256": ASSIGNMENT.site_digest(source_only),
        "template_pending_root_count": len(template_pending_roots),
        "template_pending_row_count": len(template_pending),
        "terminal_prior_evidence_pending_count": len(terminal_evidence),
    })
    public["terminal_compatibility"] = {
        "automatic_status_promotion_authorized": False,
        "candidate_current_identical": True,
        "context_terminal_nonempty_counts": {"en": 0, "sc": 0, "tc": 0},
        "context_terminals_authoritative": False,
        "ordered_register_counts": {
            "archaic": 1,
            "high_formal": 2,
            "plain": 2,
            "polite": 2,
        },
        "read_only_verified_terminal_count": 7,
    }
    private_chunks = {row["chunk_id"]: row for row in private["chunks"]}
    for chunk in public["assignment"]["chunks"]:
        private_chunk = private_chunks[chunk["chunk_id"]]
        for key in (
            "assignment_atom_union_root_count",
            "completed_selector_overlap_relation_count",
            "prior_assembly_evidence_pending_row_count",
            "prior_assembly_evidence_root_count",
            "template_atom_root_count",
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
