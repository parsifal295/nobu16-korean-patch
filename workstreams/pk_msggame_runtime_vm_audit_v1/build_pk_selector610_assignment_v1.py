#!/usr/bin/env python3
"""Build the immutable two-chunk review assignment for PK selector 610."""

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
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_"
    "post_selector568_1096_1174_v1.py"
)
RANKING_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector568_1096_1174.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector568_1096_1174.source_free.v1.json"
)
LEGACY_ASSIGNMENT_PATH = (
    WORKSTREAM / "build_pk_selector1174_assignment_v1.py"
)
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector568_1096_1174_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector568_1096_1174_consolidated_checkpoint.source_free.v1.json"
)
PREDECESSOR_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector568_1096_1174_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector610_assignment.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector610_assignment_coverage.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector610-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector610-assignment-coverage.v1"
METHOD = (
    "official_fc157a_selector610_fixed7way_"
    "owned_overlap_and_template_isolated_three_chunk_assignment"
)
SELECTOR = 610
TERMINALS = tuple(range(2000, 2007))
CHUNK_COUNT = 3
ANCHOR_A_BLOCKS = frozenset({6, 7, 8, 9, 12})
TEMPLATE_ROOTS = frozenset((15, record_id) for record_id in range(1385, 1409))
TARGET_CHUNK_SITES = (77, 77, 76)

EXPECTED_INPUT_SHA256 = {
    "ledger":
        "FC157A9907686D0EA6DC6C61C7785E81AC7F750100F2E1CDDE02DBF4F09F2DCA",
    "checkpoint_public":
        "1FCF033F1F75FC43473152CFB7115D170657519952C19D563C36C3F9BAB4CBD1",
    "ranking_builder":
        "482B6ED4C810883966E06C6B3E450331BDC69AE1B2C5E5E883B2F5505C7A8E97",
    "ranking_private":
        "183896FC6C6B398C4DF3B93DB993AE2E79104AC70460B63DBA02D870A959CD60",
    "ranking_public":
        "18E80E360667383B359764C02F4F46C7EC1D61E85A27890FB7C5C3FEDD4F7B2F",
    "legacy_assignment":
        "FFAB60E333B547158CBE349D60708BB8D26B1EBF2DE0F56AC7EF512EDD6EEC9E",
    "predecessor_decisions":
        "3260FCF12561EE116228907E1619FDB368DBDF9D0BA8565C03CD014440669B38",
}
EXPECTED_PK_CURRENT_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PK_PRISTINE_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "07E65E6338D32C1FD13F17408F82A4133E55541C722874632948C7B36C909805"
)
EXPECTED_CONTEXT_SHA256 = {
    "en": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "sc": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "tc": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}
EXPECTED_OFFICIAL_PENDING_ROWS = 7_268
EXPECTED_SITE_COUNT = 230
EXPECTED_SITE_SHA256 = (
    "FF7F860EDD682815AEEEC30D61CA6B787BE4038F4FF0BEA0DC8399AAC667F150"
)
EXPECTED_ROOT_SHA256 = (
    "B8190DCB610E251669847EDE32A272FDA8791B3F63D4A369A20134A1D43D93CB"
)
EXPECTED_SOURCE_SITE_COUNT = 243
EXPECTED_SOURCE_SITE_SHA256 = (
    "4927B74B595BEBD13968E16056C13FEF757437A211EBF2F777F7EC4313DBD015"
)
EXPECTED_SOURCE_ONLY_COUNT = 13
EXPECTED_SOURCE_ONLY_SHA256 = (
    "13849017022482E0E115529572418A27B56D83A2923237A604F09733649EDFCF"
)
EXPECTED_DIRECT_PENDING_SITES = 89
EXPECTED_DIRECT_PENDING_SITE_SHA256 = (
    "A3E80B726BA3B7599A971D5F556B3C57ED11C93E86CC11BEBEE9D22E0F5305D3"
)
EXPECTED_POTENTIAL_ROWS = 192
EXPECTED_POTENTIAL_SHA256 = (
    "F4E697FD9096034655675909FF9D13D3EB5D8B2B82020FA4E28A0D7E6E39FF71"
)
EXPECTED_OWNED_OVERLAP_ROOTS = 30
EXPECTED_OWNED_OVERLAP_ROWS = 60
EXPECTED_OWNED_OVERLAP_ROOT_SHA256 = (
    "F109A87025FA7BD5C5BE3B6D8A2680B6A7716C8228ADDD8B4FC4C349F7710D7E"
)
EXPECTED_OWNED_OVERLAP_COORDINATE_SHA256 = (
    "7C7A0272794ACB92DEAC7402165BC1F6A5ED4698FEDACBA818D263E6CA06FCAF"
)
EXPECTED_DISPATCH_NODE_SHA256 = (
    "0B7749F18531ED4DE72CE8DE490072746F890D2F6346A9B840C50F5E33CC2495"
)
EXPECTED_DISPATCH_EDGE_SHA256 = (
    "F22B26BA9FAC606FB2939894366BF2BE1EE607421C297C50C6AB056AED06A0CA"
)
EXPECTED_TERMINAL_SHA256 = (
    "8117451C2F2146019B679526BF61CC0C53CC7B16C136110DD5ACE246FFB24598"
)
EXPECTED_SITE_ROW_SHA256 = (
    "F0BDE657B81030BDF2B1B878E4E9D4E5A55147CFECF6053F54339799ACE3F7B8"
)
EXPECTED_CHUNK_METRICS = (
    (77, 77, 36, 91, 5, 0, 1663),
    (77, 77, 29, 53, 1, 0, 1666),
    (76, 76, 24, 48, 24, 24, 1669),
)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "50A4234CC7207FFF4BCC3049532EC78502E1E8F14565CF1FBFC5399A88D4D036"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "FD98F9289C6F1D429BF03B53252E9C1846262A29419E97ECDCE26695D91E9C2F"
)


class AssignmentError(ValueError):
    """Raised when selector-610 assignment evidence drifts."""


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


RANKING = load_module(RANKING_BUILDER_PATH, "pk_selector610_ranking_v1")
RANKING.CONTROL_RE = RANKING.LEGACY.CONTROL_RE
LEGACY_ASSIGNMENT = load_module(
    LEGACY_ASSIGNMENT_PATH, "pk_selector610_assignment_helpers_v1"
)
LEGACY_ASSIGNMENT.RANKING = RANKING
LEGACY_ASSIGNMENT.ENGINE = RANKING.ENGINE
LEGACY_ASSIGNMENT.SELECTOR = SELECTOR
LEGACY_ASSIGNMENT.TERMINALS = TERMINALS
ENGINE = RANKING.ENGINE
sha256_file = RANKING.sha256_file
sha256_bytes = RANKING.sha256_bytes
coordinate_digest = RANKING.coordinate_digest
root_digest = RANKING.root_digest
site_digest = RANKING.site_digest
canonical_sha256 = RANKING.canonical_sha256


def serialized_json(value: Any) -> str:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    )


def load_records() -> tuple[
    dict[tuple[int, int], Any],
    dict[tuple[int, int], Any],
    dict[tuple[int, int], Any],
    dict[str, dict[tuple[int, int], Any]],
    dict[tuple[int, int], set[str]],
]:
    steam_root = RANKING.DEFAULT_STEAM_ROOT
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
    context_paths = {
        language: steam_root / "MSG_PK" / language.upper() / "msggame.bin"
        for language in ("en", "sc", "tc")
    }
    require(
        sha256_file(current_path) == EXPECTED_PK_CURRENT_SHA256
        and sha256_file(pristine_path) == EXPECTED_PK_PRISTINE_SHA256,
        "PK current/pristine input drifted",
    )
    require(
        {
            language: sha256_file(path)
            for language, path in context_paths.items()
        }
        == EXPECTED_CONTEXT_SHA256,
        "PK multilingual context input drifted",
    )
    replacements, pending = RANKING.load_official_ledger(
        OFFICIAL_LEDGER_PATH
    )
    current_blob = current_path.read_bytes()
    candidate_blob = ENGINE.rebuild_packed_with_literals(
        current_blob, replacements
    )
    require(
        sha256_bytes(candidate_blob) == EXPECTED_PK_CANDIDATE_SHA256,
        "official candidate reconstruction drifted",
    )

    def records(blob: bytes) -> dict[tuple[int, int], Any]:
        return ENGINE.archive_records(
            ENGINE.parse_packed_msggame(blob).archive
        )

    candidate = records(candidate_blob)
    current = records(current_blob)
    source = records(pristine_path.read_bytes())
    contexts = {
        language: records(path.read_bytes())
        for language, path in context_paths.items()
    }
    require(
        set(candidate)
        == set(current)
        == set(source)
        == set(contexts["en"])
        == set(contexts["sc"])
        == set(contexts["tc"]),
        "PK multilingual record universe drifted",
    )
    return candidate, current, source, contexts, pending


def predecessor_decision_roots() -> set[tuple[int, int]]:
    roots: set[tuple[int, int]] = set()
    row_count = 0
    for line in PREDECESSOR_DECISIONS_PATH.read_text(
        encoding="utf-8"
    ).splitlines():
        if not line:
            continue
        row_count += 1
        coordinate = str(json.loads(line)["coordinate"])
        roots.add(RANKING.parse_coordinate(coordinate)[:2])
    require(row_count == 1_173, "predecessor decision count drifted")
    return roots


def anchored_three_way_balance(
    rows: Sequence[Mapping[str, Any]],
    pending_roots: set[tuple[int, int]],
) -> tuple[list[dict[str, Any]], ...]:
    root_of = lambda row: RANKING.parse_root(str(row["root"]))
    anchor_a = {
        root for root in pending_roots if root[0] in ANCHOR_A_BLOCKS
    }
    anchor_c = set(TEMPLATE_ROOTS)
    anchor_b = pending_roots - anchor_a - anchor_c
    require(
        tuple(len(group) for group in (anchor_a, anchor_b, anchor_c))
        == (36, 29, 24),
        "pending anchor-root counts drifted",
    )
    target_weight = (
        sum(int(row["workload_weight"]) for row in rows) / CHUNK_COUNT
    )

    def fill(
        mandatory_roots: set[tuple[int, int]],
        pool_blocks: set[int],
        target_count: int,
    ) -> list[dict[str, Any]]:
        mandatory = [
            dict(row) for row in rows if root_of(row) in mandatory_roots
        ]
        pool = [
            dict(row)
            for row in rows
            if root_of(row) not in pending_roots
            and root_of(row)[0] in pool_blocks
        ]
        selected: list[dict[str, Any]] = []
        selected_sites: set[str] = set()
        weight = sum(int(row["workload_weight"]) for row in mandatory)
        while len(mandatory) + len(selected) < target_count:
            slots = target_count - len(mandatory) - len(selected)
            desired = (target_weight - weight) / slots
            choice = min(
                (
                    row
                    for row in pool
                    if str(row["site"]) not in selected_sites
                ),
                key=lambda row: (
                    abs(int(row["workload_weight"]) - desired),
                    RANKING.site_key(str(row["site"])),
                ),
            )
            selected.append(choice)
            selected_sites.add(str(choice["site"]))
            weight += int(choice["workload_weight"])
        return mandatory + selected

    chunk0 = fill(anchor_a, set(ANCHOR_A_BLOCKS) | {13}, 77)
    chunk1 = fill(anchor_b, {15}, 77)
    used = {str(row["site"]) for row in chunk0 + chunk1}
    chunk2 = [dict(row) for row in rows if str(row["site"]) not in used]
    return tuple(
        sorted(chunk, key=lambda row: RANKING.site_key(str(row["site"])))
        for chunk in (chunk0, chunk1, chunk2)
    )


def assert_source_free(value: Any) -> None:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            content,
        )
        is None,
        "public assignment contains CJK text",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", content) is None,
        "public assignment contains an exact coordinate",
    )
    require('"translation"' not in content, "public contains translation")


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    immutable = {
        OFFICIAL_LEDGER_PATH: EXPECTED_INPUT_SHA256["ledger"],
        CHECKPOINT_PUBLIC_PATH: EXPECTED_INPUT_SHA256["checkpoint_public"],
        RANKING_BUILDER_PATH: EXPECTED_INPUT_SHA256["ranking_builder"],
        RANKING_PRIVATE_PATH: EXPECTED_INPUT_SHA256["ranking_private"],
        RANKING_PUBLIC_PATH: EXPECTED_INPUT_SHA256["ranking_public"],
        LEGACY_ASSIGNMENT_PATH: EXPECTED_INPUT_SHA256["legacy_assignment"],
        PREDECESSOR_DECISIONS_PATH:
            EXPECTED_INPUT_SHA256["predecessor_decisions"],
    }
    for path, expected in immutable.items():
        require(
            path.is_file() and sha256_file(path) == expected,
            f"immutable input drifted: {path}",
        )
    ranking_private = json.loads(
        RANKING_PRIVATE_PATH.read_text(encoding="utf-8")
    )
    ranking_public = json.loads(
        RANKING_PUBLIC_PATH.read_text(encoding="ascii")
    )
    target = next(
        row
        for row in ranking_private["direct_targets"]
        if row["target_coordinate"] == f"0:{SELECTOR}"
    )
    require(
        ranking_public["recommendation"]["selector_coordinate"]
        == f"0:{SELECTOR}"
        and target["classification"]
        == "eligible_fixed_seven_way_selector",
        "ranking handoff drifted",
    )

    candidate, current, source, contexts, pending = load_records()
    candidate_edges = RANKING.graph_edges(candidate)
    source_edges = RANKING.graph_edges(source)
    candidate_sites = RANKING.candidate_call_sites(candidate_edges)[
        (0, SELECTOR)
    ]
    source_sites = RANKING.candidate_call_sites(source_edges)[(0, SELECTOR)]
    candidate_roots = {
        RANKING.site_key(site)[:2] for site in candidate_sites
    }
    source_only = set(source_sites) - set(candidate_sites)
    candidate_only = set(candidate_sites) - set(source_sites)
    direct_pending_sites = [
        site
        for site in candidate_sites
        if RANKING.site_key(site)[:2] in pending
    ]
    reachable_roots = {
        RANKING.parse_root(root)
        for root in target["reachable_pending_roots"]
    }
    potential = {
        coordinate
        for root in reachable_roots
        for coordinate in pending[root]
    }
    predecessor_decision_roots()
    prior_coordinates = {
        str(json.loads(line)["coordinate"])
        for line in PREDECESSOR_DECISIONS_PATH.read_text(
            encoding="utf-8"
        ).splitlines()
        if line
    }
    require(
        not potential & prior_coordinates,
        "FC157A pending unexpectedly overlaps predecessor decisions",
    )
    owned_roots_by_selector: dict[int, set[tuple[int, int]]] = {
        selector: set() for selector in RANKING.OWNED_SELECTORS
    }
    for root in reachable_roots:
        calls = RANKING.reachable_call_targets(candidate_edges, root)
        for selector in owned_roots_by_selector:
            if (0, selector) in calls:
                owned_roots_by_selector[selector].add(root)
    owned_overlap_roots = set().union(*owned_roots_by_selector.values())
    owned_overlap_coordinates = {
        coordinate
        for root in owned_overlap_roots
        for coordinate in pending[root]
    }
    shape = RANKING.family_shape(
        candidate_edges, source_edges, (0, SELECTOR)
    )
    require(
        len(candidate_sites) == EXPECTED_SITE_COUNT
        and site_digest(candidate_sites) == EXPECTED_SITE_SHA256
        and len(candidate_roots) == EXPECTED_SITE_COUNT
        and root_digest(candidate_roots) == EXPECTED_ROOT_SHA256
        and len(source_sites) == EXPECTED_SOURCE_SITE_COUNT
        and site_digest(source_sites) == EXPECTED_SOURCE_SITE_SHA256
        and len(source_only) == EXPECTED_SOURCE_ONLY_COUNT
        and site_digest(source_only) == EXPECTED_SOURCE_ONLY_SHA256
        and not candidate_only
        and len(direct_pending_sites) == EXPECTED_DIRECT_PENDING_SITES
        and site_digest(direct_pending_sites)
        == EXPECTED_DIRECT_PENDING_SITE_SHA256
        and len(potential) == EXPECTED_POTENTIAL_ROWS
        and coordinate_digest(potential) == EXPECTED_POTENTIAL_SHA256
        and len(owned_overlap_roots) == EXPECTED_OWNED_OVERLAP_ROOTS
        and len(owned_overlap_coordinates) == EXPECTED_OWNED_OVERLAP_ROWS
        and root_digest(owned_overlap_roots)
        == EXPECTED_OWNED_OVERLAP_ROOT_SHA256
        and coordinate_digest(owned_overlap_coordinates)
        == EXPECTED_OWNED_OVERLAP_COORDINATE_SHA256,
        "selector-610 coverage drifted",
    )
    require(
        shape["seven_way"]
        and root_digest(shape["candidate_nodes"])
        == EXPECTED_DISPATCH_NODE_SHA256
        and RANKING.edge_digest(shape["candidate_dispatch"])
        == EXPECTED_DISPATCH_EDGE_SHA256
        and root_digest(shape["candidate_leaves"])
        == EXPECTED_TERMINAL_SHA256,
        "selector-610 dispatch drifted",
    )
    require(
        target["candidate_call_sites"] == candidate_sites
        and target["source_call_sites"] == source_sites
        and set(target["current_pending_coordinates"]) == potential,
        "ranking detail handoff drifted",
    )

    site_rows = LEGACY_ASSIGNMENT.build_site_rows(
        sites=candidate_sites,
        candidate=candidate,
        current=current,
        source=source,
        contexts=contexts,
    )
    require(
        canonical_sha256(site_rows) == EXPECTED_SITE_ROW_SHA256,
        "site risk matrix drifted",
    )
    chunk_rows = anchored_three_way_balance(site_rows, reachable_roots)
    chunks: list[dict[str, Any]] = []
    for chunk_id, members in enumerate(chunk_rows):
        roots = {
            RANKING.parse_root(str(row["root"])) for row in members
        }
        chunk_pending = {
            coordinate
            for root in roots
            for coordinate in pending.get(root, set())
        }
        chunk_owned = roots & owned_overlap_roots
        chunk_template = roots & set(TEMPLATE_ROOTS)
        chunk_pending_roots = roots & reachable_roots
        flags: Counter[str] = Counter()
        languages: Counter[str] = Counter()
        for row in members:
            flags.update(
                key for key, value in row["flags"].items() if value
            )
            languages.update(
                key
                for key, value in row["language_available"].items()
                if value
            )
        chunks.append(
            {
                "chunk_id": chunk_id,
                "flag_counts": {
                    key: flags[key]
                    for key in sorted(site_rows[0]["flags"])
                },
                "language_available_counts": {
                    key: languages[key]
                    for key in sorted(site_rows[0]["language_available"])
                },
                "pending_coordinates": sorted(
                    chunk_pending, key=RANKING.parse_coordinate
                ),
                "pending_row_upper_bound": len(chunk_pending),
                "pending_sha256": coordinate_digest(chunk_pending),
                "owned_overlap_root_count": len(chunk_owned),
                "owned_overlap_root_sha256": root_digest(chunk_owned),
                "pending_root_count": len(chunk_pending_roots),
                "pending_root_sha256": root_digest(chunk_pending_roots),
                "root_count": len(roots),
                "root_sha256": root_digest(roots),
                "roots": [
                    RANKING.root_string(root) for root in sorted(roots)
                ],
                "site_count": len(members),
                "site_sha256": site_digest(
                    str(row["site"]) for row in members
                ),
                "sites": [str(row["site"]) for row in members],
                "template_root_count": len(chunk_template),
                "template_root_sha256": root_digest(chunk_template),
                "workload_weight": sum(
                    int(row["workload_weight"]) for row in members
                ),
            }
        )
    observed = tuple(
        (
            chunk["site_count"],
            chunk["root_count"],
            chunk["pending_root_count"],
            chunk["pending_row_upper_bound"],
            chunk["owned_overlap_root_count"],
            chunk["template_root_count"],
            chunk["workload_weight"],
        )
        for chunk in chunks
    )
    require(observed == EXPECTED_CHUNK_METRICS, f"chunk drift: {observed}")
    require(
        not any(
            set(chunks[left]["roots"]) & set(chunks[right]["roots"])
            for left in range(CHUNK_COUNT)
            for right in range(left + 1, CHUNK_COUNT)
        )
        and set().union(*(set(chunk["sites"]) for chunk in chunks))
        == set(candidate_sites)
        and chunks[2]["template_root_count"] == 24
        and sum(chunk["template_root_count"] for chunk in chunks) == 24,
        "root partition or risk isolation drifted",
    )

    common_inputs = {
        "official_integrated_ledger_sha256":
            EXPECTED_INPUT_SHA256["ledger"],
        "official_public_checkpoint_sha256":
            EXPECTED_INPUT_SHA256["checkpoint_public"],
        "ranking_builder_sha256":
            EXPECTED_INPUT_SHA256["ranking_builder"],
        "ranking_private_sha256":
            EXPECTED_INPUT_SHA256["ranking_private"],
        "ranking_public_sha256":
            EXPECTED_INPUT_SHA256["ranking_public"],
        "predecessor_decisions_sha256":
            EXPECTED_INPUT_SHA256["predecessor_decisions"],
        "pk_context_sha256": EXPECTED_CONTEXT_SHA256,
        "pk_current_sha256": EXPECTED_PK_CURRENT_SHA256,
        "pk_pristine_sha256": EXPECTED_PK_PRISTINE_SHA256,
        "pk_rebuilt_candidate_sha256": EXPECTED_PK_CANDIDATE_SHA256,
    }
    private: dict[str, Any] = {
        "schema": PRIVATE_SCHEMA,
        "method": METHOD,
        "inputs": common_inputs,
        "scope": {
            "selector_coordinate": f"0:{SELECTOR}:0",
            "terminal_coordinates": [
                f"0:{terminal}:0" for terminal in TERMINALS
            ],
            "candidate_call_sites": candidate_sites,
            "source_call_sites": source_sites,
            "source_only_repair_sites": sorted(
                source_only, key=RANKING.site_key
            ),
            "direct_pending_call_sites": direct_pending_sites,
            "potential_current_pending_coordinates": sorted(
                potential, key=RANKING.parse_coordinate
            ),
            "owned_overlap_roots": [
                RANKING.root_string(root)
                for root in sorted(owned_overlap_roots)
            ],
        },
        "site_assignments": site_rows,
        "chunks": chunks,
        "privacy": {
            "contains_dialogue_bodies": False,
            "contains_translations": False,
            "shared_integration_mutated": False,
            "steam_write_performed": False,
        },
    }
    private["guards"] = {
        "chunks_canonical_sha256": canonical_sha256(chunks),
        "site_assignments_canonical_sha256": canonical_sha256(site_rows),
        "payload_without_guards_canonical_sha256":
            canonical_sha256(private),
    }
    private_content = serialized_json(private)
    public_chunks = [
        {
            key: chunk[key]
            for key in (
                "chunk_id",
                "flag_counts",
                "language_available_counts",
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
        for chunk in chunks
    ]
    public: dict[str, Any] = {
        "schema": PUBLIC_SCHEMA,
        "method": METHOD,
        "inputs": common_inputs,
        "scope": {
            "resource": "MSG_PK/JP/msggame.bin",
            "selector": SELECTOR,
            "terminal_count": len(TERMINALS),
            "terminal_coordinate_sha256": EXPECTED_TERMINAL_SHA256,
            "official_pending_rows": EXPECTED_OFFICIAL_PENDING_ROWS,
        },
        "dispatch_contract": {
            "source_candidate_identical": True,
            "node_count": 13,
            "node_sha256": EXPECTED_DISPATCH_NODE_SHA256,
            "edge_count": 13,
            "edge_sha256": EXPECTED_DISPATCH_EDGE_SHA256,
            "terminal_count": 7,
            "terminal_coordinate_sha256": EXPECTED_TERMINAL_SHA256,
        },
        "coverage": {
            "candidate_call_site_count": len(candidate_sites),
            "candidate_call_site_sha256": site_digest(candidate_sites),
            "candidate_call_root_count": len(candidate_roots),
            "candidate_call_root_sha256": root_digest(candidate_roots),
            "source_call_site_count": len(source_sites),
            "source_call_site_sha256": site_digest(source_sites),
            "source_only_repair_site_count": len(source_only),
            "source_only_repair_site_sha256": site_digest(source_only),
            "direct_pending_call_site_count": len(direct_pending_sites),
            "direct_pending_call_site_sha256":
                site_digest(direct_pending_sites),
            "potential_current_pending_rows": len(potential),
            "potential_current_pending_sha256":
                coordinate_digest(potential),
            "owned_overlap_root_count": len(owned_overlap_roots),
            "owned_overlap_root_sha256":
                root_digest(owned_overlap_roots),
            "owned_overlap_pending_rows":
                len(owned_overlap_coordinates),
            "owned_overlap_pending_sha256":
                coordinate_digest(owned_overlap_coordinates),
            "owned_overlap_selector_counts": {
                str(selector): {
                    "pending_root_count": len(roots),
                    "pending_row_count": sum(
                        len(pending[root]) for root in roots
                    ),
                }
                for selector, roots
                in sorted(owned_roots_by_selector.items())
            },
            "pending_predecessor_coordinate_overlap_rows": 0,
        },
        "assignment": {
            "chunk_count": CHUNK_COUNT,
            "root_split_permitted": False,
            "template_roots_indivisible_chunk": 2,
            "source_only_calls_deferred_to_repair_review": True,
            "site_risk_matrix_sha256": canonical_sha256(site_rows),
            "chunks": public_chunks,
        },
        "privacy": {
            "contains_commercial_source_text": False,
            "contains_dialogue_bodies": False,
            "contains_exact_coordinates": False,
            "contains_translations": False,
            "private_assignment_stays_below_tmp": True,
            "shared_integration_mutated": False,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    public["guards"] = {
        "private_assignment_sha256":
            sha256_bytes(private_content.encode("utf-8")),
        "payload_without_guards_canonical_sha256":
            canonical_sha256(public),
    }
    assert_source_free(public)
    return private_content, serialized_json(public), private, public


def validate_outputs(
    private_content: str,
    public_content: str,
    *,
    frozen: bool,
) -> None:
    private_sha = sha256_bytes(private_content.encode("utf-8"))
    public_sha = sha256_bytes(public_content.encode("utf-8"))
    if frozen:
        require(
            private_sha == EXPECTED_PRIVATE_FILE_SHA256,
            f"private output drifted: {private_sha}",
        )
        require(
            public_sha == EXPECTED_PUBLIC_FILE_SHA256,
            f"public output drifted: {public_sha}",
        )


def validate_paths(args: argparse.Namespace) -> None:
    private = args.private_output.resolve()
    tmp_root = DIALOGUE_TMP.resolve()
    require(
        tmp_root in private.parents,
        "private output must remain below tmp",
    )
    require(
        args.public_output.resolve() == DEFAULT_PUBLIC_OUTPUT.resolve(),
        "public output must use fixed tracked path",
    )
    require(
        "steamapps" not in str(private).lower(),
        "assignment output cannot target Steam data",
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
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
    validate_paths(args)
    private_content, public_content, _private, public = build_outputs()
    validate_outputs(
        private_content,
        public_content,
        frozen=EXPECTED_PRIVATE_FILE_SHA256 is not None,
    )
    if args.check:
        require(
            args.private_output.is_file()
            and args.private_output.read_bytes()
            == private_content.encode("utf-8"),
            "private artifact drifted",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_bytes()
            == public_content.encode("utf-8"),
            "public artifact drifted",
        )
    else:
        args.private_output.parent.mkdir(parents=True, exist_ok=True)
        args.public_output.parent.mkdir(parents=True, exist_ok=True)
        args.private_output.write_bytes(private_content.encode("utf-8"))
        args.public_output.write_bytes(public_content.encode("utf-8"))
    print(
        json.dumps(
            {
                "chunks": [
                    {
                        "chunk": row["chunk_id"],
                        "pending": row["pending_row_upper_bound"],
                        "owned_overlap_roots":
                            row["owned_overlap_root_count"],
                        "sites": row["site_count"],
                        "weight": row["workload_weight"],
                    }
                    for row in public["assignment"]["chunks"]
                ],
                "private_sha256":
                    sha256_bytes(private_content.encode("utf-8")),
                "public_sha256":
                    sha256_bytes(public_content.encode("utf-8")),
                "source_only_repair_sites":
                    public["coverage"][
                        "source_only_repair_site_count"
                    ],
                "steam_write_performed": False,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
