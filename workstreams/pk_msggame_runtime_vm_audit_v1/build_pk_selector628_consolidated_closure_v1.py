#!/usr/bin/env python3
"""Build the selector-628 single-union closure on frozen post-selector514."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
SEMANTIC_TMP = DIALOGUE_TMP / "semantic_overrides"
PUBLIC_DIR = WORKSTREAM / "public"

BASE_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector514_consolidated_closure_core_v1.py"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector628_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector628_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector628_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector514_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector514_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector628_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector628_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP
    / f"pk_selector628_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector628_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector628_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector628_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector628_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector628_consolidated_closure_promotion.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "AE64FFC67F3B8424E78026DE82D32D8A176051A4FF8B45C1FDDBB750155DE4A3"
)
EXPECTED_INPUT_SHA256 = {
    "assignment_builder":
        "4781B9533C51ED3B5A7147AE79C2E314539DECF4DAE4E2A71262340D6A4DACDE",
    "assignment_private":
        "14578A2713C45C4E3088E7B9547ED48CFA4BC0B2CCF8795EE522EF614691F87B",
    "assignment_public":
        "82CE0CA3BBC6579125AF1D0C20BFBF6A508B1F51594B53EC23103842CCF3B476",
    "official_ledger":
        "FCAB3A5CACEEAE4C610BD284D8C0631E65DA14562DB7B78A66655554EED07A79",
    "predecessor_decisions":
        "9934DEDCE404E2F27EE6680BF43E2B4E8E7870FE6F728E96D09DF566529F1444",
    "chunk0_builder":
        "C6828B7CD6EAC0E61D9E466A1CF27287F367DFD9B0C93C9C558FA285D91D577E",
    "chunk0_public":
        "6B217383997591962EEC8B166302809E18DB674E3CCC344C68CB9B5B0CD2B11C",
    "chunk0_decisions":
        "47A984E2BE18C7B8C84F9E4ADA888C5EA6AB6C6809F33517F99BE86D7F7DDB44",
    "chunk0_evidence":
        "C08808F2E9E576D9990BEC349707B64EFAF0A06436C808C57B207D9A5742AC97",
    "chunk1_builder":
        "5EFEE1D834C9C3570B7E06BE822527650A82D12DD9B4D9267942A232A385E090",
    "chunk1_public":
        "4343397CC9BD15BFAD0283BEB9353DE322ABE54984893FA517261C70DF4211C2",
    "chunk1_decisions":
        "139F319F7A964105ECDCB2A78E37DDE87BA6DBD13D341323B736BD204867B8F9",
    "chunk1_evidence":
        "C97908A6EC4CF60A8E1501943A1A8CC05F67A028B37C3584D1E098CF1844B565",
}

EXPECTED_DECISION_ROWS = 100
EXPECTED_DECISION_ROOTS = 50
EXPECTED_PROMOTIONS = 58
EXPECTED_RENEWALS = 42
EXPECTED_OVERRIDES = 60
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 40,
    "translation_override_and_runtime_promotion": 18,
    "translation_override_and_verification_renewal": 42,
}
EXPECTED_CHUNK_ROWS = (30, 70)
EXPECTED_CHUNK_SITES = (73, 72)
EXPECTED_REVIEWED_SITES = 145
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "8ACBBCAE255F2F4C1BAD8AC57D23E344EF533A93C6F0523FFE669907DD596D57"
)
EXPECTED_SOURCE_SITES = 166
EXPECTED_SOURCE_SITE_SHA256 = (
    "AF74E12952F6787BFBAB10DA19558595CE9260CB77934B08DF63BA27100134C7"
)
EXPECTED_SOURCE_ONLY_SITES = 21
EXPECTED_SOURCE_ONLY_SHA256 = (
    "23C63D343F24382696B596DD38C08FD78D4DB287F15714E520B4E60E5F09990C"
)
EXPECTED_PREDECESSOR_OVERLAPS = 1
EXPECTED_PREDECESSOR_SUPERSESSIONS = 1
EXPECTED_PENDING_BEFORE = 6_547
EXPECTED_PENDING_AFTER = 6_489
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "623C6EE2BDC25B13680C353C97847C3AC646C4B2B222A51F0F242B7A1CC2E093"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "49BB13AF414DA7A751F7B9CA9830386A3832FF99411B4FC39DC96F94FE649100"
)

EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "009C9D4B7DCE6CE0E7F07D21F827FB4633DF3C01A3BA6D097AC19F04E0CBE2C4",
    "private_evidence":
        "F99DC2F8AA28D3BF12FBB01F8B876B12F0E70598B6543E1E39E4B16F5D9AF175",
    "public_coverage":
        "19F20B71648A392E239930E36311C303C4F48DDA526329A96875CEC3EB0C5BAC",
    "public_promotion":
        "C989EF03AAEB433B3D1484B439593EE5C9BC6A61BED789C9977A87AB7FD7CEEB",
    "final_candidate":
        "28267B6928CBDBF3E98FBB8E13A4733947A4EAC6A2BF04812A848C1091F9B186",
    "decision_coordinates":
        "E59F2DCE04734EED5732D6CFD475AF379589EAFB8FF6484B3BD0A387F62B6ACE",
    "promotion_coordinates":
        "828A08D4E2E26B45BF598137C9DA16B88B240609AE33B5E180D49EE81DF1E62C",
    "renewal_coordinates":
        "C0276E37E4AABAE781766BDB612218D0AF147F0DDC5FE196B3A25FF6C97723E0",
    "override_coordinates":
        "1018F3E00D32CCA5A7A53D68BE2B669C0CE2CF03769D39358B2A07B433E48E6C",
    "predecessor_overlap_coordinates":
        "F51BC5D6A38AD5B9049D647A8BA69DA9B20278B79F9AD1BF2CBB5B22D46908B9",
    "predecessor_supersession_coordinates":
        "F51BC5D6A38AD5B9049D647A8BA69DA9B20278B79F9AD1BF2CBB5B22D46908B9",
    "source_only_proof":
        "BD8EDCC3D82F5D1DDCAB89255EFBCCF60A3F39F3241199B0306C2FB5C5FE36C7",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_BUILDER_PATH, "selector628_closure_base")
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector628_closure_input")


def configure_base() -> None:
    values = {
        "ASSIGNMENT": ASSIGNMENT,
        "ASSIGNMENT_BUILDER_PATH": ASSIGNMENT_BUILDER_PATH,
        "ASSIGNMENT_PRIVATE_PATH": ASSIGNMENT_PRIVATE_PATH,
        "ASSIGNMENT_PUBLIC_PATH": ASSIGNMENT_PUBLIC_PATH,
        "OFFICIAL_LEDGER_PATH": OFFICIAL_LEDGER_PATH,
        "PREDECESSOR_DECISIONS_PATH": PREDECESSOR_DECISIONS_PATH,
        "CHUNK_BUILDERS": CHUNK_BUILDERS,
        "CHUNK_PUBLIC": CHUNK_PUBLIC,
        "CHUNK_DECISIONS": CHUNK_DECISIONS,
        "CHUNK_EVIDENCE": CHUNK_EVIDENCE,
        "PRIVATE_DECISIONS_OUTPUT": PRIVATE_DECISIONS_OUTPUT,
        "PRIVATE_EVIDENCE_OUTPUT": PRIVATE_EVIDENCE_OUTPUT,
        "PUBLIC_COVERAGE_OUTPUT": PUBLIC_COVERAGE_OUTPUT,
        "PUBLIC_PROMOTION_OUTPUT": PUBLIC_PROMOTION_OUTPUT,
        "EXPECTED_INPUT_SHA256": EXPECTED_INPUT_SHA256,
        "EXPECTED_CHUNK_ROWS": EXPECTED_CHUNK_ROWS,
        "EXPECTED_CHUNK_SITES": EXPECTED_CHUNK_SITES,
        "EXPECTED_DECISION_ROWS": EXPECTED_DECISION_ROWS,
        "EXPECTED_DECISION_ROOTS": EXPECTED_DECISION_ROOTS,
        "EXPECTED_PROMOTIONS": EXPECTED_PROMOTIONS,
        "EXPECTED_RENEWALS": EXPECTED_RENEWALS,
        "EXPECTED_OVERRIDES": EXPECTED_OVERRIDES,
        "EXPECTED_ACTION_COUNTS": EXPECTED_ACTION_COUNTS,
        "EXPECTED_PENDING_BEFORE": EXPECTED_PENDING_BEFORE,
        "EXPECTED_PENDING_AFTER": EXPECTED_PENDING_AFTER,
        "EXPECTED_REVIEWED_SITES": EXPECTED_REVIEWED_SITES,
        "EXPECTED_CANDIDATE_SITE_SHA256": EXPECTED_CANDIDATE_SITE_SHA256,
        "EXPECTED_SOURCE_SITES": EXPECTED_SOURCE_SITES,
        "EXPECTED_SOURCE_SITE_SHA256": EXPECTED_SOURCE_SITE_SHA256,
        "EXPECTED_SOURCE_ONLY_SITES": EXPECTED_SOURCE_ONLY_SITES,
        "EXPECTED_SOURCE_ONLY_SHA256": EXPECTED_SOURCE_ONLY_SHA256,
        "EXPECTED_PREDECESSOR_OVERLAPS": EXPECTED_PREDECESSOR_OVERLAPS,
        "EXPECTED_PREDECESSOR_SUPERSESSIONS":
            EXPECTED_PREDECESSOR_SUPERSESSIONS,
        "EXPECTED_OFFICIAL_CANDIDATE_SHA256":
            EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        "EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256":
            EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256,
        "EXPECTED_OUTPUT_SHA256": {
            key: None for key in EXPECTED_OUTPUT_SHA256
        },
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.METHOD = (
        "post_selector514_selector628_two_chunk_single_coordinate_union_"
        "with_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector628-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector628-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector628-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector628-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector628_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = (
        "nobu16.kr.pk-selector628-assignment.private.v1"
    )


def validate_site_call(
    records: Mapping[tuple[int, int], Any],
    site: str,
    *,
    expected: bool,
) -> None:
    block_id, record_id, gap_id, offset = map(int, site.split(":"))
    rows = [
        row
        for row in BASE.RANKING.LEGACY.record_edges(records[(block_id, record_id)])
        if row["kind"] == "C"
        and tuple(row["target"]) == (0, 628)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-628 site drifted: {site}")


def source_only_runtime_delta_proof(
    assignment: Mapping[str, Any],
    current_records: Mapping[tuple[int, int], Any],
    candidate_records: Mapping[tuple[int, int], Any],
    source_records: Mapping[tuple[int, int], Any],
) -> dict[str, Any]:
    candidate_sites = set(map(str, assignment["scope"]["candidate_call_sites"]))
    source_only = set(
        map(str, assignment["scope"]["source_only_repair_sites"])
    )
    source_sites = candidate_sites | source_only
    BASE.require(
        len(candidate_sites) == EXPECTED_REVIEWED_SITES
        and BASE.site_digest(candidate_sites) == EXPECTED_CANDIDATE_SITE_SHA256,
        "candidate site register drifted",
    )
    BASE.require(
        len(source_sites) == EXPECTED_SOURCE_SITES
        and BASE.site_digest(source_sites) == EXPECTED_SOURCE_SITE_SHA256,
        "source site register drifted",
    )
    BASE.require(
        len(source_only) == EXPECTED_SOURCE_ONLY_SITES
        and BASE.site_digest(source_only) == EXPECTED_SOURCE_ONLY_SHA256,
        "source-only register drifted",
    )
    for site in sorted(candidate_sites, key=BASE.RANKING.site_key):
        validate_site_call(current_records, site, expected=True)
        validate_site_call(candidate_records, site, expected=True)
        validate_site_call(source_records, site, expected=True)
    proof_rows = []
    for site in sorted(source_only, key=BASE.RANKING.site_key):
        validate_site_call(source_records, site, expected=True)
        validate_site_call(current_records, site, expected=False)
        validate_site_call(candidate_records, site, expected=False)
        root = tuple(map(int, site.split(":")[:2]))
        for records, label in (
            (current_records, "current"),
            (candidate_records, "candidate"),
        ):
            calls = [
                row
                for row in BASE.RANKING.LEGACY.record_edges(records[root])
                if row["kind"] == "C" and tuple(row["target"]) == (0, 628)
            ]
            BASE.require(
                not calls, f"source-only root has a {label} selector call"
            )
        proof_rows.append(
            {
                "site": site,
                "source_call_present": True,
                "current_call_absent": True,
                "candidate_call_absent": True,
                "action": "none",
            }
        )
    return {
        "actions": 0,
        "classification": "pristine_only_control_delta_absent_from_runtime",
        "proof_rows": proof_rows,
        "proof_sha256": BASE.canonical_sha256(proof_rows),
        "site_count": len(source_only),
        "site_sha256": BASE.site_digest(source_only),
    }


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("ascii"))
    proof = coverage["proof"]
    proof.pop("all_230_candidate_sites_reviewed", None)
    proof.pop("source_only_13_absent_from_current_and_candidate", None)
    proof["all_145_candidate_sites_reviewed"] = True
    proof["source_only_21_absent_from_current_and_candidate"] = True
    coverage["guards"].pop("payload_without_guard_sha256")
    coverage["guards"]["payload_without_guard_sha256"] = BASE.canonical_sha256(
        coverage
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


def build_outputs() -> dict[Path, bytes]:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector closure base drifted",
    )
    configure_base()
    BASE.validate_site_call = validate_site_call
    BASE.source_only_runtime_delta_proof = source_only_runtime_delta_proof
    outputs = transform_outputs(BASE.build_outputs())
    labels = {
        PRIVATE_DECISIONS_OUTPUT: "private_decisions",
        PRIVATE_EVIDENCE_OUTPUT: "private_evidence",
        PUBLIC_COVERAGE_OUTPUT: "public_coverage",
        PUBLIC_PROMOTION_OUTPUT: "public_promotion",
    }
    for path, label in labels.items():
        expected = EXPECTED_OUTPUT_SHA256[label]
        BASE.require(
            expected is None or BASE.sha256_bytes(outputs[path]) == expected,
            f"frozen {label} drifted",
        )
    return outputs


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    outputs = build_outputs()
    if args.check:
        for path, content in outputs.items():
            BASE.require(
                path.is_file() and path.read_bytes() == content,
                f"selector628 closure output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(
        json.dumps(
            {
                "decision_rows": EXPECTED_DECISION_ROWS,
                "pending_after": EXPECTED_PENDING_AFTER,
                "promotions": EXPECTED_PROMOTIONS,
                "source_only_actions": 0,
                "status": "PASS",
                "steam_write_performed": False,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
