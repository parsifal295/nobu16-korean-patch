#!/usr/bin/env python3
"""Build the private selector-1096 assignment and source-free graph report."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
BASE_BUILDER_PATH = WORKSTREAM / "build_pk_selector568_assignment_v1.py"
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_bound_terminal_2546_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration."
    "post_bound_terminal_2546_checkpoint.source_free.v1.json"
)
CURRENT_A19_LEDGER_PATH = (
    DIALOGUE_TMP / "runtime_vm_integrated.private.v1.jsonl"
)
SELECTOR538_DECISION_PATHS = tuple(
    DIALOGUE_TMP
    / "semantic_overrides"
    / f"pk_selector538_chunk{chunk_id}_closure_decisions.private.v1.jsonl"
    for chunk_id in range(4)
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP / "family1096_assignment.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1096_assignment_coverage.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector1096-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector1096-assignment-coverage.v1"
METHOD = "reversed_vm_pk_selector1096_deterministic_assignment"
SELECTOR = 1096
TERMINALS = tuple(range(2581, 2588))
CHUNK_COUNT = 3
MIN_CHUNK_SITES = 50
MAX_CHUNK_SITES = 90
EXPECTED_CUTS = (56, 115, 172)

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_PK_PRISTINE_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PK_CURRENT_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_CURRENT_A19_LEDGER_SHA256 = (
    "6945B4CBAD745A808CE306599FCC5BB7C17068414AD7B085E59B02BC20818165"
)
EXPECTED_SELECTOR538_DECISION_SHA256 = (
    "6B002FF3565B1BAAED58064BA2351232B443A3B43350BD7BE9ADAFD1ED117BBF",
    "1FFA7BF45AA7DE0E53EFE3ED59BDED1E824A39F3E2CC4FD0E8CFFAC6D28A4D70",
    "1AFCCCF416F1EFFB04DAA045139E85E16D96668EB4E8F7A8CE41B6362C573BB2",
    "21F647B8D680DDA3639A95F289AAD8E9B442C00F05378CB213EEC847AE8CFC8C",
)
EXPECTED_PENDING_ROWS = 8_213
EXPECTED_CURRENT_A19_PENDING_ROWS = 8_113
EXPECTED_SITE_COUNT = 172
EXPECTED_SITE_SHA256 = (
    "D0EA848DB96E9D7D2DACC6616BBC7F83FAD71D994C8C831E8FAF79DE79780530"
)
EXPECTED_ROOT_COUNT = 171
EXPECTED_ROOT_SHA256 = (
    "DBE071033D8A2C1AB7F87198EAA98B9A12553F19F4F3135857A59982CA9967DE"
)
EXPECTED_SOURCE_SITE_COUNT = 188
EXPECTED_SOURCE_SITE_SHA256 = (
    "877F50E5F3559B81873F8B7CB09974DF78EB65D8664D149567ED730279297EA8"
)
EXPECTED_SOURCE_ROOT_COUNT = 187
EXPECTED_SOURCE_ROOT_SHA256 = (
    "11080D61E21BD09458B6E1D9FE9945955F611C7E92F5F74C9D38F625395932F0"
)
EXPECTED_SOURCE_ONLY_SITES = 16
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "E4220A8E906AFFA5BF963EE44041ADBF3BCACCFDDFB97051665F591D0474154F"
)
EXPECTED_CANDIDATE_ONLY_SITES = 0
EXPECTED_CANDIDATE_ONLY_SITE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_TERMINAL_COORDINATE_SHA256 = (
    "29CE977C1D409E7D2072AB16EF036004A68AE2BFB43D0A6DE52DD87054E236A7"
)
EXPECTED_DIRECT_PENDING_ROOTS = 115
EXPECTED_DIRECT_PENDING_ROOT_SHA256 = (
    "6802CAC3B1D6DAF4F2C4523A7D73D247F975E1DFFFBCB287524371F48CBDDD06"
)
EXPECTED_DIRECT_PENDING_ROWS = 263
EXPECTED_DIRECT_PENDING_COORDINATE_SHA256 = (
    "D67CEAA8B9AE6702FCD9CA029D1C65B27E46F77EA5D39DEE760C25D3CE7DD72E"
)
EXPECTED_CURRENT_LIVE_PENDING_ROWS = 258
EXPECTED_CURRENT_LIVE_PENDING_COORDINATE_SHA256 = (
    "716BB07569A899808ABEA6525D1AC2306897954D51B73A6C6D89C939F0BB448F"
)
EXPECTED_ALREADY_PROMOTED_ROWS = 5
EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256 = (
    "7C53C00911001CCC4C81EA047166B468BF1404255ABD4407F04EB763548537DE"
)
EXPECTED_SELECTOR538_PLANNED_PROMOTION_ROWS = 277
EXPECTED_SELECTOR538_PLANNED_PROMOTION_COORDINATE_SHA256 = (
    "B6D1D61B1681F9CA92AD6DCD2C43F4913D83916C0DC5BFE05A4C0BFEC3BED5C1"
)
EXPECTED_SELECTOR538_OVERLAP_ROWS = 16
EXPECTED_SELECTOR538_OVERLAP_COORDINATE_SHA256 = (
    "3EB78E94930FA6A70288A76D3E5118095CBB8B2DD72792357715BF38A463EF01"
)
EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_ROWS = 247
EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_COORDINATE_SHA256 = (
    "603C33D85F32707B41EDDBD0E36D2C210B2754F21A14B1DD42040771775C4E6D"
)
EXPECTED_CHUNK_LIVE_COUNTS = (
    (88, 5, 88),
    (91, 6, 85),
    (79, 5, 74),
)
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 239
EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256 = (
    "FA82BC4416848852AC94D26AB3A6FCA1B01A9B18203C4D71B7C6682C4453E03E"
)
EXPECTED_SOURCE_AFFECTED_ROOTS = 258
EXPECTED_SOURCE_AFFECTED_ROOT_SHA256 = (
    "EAD6CD856477156C41710533536934F2EC647BB50368B548E4A656694B478D34"
)
EXPECTED_STRUCTURAL_PENDING_ROOTS = 123
EXPECTED_STRUCTURAL_PENDING_ROOT_SHA256 = (
    "58E2C9FBA21C4241C3DA777D4126A7D293DD1E7CE86CCEBF40B7254690E4809D"
)
EXPECTED_STRUCTURAL_PENDING_ROWS = 271
EXPECTED_STRUCTURAL_PENDING_COORDINATE_SHA256 = (
    "EDAF708FE66315B7214F68F26317CFB7F2414FD01785BFF32E259A01A684C2CD"
)
EXPECTED_CHUNK_COUNTS = (
    (56, 56, 93, 1303),
    (59, 58, 91, 1313),
    (57, 57, 79, 1310),
)
EXPECTED_DISPATCH_ROOTS = 13
EXPECTED_DISPATCH_EDGES = 13

# Frozen after the first reproducible write/check cycle.
EXPECTED_DISPATCH_SHA256 = (
    "221D0CDEA48E054A3B063F7B71A791F73FA07679A2BBB2335338FBA6B1C39062"
)
EXPECTED_PRIVATE_FILE_SHA256 = (
    "6A76DFA45A4706B4D7524ACEDBA46DFFDC15CD592E3D6A5740A1AB46C2EE5925"
)
EXPECTED_PUBLIC_FILE_SHA256 = (
    "0B5A862BD98474B0A8A64423FEFD714EE5013D233E759C45BA4365AAC76F859D"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_BUILDER_PATH, "pk_selector1096_assignment_base_v1")
ENGINE = BASE.BASE


def patch_contract() -> None:
    names = (
        "PREDECESSOR_PRIVATE_PATH",
        "PREDECESSOR_PUBLIC_PATH",
        "CURRENT_A19_LEDGER_PATH",
        "SELECTOR538_DECISION_PATHS",
        "DEFAULT_PRIVATE_OUTPUT",
        "DEFAULT_PUBLIC_OUTPUT",
        "PRIVATE_SCHEMA",
        "PUBLIC_SCHEMA",
        "METHOD",
        "SELECTOR",
        "TERMINALS",
        "CHUNK_COUNT",
        "MIN_CHUNK_SITES",
        "MAX_CHUNK_SITES",
        "EXPECTED_CUTS",
        "EXPECTED_PREDECESSOR_PRIVATE_SHA256",
        "EXPECTED_PREDECESSOR_PUBLIC_SHA256",
        "EXPECTED_CANDIDATE_SHA256",
        "EXPECTED_PK_PRISTINE_SHA256",
        "EXPECTED_PK_CURRENT_SHA256",
        "EXPECTED_CURRENT_A19_LEDGER_SHA256",
        "EXPECTED_SELECTOR538_DECISION_SHA256",
        "EXPECTED_PENDING_ROWS",
        "EXPECTED_CURRENT_A19_PENDING_ROWS",
        "EXPECTED_SITE_COUNT",
        "EXPECTED_SITE_SHA256",
        "EXPECTED_ROOT_COUNT",
        "EXPECTED_ROOT_SHA256",
        "EXPECTED_SOURCE_SITE_COUNT",
        "EXPECTED_SOURCE_SITE_SHA256",
        "EXPECTED_SOURCE_ROOT_COUNT",
        "EXPECTED_SOURCE_ROOT_SHA256",
        "EXPECTED_SOURCE_ONLY_SITES",
        "EXPECTED_SOURCE_ONLY_SITE_SHA256",
        "EXPECTED_CANDIDATE_ONLY_SITES",
        "EXPECTED_CANDIDATE_ONLY_SITE_SHA256",
        "EXPECTED_TERMINAL_COORDINATE_SHA256",
        "EXPECTED_DIRECT_PENDING_ROOTS",
        "EXPECTED_DIRECT_PENDING_ROOT_SHA256",
        "EXPECTED_DIRECT_PENDING_ROWS",
        "EXPECTED_DIRECT_PENDING_COORDINATE_SHA256",
        "EXPECTED_CURRENT_LIVE_PENDING_ROWS",
        "EXPECTED_CURRENT_LIVE_PENDING_COORDINATE_SHA256",
        "EXPECTED_ALREADY_PROMOTED_ROWS",
        "EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256",
        "EXPECTED_SELECTOR538_PLANNED_PROMOTION_ROWS",
        "EXPECTED_SELECTOR538_PLANNED_PROMOTION_COORDINATE_SHA256",
        "EXPECTED_SELECTOR538_OVERLAP_ROWS",
        "EXPECTED_SELECTOR538_OVERLAP_COORDINATE_SHA256",
        "EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_ROWS",
        "EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_COORDINATE_SHA256",
        "EXPECTED_CHUNK_LIVE_COUNTS",
        "EXPECTED_CANDIDATE_AFFECTED_ROOTS",
        "EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256",
        "EXPECTED_SOURCE_AFFECTED_ROOTS",
        "EXPECTED_SOURCE_AFFECTED_ROOT_SHA256",
        "EXPECTED_STRUCTURAL_PENDING_ROOTS",
        "EXPECTED_STRUCTURAL_PENDING_ROOT_SHA256",
        "EXPECTED_STRUCTURAL_PENDING_ROWS",
        "EXPECTED_STRUCTURAL_PENDING_COORDINATE_SHA256",
        "EXPECTED_CHUNK_COUNTS",
        "EXPECTED_DISPATCH_ROOTS",
        "EXPECTED_DISPATCH_EDGES",
        "EXPECTED_DISPATCH_SHA256",
        "EXPECTED_PRIVATE_FILE_SHA256",
        "EXPECTED_PUBLIC_FILE_SHA256",
    )
    for name in names:
        setattr(BASE, name, globals()[name])
    ENGINE.INTEGRATED_LEDGER = PREDECESSOR_PRIVATE_PATH
    ENGINE.DEFAULT_OUTPUT = DEFAULT_PRIVATE_OUTPUT
    ENGINE.SCHEMA = PRIVATE_SCHEMA
    ENGINE.SELECTOR = SELECTOR
    ENGINE.TERMINALS = TERMINALS
    ENGINE.CHUNK_COUNT = CHUNK_COUNT
    ENGINE.MIN_CHUNK_SITES = MIN_CHUNK_SITES
    ENGINE.MAX_CHUNK_SITES = MAX_CHUNK_SITES
    ENGINE.EXPECTED_LEDGER_SHA256 = EXPECTED_PREDECESSOR_PRIVATE_SHA256
    ENGINE.EXPECTED_CANDIDATE_SHA256 = EXPECTED_CANDIDATE_SHA256
    ENGINE.EXPECTED_SITE_COUNT = EXPECTED_SITE_COUNT
    ENGINE.EXPECTED_SITE_SHA256 = EXPECTED_SITE_SHA256
    ENGINE.EXPECTED_CUTS = EXPECTED_CUTS
    ENGINE.EXPECTED_FILE_SHA256 = None


patch_contract()

AssignmentError = BASE.AssignmentError
require = BASE.require
sha256_bytes = BASE.sha256_bytes
sha256_file = BASE.sha256_file
canonical_bytes = BASE.canonical_bytes
canonical_sha256 = BASE.canonical_sha256
canonical_json = BASE.canonical_json
coordinate_digest = BASE.coordinate_digest
root_digest = BASE.root_digest
site_digest = BASE.site_digest
roots_from_sites = BASE.roots_from_sites
coordinates_for_roots = BASE.coordinates_for_roots
load_ledger_path = BASE.load_ledger_path
selector538_planned_promotions = BASE.selector538_planned_promotions
_BASE_BUILD_GRAPH_EVIDENCE = BASE.build_graph_evidence


def dispatch_edges(
    edges: dict[tuple[int, int], set[tuple[int, int]]],
) -> list[list[str]]:
    start = (0, SELECTOR)
    terminals = {(0, terminal) for terminal in TERMINALS}
    pending = [start]
    visited: set[tuple[int, int]] = set()
    result: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    while pending:
        root = pending.pop()
        if root in visited or root in terminals:
            continue
        visited.add(root)
        for target in edges.get(root, set()):
            result.add((root, target))
            if target not in terminals:
                pending.append(target)
    return [
        [f"{source[0]}:{source[1]}", f"{target[0]}:{target[1]}"]
        for source, target in sorted(result)
    ]


def build_graph_evidence(
    manifest: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    private, public = _BASE_BUILD_GRAPH_EVIDENCE(manifest)
    *_unused, bundle = BASE.final_outputs()
    candidate_records = bundle["analysis"]["candidate_records"]
    prepared = CALLER.ENGINE.prepare_artifacts(
        CALLER.ENGINE.DEFAULT_STEAM_ROOT,
        CALLER.ENGINE.DEFAULT_BASE_PRISTINE,
        CALLER.ENGINE.DEFAULT_PK_PRISTINE,
    )
    resource = prepared.resources["pk_msggame"]
    source_records = CALLER.ENGINE.archive_records(
        resource.pristine_archive
    )
    current_records = CALLER.ENGINE.archive_records(
        resource.current_archive
    )
    inputs = type(
        "Selector1096DispatchInputs",
        (),
        {
            "pk_source_records": source_records,
            "pk_current_records": current_records,
            "pk_candidate_records": candidate_records,
        },
    )()
    _profiles, candidate_graph = (
        CALLER.CROSS.RESIDUAL_AUDIT.build_record_profiles(inputs=inputs)
    )
    source_graph = CALLER.HONORIFIC.graph_edges(
        source_records,
        conservative_operand_scan=True,
    )
    candidate_dispatch = dispatch_edges(candidate_graph)
    source_dispatch = dispatch_edges(source_graph)
    roots = {
        coordinate
        for edge in candidate_dispatch
        for coordinate in edge
    }
    digest = canonical_sha256(candidate_dispatch)
    require(
        candidate_dispatch == source_dispatch
        and len(roots) == EXPECTED_DISPATCH_ROOTS
        and len(candidate_dispatch) == EXPECTED_DISPATCH_EDGES
        and (
            EXPECTED_DISPATCH_SHA256 is None
            or digest == EXPECTED_DISPATCH_SHA256
        ),
        "selector-1096 dispatch graph drifted",
    )
    private = dict(private)
    private["selector_dispatch"] = {
        "candidate_and_source_identical": True,
        "edges": candidate_dispatch,
        "root_count": len(roots),
        "terminal_coordinates": [
            f"0:{terminal}:0" for terminal in TERMINALS
        ],
    }
    public = dict(public)
    public["selector_dispatch"] = {
        "candidate_and_source_identical": True,
        "edge_count": len(candidate_dispatch),
        "edge_sha256": digest,
        "root_count": len(roots),
        "terminal_count": len(TERMINALS),
        "terminal_coordinate_sha256":
            EXPECTED_TERMINAL_COORDINATE_SHA256,
    }
    return private, public


BASE.build_graph_evidence = build_graph_evidence
assert_source_free = BASE.assert_source_free
build_outputs = BASE.build_outputs
validate_outputs = BASE.validate_outputs
validate_paths = BASE.validate_paths
parse_args = BASE.parse_args
CALLER = BASE.CALLER
BASE_AUDIT = BASE.BASE_AUDIT


def main(argv: Sequence[str] | None = None) -> int:
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
