#!/usr/bin/env python3
"""Rank remaining PK seven-way selector families on the FC157A checkpoint.

This read-only planning audit rebuilds the PK candidate from the immutable
post-selector568/1096/1174 integrated ledger, walks every 0143/014A closure
reachable from a still-pending record, identifies the fixed seven-terminal
selector shape, and excludes the already completed selector families.

No translation is proposed. Coordinate-bearing graph detail stays below
``tmp``; the tracked report contains source-free counts and cryptographic
guards. There is no Steam write path.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
LEGACY_BUILDER_PATH = (
    WORKSTREAM / "build_pk_next_selector_family_ranking_v1.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector568_1096_1174_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector568_1096_1174_consolidated_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector568_1096_1174.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector568_1096_1174.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector568-1096-1174.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector568-1096-1174-source-free.v1"
)
METHOD = (
    "official_fc157a_pending_reachable_0143_"
    "seven_way_selector_ranking"
)
OWNED_SELECTORS = (538, 568, 1096, 1174)

EXPECTED_LEDGER_SHA256 = (
    "FC157A9907686D0EA6DC6C61C7785E81AC7F750100F2E1CDDE02DBF4F09F2DCA"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "1FCF033F1F75FC43473152CFB7115D170657519952C19D563C36C3F9BAB4CBD1"
)
EXPECTED_PK_CURRENT_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PK_PRISTINE_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "07E65E6338D32C1FD13F17408F82A4133E55541C722874632948C7B36C909805"
)
EXPECTED_LEDGER_ROWS = 52_803
EXPECTED_PK_PENDING_ROWS = 7_268
EXPECTED_PK_PENDING_ROOTS = 4_536
EXPECTED_PK_PENDING_ROOT_SHA256 = (
    "F2BA2756AD977B452CCC26E7F5EA33E4201BC668721E3DF14808D63752C5ADE1"
)
EXPECTED_REACHABLE_CALL_TARGETS = 161
EXPECTED_OWNED_CALL_TARGETS = 5
EXPECTED_NON_SEVEN_WAY_TARGETS = 26
EXPECTED_ELIGIBLE_FAMILIES = 130
EXPECTED_ELIGIBLE_UNION_ROWS = 2_065
EXPECTED_ELIGIBLE_UNION_SHA256 = (
    "F6D2D87581769715D779BB7C00A6110C360B018BF680FC3CC474AA0BC8F20D99"
)
EXPECTED_RECOMMENDED_SELECTOR = "0:610"
EXPECTED_RECOMMENDED_TERMINALS = tuple(
    f"0:{record_id}" for record_id in range(2000, 2007)
)
EXPECTED_RECOMMENDED_PENDING_ROWS = 192
EXPECTED_RECOMMENDED_PENDING_ROOTS = 89
EXPECTED_RECOMMENDED_PENDING_SITES = 89
EXPECTED_RECOMMENDED_CANDIDATE_SITES = 230
EXPECTED_RECOMMENDED_SOURCE_SITES = 243
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES = 13
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES = 0

# Completed-family yields are historical audit facts. They are not recovered
# by intersecting their decisions with the FC157A pending set because those
# promotions have already left that set.
COMPARABLE_ACTUAL_PROMOTIONS = {568: 225, 1096: 206, 1174: 197}
COMPARABLE_PENDING_UPPER_BOUNDS = {568: 331, 1096: 247, 1174: 224}
EXPECTED_POINT_ESTIMATE = 150
EXPECTED_ESTIMATE_RANGE = (131, 169)

# Frozen after the first reproducible write/check cycle.
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "183896FC6C6B398C4DF3B93DB993AE2E79104AC70460B63DBA02D870A959CD60"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "18E80E360667383B359764C02F4F46C7EC1D61E85A27890FB7C5C3FEDD4F7B2F"
)


class RankingError(ValueError):
    """Raised when immutable ranking inputs or results drift."""


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


LEGACY = load_module(
    LEGACY_BUILDER_PATH,
    "pk_next_selector_post_1174_legacy_helpers_v1",
)
ENGINE = LEGACY.ENGINE
sha256_bytes = LEGACY.sha256_bytes
sha256_file = LEGACY.sha256_file
canonical_sha256 = LEGACY.canonical_sha256
serialized_json = LEGACY.serialized_json
parse_coordinate = LEGACY.parse_coordinate
parse_root = LEGACY.parse_root
root_string = LEGACY.root_string
root_digest = LEGACY.root_digest
coordinate_digest = LEGACY.coordinate_digest
site_key = LEGACY.site_key
site_digest = LEGACY.site_digest
edge_digest = LEGACY.edge_digest
graph_edges = LEGACY.graph_edges
candidate_call_sites = LEGACY.candidate_call_sites
reachable_call_targets = LEGACY.reachable_call_targets
family_shape = LEGACY.family_shape


def load_official_ledger(
    path: Path,
) -> tuple[
    dict[tuple[int, int, int], str],
    dict[tuple[int, int], set[str]],
]:
    replacements: dict[tuple[int, int, int], str] = {}
    pending: defaultdict[tuple[int, int], set[str]] = defaultdict(set)
    seen: set[str] = set()
    row_count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row_count += 1
        row = json.loads(line)
        if row.get("resource") != "pk_msggame":
            continue
        coordinate = str(row["coordinate"])
        require(coordinate not in seen, f"duplicate ledger coordinate: {coordinate}")
        seen.add(coordinate)
        key = parse_coordinate(coordinate)
        if "translation" in row:
            replacements[key] = str(row["translation"])
        if row.get("runtime_review") == "pending":
            pending[key[:2]].add(coordinate)
    require(
        row_count == EXPECTED_LEDGER_ROWS,
        f"ledger row count drifted: {row_count}",
    )
    require(
        sum(len(values) for values in pending.values())
        == EXPECTED_PK_PENDING_ROWS,
        "official PK pending count drifted",
    )
    return replacements, dict(pending)


def completed_yield_estimate(pending_rows: int) -> tuple[int, tuple[int, int]]:
    ratios = [
        COMPARABLE_ACTUAL_PROMOTIONS[key]
        / COMPARABLE_PENDING_UPPER_BOUNDS[key]
        for key in sorted(COMPARABLE_ACTUAL_PROMOTIONS)
    ]
    point = round(
        pending_rows
        * sum(COMPARABLE_ACTUAL_PROMOTIONS.values())
        / sum(COMPARABLE_PENDING_UPPER_BOUNDS.values())
    )
    return point, (
        round(pending_rows * min(ratios)),
        round(pending_rows * max(ratios)),
    )


def build_outputs(
    *,
    steam_root: Path = DEFAULT_STEAM_ROOT,
    ledger_path: Path = DEFAULT_LEDGER,
    checkpoint_public_path: Path = CHECKPOINT_PUBLIC,
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
        "checkpoint_public": sha256_file(checkpoint_public_path),
        "pk_current": sha256_file(current_path),
        "pk_pristine": sha256_file(pristine_path),
    }
    require(
        inputs["ledger"] == EXPECTED_LEDGER_SHA256,
        "official integrated ledger drifted",
    )
    require(
        inputs["checkpoint_public"] == EXPECTED_CHECKPOINT_PUBLIC_SHA256,
        "official public checkpoint drifted",
    )
    require(
        inputs["pk_current"] == EXPECTED_PK_CURRENT_SHA256,
        "shadow current PK input drifted",
    )
    require(
        inputs["pk_pristine"] == EXPECTED_PK_PRISTINE_SHA256,
        "pristine PK input drifted",
    )

    replacements, pending_by_root = load_official_ledger(ledger_path)
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
        pending = {
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
        private_targets.append(
            {
                "classification": classification,
                "target_coordinate": root_string(target),
                "reachable_pending_roots": [
                    root_string(root) for root in sorted(roots)
                ],
                "reachable_pending_root_count": len(roots),
                "reachable_pending_root_sha256": root_digest(roots),
                "current_pending_coordinates": sorted(
                    pending, key=parse_coordinate
                ),
                "current_pending_row_count": len(pending),
                "current_pending_coordinate_sha256": coordinate_digest(
                    pending
                ),
                "candidate_call_sites": all_candidate_sites,
                "candidate_call_site_count": len(all_candidate_sites),
                "candidate_call_site_sha256": site_digest(
                    all_candidate_sites
                ),
                "source_call_sites": all_source_sites,
                "source_call_site_count": len(all_source_sites),
                "source_call_site_sha256": site_digest(all_source_sites),
                "direct_pending_call_sites": pending_direct_sites,
                "direct_pending_call_site_count": len(pending_direct_sites),
                "direct_pending_root_count": len(direct_pending_roots),
                "direct_pending_root_sha256": root_digest(
                    direct_pending_roots
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

        eligible_union.update(pending)
        source_only_sites = set(all_source_sites).difference(
            all_candidate_sites
        )
        candidate_only_sites = set(all_candidate_sites).difference(
            all_source_sites
        )
        public_ranking.append(
            {
                "selector_coordinate": root_string(target),
                "current_pending_rows": len(pending),
                "current_pending_coordinate_sha256": coordinate_digest(
                    pending
                ),
                "reachable_pending_root_count": len(roots),
                "reachable_pending_root_sha256": root_digest(roots),
                "direct_pending_root_count": len(direct_pending_roots),
                "direct_pending_call_site_count": len(pending_direct_sites),
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
            -int(row["current_pending_rows"]),
            parse_root(str(row["selector_coordinate"])),
        )
    )
    require(
        classification_counts[
            "already_owned_selector_or_dispatch_closure"
        ]
        == EXPECTED_OWNED_CALL_TARGETS,
        f"owned reachable call-target count drifted: {classification_counts}",
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
        len(eligible_union) == EXPECTED_ELIGIBLE_UNION_ROWS
        and coordinate_digest(eligible_union)
        == EXPECTED_ELIGIBLE_UNION_SHA256,
        "eligible family pending union drifted",
    )

    top = public_ranking[0]
    top_private = next(
        row
        for row in private_targets
        if row["target_coordinate"] == top["selector_coordinate"]
    )
    top_terminals = tuple(
        top_private["jump_closure"]["terminal_coordinates"]
    )
    require(
        top["selector_coordinate"] == EXPECTED_RECOMMENDED_SELECTOR
        and top_terminals == EXPECTED_RECOMMENDED_TERMINALS
        and top["current_pending_rows"]
        == EXPECTED_RECOMMENDED_PENDING_ROWS
        and top["reachable_pending_root_count"]
        == EXPECTED_RECOMMENDED_PENDING_ROOTS
        and top["direct_pending_call_site_count"]
        == EXPECTED_RECOMMENDED_PENDING_SITES
        and top["candidate_call_site_count"]
        == EXPECTED_RECOMMENDED_CANDIDATE_SITES
        and top["source_call_site_count"]
        == EXPECTED_RECOMMENDED_SOURCE_SITES
        and top["source_only_call_site_count"]
        == EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES
        and top["candidate_only_call_site_count"]
        == EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES,
        "recommended selector-610 metrics drifted",
    )
    pending_root_digest = root_digest(pending_by_root)
    require(
        len(pending_by_root) == EXPECTED_PK_PENDING_ROOTS
        and pending_root_digest == EXPECTED_PK_PENDING_ROOT_SHA256,
        "official pending-root universe drifted",
    )
    point_estimate, estimate_range = completed_yield_estimate(
        int(top["current_pending_rows"])
    )
    require(
        point_estimate == EXPECTED_POINT_ESTIMATE
        and estimate_range == EXPECTED_ESTIMATE_RANGE,
        "completed-family yield estimate drifted",
    )

    common_inputs = {
        "official_integrated_ledger_sha256": inputs["ledger"],
        "official_public_checkpoint_sha256":
            inputs["checkpoint_public"],
        "pk_current_sha256": inputs["pk_current"],
        "pk_pristine_sha256": inputs["pk_pristine"],
        "pk_rebuilt_candidate_sha256": candidate_sha256,
    }
    scope = {
        "resource": "pk_msggame",
        "official_pending_rows": EXPECTED_PK_PENDING_ROWS,
        "official_pending_root_count": len(pending_by_root),
        "official_pending_root_sha256": pending_root_digest,
        "reachable_0143_call_target_count": len(reachable_roots),
        "eligible_fixed_seven_way_family_count": len(public_ranking),
        "eligible_family_current_pending_union_rows": len(eligible_union),
        "eligible_family_current_pending_union_coordinate_sha256":
            coordinate_digest(eligible_union),
    }
    recommendation = {
        "selector_coordinate": top["selector_coordinate"],
        "terminal_count": top["dispatch_contract"]["terminal_count"],
        "terminal_coordinate_sha256":
            top["dispatch_contract"]["terminal_coordinate_sha256"],
        "exact_current_pending_upper_bound":
            top["current_pending_rows"],
        "estimated_actual_promotion_rows": point_estimate,
        "estimated_actual_promotion_range": list(estimate_range),
        "estimate_basis": {
            "completed_family_actual_promotions": {
                str(key): value
                for key, value
                in sorted(COMPARABLE_ACTUAL_PROMOTIONS.items())
            },
            "completed_family_pending_upper_bounds": {
                str(key): value
                for key, value
                in sorted(COMPARABLE_PENDING_UPPER_BOUNDS.items())
            },
            "derived_from_current_pending_intersections": False,
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
            "official_public_checkpoint_path": str(
                checkpoint_public_path.relative_to(REPO)
            ).replace("\\", "/"),
            "pk_current_path": str(
                current_path.relative_to(REPO)
            ).replace("\\", "/"),
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
        "eligible_ranking_canonical_sha256":
            canonical_sha256(public_ranking),
        "payload_without_guards_canonical_sha256":
            canonical_sha256(private),
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
        "--checkpoint-public",
        type=Path,
        default=CHECKPOINT_PUBLIC,
    )
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
        checkpoint_public_path=args.checkpoint_public,
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
        resolved_private = args.private_output.resolve()
        tmp_root = DIALOGUE_TMP.resolve()
        require(
            resolved_private == tmp_root
            or tmp_root in resolved_private.parents,
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
                "exact_current_pending_upper_bound":
                    public["recommendation"][
                        "exact_current_pending_upper_bound"
                    ],
                "private_sha256": private_sha256,
                "public_sha256": public_sha256,
                "recommended_selector":
                    public["recommendation"]["selector_coordinate"],
                "steam_write_performed": False,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
