#!/usr/bin/env python3
"""Build the shared selector-730 same-gap Cartesian assembly manifest."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
PUBLIC_DIR = WORKSTREAM / "public"

RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_selector562_consolidated_v1.py"
)
RANKING_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector562_consolidated.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    PUBLIC_DIR
    / "pk_next_selector_family_ranking."
    "post_selector562_consolidated.source_free.v1.json"
)
ASSIGNMENT_HELPER_PATH = WORKSTREAM / "build_pk_selector562_assignment_v1.py"
OPTIONAL_ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector730_assignment.private.v1.json"
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector730_assignment_v1.py"
ASSIGNMENT_PUBLIC_PATH = (
    PUBLIC_DIR / "pk_selector730_assignment_coverage.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_selector730_shared_cartesian_assembly_manifest.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    PUBLIC_DIR / "pk_selector730_shared_cartesian_assembly_coverage.v1.json"
)

SELECTOR = 730
TERMINALS = tuple(range(2140, 2147))
PRIVATE_SCHEMA = "nobu16.kr.pk-selector730-shared-cartesian-manifest.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector730-shared-cartesian-coverage.v1"
METHOD = (
    "post_selector562_selector730_ordered_two_control_seven_by_seven_"
    "shared_cartesian_assembly_manifest"
)

EXPECTED_INPUT_SHA256 = {
    "ranking_builder":
        "09FD073859C3D75B2C4343D722A0498B6B20B0B8C5AD289A95C657CF052C92B8",
    "ranking_private":
        "1A8479D8CE3EEFE52E853B1B8F1AE0D194FF63D9E7CB1C27D4B0936D32041056",
    "ranking_public":
        "85E6DED228DF9771A973BE907C0B1973D15E5EFF59BDADEE4C64BED6B84CDA66",
    "assignment_helper":
        "FEBE7891BE6CA37EF8C2708F7E73F3F8647E2A1BCD55B85CD00F87FEF08F7395",
    "official_ledger":
        "8E31995689359D5F8DD1F23FC7A894C07AC8BBB3C08EF2B87651E6E3E8B1086A",
    "checkpoint_public":
        "5445CD4A9C9515A8732446DA397D0FF0BB66E657A17C14BEDC374CCC745CDF76",
    "selector730_assignment_builder":
        "94E9846279014E431832E232509B1C495BEE3D9EFEF01B8D8EBAB687D0968AA8",
    "selector730_assignment_private":
        "D9554CC8E6BED91EB9141CFC11F142E389868565AFC7B82B230FC9F931DB4781",
    "selector730_assignment_public":
        "07EA6FE891F17C7E4CF22C6C42625D1E224FF606524A2683ED0CA58C767CD454",
}
EXPECTED_PK_CANDIDATE_SHA256 = (
    "B7CBFA388BDD50F60CD5EEF88A63B62D357475925A0A3AA6D7DCA1A191607815"
)
EXPECTED_CANDIDATE_SITES = 41
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "97C3B98B672FF969B99680AB35AA80D77A82726196BC53C1C02BD1813BC3C877"
)
EXPECTED_SOURCE_SITES = 46
EXPECTED_SOURCE_SITE_SHA256 = (
    "A859360269D58C7B7FF77E44BB33AF739BBBE59E2E2592981598C1AB62ED8481"
)
EXPECTED_SOURCE_ONLY_SITES = 5
EXPECTED_SOURCE_ONLY_SHA256 = (
    "AFF05F3C748B8B3A4044013477DAEC82615EAAC0CBF4526450BA0F38B3D0A586"
)
EXPECTED_SAME_GAP_SITES = 37
EXPECTED_SAME_GAP_ROOTS = 37
EXPECTED_PENDING_SAME_GAP_ROOTS = 17
EXPECTED_PENDING_SAME_GAP_ROWS = 34
EXPECTED_SIBLING_FAMILIES = 17
EXPECTED_CONTROLS_PER_GAP = 2
EXPECTED_BRANCHES_PER_ROOT = 49
EXPECTED_CARTESIAN_BRANCHES = 1_813
EXPECTED_SELECTOR_TERMINAL_CANDIDATE_SHA256 = (
    "B5B654EB01F84F558645B732B7E7A11DCA0B770887050E718B301A30AD78E6A5"
)
EXPECTED_SELECTOR_TERMINAL_CURRENT_SHA256 = (
    "0601646BF63BA7CED310F7913DCC3BFFDDE26F9124FB459B99C8604F8147D07F"
)
EXPECTED_SELECTOR_TERMINAL_SOURCE_SHA256 = (
    "BE3648C0B9ABD158FB4ADFCACECF53AE3B340174A818EC580B953D3121AA088B"
)
EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_PRIVATE_OUTPUT_SHA256 = (
    "BB00FFACC84CE778AFCEFB5E531B23BDA8BB03CFEE06E42DC885BC164314C173"
)
EXPECTED_PUBLIC_OUTPUT_SHA256 = (
    "F9F2F82231DD417F397EE05B23C4AFF7FB60056865ABF22B87B99CCFD58A4DE1"
)


class CartesianManifestError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CartesianManifestError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RANKING_WRAPPER = load_module(
    RANKING_BUILDER_PATH, "pk_selector730_cartesian_ranking_v1"
)
ASSIGNMENT_WRAPPER = load_module(
    ASSIGNMENT_HELPER_PATH, "pk_selector730_cartesian_assignment_helpers_v1"
)
ASSIGNMENT = ASSIGNMENT_WRAPPER.ASSIGNMENT
RANKING = RANKING_WRAPPER.RANKING
ENGINE = RANKING.ENGINE
RANKING.CONTROL_RE = RANKING.LEGACY.CONTROL_RE


def configure_record_loader() -> None:
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


configure_record_loader()


def sha256_bytes(value: bytes) -> str:
    return ASSIGNMENT.BASE.sha256_bytes(value)


def sha256_file(path: Path) -> str:
    return ASSIGNMENT.BASE.sha256_file(path)


def canonical_sha256(value: Any) -> str:
    return ASSIGNMENT.BASE.canonical_sha256(value)


def serialized_json(value: Any) -> bytes:
    return ASSIGNMENT.BASE.serialized_json(value).encode("utf-8")


def root_string(root: tuple[int, int]) -> str:
    return RANKING.root_string(root)


def first_literal(
    records: Mapping[tuple[int, int], Any], root: tuple[int, int]
) -> str:
    literals = ENGINE.parse_record_literals(records[root])
    require(len(literals) == 1, f"terminal literal shape drifted: {root}")
    return literals[0].text


def terminal_digest(
    records: Mapping[tuple[int, int], Any],
    terminal_roots: Sequence[tuple[int, int]],
) -> str:
    return sha256_bytes(
        "\0".join(first_literal(records, root) for root in terminal_roots)
        .encode("utf-8")
    )


def terminal_family(
    candidate: Mapping[tuple[int, int], Any],
    current: Mapping[tuple[int, int], Any],
    source: Mapping[tuple[int, int], Any],
    candidate_edges: Mapping[tuple[int, int], list[dict[str, Any]]],
    source_edges: Mapping[tuple[int, int], list[dict[str, Any]]],
    selector: int,
) -> dict[str, Any]:
    shape = RANKING.family_shape(
        candidate_edges, source_edges, (0, selector)
    )
    require(
        shape["seven_way"]
        and shape["source_candidate_identical"]
        and len(shape["candidate_leaves"]) == 7,
        f"sibling selector family drifted: {selector}",
    )
    roots = tuple(sorted(tuple(root) for root in shape["candidate_leaves"]))
    body = {
        "selector": selector,
        "terminal_roots": [root_string(root) for root in roots],
        "terminal_root_sha256": ASSIGNMENT.BASE.root_digest(roots),
        "candidate_terminal_sha256": terminal_digest(candidate, roots),
        "current_terminal_sha256": terminal_digest(current, roots),
        "source_terminal_sha256": terminal_digest(source, roots),
        "source_candidate_dispatch_identical": True,
        "terminal_count": 7,
        "read_only": True,
    }
    body["family_identifier_sha256"] = canonical_sha256(body)
    return body


def assemble(
    records: Mapping[tuple[int, int], Any],
    root: tuple[int, int],
    gap_id: int,
    ordered_controls: Sequence[Mapping[str, Any]],
    ordinals: Mapping[int, int],
    families: Mapping[int, Mapping[str, Any]],
) -> str:
    literals = ENGINE.parse_record_literals(records[root])
    require(0 < gap_id <= len(literals), f"invalid assembly gap: {root}")
    result = literals[gap_id - 1].text
    for control in ordered_controls:
        selector = int(control["selector"])
        ordinal = int(ordinals[selector])
        terminal = RANKING.parse_root(
            str(families[selector]["terminal_roots"][ordinal])
        )
        result += first_literal(records, terminal)
    if gap_id < len(literals):
        result += literals[gap_id].text
    return result


def line_widths(value: str) -> list[int]:
    return [
        int(width)
        for width in ASSIGNMENT.HELPER.LEGACY.line_widths(value)
    ]


def validate_assignment_partition(
    assignment: Mapping[str, Any],
    candidate_sites: Sequence[str],
    same_gap_roots: set[str],
) -> dict[str, Any]:
    chunks = list(assignment.get("chunks", []))
    require(chunks, "selector730 assignment has no chunks")
    expected_sites = set(candidate_sites)
    observed_sites: list[str] = []
    root_owners: dict[str, int] = {}
    for chunk in chunks:
        chunk_id = int(chunk["chunk_id"])
        roots = {str(root) for root in chunk["roots"]}
        sites = [str(site) for site in chunk["sites"]]
        observed_sites.extend(sites)
        for root in roots:
            require(root not in root_owners, f"assignment root split: {root}")
            root_owners[root] = chunk_id
        require(
            all(":".join(site.split(":")[:2]) in roots for site in sites),
            f"assignment site/root mismatch in chunk {chunk_id}",
        )
    require(
        len(observed_sites) == len(set(observed_sites))
        and set(observed_sites) == expected_sites,
        "assignment candidate-site partition drifted",
    )
    require(
        same_gap_roots <= set(root_owners),
        "same-gap root absent from assignment",
    )
    mapping = [
        {"chunk_id": root_owners[root], "root": root}
        for root in sorted(
            same_gap_roots, key=RANKING.parse_root
        )
    ]
    return {
        "assignment_chunk_count": len(chunks),
        "candidate_sites_partitioned": len(observed_sites),
        "root_split_count": 0,
        "same_gap_roots_partitioned": len(mapping),
        "same_gap_root_to_chunk_sha256": canonical_sha256(mapping),
        "status": "validated",
    }


def assignment_partition(
    candidate_sites: Sequence[str],
    same_gap_roots: set[str],
) -> dict[str, Any]:
    if not OPTIONAL_ASSIGNMENT_PATH.is_file():
        return {
            "assignment_chunk_count": 0,
            "candidate_sites_partitioned": 0,
            "root_split_count": 0,
            "same_gap_roots_partitioned": 0,
            "same_gap_root_to_chunk_sha256": None,
            "status": "pending_assignment",
        }
    assignment = json.loads(
        OPTIONAL_ASSIGNMENT_PATH.read_text(encoding="utf-8")
    )
    result = validate_assignment_partition(
        assignment, candidate_sites, same_gap_roots
    )
    result["assignment_private_sha256"] = sha256_file(
        OPTIONAL_ASSIGNMENT_PATH
    )
    return result


def assert_source_free(value: Any, path: str = "$") -> None:
    cjk = re.compile(
        r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
        r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
    )
    if isinstance(value, dict):
        for key, item in value.items():
            assert_source_free(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            assert_source_free(item, f"{path}[{index}]")
    elif isinstance(value, str):
        require(cjk.search(value) is None, f"CJK leaked at {path}")


def validate_inputs() -> None:
    paths = {
        "ranking_builder": RANKING_BUILDER_PATH,
        "ranking_private": RANKING_PRIVATE_PATH,
        "ranking_public": RANKING_PUBLIC_PATH,
        "assignment_helper": ASSIGNMENT_HELPER_PATH,
        "official_ledger": RANKING_WRAPPER.DEFAULT_LEDGER,
        "checkpoint_public": RANKING_WRAPPER.CHECKPOINT_PUBLIC,
        "selector730_assignment_builder": ASSIGNMENT_BUILDER_PATH,
        "selector730_assignment_private": OPTIONAL_ASSIGNMENT_PATH,
        "selector730_assignment_public": ASSIGNMENT_PUBLIC_PATH,
    }
    for name, path in paths.items():
        require(
            path.is_file()
            and sha256_file(path) == EXPECTED_INPUT_SHA256[name],
            f"input drifted: {name}",
        )


def build_outputs() -> tuple[bytes, bytes, dict[str, Any], dict[str, Any]]:
    validate_inputs()
    ranking = json.loads(RANKING_PRIVATE_PATH.read_text(encoding="utf-8"))
    target = next(
        row
        for row in ranking["direct_targets"]
        if row["target_coordinate"] == f"0:{SELECTOR}"
    )
    candidate_sites = list(target["candidate_call_sites"])
    source_sites = list(target["source_call_sites"])
    source_only = set(source_sites) - set(candidate_sites)
    require(
        len(candidate_sites) == EXPECTED_CANDIDATE_SITES
        and target["candidate_call_site_sha256"]
            == EXPECTED_CANDIDATE_SITE_SHA256
        and len(source_sites) == EXPECTED_SOURCE_SITES
        and target["source_call_site_sha256"] == EXPECTED_SOURCE_SITE_SHA256
        and len(source_only) == EXPECTED_SOURCE_ONLY_SITES
        and ASSIGNMENT.BASE.site_digest(source_only)
            == EXPECTED_SOURCE_ONLY_SHA256,
        "selector730 ranking scope drifted",
    )

    candidate, current, source, contexts, pending = (
        ASSIGNMENT.RECORDS.load_records()
    )
    candidate_edges = RANKING.graph_edges(candidate)
    source_edges = RANKING.graph_edges(source)
    same_gap_rows: list[dict[str, Any]] = []
    same_gap_roots: set[str] = set()
    sibling_selectors: set[int] = set()
    family_cache: dict[int, dict[str, Any]] = {}

    for site in candidate_sites:
        block_id, record_id, gap_id, site_offset = RANKING.site_key(site)
        root = (block_id, record_id)
        siblings = sorted(
            (
                edge
                for edge in candidate_edges[root]
                if int(edge["gap_id"]) == gap_id
            ),
            key=lambda row: int(row["offset"]),
        )
        if len(siblings) == 1:
            continue
        require(
            len(siblings) == EXPECTED_CONTROLS_PER_GAP
            and sum(tuple(row["target"]) == (0, SELECTOR) for row in siblings)
            == 1,
            f"same-gap control shape drifted: {site}",
        )
        sibling_selector = next(
            int(row["target"][1])
            for row in siblings
            if tuple(row["target"]) != (0, SELECTOR)
        )
        sibling_selectors.add(sibling_selector)
        for selector in (SELECTOR, sibling_selector):
            if selector not in family_cache:
                family_cache[selector] = terminal_family(
                    candidate,
                    current,
                    source,
                    candidate_edges,
                    source_edges,
                    selector,
                )
        ordered_controls = [
            {
                "family_identifier_sha256":
                    family_cache[int(row["target"][1])][
                        "family_identifier_sha256"
                    ],
                "offset": int(row["offset"]),
                "selector": int(row["target"][1]),
            }
            for row in siblings
        ]
        literals = ENGINE.parse_record_literals(candidate[root])
        current_literals = ENGINE.parse_record_literals(current[root])
        left = literals[gap_id - 1].text
        right = literals[gap_id].text if gap_id < len(literals) else ""
        current_left = current_literals[gap_id - 1].text
        current_right = (
            current_literals[gap_id].text
            if gap_id < len(current_literals)
            else ""
        )
        branches = []
        positive_expansion_count = 0
        linebreak_change_count = 0
        maximum_positive_delta = 0
        for selector_ordinal in range(7):
            for sibling_ordinal in range(7):
                ordinals = {
                    SELECTOR: selector_ordinal,
                    sibling_selector: sibling_ordinal,
                }
                candidate_value = assemble(
                    candidate,
                    root,
                    gap_id,
                    ordered_controls,
                    ordinals,
                    family_cache,
                )
                current_value = assemble(
                    current,
                    root,
                    gap_id,
                    ordered_controls,
                    ordinals,
                    family_cache,
                )
                source_value = assemble(
                    source,
                    root,
                    gap_id,
                    ordered_controls,
                    ordinals,
                    family_cache,
                )
                candidate_widths = line_widths(candidate_value)
                current_widths = line_widths(current_value)
                deltas = [
                    left_width - right_width
                    for left_width, right_width in zip(
                        candidate_widths, current_widths
                    )
                ]
                maximum_delta = max(deltas, default=0)
                positive_expansion = (
                    len(candidate_widths) != len(current_widths)
                    or maximum_delta > 0
                )
                linebreak_changed = (
                    candidate_value.count("\n")
                    != current_value.count("\n")
                )
                positive_expansion_count += int(positive_expansion)
                linebreak_change_count += int(linebreak_changed)
                maximum_positive_delta = max(
                    maximum_positive_delta, maximum_delta
                )
                selected_terminals = []
                for control in ordered_controls:
                    selector = int(control["selector"])
                    selected_terminals.append(
                        family_cache[selector]["terminal_roots"][
                            ordinals[selector]
                        ]
                    )
                branches.append({
                    "assembled_candidate_sha256": sha256_bytes(
                        candidate_value.encode("utf-8")
                    ),
                    "assembled_current_sha256": sha256_bytes(
                        current_value.encode("utf-8")
                    ),
                    "assembled_source_sha256": sha256_bytes(
                        source_value.encode("utf-8")
                    ),
                    "candidate_line_widths_raw_g1n_px": candidate_widths,
                    "current_line_widths_raw_g1n_px": current_widths,
                    "grammar_risk": {
                        "automatic_space_inserted": False,
                        "linebreak_count_changed": linebreak_changed,
                        "positive_raw_width_expansion": positive_expansion,
                        "right_boundary_present": bool(right),
                    },
                    "maximum_positive_raw_g1n_delta_px": maximum_delta,
                    "ordered_selected_terminal_roots": selected_terminals,
                    "selector730_ordinal": selector_ordinal,
                    "sibling_ordinal": sibling_ordinal,
                })
        root_text_hashes = {
            "candidate_left_sha256": sha256_bytes(left.encode("utf-8")),
            "candidate_right_sha256": sha256_bytes(right.encode("utf-8")),
            "current_left_sha256": sha256_bytes(
                current_left.encode("utf-8")
            ),
            "current_right_sha256": sha256_bytes(
                current_right.encode("utf-8")
            ),
        }
        same_gap_rows.append({
            "branch_count": len(branches),
            "branches": branches,
            "control_count": len(ordered_controls),
            "gap_id": gap_id,
            "grammar_risk": {
                "linebreak_change_branch_count": linebreak_change_count,
                "maximum_positive_raw_g1n_delta_px":
                    maximum_positive_delta,
                "outer_space_protected": (
                    left.endswith(" ") or right.startswith(" ")
                ),
                "positive_expansion_branch_count":
                    positive_expansion_count,
                "right_boundary_present": bool(right),
            },
            "ordered_controls": ordered_controls,
            "root": root_string(root),
            "site": site,
            "site_offset": site_offset,
            "text_boundary_sha256": canonical_sha256(root_text_hashes),
        })
        same_gap_roots.add(root_string(root))

    pending_roots = {
        RANKING.parse_root(root)
        for root in target["reachable_pending_roots"]
    }
    pending_same_gap_roots = {
        RANKING.parse_root(root)
        for root in same_gap_roots
    } & pending_roots
    pending_same_gap_rows = {
        coordinate
        for root in pending_same_gap_roots
        for coordinate in pending[root]
    }
    selector_family = family_cache[SELECTOR]
    require(
        len(same_gap_rows) == EXPECTED_SAME_GAP_SITES
        and len(same_gap_roots) == EXPECTED_SAME_GAP_ROOTS
        and len(pending_same_gap_roots) == EXPECTED_PENDING_SAME_GAP_ROOTS
        and len(pending_same_gap_rows) == EXPECTED_PENDING_SAME_GAP_ROWS
        and len(sibling_selectors) == EXPECTED_SIBLING_FAMILIES
        and sum(row["branch_count"] for row in same_gap_rows)
            == EXPECTED_CARTESIAN_BRANCHES
        and all(
            row["branch_count"] == EXPECTED_BRANCHES_PER_ROOT
            and row["control_count"] == EXPECTED_CONTROLS_PER_GAP
            for row in same_gap_rows
        ),
        "selector730 Cartesian scope drifted",
    )
    require(
        selector_family["candidate_terminal_sha256"]
            == EXPECTED_SELECTOR_TERMINAL_CANDIDATE_SHA256
        and selector_family["current_terminal_sha256"]
            == EXPECTED_SELECTOR_TERMINAL_CURRENT_SHA256
        and selector_family["source_terminal_sha256"]
            == EXPECTED_SELECTOR_TERMINAL_SOURCE_SHA256
        and all(
            terminal_digest(contexts[language], tuple(
                RANKING.parse_root(root)
                for root in selector_family["terminal_roots"]
            )) == EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256
            for language in ("en", "sc", "tc")
        ),
        "selector730 shared terminal read-only contract drifted",
    )

    partition = assignment_partition(candidate_sites, same_gap_roots)
    families = [
        family_cache[selector] for selector in sorted(family_cache)
    ]
    private: dict[str, Any] = {
        "schema": PRIVATE_SCHEMA,
        "method": METHOD,
        "inputs": {
            **EXPECTED_INPUT_SHA256,
            "pk_rebuilt_candidate_sha256":
                EXPECTED_PK_CANDIDATE_SHA256,
        },
        "scope": {
            "candidate_sites": candidate_sites,
            "candidate_site_count": len(candidate_sites),
            "pending_same_gap_coordinates": sorted(
                pending_same_gap_rows, key=RANKING.parse_coordinate
            ),
            "same_gap_root_count": len(same_gap_roots),
            "same_gap_sites": [
                row["site"] for row in same_gap_rows
            ],
            "selector_coordinate": f"0:{SELECTOR}",
            "source_only_sites": sorted(
                source_only, key=RANKING.site_key
            ),
        },
        "assignment_partition": partition,
        "cartesian_roots": same_gap_rows,
        "terminal_families": families,
        "proof": {
            "automatic_space_or_grammar_repair_by_vm": False,
            "cartesian_branches_computed_once": True,
            "full_dialogue_rebuild_performed": False,
            "semantic_decision_rows": 0,
            "same_gap_partial_pass_authorized": False,
            "source_only_action_count": 0,
            "steam_write_performed": False,
            "terminal_records_read_only": True,
        },
    }
    private["guards"] = {
        "cartesian_roots_canonical_sha256":
            canonical_sha256(same_gap_rows),
        "payload_without_guards_canonical_sha256":
            canonical_sha256(private),
        "terminal_families_canonical_sha256":
            canonical_sha256(families),
    }

    risk = Counter()
    maximum_positive_delta = 0
    for row in same_gap_rows:
        grammar = row["grammar_risk"]
        risk["right_boundary_sites"] += int(
            grammar["right_boundary_present"]
        )
        risk["outer_space_protected_sites"] += int(
            grammar["outer_space_protected"]
        )
        risk["positive_expansion_branches"] += int(
            grammar["positive_expansion_branch_count"]
        )
        risk["linebreak_change_branches"] += int(
            grammar["linebreak_change_branch_count"]
        )
        maximum_positive_delta = max(
            maximum_positive_delta,
            int(grammar["maximum_positive_raw_g1n_delta_px"]),
        )
    public: dict[str, Any] = {
        "schema": PUBLIC_SCHEMA,
        "method": METHOD,
        "inputs": {
            "official_checkpoint_public_sha256":
                EXPECTED_INPUT_SHA256["checkpoint_public"],
            "official_integrated_ledger_sha256":
                EXPECTED_INPUT_SHA256["official_ledger"],
            "pk_rebuilt_candidate_sha256":
                EXPECTED_PK_CANDIDATE_SHA256,
            "ranking_private_sha256":
                EXPECTED_INPUT_SHA256["ranking_private"],
            "ranking_public_sha256":
                EXPECTED_INPUT_SHA256["ranking_public"],
            "selector730_assignment_builder_sha256":
                EXPECTED_INPUT_SHA256["selector730_assignment_builder"],
            "selector730_assignment_private_sha256":
                EXPECTED_INPUT_SHA256["selector730_assignment_private"],
            "selector730_assignment_public_sha256":
                EXPECTED_INPUT_SHA256["selector730_assignment_public"],
        },
        "scope": {
            "candidate_call_sites": len(candidate_sites),
            "controls_per_same_gap": EXPECTED_CONTROLS_PER_GAP,
            "ordered_cartesian_branches": EXPECTED_CARTESIAN_BRANCHES,
            "pending_same_gap_roots": len(pending_same_gap_roots),
            "pending_same_gap_rows": len(pending_same_gap_rows),
            "same_gap_roots": len(same_gap_roots),
            "same_gap_sites": len(same_gap_rows),
            "selector": SELECTOR,
            "sibling_seven_way_families": len(sibling_selectors),
            "source_call_sites": len(source_sites),
            "source_only_sites": len(source_only),
        },
        "assignment_partition": {
            key: value
            for key, value in partition.items()
            if key != "assignment_private_sha256"
        },
        "risk": {
            **dict(sorted(risk.items())),
            "maximum_positive_raw_g1n_delta_px":
                maximum_positive_delta,
        },
        "proof": {
            "all_sibling_families_fixed_seven_way": True,
            "all_sibling_source_candidate_dispatch_identical": True,
            "automatic_space_or_grammar_repair_by_vm": False,
            "cartesian_branches_computed_once": True,
            "full_dialogue_rebuild_performed": False,
            "semantic_decision_rows": 0,
            "same_gap_root_atomicity_required": True,
            "source_only_action_count": 0,
            "steam_write_performed": False,
            "terminal_records_read_only": True,
        },
        "guards": {
            "private_cartesian_roots_canonical_sha256":
                private["guards"]["cartesian_roots_canonical_sha256"],
            "private_terminal_families_canonical_sha256":
                private["guards"]["terminal_families_canonical_sha256"],
            "same_gap_root_sha256": ASSIGNMENT.BASE.root_digest(
                RANKING.parse_root(root) for root in same_gap_roots
            ),
            "source_only_site_sha256": EXPECTED_SOURCE_ONLY_SHA256,
        },
        "privacy": {
            "contains_commercial_source_text": False,
            "contains_exact_coordinates": False,
            "contains_translations": False,
            "private_evidence_stays_below_tmp": True,
        },
        "status": "PASS",
    }
    public["guards"]["payload_without_final_guard_canonical_sha256"] = (
        canonical_sha256(public)
    )
    assert_source_free(public)
    private_content = serialized_json(private)
    public_content = serialized_json(public)
    return private_content, public_content, private, public


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--bootstrap-output-pins", action="store_true")
    args = parser.parse_args(argv)
    private_content, public_content, _private, public = build_outputs()
    private_sha = sha256_bytes(private_content)
    public_sha = sha256_bytes(public_content)
    require(
        (
            EXPECTED_PRIVATE_OUTPUT_SHA256 is not None
            and EXPECTED_PUBLIC_OUTPUT_SHA256 is not None
        )
        or args.bootstrap_output_pins,
        "output hashes are not pinned; use --bootstrap-output-pins once",
    )
    if EXPECTED_PRIVATE_OUTPUT_SHA256 is not None:
        require(
            private_sha == EXPECTED_PRIVATE_OUTPUT_SHA256,
            f"private output hash drifted: {private_sha}",
        )
    if EXPECTED_PUBLIC_OUTPUT_SHA256 is not None:
        require(
            public_sha == EXPECTED_PUBLIC_OUTPUT_SHA256,
            f"public output hash drifted: {public_sha}",
        )
    if args.check:
        require(
            EXPECTED_PRIVATE_OUTPUT_SHA256 is not None
            and EXPECTED_PUBLIC_OUTPUT_SHA256 is not None,
            "--check requires frozen output hashes",
        )
        require(
            DEFAULT_PRIVATE_OUTPUT.is_file()
            and DEFAULT_PRIVATE_OUTPUT.read_bytes() == private_content,
            "private Cartesian manifest drifted",
        )
        require(
            DEFAULT_PUBLIC_OUTPUT.is_file()
            and DEFAULT_PUBLIC_OUTPUT.read_bytes() == public_content,
            "public Cartesian coverage drifted",
        )
    else:
        DEFAULT_PRIVATE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PRIVATE_OUTPUT.write_bytes(private_content)
        DEFAULT_PUBLIC_OUTPUT.write_bytes(public_content)
    print(json.dumps({
        "assignment_partition_status":
            public["assignment_partition"]["status"],
        "cartesian_branches": EXPECTED_CARTESIAN_BRANCHES,
        "private_sha256": private_sha,
        "public_sha256": public_sha,
        "semantic_decision_rows": 0,
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
