#!/usr/bin/env python3
"""Validate selector-568 chunk-0 and build its source-free review report."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
BASE_BUILDER = WORKSTREAM / "build_pk_selector538_chunk0_review_v1.py"
ASSIGNMENT_BUILDER = WORKSTREAM / "build_pk_selector568_assignment_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "family568_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector568_assignment_coverage.v1.json"
)
PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family568_chunk0_analysis.private.v1.json"
)
DEFAULT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector568_chunk0_review_proposal.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector568-chunk0-analysis.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector568-chunk0-review-proposal.v1"
METHOD = "reversed_vm_pk_selector568_chunk0_full_caller_review"
SELECTOR = 568
TERMINALS = tuple(range(1951, 1958))
PLAIN_TERMINALS = {1952, 1957}
ARCHAIC_POLITE_TERMINALS = {1951, 1956}
ORDINAL_START = 0
ORDINAL_END = 76
EXPECTED_SITE_COUNT = 77
EXPECTED_ROOT_COUNT = 75
EXPECTED_ASSEMBLY_COUNT = 539
EXPECTED_ACCEPTED = 62
EXPECTED_REWRITE = 59
EXPECTED_KEEP = 3
EXPECTED_REJECT = 15
EXPECTED_ACCEPTED_ROOTS = 61
EXPECTED_REJECTED_ROOTS = 14
EXPECTED_ACCEPTED_ASSEMBLIES = 434
EXPECTED_REJECTED_ASSEMBLIES = 105
EXPECTED_POTENTIAL_PROMOTION_COUNT = 92
EXPECTED_BLOCKED_PENDING_COUNT = 39

EXPECTED_ASSIGNMENT_SHA256 = (
    "B55F2C43D8B4149DDE1739D35FF322E5A6A30C3D58E77AC2500D45200A4AAB98"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "BF889606D3C2748B5923CDD9FC46936ED5DE6DED9993FC1B29D5F00785FB6D91"
)
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_LEDGER_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_CHUNK_SITE_SHA256 = (
    "0DD979A72792AA44E0E5D79C4BEF3F0262E02F157B298622933431208A1BFF8C"
)
EXPECTED_CHUNK_ROOT_SHA256 = (
    "37A28097D7D31D6683183E5BB6E5085F975787B18FE3CCE2BE3CE32B28FF529A"
)
EXPECTED_PENDING_COORDINATE_SHA256 = (
    "567251B91AEE376B198425B1E2228A177F4730D28F19D983E7C863969601FC18"
)
EXPECTED_PENDING_ROW_UPPER_BOUND = 131
EXPECTED_CHUNK0_CURRENT_LIVE_PENDING = 126
EXPECTED_CHUNK0_LIVE_AFTER_SELECTOR538_PLAN = 126
EXPECTED_CHUNK0_PRIORITY_SHA256 = (
    "B6E971EB92B5EA70069F24F1814C4C8D3F71F29935E0156CDD4BA007D2CBAFD6"
)

# Frozen after the private handoff and public proposal are reproduced.
EXPECTED_PRIVATE_HANDOFF_SHA256: str | None = (
    "07F069C6F6792DE68D84FA7E9FBCF8E9AD809A5509B825E18663BA729191CAF4"
)
EXPECTED_PROPOSAL_CANDIDATE_SHA256: str | None = (
    "85712C168C725C99824748B109A1AEC5BD79445FB2461460FCE31366EEDD6A51"
)
EXPECTED_REWRITE_COORDINATE_SHA256: str | None = (
    "F9692E0730E531A6E819E39ABE0921E5B93D9BF6CABAA12B054E63BE105408E4"
)
EXPECTED_KEEP_COORDINATE_SHA256: str | None = (
    "2CE170B713C37FE7D35EE7F0DFB5D68B0818624EA73AD785DE5D731A4201BD32"
)
EXPECTED_REJECT_COORDINATE_SHA256: str | None = (
    "230509FD6E5EB20909C3712C456B408EF7D69A385BA158B191011B7EE7FC2EE3"
)
EXPECTED_ACCEPTED_SITE_SHA256: str | None = (
    "0B6922C76EF0C6CC10DC8D18D0D808EE2B955F5315621DC13B44FE53152DC12C"
)
EXPECTED_REJECTED_SITE_SHA256: str | None = (
    "FD900D5E544C4CD2E70A1AADBC72764C72848FAA41FCFDEDF79E3E6B8B5394D2"
)
EXPECTED_ASSEMBLY_SHA256: str | None = (
    "498DA28B444C0466BED645E0CED6ACBFA28DD2A6E30A5BC2665F805701BCB373"
)
EXPECTED_ACCEPTED_ROOT_SHA256: str | None = (
    "84C3A31CB2453469A516A88FEB40EE813FB15D8E4818E3364E64A7C620520342"
)
EXPECTED_REJECTED_ROOT_SHA256: str | None = (
    "AFAF54C02B2785B7BE0092393DAFAC15BC6E64881866EDB48ADF27B905939759"
)
EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256: str | None = (
    "793AFC5890C74D96D7087E758E55AFBB26681DE589A031638A0347B385B99A78"
)
EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256: str | None = (
    "1C25964442B1E724A38E75C77191FD39E8283CC74816D4F6AFF0B8CB5DA6A980"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "214672A7D195B2162A3E2CF687B5071D1A1485C232305FB7AC16B5D959BDD97C"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_BUILDER, "pk_selector568_chunk0_review_base_v1")
ASSIGN = load_module(
    ASSIGNMENT_BUILDER,
    "pk_selector568_chunk0_review_assignment_v1",
)
ASSIGN.adjacent_literals = ASSIGN.BASE.adjacent_literals
ReviewError = BASE.ReviewError
require = BASE.require
sha256_bytes = BASE.sha256_bytes
sha256_file = BASE.sha256_file
canonical_bytes = BASE.canonical_bytes
canonical_sha256 = BASE.canonical_sha256
coordinate_digest = BASE.coordinate_digest
site_digest = BASE.site_digest
root_digest = BASE.root_digest
parse_coordinate = BASE.parse_coordinate
site_root = BASE.site_root
line_metrics = BASE.line_metrics
current_relative_nonexpanding = BASE.current_relative_nonexpanding
outer_whitespace_signature = BASE.outer_whitespace_signature
record_gap_sha256 = BASE.record_gap_sha256
adjacent_literals = BASE.adjacent_literals
terminal_literals = BASE.terminal_literals
load_json_exact = BASE.load_json_exact
CALLER = ASSIGN.CALLER
BASE_AUDIT = CALLER.BASE_AUDIT
ENGINE = CALLER.ENGINE

_CONTRACT = {
    "ASSIGN": ASSIGN,
    "CALLER": CALLER,
    "BASE_AUDIT": BASE_AUDIT,
    "ENGINE": ENGINE,
    "ASSIGNMENT_PATH": ASSIGNMENT_PATH,
    "PRIVATE_HANDOFF_PATH": PRIVATE_HANDOFF_PATH,
    "DEFAULT_OUTPUT": DEFAULT_OUTPUT,
    "PRIVATE_SCHEMA": PRIVATE_SCHEMA,
    "PUBLIC_SCHEMA": PUBLIC_SCHEMA,
    "METHOD": METHOD,
    "SELECTOR": SELECTOR,
    "TERMINALS": TERMINALS,
}
for _name in (
    "ORDINAL_START",
    "ORDINAL_END",
    "EXPECTED_SITE_COUNT",
    "EXPECTED_ASSEMBLY_COUNT",
    "EXPECTED_ACCEPTED",
    "EXPECTED_REWRITE",
    "EXPECTED_KEEP",
    "EXPECTED_REJECT",
    "EXPECTED_ACCEPTED_ASSEMBLIES",
    "EXPECTED_REJECTED_ASSEMBLIES",
    "EXPECTED_ASSIGNMENT_SHA256",
    "EXPECTED_BASELINE_CANDIDATE_SHA256",
    "EXPECTED_LEDGER_SHA256",
    "EXPECTED_CHUNK_SITE_SHA256",
    "EXPECTED_CHUNK_ROOT_SHA256",
    "EXPECTED_PENDING_COORDINATE_SHA256",
    "EXPECTED_PENDING_ROW_UPPER_BOUND",
    "EXPECTED_PRIVATE_HANDOFF_SHA256",
    "EXPECTED_PROPOSAL_CANDIDATE_SHA256",
    "EXPECTED_REWRITE_COORDINATE_SHA256",
    "EXPECTED_KEEP_COORDINATE_SHA256",
    "EXPECTED_REJECT_COORDINATE_SHA256",
    "EXPECTED_ACCEPTED_SITE_SHA256",
    "EXPECTED_REJECTED_SITE_SHA256",
    "EXPECTED_ASSEMBLY_SHA256",
    "EXPECTED_ACCEPTED_ROOT_SHA256",
    "EXPECTED_REJECTED_ROOT_SHA256",
    "EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256",
    "EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256",
    "EXPECTED_PUBLIC_FILE_SHA256",
):
    _CONTRACT[_name] = globals()[_name]
for _name, _value in _CONTRACT.items():
    setattr(BASE, _name, _value)


def load_assignment() -> tuple[dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(ASSIGNMENT_PATH) == EXPECTED_ASSIGNMENT_SHA256,
        "selector 568 assignment hash drifted",
    )
    assignment = load_json_exact(ASSIGNMENT_PATH)
    require(
        assignment.get("schema") == ASSIGN.PRIVATE_SCHEMA,
        "selector 568 assignment schema drifted",
    )
    chunk = assignment["chunks"][0]
    require(
        chunk.get("chunk_id") == 0
        and chunk.get("ordinal_start") == ORDINAL_START
        and chunk.get("ordinal_end") == ORDINAL_END
        and chunk.get("site_count") == EXPECTED_SITE_COUNT
        and chunk.get("root_count") == EXPECTED_ROOT_COUNT
        and chunk.get("site_sha256") == EXPECTED_CHUNK_SITE_SHA256
        and chunk.get("root_sha256") == EXPECTED_CHUNK_ROOT_SHA256
        and chunk.get("pending_coordinate_sha256")
        == EXPECTED_PENDING_COORDINATE_SHA256
        and chunk.get("pending_row_upper_bound")
        == EXPECTED_PENDING_ROW_UPPER_BOUND,
        "selector 568 chunk-0 assignment drifted",
    )
    return assignment, chunk


def load_world() -> dict[str, Any]:
    *_unused, bundle = ASSIGN.final_outputs()
    analysis = bundle["analysis"]
    candidate_blob = analysis["candidate_blob"]
    require(
        sha256_bytes(candidate_blob) == EXPECTED_BASELINE_CANDIDATE_SHA256,
        "selector 568 baseline candidate drifted",
    )
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    resource = prepared.resources["pk_msggame"]
    return {
        "candidate_blob": candidate_blob,
        "candidate_records": analysis["candidate_records"],
        "current_records": ENGINE.archive_records(resource.current_archive),
        "language_records": {
            "jp": ENGINE.archive_records(resource.pristine_archive),
            "sc": ENGINE.archive_records(resource.context_archives["SC"]),
            "tc": ENGINE.archive_records(resource.context_archives["TC"]),
            "en": ENGINE.archive_records(resource.context_archives["EN"]),
        },
    }


_BASE_VALIDATE_PRIVATE_HANDOFF = BASE.validate_private_handoff


def semantic_register(terminal: int) -> str:
    if terminal in PLAIN_TERMINALS:
        return "plain"
    if terminal in ARCHAIC_POLITE_TERMINALS:
        return "archaic_polite"
    return "formal_polite"


def validate_private_handoff(
    handoff: Mapping[str, Any],
    *,
    assignment: Mapping[str, Any],
    chunk: Mapping[str, Any],
    world: Mapping[str, Any],
) -> dict[str, Any]:
    result = _BASE_VALIDATE_PRIVATE_HANDOFF(
        handoff,
        assignment=assignment,
        chunk=chunk,
        world=world,
    )
    for row in handoff["site_reviews"]:
        for terminal, branch in zip(TERMINALS, row["assemblies"]):
            require(
                branch.get("register_semantic")
                == semantic_register(terminal),
                f"selector 568 semantic register drifted: "
                f"{row['site']}/{terminal}",
            )
    return result


BASE.load_assignment = load_assignment
BASE.load_world = load_world
BASE.validate_private_handoff = validate_private_handoff


def assert_source_free(value: Any) -> None:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            serialized,
        )
        is None,
        "public selector-568 review contains dialogue text",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", serialized) is None,
        "public selector-568 review contains an exact coordinate",
    )


def build_report() -> tuple[dict[str, Any], dict[str, str]]:
    assignment, chunk = load_assignment()
    require(
        sha256_file(ASSIGNMENT_PUBLIC_PATH)
        == EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        "selector 568 public assignment evidence drifted",
    )
    live_steam_path = Path(CALLER.LIVE_STEAM_PK)
    require(live_steam_path.is_file(), "live Steam PK msggame is absent")
    steam_before = sha256_file(live_steam_path)
    world = load_world()
    handoff = load_json_exact(PRIVATE_HANDOFF_PATH)
    private_sha256 = sha256_file(PRIVATE_HANDOFF_PATH)
    if EXPECTED_PRIVATE_HANDOFF_SHA256 is not None:
        require(
            private_sha256 == EXPECTED_PRIVATE_HANDOFF_SHA256,
            "private selector-568 handoff hash drifted",
        )
    validated = validate_private_handoff(
        handoff,
        assignment=assignment,
        chunk=chunk,
        world=world,
    )
    steam_after = sha256_file(live_steam_path)
    require(steam_before == steam_after, "Steam archive changed during review")

    rewrite_coordinates = sorted(
        validated["rewrite_map"], key=parse_coordinate
    )
    keep_coordinates = sorted(validated["keep_map"], key=parse_coordinate)
    reject_coordinates = sorted(validated["reject_map"], key=parse_coordinate)
    accepted_sites = sorted(validated["accepted_sites"])
    rejected_sites = sorted(validated["rejected_sites"])
    accepted_roots = {site_root(site) for site in accepted_sites}
    rejected_roots = {site_root(site) for site in rejected_sites}
    require(
        len(accepted_roots) == EXPECTED_ACCEPTED_ROOTS
        and len(rejected_roots) == EXPECTED_REJECTED_ROOTS
        and accepted_roots.isdisjoint(rejected_roots),
        "selector-568 accepted/rejected root partition drifted",
    )
    pending_coordinates = list(chunk["pending_coordinates"])
    potential_promotion_coordinates = [
        coordinate
        for coordinate in pending_coordinates
        if parse_coordinate(coordinate)[:2] in accepted_roots
    ]
    blocked_pending_coordinates = [
        coordinate
        for coordinate in pending_coordinates
        if parse_coordinate(coordinate)[:2] in rejected_roots
    ]
    require(
        len(potential_promotion_coordinates)
        == EXPECTED_POTENTIAL_PROMOTION_COUNT
        and len(blocked_pending_coordinates)
        == EXPECTED_BLOCKED_PENDING_COUNT
        and len(potential_promotion_coordinates)
        + len(blocked_pending_coordinates)
        == EXPECTED_PENDING_ROW_UPPER_BOUND,
        "selector-568 chunk-0 pending partition drifted",
    )
    site_rows = validated["site_rows"]
    language_counts = {
        language: sum(
            bool(row["multilingual_authority"][language]["available"])
            for row in site_rows
        )
        for language in ("jp", "sc", "tc", "en")
    }
    blocker_counts = Counter(
        str(row["reject_reason"]) for row in site_rows
        if row["decision"] == "reject"
    )
    assignment_graph = assignment["graph_evidence"]
    current_live = set(
        assignment_graph["current_live_pending_coordinates"]
    )
    live_after_plan = set(
        assignment_graph["live_after_selector538_plan_coordinates"]
    )
    accepted_current_live = (
        set(potential_promotion_coordinates) & current_live
    )
    accepted_live_after_plan = (
        set(potential_promotion_coordinates) & live_after_plan
    )

    report: dict[str, Any] = {
        "distribution_policy": {
            "private_handoff_contains_dialogue_bodies": True,
            "private_handoff_stays_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_translation_map_keys": False,
        },
        "inputs": {
            "assignment_private_sha256": EXPECTED_ASSIGNMENT_SHA256,
            "assignment_public_sha256":
                EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
            "baseline_candidate_sha256":
                EXPECTED_BASELINE_CANDIDATE_SHA256,
            "integrated_ledger_sha256": EXPECTED_LEDGER_SHA256,
        },
        "method": METHOD,
        "proof": {
            "accepted_assembly_branches": EXPECTED_ACCEPTED_ASSEMBLIES,
            "all_77_sites_classified": True,
            "all_accepted_current_relative_raw_g1n_nonexpanding": True,
            "all_accepted_register_branches_proven": True,
            "all_changed_record_control_gaps_preserved": True,
            "all_literal_linebreak_counts_preserved": True,
            "all_outer_whitespace_signatures_preserved": True,
            "assembly_branches_recorded": EXPECTED_ASSEMBLY_COUNT,
            "assembly_canonical_sha256": canonical_sha256(
                validated["assembly_manifest"]
            ),
            "auxiliary_language_available_counts": language_counts,
            "blocker_reason_counts": dict(sorted(blocker_counts.items())),
            "chunk0_live_pending_priority_sha256":
                EXPECTED_CHUNK0_PRIORITY_SHA256,
            "fresh_semantic_review_sites": EXPECTED_SITE_COUNT,
            "historical_term_review_sites": EXPECTED_SITE_COUNT,
            "jp_authority_sites": EXPECTED_SITE_COUNT,
            "rejected_assembly_branches": EXPECTED_REJECTED_ASSEMBLIES,
            "speaker_tone_review_sites": EXPECTED_SITE_COUNT,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": {
            "accepted_current_a19_live_pending_count":
                len(accepted_current_live),
            "accepted_current_a19_live_pending_sha256":
                coordinate_digest(accepted_current_live),
            "accepted_live_after_selector538_plan_count":
                len(accepted_live_after_plan),
            "accepted_live_after_selector538_plan_sha256":
                coordinate_digest(accepted_live_after_plan),
            "accepted_root_count": len(accepted_roots),
            "accepted_root_sha256": root_digest(accepted_roots),
            "accepted_site_count": EXPECTED_ACCEPTED,
            "accepted_site_sha256": site_digest(accepted_sites),
            "blocked_pending_coordinate_count":
                len(blocked_pending_coordinates),
            "blocked_pending_coordinate_sha256": coordinate_digest(
                blocked_pending_coordinates
            ),
            "keep_coordinate_count": EXPECTED_KEEP,
            "keep_coordinate_sha256": coordinate_digest(keep_coordinates),
            "potential_promotion_coordinate_count":
                len(potential_promotion_coordinates),
            "potential_promotion_coordinate_sha256": coordinate_digest(
                potential_promotion_coordinates
            ),
            "proposal_candidate_sha256":
                validated["proposal_candidate_sha256"],
            "reject_coordinate_count": EXPECTED_REJECT,
            "reject_coordinate_sha256": coordinate_digest(
                reject_coordinates
            ),
            "rejected_root_count": len(rejected_roots),
            "rejected_root_sha256": root_digest(rejected_roots),
            "rejected_site_count": EXPECTED_REJECT,
            "rejected_site_sha256": site_digest(rejected_sites),
            "rewrite_coordinate_count": EXPECTED_REWRITE,
            "rewrite_coordinate_sha256": coordinate_digest(
                rewrite_coordinates
            ),
        },
        "schema": PUBLIC_SCHEMA,
        "scope": {
            "chunk_id": 0,
            "ordinal_end": ORDINAL_END,
            "ordinal_start": ORDINAL_START,
            "pending_coordinate_sha256":
                EXPECTED_PENDING_COORDINATE_SHA256,
            "pending_row_upper_bound": EXPECTED_PENDING_ROW_UPPER_BOUND,
            "root_count": EXPECTED_ROOT_COUNT,
            "root_sha256": EXPECTED_CHUNK_ROOT_SHA256,
            "selector": SELECTOR,
            "site_count": EXPECTED_SITE_COUNT,
            "site_sha256": EXPECTED_CHUNK_SITE_SHA256,
            "terminal_count": len(TERMINALS),
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    report["guards"] = {
        "private_handoff_sha256": private_sha256,
        "report_payload_sha256": canonical_sha256(report),
        "steam_archive_sha256_after": steam_after,
        "steam_archive_sha256_before": steam_before,
    }
    assert_source_free(report)
    frozen = {
        "accepted_root_sha256": report["result"]["accepted_root_sha256"],
        "accepted_site_sha256": report["result"]["accepted_site_sha256"],
        "assembly_sha256": report["proof"]["assembly_canonical_sha256"],
        "blocked_pending_coordinate_sha256": report["result"][
            "blocked_pending_coordinate_sha256"
        ],
        "keep_coordinate_sha256": report["result"][
            "keep_coordinate_sha256"
        ],
        "private_handoff_sha256": private_sha256,
        "proposal_candidate_sha256": report["result"][
            "proposal_candidate_sha256"
        ],
        "potential_promotion_coordinate_sha256": report["result"][
            "potential_promotion_coordinate_sha256"
        ],
        "reject_coordinate_sha256": report["result"][
            "reject_coordinate_sha256"
        ],
        "rejected_root_sha256": report["result"][
            "rejected_root_sha256"
        ],
        "rejected_site_sha256": report["result"][
            "rejected_site_sha256"
        ],
        "rewrite_coordinate_sha256": report["result"][
            "rewrite_coordinate_sha256"
        ],
    }
    return report, frozen


def validate_frozen(frozen: Mapping[str, str]) -> None:
    expected = {
        "accepted_root_sha256": EXPECTED_ACCEPTED_ROOT_SHA256,
        "accepted_site_sha256": EXPECTED_ACCEPTED_SITE_SHA256,
        "assembly_sha256": EXPECTED_ASSEMBLY_SHA256,
        "blocked_pending_coordinate_sha256":
            EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256,
        "keep_coordinate_sha256": EXPECTED_KEEP_COORDINATE_SHA256,
        "private_handoff_sha256": EXPECTED_PRIVATE_HANDOFF_SHA256,
        "proposal_candidate_sha256": EXPECTED_PROPOSAL_CANDIDATE_SHA256,
        "potential_promotion_coordinate_sha256":
            EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256,
        "reject_coordinate_sha256": EXPECTED_REJECT_COORDINATE_SHA256,
        "rejected_root_sha256": EXPECTED_REJECTED_ROOT_SHA256,
        "rejected_site_sha256": EXPECTED_REJECTED_SITE_SHA256,
        "rewrite_coordinate_sha256": EXPECTED_REWRITE_COORDINATE_SHA256,
    }
    for key, value in expected.items():
        if value is not None:
            require(frozen[key] == value, f"frozen {key} drifted")


def serialized_report() -> tuple[bytes, dict[str, str]]:
    report, frozen = build_report()
    validate_frozen(frozen)
    return canonical_bytes(report) + b"\n", frozen


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(
        args.output.resolve(strict=False)
        == DEFAULT_OUTPUT.resolve(strict=False),
        "selector-568 public report must use its fixed tracked path",
    )
    content, frozen = serialized_report()
    file_sha256 = sha256_bytes(content)
    if EXPECTED_PUBLIC_FILE_SHA256 is not None:
        require(
            file_sha256 == EXPECTED_PUBLIC_FILE_SHA256,
            "selector-568 public proposal file hash drifted",
        )
    if args.check:
        require(args.output.is_file(), f"proposal is absent: {args.output}")
        require(
            args.output.read_bytes() == content,
            "selector-568 public proposal content drifted",
        )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(content)
    print(
        json.dumps(
            {
                "file_sha256": file_sha256,
                "frozen": frozen,
                "output": str(args.output),
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
