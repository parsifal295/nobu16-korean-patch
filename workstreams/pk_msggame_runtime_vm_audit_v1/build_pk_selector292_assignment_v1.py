#!/usr/bin/env python3
"""Build the immutable two-chunk PK selector-292 assignment."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
BASE_BUILDER_PATH = WORKSTREAM / "build_pk_selector238_assignment_v1.py"
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_selector238_consolidated_v1.py"
)
RANKING_PRIVATE_PATH = (
    TMP
    / "pk_next_selector_family_ranking."
    "post_selector238_consolidated.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    WORKSTREAM / "public"
    / "pk_next_selector_family_ranking."
    "post_selector238_consolidated.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = TMP / "pk_selector292_assignment.private.v1.json"
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector292_assignment_coverage.v1.json"
)
CONTEXT_MANIFEST_PATH = (
    TMP / "pk_selector292_context_inventory.private.v1.json"
)
LAYOUT_MANIFEST_PATH = (
    TMP / "pk_selector292_layout_manifest.selector178_chunk1_fast.private.v1.json"
)

SELECTOR = 292
TERMINALS = tuple(range(1615, 1622))
PRIVATE_SCHEMA = "nobu16.kr.pk-selector292-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector292-assignment-coverage.v1"
METHOD = (
    "post_selector238_selector292_root_disjoint_two_chunk_"
    "structural_relation_atom_assignment"
)
EXPECTED_INPUT_SHA256 = {
    "ledger":
        "AC10F7E71CFAD259ABBC08139BE0DB848CF5309578045532A48991F40E0035AB",
    "checkpoint_public":
        "0CAE7231474FBAE0BCE8E1E98D44225DCC5445EEEA435378E0D56BD1F83A5384",
    "ranking_builder":
        "52C8E1015F09BB30BA90FD2C8B86868C5B7CDE2E20575797333776BD10F12094",
    "ranking_private":
        "89F45139F0D684F9FA87CF47A3C964B50EA4546851D79F8656F7B335025FB164",
    "ranking_public":
        "C29C242A66BE2AAC13F8C9C02CC4D42A1E02FBF7D839B5401E926F9A0407ACBF",
    "base_assignment":
        "AE1428FBF34BA042F1588E89DAA02623752D791BCD498687B9AD8595ED4BD7FF",
    "helper":
        "E39ED4738833FB56680E81E5B06A68F04472BABE7279D92CB608A40DB7D17CF5",
}
EXPECTED_BASE_BUILDER_SHA256 = (
    "4C09CA6AAC9DBE0EBB83E8A855C20724721AAF1875BE0C12B45ACDA9D1AEFE40"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "9E5C60A451DB7CCA7B046AFD8CFF199CB3665E003CB0C751120478F693D20C24"
)
EXPECTED_COVERAGE = (26, 26, 31, 5, 0, 11, 11, 33)
EXPECTED_SITE_ROW_SHA256 = (
    "DCA4A76F0E3970D8EE1788688B4DDDCF5742023DF66AD7B731DB52962B7FD0E5"
)
EXPECTED_TEMPLATE_SIZES = (2, 2)
EXPECTED_REGISTER_GROUP_SIZES = (2, 2)
EXPECTED_CHUNK_METRICS = (
    (13, 13, 5, 13, 0, 343),
    (13, 13, 6, 20, 1, 342),
)
EXPECTED_COMPLETED_OVERLAP = (1, 1, 4)
EXPECTED_PRIOR_ASSEMBLY_EVIDENCE = (11, 18)
EXPECTED_CARTESIAN = (8, 8, 8, 1, 1, 392)
EXPECTED_ATOMIC_SENSITIVE_ROOTS = 17
EXPECTED_FLAG_COUNTS = (23, 12, 312)
EXPECTED_TERMINAL_STATES = (6, 1)
EXPECTED_TERMINAL_COMPARISON = (6, 1)
EXPECTED_ORDINARY_PENDING_BRANCHES = 70
EXPECTED_HARD_BLOCKS = (2, 5)
EXPECTED_REWRITE_CANDIDATES = (9, 28)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "F18978DBB58A5D8AF1ED4B2266FE2B599C98A038D5A85BDAAC2222FDEB8C51A6"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "84EE1EB18E39223AA009868B7FB99119073A6DFC7CA8FC899C70C464F8346B47"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "798B6E4A8099F9FCA1BF5033F8315B17832B8D17178826029B800738EAD905C2"
)
EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_CONTEXT_MANIFEST_SHA256 = (
    "2DC02C44C2698F407970BB0291E3023A597D6F9944B330E91A3C4778C621685D"
)
EXPECTED_LAYOUT_MANIFEST_SHA256 = (
    "A19F3696797F141A282826D1E87DEA1D80EF11E0BB55F21EF49EF061CCE0FA99"
)
EXPECTED_SOURCE_ONLY_SHA256: str | None = (
    "4B5C5E8AAF5AA1D14BAABFF35200E062154343CC777503EE652DC1D5D3B324D0"
)
EXPECTED_PRIVATE_FILE_SHA256 = (
    "B2FD0DD7B016B20CCAB04CA903643CD158008299BBC9EF8FAA89187A5C9D6372"
)
EXPECTED_PUBLIC_FILE_SHA256 = (
    "AAA5F7F7A503A508712AC1E0DB304F04A9152FA1E3CE30D5A53598B1AE3B06DD"
)

REGISTER_ROOT_GROUPS = (
    ("15:1510", "15:1516"),
    ("15:1511", "15:1518"),
)
REGISTER_REPEAT_RISK_ROOT = "15:1519"


def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE_WRAPPER = load(BASE_BUILDER_PATH, "selector292_assignment_base")
ASSIGNMENT = BASE_WRAPPER.ASSIGNMENT
RANKING_WRAPPER = load(RANKING_BUILDER_PATH, "selector292_ranking")
RANKING = RANKING_WRAPPER.RANKING
ENGINE = RANKING.ENGINE
ORIGINAL_JSON_LOADS = json.loads
ORIGINAL_TEMPLATE_ATOMS = BASE_WRAPPER.ORIGINAL_TEMPLATE_ATOMS
AssignmentError = ASSIGNMENT.AssignmentError
require = ASSIGNMENT.require


def structural_atoms(
    sites: Sequence[str],
    record_sets: Sequence[Any],
) -> list[set[tuple[int, int]]]:
    templates = ORIGINAL_TEMPLATE_ATOMS(sites, record_sets)
    register_groups = [
        {RANKING.parse_root(root) for root in group}
        for group in REGISTER_ROOT_GROUPS
    ]
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
    grouped = (
        set().union(*templates, *register_groups)
        if templates or register_groups
        else set()
    )
    sensitive = same_gap_roots | owned
    return templates + register_groups + [
        {root} for root in sorted(sensitive - grouped)
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
    ASSIGNMENT.RANKING_WRAPPER = RANKING_WRAPPER
    ASSIGNMENT.RANKING = RANKING
    ASSIGNMENT.ENGINE = ENGINE
    ASSIGNMENT.balanced_chunks = ASSIGNMENT.BASE.balanced_chunks
    RANKING.CONTROL_RE = RANKING.LEGACY.CONTROL_RE
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
sha256_file = ASSIGNMENT.sha256_file
assert_source_free = ASSIGNMENT.assert_source_free


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector238 assignment base drifted",
    )
    for path, expected in (
        (CONTEXT_MANIFEST_PATH, EXPECTED_CONTEXT_MANIFEST_SHA256),
        (LAYOUT_MANIFEST_PATH, EXPECTED_LAYOUT_MANIFEST_SHA256),
    ):
        require(
            path.is_file() and sha256_file(path) == expected,
            f"private preaudit manifest drifted: {path}",
        )
    original_loads = ASSIGNMENT.json.loads

    def adapted_loads(value: str, *args: Any, **kwargs: Any) -> Any:
        result = original_loads(value, *args, **kwargs)
        if not isinstance(result, dict):
            return result
        for row in result.get("direct_targets", []):
            if row.get("target_coordinate") == "0:292":
                row["target_coordinate"] = "0:1198"
        recommendation = result.get("recommendation")
        if (
            isinstance(recommendation, dict)
            and recommendation.get("selector_coordinate") == "0:292"
        ):
            recommendation["selector_coordinate"] = "0:1198"
        return result

    ASSIGNMENT.json.loads = adapted_loads
    try:
        _private_text, _public_text, private, public = (
            ASSIGNMENT.build_outputs()
        )
    finally:
        ASSIGNMENT.json.loads = original_loads

    chunks = tuple(
        (
            int(chunk["site_count"]),
            int(chunk["root_count"]),
            int(chunk["pending_root_count"]),
            int(chunk["pending_row_upper_bound"]),
            int(chunk["owned_overlap_root_count"]),
            int(chunk["workload_weight"]),
        )
        for chunk in private["chunks"]
    )
    if EXPECTED_CHUNK_METRICS is not None:
        require(chunks == EXPECTED_CHUNK_METRICS, "chunk metrics drifted")
    site_row_sha = str(private["guards"]["site_matrix_sha256"])
    if EXPECTED_SITE_ROW_SHA256 is not None:
        require(site_row_sha == EXPECTED_SITE_ROW_SHA256, "site matrix drifted")

    private["schema"] = PRIVATE_SCHEMA
    private["method"] = METHOD
    private["scope"]["selector_coordinate"] = "0:292:0"
    private["preaudit_manifests"] = {
        "context_inventory_basename": CONTEXT_MANIFEST_PATH.name,
        "context_inventory_sha256": EXPECTED_CONTEXT_MANIFEST_SHA256,
        "layout_manifest_basename": LAYOUT_MANIFEST_PATH.name,
        "layout_manifest_sha256": EXPECTED_LAYOUT_MANIFEST_SHA256,
    }
    private["review_guards"] = {
        "automatic_prior_evidence_promotion_authorized": False,
        "automatic_terminal_promotion_authorized": False,
        "source_only_action_count": 0,
        "terminal_action_count": 0,
        "terminal_pending_read_only_rows": 1,
        "terminal_verified_read_only_rows": 6,
    }

    public["schema"] = PUBLIC_SCHEMA
    public["method"] = METHOD
    public["scope"]["selector"] = SELECTOR
    public["scope"]["official_pending_rows"] = 6_151
    public["preaudit"] = {
        "context_inventory_sha256": EXPECTED_CONTEXT_MANIFEST_SHA256,
        "layout_manifest_sha256": EXPECTED_LAYOUT_MANIFEST_SHA256,
        "ordinary_runtime_branches": 126,
        "ordinary_runtime_pass_branches": 75,
        "same_gap_atom_count": 8,
        "same_gap_cartesian_branches": 392,
        "same_gap_cartesian_pass_branches": 36,
        "source_only_action_count": 0,
        "source_only_site_count": 5,
        "terminal_action_count": 0,
        "terminal_pending_read_only_rows": 1,
        "terminal_verified_read_only_rows": 6,
        "total_runtime_assemblies": 518,
        "total_runtime_pass_assemblies": 111,
    }
    public["assignment"]["identical_template_atom_count"] = 2
    public["assignment"]["register_signature_atom_count"] = 2
    public["assignment"]["same_gap_atom_count"] = 8
    public["assignment"]["same_gap_cartesian_branch_count"] = 392

    private_content = ASSIGNMENT.serialized_json(private)
    public["guards"] = {
        "private_assignment_sha256":
            ASSIGNMENT.sha256_bytes(private_content.encode("utf-8")),
        "site_matrix_sha256": site_row_sha,
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
    parser.add_argument("--bootstrap", action="store_true")
    args = parser.parse_args(argv)
    private_content, public_content, _private, public = build_outputs()
    private_sha = ASSIGNMENT.sha256_bytes(private_content.encode("utf-8"))
    public_sha = ASSIGNMENT.sha256_bytes(public_content.encode("utf-8"))
    chunks = tuple(
        (
            int(row["site_count"]),
            int(row["root_count"]),
            int(row["pending_root_count"]),
            int(row["pending_row_upper_bound"]),
            int(row["owned_overlap_root_count"]),
            int(row["workload_weight"]),
        )
        for row in public["assignment"]["chunks"]
    )
    resolved = all(
        value is not None
        for value in (
            EXPECTED_SITE_ROW_SHA256,
            EXPECTED_CHUNK_METRICS,
            EXPECTED_PRIVATE_FILE_SHA256,
            EXPECTED_PUBLIC_FILE_SHA256,
        )
    )
    if args.bootstrap:
        require(not resolved, "bootstrap forbidden after assignment freeze")
    else:
        require(resolved, "assignment bootstrap pins unresolved")
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
        "chunks": chunks,
        "private_sha256": private_sha,
        "public_sha256": public_sha,
        "site_matrix_sha256": public["guards"]["site_matrix_sha256"],
        "steam_write_performed": False,
    }, sort_keys=True))
    return 0


def terminal_digest(records: Any) -> str:
    values = []
    for terminal in TERMINALS:
        literals = ENGINE.parse_record_literals(records[(0, terminal)])
        require(len(literals) == 1, "terminal literal shape drifted")
        values.append(literals[0].text)
    return ASSIGNMENT.sha256_bytes("\0".join(values).encode("utf-8"))


def manifest_rows(
    manifest: Mapping[str, Any],
    order_key: str,
    rows_key: str,
) -> list[dict[str, Any]]:
    order = [str(value) for value in manifest[order_key]]
    return [
        dict(zip(order, row, strict=True))
        for row in manifest[rows_key]
    ]


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    immutable = {
        BASE_BUILDER_PATH: EXPECTED_BASE_BUILDER_SHA256,
        CONTEXT_MANIFEST_PATH: EXPECTED_CONTEXT_MANIFEST_SHA256,
        LAYOUT_MANIFEST_PATH: EXPECTED_LAYOUT_MANIFEST_SHA256,
    }
    for path, expected in immutable.items():
        require(
            path.is_file() and sha256_file(path) == expected,
            f"selector292 immutable input drifted: {path}",
        )
    context_manifest = ORIGINAL_JSON_LOADS(
        CONTEXT_MANIFEST_PATH.read_text(encoding="utf-8")
    )
    layout_manifest = ORIGINAL_JSON_LOADS(
        LAYOUT_MANIFEST_PATH.read_text(encoding="utf-8")
    )
    require(
        context_manifest["schema"]
        == "nobu16.kr.pk-selector292-context-inventory.private.v1"
        and layout_manifest["schema"]
        == "nobu16.kr.pk-selector292-read-only-layout-manifest.private.v1"
        and context_manifest["inputs"]["candidate_sha256"]
        == EXPECTED_PK_CANDIDATE_SHA256
        and layout_manifest["inputs"]["official_candidate_sha256"]
        == EXPECTED_PK_CANDIDATE_SHA256,
        "selector292 private evidence manifest drifted",
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
            elif target == "0:292":
                row["target_coordinate"] = "0:1198"
        recommendation = result.get("recommendation")
        if (
            isinstance(recommendation, dict)
            and recommendation.get("selector_coordinate") == "0:292"
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
        if row["target_coordinate"] == "0:292"
    )
    reachable = {
        RANKING.parse_root(root)
        for root in target["reachable_pending_roots"]
    }
    potential = {
        coordinate for root in reachable for coordinate in pending[root]
    }
    candidate_sites = [str(row["site"]) for row in private["site_assignments"]]
    candidate_roots = {
        RANKING.site_key(site)[:2] for site in candidate_sites
    }
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
    register_groups = [
        {RANKING.parse_root(root) for root in group}
        for group in REGISTER_ROOT_GROUPS
    ]
    require(
        tuple(sorted(len(group) for group in register_groups))
        == EXPECTED_REGISTER_GROUP_SIZES
        and all(group <= candidate_roots for group in register_groups)
        and not any(group & template_union for group in register_groups),
        "register atom drifted",
    )
    register_union = set().union(*register_groups)
    context_repeats = context_manifest["repeated_stems"][
        "exact_candidate_record_groups"
    ]
    require(
        any(
            set(row["members"]) == {"15:1516", REGISTER_REPEAT_RISK_ROOT}
            for row in context_repeats
        )
        and all(
            RANKING.parse_root(REGISTER_REPEAT_RISK_ROOT) not in group
            for group in register_groups
        ),
        "register repeat-risk separation drifted",
    )

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

    layout_roots = {
        str(row["root"]): row
        for row in manifest_rows(
            layout_manifest, "root_layout_field_order", "per_root_layout"
        )
    }
    layout_same_gap = manifest_rows(
        layout_manifest, "same_gap_atom_field_order", "same_gap_atoms"
    )
    same_gap_relations = []
    for row in layout_same_gap:
        root = RANKING.parse_root(str(row["root"]))
        site = str(row["site"])
        gap = int(row["gap_id"])
        controls = sorted(
            (
                edge for edge in edges[root]
                if int(edge["gap_id"]) == gap
            ),
            key=lambda edge: int(edge["offset"]),
        )
        ordered = [int(edge["target"][1]) for edge in controls]
        require(
            site in candidate_sites
            and ordered == [
                int(value)
                for value in row["control_selectors_in_runtime_order"]
            ],
            "same-gap layout reference drifted",
        )
        same_gap_relations.append({
            "all_branches_current_relative_nonexpanding":
                bool(row["all_branches_current_relative_nonexpanding"]),
            "branch_manifest_canonical_sha256":
                str(row["branch_manifest_canonical_sha256"]),
            "cartesian_branch_count": int(row["cartesian_branch_count"]),
            "control_count": len(controls),
            "ordered_targets": [
                {
                    "offset": int(edge["offset"]),
                    "selector": int(edge["target"][1]),
                }
                for edge in controls
            ],
            "root": str(row["root"]),
            "site": site,
            "sibling_selectors": [
                value for value in ordered if value != SELECTOR
            ],
        })
    same_gap_roots = {
        RANKING.parse_root(row["root"]) for row in same_gap_relations
    }
    same_gap_pending_roots = same_gap_roots & set(pending)
    same_gap_pending = {
        coordinate
        for root in same_gap_pending_roots
        for coordinate in pending[root]
    }
    cartesian_observed = (
        len(same_gap_relations),
        len(same_gap_roots),
        len(same_gap_relations),
        len(same_gap_pending_roots),
        len(same_gap_pending),
        sum(
            int(row["cartesian_branch_count"])
            for row in same_gap_relations
        ),
    )
    require(
        cartesian_observed == EXPECTED_CARTESIAN,
        f"same-gap Cartesian scope drifted: {cartesian_observed}",
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
        ledger_row = pk_ledger[coordinate]
        terminal_manifest.append({
            "automatic_status_promotion_authorized": False,
            "candidate_current_identical":
                candidate[root].data == current[root].data,
            "coordinate": coordinate,
            "read_only": True,
            "runtime_review": ledger_row["runtime_review"],
            "scope_classification": ledger_row["scope_classification"],
        })
    terminal_states = (
        sum(row["runtime_review"] == "verified" for row in terminal_manifest),
        sum(row["runtime_review"] == "pending" for row in terminal_manifest),
    )
    require(
        terminal_states == EXPECTED_TERMINAL_STATES
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
        len(source_only) == 5
        and ASSIGNMENT.site_digest(source_only)
        == EXPECTED_SOURCE_ONLY_SHA256,
        "source-only scope drifted",
    )

    hard_block_roots = (
        {RANKING.parse_root(root) for root in owned_roots}
        | same_gap_pending_roots
    )
    hard_block_pending = {
        coordinate
        for root in hard_block_roots
        for coordinate in pending[root]
    }
    rewrite_roots = reachable - hard_block_roots
    rewrite_pending = {
        coordinate
        for root in rewrite_roots
        for coordinate in pending[root]
    }
    ordinary_pending_roots = reachable - same_gap_pending_roots
    require(
        (len(hard_block_roots), len(hard_block_pending))
        == EXPECTED_HARD_BLOCKS
        and (len(rewrite_roots), len(rewrite_pending))
        == EXPECTED_REWRITE_CANDIDATES
        and len(ordinary_pending_roots) * 7
        == EXPECTED_ORDINARY_PENDING_BRANCHES,
        "review partition drifted",
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
    observed_flags = (
        expansion_count, grammar_count, maximum_expansion
    )
    if EXPECTED_FLAG_COUNTS is not None:
        require(
            observed_flags == EXPECTED_FLAG_COUNTS,
            f"risk flags drifted: {observed_flags}",
        )

    atomic_sensitive = (
        template_union | register_union | same_gap_roots
        | {RANKING.parse_root(root) for root in owned_roots}
    )
    require(
        len(atomic_sensitive) == EXPECTED_ATOMIC_SENSITIVE_ROOTS,
        "atomic-sensitive union drifted",
    )
    root_to_chunk = {
        RANKING.parse_root(root): int(chunk["chunk_id"])
        for chunk in private["chunks"]
        for root in chunk["roots"]
    }
    for groups, message in (
        (templates, "template atom split"),
        (register_groups, "register atom split"),
    ):
        require(
            all(
                len({root_to_chunk[root] for root in group}) == 1
                for group in groups
            ),
            message,
        )

    private["schema"] = PRIVATE_SCHEMA
    private["method"] = METHOD
    private["inputs"].update({
        "context_inventory_sha256": EXPECTED_CONTEXT_MANIFEST_SHA256,
        "layout_manifest_sha256": EXPECTED_LAYOUT_MANIFEST_SHA256,
    })
    private["scope"]["selector_coordinate"] = "0:292:0"
    private["identical_template_atoms"] = [
        [RANKING.root_string(root) for root in sorted(group)]
        for group in templates
    ]
    private["register_root_atoms"] = [
        [RANKING.root_string(root) for root in sorted(group)]
        for group in register_groups
    ]
    private["register_repeat_risk"] = {
        "automatic_atom_union_authorized": False,
        "root": REGISTER_REPEAT_RISK_ROOT,
        "reason":
            "candidate_repeat_but_jp_teaching_expression_differs",
    }
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
    private["review_partition"] = {
        "hard_block_pending_coordinates": sorted(
            hard_block_pending, key=RANKING.parse_coordinate
        ),
        "hard_block_roots": [
            RANKING.root_string(root) for root in sorted(hard_block_roots)
        ],
        "hard_block_rule":
            "completed_owned_overlap_or_pending_same_gap_cartesian",
        "ordinary_pending_branch_count": EXPECTED_ORDINARY_PENDING_BRANCHES,
        "rewrite_candidate_pending_coordinates": sorted(
            rewrite_pending, key=RANKING.parse_coordinate
        ),
        "rewrite_candidate_roots": [
            RANKING.root_string(root) for root in sorted(rewrite_roots)
        ],
        "root_rewrite_maximum": 1,
    }
    private["reused_evidence"] = {
        "cartesian_branches_recomputed": 0,
        "context_inventory_path": CONTEXT_MANIFEST_PATH.name,
        "layout_manifest_path": LAYOUT_MANIFEST_PATH.name,
        "same_gap_cartesian_branches_reused": EXPECTED_CARTESIAN[-1],
    }

    structural_union = template_union | register_union
    private_chunks = {int(row["chunk_id"]): row for row in private["chunks"]}
    for chunk in private["chunks"]:
        roots = {RANKING.parse_root(root) for root in chunk["roots"]}
        root_strings = {RANKING.root_string(root) for root in roots}
        chunk["atomic_sensitive_root_count"] = len(roots & atomic_sensitive)
        chunk["completed_selector_overlap_relation_count"] = sum(
            root in root_strings for root, _selector in owned_relations
        )
        chunk["hard_block_pending_row_count"] = len(
            set(chunk["pending_coordinates"]) & hard_block_pending
        )
        chunk["hard_block_root_count"] = len(roots & hard_block_roots)
        chunk["prior_assembly_evidence_pending_row_count"] = len(
            set(chunk["pending_coordinates"]) & assembly_coordinates
        )
        chunk["prior_assembly_evidence_root_count"] = len(
            root_strings & assembly_roots
        )
        chunk["register_root_count"] = len(roots & register_union)
        chunk["register_root_sha256"] = ASSIGNMENT.root_digest(
            roots & register_union
        )
        chunk["rewrite_candidate_pending_row_count"] = len(
            set(chunk["pending_coordinates"]) & rewrite_pending
        )
        chunk["rewrite_candidate_root_count"] = len(roots & rewrite_roots)
        chunk["same_gap_atom_count"] = len(roots & same_gap_roots)
        chunk["same_gap_cartesian_branch_count"] = sum(
            int(row["cartesian_branch_count"])
            for row in same_gap_relations
            if RANKING.parse_root(row["root"]) in roots
        )
        chunk["structural_relation_root_count"] = len(
            roots & structural_union
        )
        chunk["template_root_count"] = len(roots & template_union)
        chunk["template_root_sha256"] = ASSIGNMENT.root_digest(
            roots & template_union
        )

    observed_chunks = tuple(
        (
            int(row["site_count"]),
            int(row["root_count"]),
            int(row["pending_root_count"]),
            int(row["pending_row_upper_bound"]),
            int(row["owned_overlap_root_count"]),
            int(row["workload_weight"]),
        )
        for row in private["chunks"]
    )
    if EXPECTED_CHUNK_METRICS is not None:
        require(
            observed_chunks == EXPECTED_CHUNK_METRICS,
            f"selector292 chunk drift: {observed_chunks}",
        )

    public["schema"] = PUBLIC_SCHEMA
    public["method"] = METHOD
    public["inputs"].update({
        "context_inventory_sha256": EXPECTED_CONTEXT_MANIFEST_SHA256,
        "layout_manifest_sha256": EXPECTED_LAYOUT_MANIFEST_SHA256,
    })
    public["scope"]["selector"] = SELECTOR
    public["scope"]["official_pending_rows"] = 6_151
    public["assignment"].update({
        "atomic_sensitive_root_count": len(atomic_sensitive),
        "giant_atom_created": False,
        "identical_template_atom_count": len(templates),
        "identical_template_root_count": len(template_union),
        "maximum_assignment_atom_root_count": 2,
        "multi_control_atom_count": len(same_gap_roots),
        "register_atom_count": len(register_groups),
        "register_root_count": len(register_union),
        "same_gap_atom_count": len(same_gap_roots),
        "same_gap_atom_split": False,
        "same_gap_cartesian_branch_count": EXPECTED_CARTESIAN[-1],
        "same_gap_sibling_family_count": len({
            selector
            for row in same_gap_relations
            for selector in row["sibling_selectors"]
        }),
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
    public["review_partition"] = {
        "automatic_status_promotion_authorized": False,
        "hard_block_pending_row_count": len(hard_block_pending),
        "hard_block_root_count": len(hard_block_roots),
        "ordinary_pending_branch_count": EXPECTED_ORDINARY_PENDING_BRANCHES,
        "rewrite_candidate_pending_row_count": len(rewrite_pending),
        "rewrite_candidate_root_count": len(rewrite_roots),
        "root_rewrite_maximum": 1,
    }
    public["terminal_compatibility"] = {
        "automatic_status_promotion_authorized": False,
        "candidate_current_different_terminal_count":
            EXPECTED_TERMINAL_COMPARISON[1],
        "candidate_current_identical_terminal_count":
            EXPECTED_TERMINAL_COMPARISON[0],
        "context_terminals_authoritative": False,
        "read_only_pending_terminal_count": EXPECTED_TERMINAL_STATES[1],
        "read_only_verified_terminal_count": EXPECTED_TERMINAL_STATES[0],
    }
    public["reused_private_evidence"] = {
        "cartesian_branches_recomputed": 0,
        "context_inventory_sha256": EXPECTED_CONTEXT_MANIFEST_SHA256,
        "layout_manifest_sha256": EXPECTED_LAYOUT_MANIFEST_SHA256,
        "same_gap_cartesian_branches_reused": EXPECTED_CARTESIAN[-1],
    }
    for chunk in public["assignment"]["chunks"]:
        source_chunk = private_chunks[int(chunk["chunk_id"])]
        for key in (
            "atomic_sensitive_root_count",
            "completed_selector_overlap_relation_count",
            "hard_block_pending_row_count",
            "hard_block_root_count",
            "prior_assembly_evidence_pending_row_count",
            "prior_assembly_evidence_root_count",
            "register_root_count",
            "register_root_sha256",
            "rewrite_candidate_pending_row_count",
            "rewrite_candidate_root_count",
            "same_gap_atom_count",
            "same_gap_cartesian_branch_count",
            "structural_relation_root_count",
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
    private_content, public_content, private, public = build_outputs()
    private_sha = ASSIGNMENT.sha256_bytes(private_content.encode("utf-8"))
    public_sha = ASSIGNMENT.sha256_bytes(public_content.encode("utf-8"))
    site_row_sha = public["assignment"]["site_risk_matrix_sha256"]
    observed_flags = (
        sum(
            bool(row["flags"]["layout_relative_expansion"])
            for row in private["site_assignments"]
        ),
        sum(
            bool(row["flags"]["grammar_right_boundary"])
            for row in private["site_assignments"]
        ),
        max(
            int(row["maximum_positive_raw_g1n_delta_px"])
            for row in private["site_assignments"]
        ),
    )
    observed_chunks = tuple(
        (
            int(row["site_count"]),
            int(row["root_count"]),
            int(row["pending_root_count"]),
            int(row["pending_row_upper_bound"]),
            int(row["owned_overlap_root_count"]),
            int(row["workload_weight"]),
        )
        for row in private["chunks"]
    )
    pins_resolved = (
        EXPECTED_SITE_ROW_SHA256 is not None
        and EXPECTED_FLAG_COUNTS is not None
        and EXPECTED_CHUNK_METRICS is not None
        and EXPECTED_PRIVATE_FILE_SHA256 is not None
        and EXPECTED_PUBLIC_FILE_SHA256 is not None
    )
    if args.bootstrap:
        require(not pins_resolved, "bootstrap forbidden after assignment freeze")
    else:
        require(pins_resolved, "assignment bootstrap pins unresolved")
        require(
            site_row_sha == EXPECTED_SITE_ROW_SHA256
            and observed_flags == EXPECTED_FLAG_COUNTS
            and observed_chunks == EXPECTED_CHUNK_METRICS
            and private_sha == EXPECTED_PRIVATE_FILE_SHA256
            and public_sha == EXPECTED_PUBLIC_FILE_SHA256,
            "selector292 assignment output drifted",
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
        "bootstrap_pins": {
            "chunk_metrics": observed_chunks,
            "flag_counts": observed_flags,
            "private_sha256": private_sha,
            "public_sha256": public_sha,
            "site_row_sha256": site_row_sha,
        },
        "hard_block_pending_rows":
            public["review_partition"]["hard_block_pending_row_count"],
        "rewrite_candidate_pending_rows":
            public["review_partition"]["rewrite_candidate_pending_row_count"],
        "same_gap_cartesian_branches":
            public["assignment"]["same_gap_cartesian_branch_count"],
        "steam_write_performed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
