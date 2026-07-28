#!/usr/bin/env python3
"""Build the private selector-568 assignment and source-free graph report."""

from __future__ import annotations

import argparse
import functools
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
ENGINE_PATH = WORKSTREAM / "build_pk_selector538_assignment_v1.py"
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
    DIALOGUE_TMP / "family568_assignment.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector568_assignment_coverage.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector568-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector568-assignment-coverage.v1"
METHOD = "reversed_vm_pk_selector568_deterministic_assignment"
SELECTOR = 568
TERMINALS = tuple(range(1951, 1958))
CHUNK_COUNT = 3
MIN_CHUNK_SITES = 50
MAX_CHUNK_SITES = 90
EXPECTED_CUTS = (77, 144, 222)

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
EXPECTED_SITE_COUNT = 222
EXPECTED_SITE_SHA256 = (
    "02B65958DBCE49707D50D2C8F51041FB933B06CD8674E71FAD2E6E5446B5C5B8"
)
EXPECTED_ROOT_COUNT = 215
EXPECTED_ROOT_SHA256 = (
    "1FC5BDF7D2DF321990B715BAB462DF289849D9B0AD0E6F84D8535F857D48B7B1"
)
EXPECTED_SOURCE_SITE_COUNT = 231
EXPECTED_SOURCE_SITE_SHA256 = (
    "C93EB83205FFB727CB33CD188C8D09135A8569405578FE6FB697033E53C88224"
)
EXPECTED_SOURCE_ROOT_COUNT = 224
EXPECTED_SOURCE_ROOT_SHA256 = (
    "5F95984BB5C4D283E99B3BEB06373AA060D41B9AFE82C6FF1B29550877C10DA4"
)
EXPECTED_SOURCE_ONLY_SITES = 9
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "8BBBC7E976BCB715CB325B344759BE0269EE50C536F8DC718C78B34AD4F75B7B"
)
EXPECTED_CANDIDATE_ONLY_SITES = 0
EXPECTED_CANDIDATE_ONLY_SITE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_TERMINAL_COORDINATE_SHA256 = (
    "B49C5ADF284B2FBF52B8AAB8C0B24EEF6BBA694963D98CBC7A403DBF9AE8732F"
)
EXPECTED_DIRECT_PENDING_ROOTS = 147
EXPECTED_DIRECT_PENDING_ROOT_SHA256 = (
    "FD34E713744D85BDB59849D998D7FF4472185C35C8411431B9D5A1DCC25CDC8C"
)
EXPECTED_DIRECT_PENDING_ROWS = 348
EXPECTED_DIRECT_PENDING_COORDINATE_SHA256 = (
    "ADD36B06C84C3E85C06B314F477114BA86165876194518EA397EF0D536DD5650"
)
EXPECTED_CURRENT_LIVE_PENDING_ROWS = 343
EXPECTED_CURRENT_LIVE_PENDING_COORDINATE_SHA256 = (
    "90616207A12C6A2315E9F6B60BA82224FE84726439FB6C4E6FF5268E3F74357A"
)
EXPECTED_ALREADY_PROMOTED_ROWS = 5
EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256 = (
    "01A2FD18B93822F59ABFA6EE567C48110E3DB344AE896D3116EB66177AC76A04"
)
EXPECTED_SELECTOR538_PLANNED_PROMOTION_ROWS = 277
EXPECTED_SELECTOR538_PLANNED_PROMOTION_COORDINATE_SHA256 = (
    "B6D1D61B1681F9CA92AD6DCD2C43F4913D83916C0DC5BFE05A4C0BFEC3BED5C1"
)
EXPECTED_SELECTOR538_OVERLAP_ROWS = 17
EXPECTED_SELECTOR538_OVERLAP_COORDINATE_SHA256 = (
    "6582123A978134EC5E714F722E7476B06B8609687497E7BCB5D2D578C6D41E5E"
)
EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_ROWS = 331
EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_COORDINATE_SHA256 = (
    "76D57C4AD80FCB41E4144A2C1AF79ABC28BA85645D0C41F1FA624E19EA066C4C"
)
EXPECTED_CHUNK_LIVE_COUNTS = (
    (126, 5, 126),
    (131, 3, 128),
    (86, 9, 77),
)
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 281
EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256 = (
    "493955409CFECBA5A3B3D93193BDAF0ECB3544A26664919006AC3424EE58E0FA"
)
EXPECTED_SOURCE_AFFECTED_ROOTS = 291
EXPECTED_SOURCE_AFFECTED_ROOT_SHA256 = (
    "B6A76B74CAEC9C25746B5EA863FAB92C8192DF2A7080FEFA5AD475F22374DFF0"
)
EXPECTED_STRUCTURAL_PENDING_ROOTS = 150
EXPECTED_STRUCTURAL_PENDING_ROOT_SHA256 = (
    "653BEAFE72180463F14A9DE0AB51033930A7BAC74BD7F03D899C2A171C0D67A2"
)
EXPECTED_STRUCTURAL_PENDING_ROWS = 352
EXPECTED_STRUCTURAL_PENDING_COORDINATE_SHA256 = (
    "97E37018F2202DC7AE82EB240C42297788915CCF9CE1419037CE6B4E72119824"
)
EXPECTED_CHUNK_COUNTS = (
    (77, 75, 131, 1471),
    (67, 62, 131, 1481),
    (78, 78, 86, 1479),
)

# Frozen after the first reproducible write/check cycle.
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "B55F2C43D8B4149DDE1739D35FF322E5A6A30C3D58E77AC2500D45200A4AAB98"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "BF889606D3C2748B5923CDD9FC46936ED5DE6DED9993FC1B29D5F00785FB6D91"
)


class AssignmentError(ValueError):
    """Raised when selector-568 assignment evidence drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssignmentError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(
        spec is not None and spec.loader is not None,
        f"cannot import {path}",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(ENGINE_PATH, "pk_selector568_assignment_engine_v1")
BASE.INTEGRATED_LEDGER = PREDECESSOR_PRIVATE_PATH
BASE.DEFAULT_OUTPUT = DEFAULT_PRIVATE_OUTPUT
BASE.SCHEMA = PRIVATE_SCHEMA
BASE.SELECTOR = SELECTOR
BASE.TERMINALS = TERMINALS
BASE.CHUNK_COUNT = CHUNK_COUNT
BASE.MIN_CHUNK_SITES = MIN_CHUNK_SITES
BASE.MAX_CHUNK_SITES = MAX_CHUNK_SITES
BASE.EXPECTED_LEDGER_SHA256 = EXPECTED_PREDECESSOR_PRIVATE_SHA256
BASE.EXPECTED_CANDIDATE_SHA256 = EXPECTED_CANDIDATE_SHA256
BASE.EXPECTED_SITE_COUNT = EXPECTED_SITE_COUNT
BASE.EXPECTED_SITE_SHA256 = EXPECTED_SITE_SHA256
BASE.EXPECTED_CUTS = EXPECTED_CUTS
BASE.EXPECTED_FILE_SHA256 = None

_ORIGINAL_FINAL_BUILD_OUTPUTS = BASE.FINAL.build_outputs


@functools.lru_cache(maxsize=1)
def final_outputs() -> tuple[Any, ...]:
    return _ORIGINAL_FINAL_BUILD_OUTPUTS()


BASE.FINAL.build_outputs = final_outputs
CALLER = BASE.CALLER
BASE_AUDIT = CALLER.BASE_AUDIT


def sha256_bytes(value: bytes) -> str:
    return BASE.sha256_bytes(value)


def sha256_file(path: Path) -> str:
    return BASE.sha256_file(path)


def canonical_bytes(value: Any) -> bytes:
    return BASE.canonical_bytes(value)


def canonical_sha256(value: Any) -> str:
    return BASE.canonical_sha256(value)


def canonical_json(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8") + "\n"


def coordinate_digest(values: Iterable[str]) -> str:
    return BASE.coordinate_digest(values)


def root_digest(values: Iterable[tuple[int, int]]) -> str:
    return BASE.root_digest(values)


def site_digest(values: Iterable[str]) -> str:
    return BASE.site_digest(values)


def roots_from_sites(sites: Iterable[str]) -> set[tuple[int, int]]:
    return {
        tuple(map(int, site.split(":")[:2]))
        for site in sites
    }


def coordinates_for_roots(
    roots: Iterable[tuple[int, int]],
    pending_by_root: Mapping[tuple[int, int], Sequence[str]],
) -> set[str]:
    return {
        coordinate
        for root in roots
        for coordinate in pending_by_root.get(root, ())
    }


def load_ledger_path(
    path: Path,
) -> dict[tuple[str, str], dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        rows[(str(row["resource"]), str(row["coordinate"]))] = row
    return rows


def selector538_planned_promotions() -> set[str]:
    result: set[str] = set()
    for chunk_id, path in enumerate(SELECTOR538_DECISION_PATHS):
        require(
            sha256_file(path)
            == EXPECTED_SELECTOR538_DECISION_SHA256[chunk_id],
            f"selector-538 chunk-{chunk_id} decision drifted",
        )
        field = f"selector538_chunk{chunk_id}_update_action"
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if "runtime_promotion" in str(row.get(field, "")):
                result.add(str(row["coordinate"]))
    require(
        len(result) == EXPECTED_SELECTOR538_PLANNED_PROMOTION_ROWS
        and coordinate_digest(result)
        == EXPECTED_SELECTOR538_PLANNED_PROMOTION_COORDINATE_SHA256,
        "selector-538 planned promotion union drifted",
    )
    return result


def build_graph_evidence(
    manifest: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    *_unused, bundle = final_outputs()
    analysis = bundle["analysis"]
    candidate_blob = analysis["candidate_blob"]
    candidate_records = analysis["candidate_records"]
    require(
        sha256_bytes(candidate_blob) == EXPECTED_CANDIDATE_SHA256,
        "selector-568 candidate drifted",
    )

    prepared = CALLER.ENGINE.prepare_artifacts(
        CALLER.ENGINE.DEFAULT_STEAM_ROOT,
        CALLER.ENGINE.DEFAULT_BASE_PRISTINE,
        CALLER.ENGINE.DEFAULT_PK_PRISTINE,
    )
    resource = prepared.resources["pk_msggame"]
    current_records = CALLER.ENGINE.archive_records(
        resource.current_archive
    )
    source_records = CALLER.ENGINE.archive_records(
        resource.pristine_archive
    )
    source_sites = CALLER.call_sites(source_records, SELECTOR)
    candidate_sites = CALLER.call_sites(candidate_records, SELECTOR)
    source_roots = roots_from_sites(source_sites)
    candidate_roots = roots_from_sites(candidate_sites)
    source_only_sites = sorted(set(source_sites) - set(candidate_sites))
    candidate_only_sites = sorted(set(candidate_sites) - set(source_sites))
    require(
        len(candidate_sites) == EXPECTED_SITE_COUNT
        and site_digest(candidate_sites) == EXPECTED_SITE_SHA256
        and len(candidate_roots) == EXPECTED_ROOT_COUNT
        and root_digest(candidate_roots) == EXPECTED_ROOT_SHA256
        and len(source_sites) == EXPECTED_SOURCE_SITE_COUNT
        and site_digest(source_sites) == EXPECTED_SOURCE_SITE_SHA256
        and len(source_roots) == EXPECTED_SOURCE_ROOT_COUNT
        and root_digest(source_roots) == EXPECTED_SOURCE_ROOT_SHA256
        and len(source_only_sites) == EXPECTED_SOURCE_ONLY_SITES
        and site_digest(source_only_sites)
        == EXPECTED_SOURCE_ONLY_SITE_SHA256
        and len(candidate_only_sites) == EXPECTED_CANDIDATE_ONLY_SITES
        and site_digest(candidate_only_sites)
        == EXPECTED_CANDIDATE_ONLY_SITE_SHA256,
        "selector-568 source/candidate call-site graph drifted",
    )

    ledger_rows, pending_by_root = BASE.load_ledger()
    pending_rows = sum(len(values) for values in pending_by_root.values())
    require(
        len(ledger_rows) == 52_803
        and pending_rows == EXPECTED_PENDING_ROWS,
        "selector-568 predecessor ledger drifted",
    )
    direct_pending_roots = candidate_roots & set(pending_by_root)
    direct_pending_coordinates = coordinates_for_roots(
        direct_pending_roots,
        pending_by_root,
    )

    inputs = type(
        "Selector568GraphInputs",
        (),
        {
            "pk_source_records": source_records,
            "pk_current_records": current_records,
            "pk_candidate_records": candidate_records,
        },
    )()
    _profiles, candidate_edges = (
        CALLER.CROSS.RESIDUAL_AUDIT.build_record_profiles(inputs=inputs)
    )
    source_edges = CALLER.HONORIFIC.graph_edges(
        source_records,
        conservative_operand_scan=True,
    )
    terminal_roots = tuple((0, terminal) for terminal in TERMINALS)
    candidate_affected = CALLER.HONORIFIC.reverse_ancestors(
        edges=candidate_edges,
        targets=terminal_roots,
    )
    source_affected = CALLER.HONORIFIC.reverse_ancestors(
        edges=source_edges,
        targets=terminal_roots,
    )
    structural_pending_roots = (
        candidate_affected | source_affected
    ) & set(pending_by_root)
    structural_pending_coordinates = coordinates_for_roots(
        structural_pending_roots,
        pending_by_root,
    )
    require(
        len(direct_pending_roots) == EXPECTED_DIRECT_PENDING_ROOTS
        and root_digest(direct_pending_roots)
        == EXPECTED_DIRECT_PENDING_ROOT_SHA256
        and len(direct_pending_coordinates) == EXPECTED_DIRECT_PENDING_ROWS
        and coordinate_digest(direct_pending_coordinates)
        == EXPECTED_DIRECT_PENDING_COORDINATE_SHA256
        and len(candidate_affected) == EXPECTED_CANDIDATE_AFFECTED_ROOTS
        and root_digest(candidate_affected)
        == EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256
        and len(source_affected) == EXPECTED_SOURCE_AFFECTED_ROOTS
        and root_digest(source_affected)
        == EXPECTED_SOURCE_AFFECTED_ROOT_SHA256
        and len(structural_pending_roots)
        == EXPECTED_STRUCTURAL_PENDING_ROOTS
        and root_digest(structural_pending_roots)
        == EXPECTED_STRUCTURAL_PENDING_ROOT_SHA256
        and len(structural_pending_coordinates)
        == EXPECTED_STRUCTURAL_PENDING_ROWS
        and coordinate_digest(structural_pending_coordinates)
        == EXPECTED_STRUCTURAL_PENDING_COORDINATE_SHA256,
        "selector-568 direct/structural pending ceiling drifted",
    )

    chunks = manifest["chunks"]
    observed_chunks = tuple(
        (
            int(chunk["site_count"]),
            int(chunk["root_count"]),
            int(chunk["pending_row_upper_bound"]),
            int(chunk["workload_weight"]),
        )
        for chunk in chunks
    )
    require(
        observed_chunks == EXPECTED_CHUNK_COUNTS,
        f"selector-568 chunk partition drifted: {observed_chunks}",
    )
    require(
        sha256_file(CURRENT_A19_LEDGER_PATH)
        == EXPECTED_CURRENT_A19_LEDGER_SHA256,
        "current a19 integrated ledger drifted",
    )
    current_a19_rows = load_ledger_path(CURRENT_A19_LEDGER_PATH)
    current_a19_pending = {
        coordinate
        for (resource_name, coordinate), row in current_a19_rows.items()
        if resource_name == "pk_msggame"
        and row.get("runtime_review") == "pending"
    }
    require(
        len(current_a19_rows) == 52_803
        and sum(
            row.get("runtime_review") == "pending"
            for row in current_a19_rows.values()
        )
        == EXPECTED_CURRENT_A19_PENDING_ROWS,
        "current a19 pending ledger contract drifted",
    )
    potential_promotions = direct_pending_coordinates
    current_live_pending = potential_promotions & current_a19_pending
    already_promoted = potential_promotions - current_live_pending
    selector538_planned = selector538_planned_promotions()
    selector538_overlap = potential_promotions & selector538_planned
    live_after_selector538_plan = (
        potential_promotions - selector538_planned
    )
    require(
        len(current_live_pending) == EXPECTED_CURRENT_LIVE_PENDING_ROWS
        and coordinate_digest(current_live_pending)
        == EXPECTED_CURRENT_LIVE_PENDING_COORDINATE_SHA256
        and len(already_promoted) == EXPECTED_ALREADY_PROMOTED_ROWS
        and coordinate_digest(already_promoted)
        == EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256
        and already_promoted <= selector538_planned
        and len(selector538_overlap) == EXPECTED_SELECTOR538_OVERLAP_ROWS
        and coordinate_digest(selector538_overlap)
        == EXPECTED_SELECTOR538_OVERLAP_COORDINATE_SHA256
        and len(live_after_selector538_plan)
        == EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_ROWS
        and coordinate_digest(live_after_selector538_plan)
        == EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_COORDINATE_SHA256,
        "selector-568 a19/planned selector-538 overlap drifted",
    )
    observed_chunk_live: list[tuple[int, int, int]] = []
    for chunk in chunks:
        chunk_potential = set(chunk["pending_coordinates"])
        observed_chunk_live.append(
            (
                len(chunk_potential & current_live_pending),
                len(chunk_potential & selector538_planned),
                len(chunk_potential - selector538_planned),
            )
        )
    require(
        tuple(observed_chunk_live) == EXPECTED_CHUNK_LIVE_COUNTS,
        f"selector-568 per-chunk live contribution drifted: "
        f"{observed_chunk_live}",
    )

    chunk0_first_ordinal: dict[tuple[int, int], int] = {}
    for assignment_row in manifest["site_assignments"][
        : EXPECTED_CUTS[0]
    ]:
        root = tuple(
            map(int, str(assignment_row["root"]).split(":"))
        )
        chunk0_first_ordinal.setdefault(
            root,
            int(assignment_row["ordinal"]),
        )
    chunk0_priority: list[dict[str, Any]] = []
    for root_string in chunks[0]["roots"]:
        root = tuple(map(int, str(root_string).split(":")))
        root_potential = set(pending_by_root.get(root, ()))
        chunk0_priority.append(
            {
                "already_promoted_count":
                    len(root_potential & already_promoted),
                "current_live_pending_count":
                    len(root_potential & current_live_pending),
                "first_ordinal": chunk0_first_ordinal[root],
                "live_after_selector538_plan_count":
                    len(root_potential - selector538_planned),
                "planned_selector538_overlap_count":
                    len(root_potential & selector538_planned),
                "potential_promotion_count": len(root_potential),
                "root": root_string,
            }
        )
    chunk0_priority.sort(
        key=lambda row: (
            -int(row["live_after_selector538_plan_count"]),
            -int(row["current_live_pending_count"]),
            int(row["first_ordinal"]),
            str(row["root"]),
        )
    )

    private = {
        "already_promoted_coordinates": sorted(
            already_promoted,
            key=CALLER.parse_coordinate,
        ),
        "candidate_affected_roots": sorted(
            f"{root[0]}:{root[1]}" for root in candidate_affected
        ),
        "candidate_call_sites": candidate_sites,
        "candidate_only_sites": candidate_only_sites,
        "chunk0_live_pending_priority": chunk0_priority,
        "current_live_pending_coordinates": sorted(
            current_live_pending,
            key=CALLER.parse_coordinate,
        ),
        "direct_pending_coordinates": sorted(
            direct_pending_coordinates,
            key=CALLER.parse_coordinate,
        ),
        "direct_pending_roots": sorted(
            f"{root[0]}:{root[1]}" for root in direct_pending_roots
        ),
        "source_affected_roots": sorted(
            f"{root[0]}:{root[1]}" for root in source_affected
        ),
        "source_call_sites": source_sites,
        "source_only_sites": source_only_sites,
        "selector538_planned_overlap_coordinates": sorted(
            selector538_overlap,
            key=CALLER.parse_coordinate,
        ),
        "structural_pending_coordinates": sorted(
            structural_pending_coordinates,
            key=CALLER.parse_coordinate,
        ),
        "structural_pending_roots": sorted(
            f"{root[0]}:{root[1]}" for root in structural_pending_roots
        ),
        "live_after_selector538_plan_coordinates": sorted(
            live_after_selector538_plan,
            key=CALLER.parse_coordinate,
        ),
    }
    public = {
        "a19_and_selector538_overlap": {
            "already_promoted_count": len(already_promoted),
            "already_promoted_sha256": coordinate_digest(
                already_promoted
            ),
            "chunk_live_counts": [
                {
                    "chunk_id": chunk_id,
                    "current_live_pending_count": counts[0],
                    "live_after_selector538_plan_count": counts[2],
                    "planned_selector538_overlap_count": counts[1],
                }
                for chunk_id, counts in enumerate(observed_chunk_live)
            ],
            "chunk0_priority_root_count": len(chunk0_priority),
            "chunk0_priority_sha256": canonical_sha256(
                chunk0_priority
            ),
            "current_live_pending_count": len(current_live_pending),
            "current_live_pending_sha256": coordinate_digest(
                current_live_pending
            ),
            "live_after_selector538_plan_count":
                len(live_after_selector538_plan),
            "live_after_selector538_plan_sha256": coordinate_digest(
                live_after_selector538_plan
            ),
            "planned_selector538_overlap_count":
                len(selector538_overlap),
            "planned_selector538_overlap_sha256": coordinate_digest(
                selector538_overlap
            ),
            "selector538_full_planned_promotion_count":
                len(selector538_planned),
            "selector538_full_planned_promotion_sha256":
                coordinate_digest(selector538_planned),
        },
        "candidate_affected_root_count": len(candidate_affected),
        "candidate_affected_root_sha256": root_digest(candidate_affected),
        "candidate_call_root_count": len(candidate_roots),
        "candidate_call_root_sha256": root_digest(candidate_roots),
        "candidate_call_site_count": len(candidate_sites),
        "candidate_call_site_sha256": site_digest(candidate_sites),
        "candidate_only_site_count": len(candidate_only_sites),
        "candidate_only_site_sha256": site_digest(candidate_only_sites),
        "direct_pending_ceiling": {
            "pending_root_count": len(direct_pending_roots),
            "pending_root_sha256": root_digest(direct_pending_roots),
            "pending_row_count": len(direct_pending_coordinates),
            "pending_row_sha256": coordinate_digest(
                direct_pending_coordinates
            ),
        },
        "source_affected_root_count": len(source_affected),
        "source_affected_root_sha256": root_digest(source_affected),
        "source_call_root_count": len(source_roots),
        "source_call_root_sha256": root_digest(source_roots),
        "source_call_site_count": len(source_sites),
        "source_call_site_sha256": site_digest(source_sites),
        "source_only_site_count": len(source_only_sites),
        "source_only_site_sha256": site_digest(source_only_sites),
        "structural_pending_ceiling": {
            "pending_root_count": len(structural_pending_roots),
            "pending_root_sha256": root_digest(structural_pending_roots),
            "pending_row_count": len(structural_pending_coordinates),
            "pending_row_sha256": coordinate_digest(
                structural_pending_coordinates
            ),
        },
    }
    return private, public


def assert_source_free(value: Any) -> None:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            serialized,
        )
        is None,
        "public assignment report contains dialogue text",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", serialized) is None,
        "public assignment report contains an exact coordinate",
    )


def build_outputs() -> tuple[
    str,
    str,
    dict[str, Any],
    dict[str, Any],
]:
    require(
        sha256_file(PREDECESSOR_PRIVATE_PATH)
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and sha256_file(PREDECESSOR_PUBLIC_PATH)
        == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and sha256_file(Path(BASE_AUDIT.DEFAULT_PK_PRISTINE))
        == EXPECTED_PK_PRISTINE_SHA256
        and sha256_file(Path(BASE_AUDIT.DEFAULT_PK_CURRENT))
        == EXPECTED_PK_CURRENT_SHA256,
        "selector-568 immutable inputs drifted",
    )
    steam_before = sha256_file(Path(BASE_AUDIT.DEFAULT_PK_CURRENT))
    manifest = BASE.build_manifest()
    private_graph, public_graph = build_graph_evidence(manifest)
    manifest = dict(manifest)
    manifest["graph_evidence"] = private_graph
    manifest["guards"] = dict(manifest["guards"])
    manifest["guards"]["graph_evidence_canonical_sha256"] = (
        canonical_sha256(private_graph)
    )
    manifest["guards"]["payload_with_graph_canonical_sha256"] = (
        canonical_sha256(manifest)
    )
    private_content = canonical_json(manifest)

    chunk_summaries = [
        {
            "chunk_id": chunk["chunk_id"],
            "language_available_counts":
                chunk["language_available_counts"],
            "ordinal_end": chunk["ordinal_end"],
            "ordinal_start": chunk["ordinal_start"],
            "pending_row_upper_bound":
                chunk["pending_row_upper_bound"],
            "root_count": chunk["root_count"],
            "root_sha256": chunk["root_sha256"],
            "site_count": chunk["site_count"],
            "site_sha256": chunk["site_sha256"],
            "workload_weight": chunk["workload_weight"],
        }
        for chunk in manifest["chunks"]
    ]
    report: dict[str, Any] = {
        "assignment": {
            "chunk_count": CHUNK_COUNT,
            "chunks": chunk_summaries,
            "cuts": list(EXPECTED_CUTS),
            "deterministic_balancing": True,
        },
        "distribution_policy": {
            "private_assignment_contains_exact_coordinates": True,
            "private_assignment_stays_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
        },
        "graph": public_graph,
        "inputs": {
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "current_a19_ledger_sha256":
                EXPECTED_CURRENT_A19_LEDGER_SHA256,
            "pk_current_sha256": EXPECTED_PK_CURRENT_SHA256,
            "pk_pristine_sha256": EXPECTED_PK_PRISTINE_SHA256,
            "predecessor_private_sha256":
                EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "predecessor_public_sha256":
                EXPECTED_PREDECESSOR_PUBLIC_SHA256,
            "selector538_decision_sha256": list(
                EXPECTED_SELECTOR538_DECISION_SHA256
            ),
        },
        "method": METHOD,
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "scope": {
            "pending_rows_before": EXPECTED_PENDING_ROWS,
            "selector": SELECTOR,
            "terminal_count": len(TERMINALS),
            "terminal_coordinate_sha256":
                EXPECTED_TERMINAL_COORDINATE_SHA256,
        },
        "schema": PUBLIC_SCHEMA,
        "status": "PASS",
        "steam_write_performed": False,
    }
    report["guards"] = {
        "private_assignment_sha256": sha256_bytes(
            private_content.encode("utf-8")
        ),
        "report_payload_sha256": canonical_sha256(report),
    }
    public_content = canonical_json(report)
    assert_source_free(report)
    steam_after = sha256_file(Path(BASE_AUDIT.DEFAULT_PK_CURRENT))
    require(
        steam_before == steam_after == EXPECTED_PK_CURRENT_SHA256,
        "Steam shadow archive changed during selector-568 assignment",
    )
    return private_content, public_content, manifest, report


def validate_outputs(
    private_content: str,
    public_content: str,
    *,
    require_frozen_hashes: bool = True,
) -> None:
    actual = (
        sha256_bytes(private_content.encode("utf-8")),
        sha256_bytes(public_content.encode("utf-8")),
    )
    expected = (
        EXPECTED_PRIVATE_FILE_SHA256,
        EXPECTED_PUBLIC_FILE_SHA256,
    )
    if require_frozen_hashes:
        require(
            all(expected) and actual == expected,
            f"selector-568 frozen output drifted: {actual}",
        )


def validate_paths(args: argparse.Namespace) -> None:
    private_root = DIALOGUE_TMP.resolve(strict=False)
    require(
        private_root
        in args.private_output.resolve(strict=False).parents,
        "private assignment must remain below tmp",
    )
    require(
        args.public_output.resolve(strict=False)
        == DEFAULT_PUBLIC_OUTPUT.resolve(strict=False),
        "public assignment report must use its fixed tracked path",
    )
    steam_paths = {
        Path(BASE_AUDIT.DEFAULT_PK_CURRENT).resolve(strict=False),
        Path(BASE_AUDIT.DEFAULT_PK_PRISTINE).resolve(strict=False),
    }
    require(
        args.private_output.resolve(strict=False) not in steam_paths
        and args.public_output.resolve(strict=False) not in steam_paths,
        "assignment output may not target Steam data",
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--private-output",
        type=Path,
        default=DEFAULT_PRIVATE_OUTPUT,
    )
    parser.add_argument(
        "--public-output",
        type=Path,
        default=DEFAULT_PUBLIC_OUTPUT,
    )
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    validate_paths(args)
    private_content, public_content, _manifest, report = build_outputs()
    validate_outputs(
        private_content,
        public_content,
        require_frozen_hashes=bool(
            EXPECTED_PRIVATE_FILE_SHA256 and EXPECTED_PUBLIC_FILE_SHA256
        ),
    )
    outputs = {
        args.private_output: private_content,
        args.public_output: public_content,
    }
    if args.check:
        for path, content in outputs.items():
            require(path.is_file(), f"assignment output missing: {path}")
            require(
                path.read_text(encoding="utf-8") == content,
                f"assignment output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "chunks": EXPECTED_CHUNK_COUNTS,
                "direct_pending_ceiling": EXPECTED_DIRECT_PENDING_ROWS,
                "private_sha256": report["guards"][
                    "private_assignment_sha256"
                ],
                "public_sha256": sha256_bytes(
                    public_content.encode("utf-8")
                ),
                "selector": SELECTOR,
                "site_count": EXPECTED_SITE_COUNT,
                "status": "PASS",
                "structural_pending_ceiling":
                    EXPECTED_STRUCTURAL_PENDING_ROWS,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
