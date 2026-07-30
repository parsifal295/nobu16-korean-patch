#!/usr/bin/env python3
"""Build the independent selector-568 chunk-0 runtime closure layer.

BF7B remains the immutable graph-analysis baseline.  The current a19
integrated ledger is a second, read-only integration predecessor: five BF7B
potential promotions already carry selector-538 verification, so only the
remaining eighty-seven rows may be promoted when this layer is integrated.
Dialogue bodies and exact overrides remain private below ``tmp``.  Shared
integration code, progress, and Steam remain read only.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
BASE_CLOSURE_PATH = WORKSTREAM / "build_pk_selector538_chunk0_closure_v1.py"
REVIEW_BUILDER_PATH = WORKSTREAM / "build_pk_selector568_chunk0_review_v1.py"
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
ACTUAL_PREDECESSOR_PATH = (
    DIALOGUE_TMP / "runtime_vm_integrated.private.v1.jsonl"
)
PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family568_chunk0_analysis.private.v1.json"
)
REVIEW_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector568_chunk0_review_proposal.v1.json"
)
SELECTOR538_DECISION_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector538_chunk0_closure_decisions.private.v1.jsonl"
)
SELECTOR538_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector538_chunk0_closure_evidence.private.v1.jsonl"
)
SELECTOR538_PROMOTION_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk0_closure_promotion.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector568_chunk0_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector568_chunk0_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector568_chunk0_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector568_chunk0_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = "nobu16.kr.pk-selector568-chunk0-closure-coverage.v1"
PROMOTION_SCHEMA = "nobu16.kr.pk-selector568-chunk0-closure-promotion.v1"
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector568-chunk0-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = "nobu16.kr.pk-selector568-chunk0-exact-override.v1"
METHOD = "reversed_vm_pk_selector568_chunk0_independent_closure"
UPDATE_ACTION_FIELD = "selector568_chunk0_update_action"
BF7B_ACTION_FIELD = "selector568_chunk0_bf7b_action"
EXACT_OVERRIDE_FIELD = "selector568_chunk0_exact_override_evidence"
SELECTOR = 568
TERMINALS = tuple(range(1951, 1958))

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_ACTUAL_PREDECESSOR_SHA256 = (
    "6945B4CBAD745A808CE306599FCC5BB7C17068414AD7B085E59B02BC20818165"
)
EXPECTED_HANDOFF_SHA256 = (
    "07F069C6F6792DE68D84FA7E9FBCF8E9AD809A5509B825E18663BA729191CAF4"
)
EXPECTED_REVIEW_PUBLIC_SHA256 = (
    "214672A7D195B2162A3E2CF687B5071D1A1485C232305FB7AC16B5D959BDD97C"
)
EXPECTED_SELECTOR538_DECISION_SHA256 = (
    "6B002FF3565B1BAAED58064BA2351232B443A3B43350BD7BE9ADAFD1ED117BBF"
)
EXPECTED_SELECTOR538_EVIDENCE_SHA256 = (
    "AA38C99D83D42733BA8E271D26F9EB711FE0F1B626B9F9C266E8045FFBBF5F54"
)
EXPECTED_SELECTOR538_PROMOTION_SHA256 = (
    "E08B23BAEB01C6EA3DA61AA9C2C85B6E5CBC981A646ED3DD494F90A7B230771D"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_213
EXPECTED_PENDING_AFTER = 8_121
EXPECTED_ACTUAL_PREDECESSOR_PENDING = 8_113
EXPECTED_ACTUAL_PENDING_AFTER = 8_026
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "85712C168C725C99824748B109A1AEC5BD79445FB2461460FCE31366EEDD6A51"
)
EXPECTED_ACTUAL_CANDIDATE_SHA256 = (
    "69E330801D41F0A702D97781489593C48FA567135E9AA900D74209BD3BEE47F2"
)
EXPECTED_BF7B_DECISION_PROJECTION_CANDIDATE_SHA256 = (
    "EA7F9C35B1ECE2A50CFFA2AE2289CE3F7D7EF089CF11606120AFA769C84EC077"
)
EXPECTED_REWRITE_ROWS = 59
EXPECTED_KEEP_ROWS = 3
EXPECTED_REJECTED_SITES = 15
EXPECTED_ACCEPTED_SITES = 62
EXPECTED_ACCEPTED_ASSEMBLIES = 434
EXPECTED_PROMOTION_ROWS = 92
EXPECTED_PROMOTION_ROOTS = 43
EXPECTED_PLANNED_LIVE_PROMOTION_ROWS = 87
EXPECTED_PLANNED_LIVE_PROMOTION_ROOTS = 42
EXPECTED_ALREADY_PROMOTED_ROWS = 5
EXPECTED_REJECTED_PENDING_ROWS = 39
EXPECTED_REJECTED_ROOTS = 14
EXPECTED_REJECTED_PENDING_ROOTS = 11
EXPECTED_RENEWAL_ROWS = 261
EXPECTED_RENEWAL_ROOTS = 142
EXPECTED_DECISION_ROWS = 353
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 281
EXPECTED_SOURCE_AFFECTED_ROOTS = 291
EXPECTED_SELECTOR538_SUPERSESSION_ROWS = 24
EXPECTED_SELECTOR538_RENEWAL_SUPERSESSION_ROWS = 19
EXPECTED_ACTION_COUNTS = {
    "evidence_supersession": 4,
    "runtime_promotion": 73,
    "translation_override_and_evidence_supersession": 1,
    "translation_override_and_runtime_promotion": 14,
    "translation_override_and_verification_renewal": 44,
    "verification_renewal": 217,
}
EXPECTED_BF7B_ACTION_COUNTS = {
    "runtime_promotion": 77,
    "translation_override_and_runtime_promotion": 15,
    "translation_override_and_verification_renewal": 44,
    "verification_renewal": 217,
}

EXPECTED_REWRITE_COORDINATE_SHA256 = (
    "F9692E0730E531A6E819E39ABE0921E5B93D9BF6CABAA12B054E63BE105408E4"
)
EXPECTED_REWRITE_MAP_SHA256 = (
    "3E2DC31F926203148EE1BD0FF05CC480E233F90FAADA113170CEAC0EDBC1064B"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "0B6922C76EF0C6CC10DC8D18D0D808EE2B955F5315621DC13B44FE53152DC12C"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "FD900D5E544C4CD2E70A1AADBC72764C72848FAA41FCFDEDF79E3E6B8B5394D2"
)
EXPECTED_ACCEPTED_ROOT_SHA256 = (
    "84C3A31CB2453469A516A88FEB40EE813FB15D8E4818E3364E64A7C620520342"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "793AFC5890C74D96D7087E758E55AFBB26681DE589A031638A0347B385B99A78"
)
EXPECTED_PROMOTION_ROOT_SHA256 = (
    "22F983E08769A79A29C8520BD246B3D946ADB302B1BBCEBC02AC48FF003F3390"
)
EXPECTED_PLANNED_LIVE_PROMOTION_COORDINATE_SHA256 = (
    "9140999AA8196CAB583FF031DEEFCAE4912C51EAAD703FCDF90FAD7220283F78"
)
EXPECTED_PLANNED_LIVE_PROMOTION_ROOT_SHA256 = (
    "77F3364384D05DF68DB0B521DDC6B354F7B7F73C862BC8326CFA51EB10A2B10B"
)
EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256 = (
    "01A2FD18B93822F59ABFA6EE567C48110E3DB344AE896D3116EB66177AC76A04"
)
EXPECTED_REJECTED_COORDINATE_SHA256 = (
    "1C25964442B1E724A38E75C77191FD39E8283CC74816D4F6AFF0B8CB5DA6A980"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "AFAF54C02B2785B7BE0092393DAFAC15BC6E64881866EDB48ADF27B905939759"
)
EXPECTED_REJECTED_PENDING_ROOT_SHA256 = (
    "F58453E5285D50F2BA0EC5EDEB312C976151F2A07370FB387FAD78993195BBDB"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "B9020FDF90392ACD95869EA9553FB77286A6B7E373403443DB5444D10116DE6C"
)
EXPECTED_RENEWAL_ROOT_SHA256 = (
    "B4A3EAA1B5AB6526921FCC73FCAA6F87BB66758CD2EF8639F141A05522DF9606"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "CB94D51D3522071B9C9BEE37028B584C9EF34EC99AB8E96E01FCACD3A6B8ABAF"
)
EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256 = (
    "493955409CFECBA5A3B3D93193BDAF0ECB3544A26664919006AC3424EE58E0FA"
)
EXPECTED_SOURCE_AFFECTED_ROOT_SHA256 = (
    "B6A76B74CAEC9C25746B5EA863FAB92C8192DF2A7080FEFA5AD475F22374DFF0"
)
EXPECTED_SELECTOR538_SUPERSESSION_COORDINATE_SHA256 = (
    "E71F5353C17B8355C3439E7C11CCE666A738C4DC60FA1682812D53666F799ACD"
)
EXPECTED_SELECTOR538_RENEWAL_SUPERSESSION_COORDINATE_SHA256 = (
    "1A85CF5FE5F31E5F38BAFF706ADA25BA75F4ABE50112D32752C46752030EA88A"
)
EXPECTED_ACCEPTED_ASSEMBLY_SHA256: str | None = (
    "BEA3796B9AEE5D26D1BB0B0DC22131CAE57AD3547D278FBC0117B0DAFFFAFE4D"
)

# Frozen after independently reproducible outputs are generated.
EXPECTED_AUDIT_FILE_SHA256: str | None = (
    "3302BB2766462FC1A304CD23C1188A1C40D01C7DD3A2396EAB92492A81D73365"
)
EXPECTED_PROMOTION_FILE_SHA256: str | None = (
    "E0D783536EEE92A600CF73E59C34B3E426A3C3864F5F828C8277F600A85E1835"
)
EXPECTED_DECISION_FILE_SHA256: str | None = (
    "0196222A0460783741CA8F75B88208F30556B80B5B2C76DFDCBC39D099F3801E"
)
EXPECTED_EVIDENCE_FILE_SHA256: str | None = (
    "C9499F989A0D9AC1DCD1BFF705771AD6D87F02CE038E92B0F7EF78FD28298856"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_CLOSURE_PATH, "pk_selector568_chunk0_closure_base_v1")
REVIEW = load_module(REVIEW_BUILDER_PATH, "pk_selector568_chunk0_closure_review_v1")

_BASE_BUILD_ANALYSIS = BASE.build_analysis
_BASE_BUILD_AUDIT = BASE.build_audit
_BASE_BUILD_PROMOTION = BASE.build_promotion
_BASE_VALIDATE_OUTPUTS = BASE.validate_outputs


def patch_base_contract() -> None:
    replacements = {
        "REVIEW": REVIEW,
        "CALLER": REVIEW.CALLER,
        "HONORIFIC": REVIEW.CALLER.HONORIFIC,
        "CROSS": REVIEW.CALLER.CROSS,
        "BASE_AUDIT": REVIEW.BASE_AUDIT,
        "ENGINE": REVIEW.ENGINE,
        "LIVE_STEAM_BASE": Path(REVIEW.CALLER.LIVE_STEAM_BASE),
        "LIVE_STEAM_PK": Path(REVIEW.CALLER.LIVE_STEAM_PK),
        "PREDECESSOR_PRIVATE_PATH": PREDECESSOR_PRIVATE_PATH,
        "PREDECESSOR_PUBLIC_PATH": PREDECESSOR_PUBLIC_PATH,
        "PRIVATE_HANDOFF_PATH": PRIVATE_HANDOFF_PATH,
        "REVIEW_PUBLIC_PATH": REVIEW_PUBLIC_PATH,
        "DEFAULT_AUDIT_OUTPUT": DEFAULT_AUDIT_OUTPUT,
        "DEFAULT_PROMOTION_OUTPUT": DEFAULT_PROMOTION_OUTPUT,
        "DEFAULT_DECISION_OUTPUT": DEFAULT_DECISION_OUTPUT,
        "DEFAULT_EVIDENCE_OUTPUT": DEFAULT_EVIDENCE_OUTPUT,
        "AUDIT_SCHEMA": AUDIT_SCHEMA,
        "PROMOTION_SCHEMA": PROMOTION_SCHEMA,
        "EVIDENCE_SCHEMA": EVIDENCE_SCHEMA,
        "OVERRIDE_SCHEMA": OVERRIDE_SCHEMA,
        "METHOD": METHOD,
        "UPDATE_ACTION_FIELD": UPDATE_ACTION_FIELD,
        "SELECTOR": SELECTOR,
        "TERMINALS": TERMINALS,
    }
    for name in (
        "EXPECTED_PREDECESSOR_PRIVATE_SHA256",
        "EXPECTED_PREDECESSOR_PUBLIC_SHA256",
        "EXPECTED_HANDOFF_SHA256",
        "EXPECTED_REVIEW_PUBLIC_SHA256",
        "EXPECTED_PREDECESSOR_ROWS",
        "EXPECTED_PREDECESSOR_PENDING",
        "EXPECTED_PENDING_AFTER",
        "EXPECTED_BASELINE_CANDIDATE_SHA256",
        "EXPECTED_CANDIDATE_SHA256",
        "EXPECTED_REWRITE_ROWS",
        "EXPECTED_KEEP_ROWS",
        "EXPECTED_REJECTED_SITES",
        "EXPECTED_ACCEPTED_SITES",
        "EXPECTED_ACCEPTED_ASSEMBLIES",
        "EXPECTED_PROMOTION_ROWS",
        "EXPECTED_PROMOTION_ROOTS",
        "EXPECTED_REJECTED_PENDING_ROWS",
        "EXPECTED_REJECTED_ROOTS",
        "EXPECTED_REJECTED_PENDING_ROOTS",
        "EXPECTED_RENEWAL_ROWS",
        "EXPECTED_RENEWAL_ROOTS",
        "EXPECTED_DECISION_ROWS",
        "EXPECTED_CANDIDATE_AFFECTED_ROOTS",
        "EXPECTED_SOURCE_AFFECTED_ROOTS",
        "EXPECTED_ACTION_COUNTS",
        "EXPECTED_REWRITE_COORDINATE_SHA256",
        "EXPECTED_REWRITE_MAP_SHA256",
        "EXPECTED_ACCEPTED_SITE_SHA256",
        "EXPECTED_REJECTED_SITE_SHA256",
        "EXPECTED_ACCEPTED_ROOT_SHA256",
        "EXPECTED_PROMOTION_COORDINATE_SHA256",
        "EXPECTED_PROMOTION_ROOT_SHA256",
        "EXPECTED_REJECTED_COORDINATE_SHA256",
        "EXPECTED_REJECTED_ROOT_SHA256",
        "EXPECTED_REJECTED_PENDING_ROOT_SHA256",
        "EXPECTED_RENEWAL_COORDINATE_SHA256",
        "EXPECTED_RENEWAL_ROOT_SHA256",
        "EXPECTED_DECISION_COORDINATE_SHA256",
        "EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256",
        "EXPECTED_SOURCE_AFFECTED_ROOT_SHA256",
        "EXPECTED_ACCEPTED_ASSEMBLY_SHA256",
        "EXPECTED_AUDIT_FILE_SHA256",
        "EXPECTED_PROMOTION_FILE_SHA256",
        "EXPECTED_DECISION_FILE_SHA256",
        "EXPECTED_EVIDENCE_FILE_SHA256",
    ):
        replacements[name] = globals()[name]
    for name, value in replacements.items():
        setattr(BASE, name, value)


def load_jsonl_rows(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    with path.open("r", encoding="utf-8", errors="strict", newline="") as stream:
        for line_number, line in enumerate(stream, start=1):
            BASE.require(line.endswith("\n"), f"line {line_number} lacks LF: {path}")
            row = json.loads(line)
            key = (str(row["resource"]), str(row["coordinate"]))
            BASE.require(key not in rows, f"duplicate row {key}: {path}")
            rows[key] = row
    return rows


def load_actual_predecessor() -> dict[tuple[str, str], dict[str, Any]]:
    BASE.require(
        BASE.sha256_file(ACTUAL_PREDECESSOR_PATH)
        == EXPECTED_ACTUAL_PREDECESSOR_SHA256,
        "current a19 integrated ledger drifted",
    )
    rows = load_jsonl_rows(ACTUAL_PREDECESSOR_PATH)
    BASE.require(
        len(rows) == EXPECTED_PREDECESSOR_ROWS
        and sum(row.get("runtime_review") == "pending" for row in rows.values())
        == EXPECTED_ACTUAL_PREDECESSOR_PENDING,
        "current a19 ledger row/status universe drifted",
    )
    return rows


def load_selector538_evidence() -> dict[str, dict[str, Any]]:
    BASE.require(
        BASE.sha256_file(SELECTOR538_DECISION_PATH)
        == EXPECTED_SELECTOR538_DECISION_SHA256,
        "selector-538 chunk-0 decision evidence drifted",
    )
    BASE.require(
        BASE.sha256_file(SELECTOR538_EVIDENCE_PATH)
        == EXPECTED_SELECTOR538_EVIDENCE_SHA256,
        "selector-538 chunk-0 evidence drifted",
    )
    BASE.require(
        BASE.sha256_file(SELECTOR538_PROMOTION_PATH)
        == EXPECTED_SELECTOR538_PROMOTION_SHA256,
        "selector-538 chunk-0 promotion report drifted",
    )
    rows = load_jsonl_rows(SELECTOR538_EVIDENCE_PATH)
    return {
        coordinate: row
        for (resource, coordinate), row in rows.items()
        if resource == "pk_msggame"
    }


def load_review() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    BASE.require(
        BASE.sha256_file(PRIVATE_HANDOFF_PATH) == EXPECTED_HANDOFF_SHA256,
        "private selector-568 chunk-0 handoff drifted",
    )
    public = BASE.load_json_exact(
        REVIEW_PUBLIC_PATH,
        EXPECTED_REVIEW_PUBLIC_SHA256,
    )
    assignment, chunk = REVIEW.load_assignment()
    world = REVIEW.load_world()
    handoff = REVIEW.load_json_exact(PRIVATE_HANDOFF_PATH)
    validated = REVIEW.validate_private_handoff(
        handoff,
        assignment=assignment,
        chunk=chunk,
        world=world,
    )
    result = public.get("result", {})
    proof = public.get("proof", {})
    BASE.require(
        public.get("schema") == REVIEW.PUBLIC_SCHEMA
        and public.get("status") == "PASS"
        and result.get("accepted_site_count") == EXPECTED_ACCEPTED_SITES
        and result.get("rewrite_coordinate_count") == EXPECTED_REWRITE_ROWS
        and result.get("keep_coordinate_count") == EXPECTED_KEEP_ROWS
        and result.get("reject_coordinate_count") == EXPECTED_REJECTED_SITES
        and result.get("proposal_candidate_sha256")
        == EXPECTED_CANDIDATE_SHA256
        and result.get("potential_promotion_coordinate_count")
        == EXPECTED_PROMOTION_ROWS
        and result.get("accepted_current_a19_live_pending_count")
        == EXPECTED_PLANNED_LIVE_PROMOTION_ROWS
        and result.get("blocked_pending_coordinate_count")
        == EXPECTED_REJECTED_PENDING_ROWS
        and proof.get("accepted_assembly_branches")
        == EXPECTED_ACCEPTED_ASSEMBLIES
        and proof.get("assembly_branches_recorded") == 539
        and proof.get("all_accepted_current_relative_raw_g1n_nonexpanding")
        is True
        and proof.get("all_accepted_register_branches_proven") is True
        and public.get("steam_write_performed") is False,
        "source-free selector-568 chunk-0 proposal drifted",
    )
    return handoff, public, world, validated


def build_analysis(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    world: Mapping[str, Any],
    handoff: Mapping[str, Any],
    validated: Mapping[str, Any],
) -> dict[str, Any]:
    analysis = _BASE_BUILD_ANALYSIS(
        predecessor_rows=predecessor_rows,
        world=world,
        handoff=handoff,
        validated=validated,
    )
    result = dict(analysis)
    assignment, _chunk = REVIEW.load_assignment()
    actual_rows = load_actual_predecessor()
    selector538_evidence = load_selector538_evidence()
    promotion_coordinates = set(result["promotion_coordinates"])
    renewal_coordinates = set(result["renewal_coordinates"])
    already_promoted = (
        set(assignment["graph_evidence"]["already_promoted_coordinates"])
        & promotion_coordinates
    )
    planned_live = promotion_coordinates - already_promoted
    selector538_supersession = {
        coordinate
        for coordinate in result["update_coordinates"]
        if coordinate in selector538_evidence
        and "selector538_chunk0_update_action"
        in actual_rows[("pk_msggame", coordinate)]
    }
    selector538_renewal_supersession = (
        selector538_supersession & renewal_coordinates
    )
    BASE.require(
        len(already_promoted) == EXPECTED_ALREADY_PROMOTED_ROWS
        and BASE.coordinate_digest(already_promoted)
        == EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256
        and len(planned_live) == EXPECTED_PLANNED_LIVE_PROMOTION_ROWS
        and BASE.coordinate_digest(planned_live)
        == EXPECTED_PLANNED_LIVE_PROMOTION_COORDINATE_SHA256
        and len({BASE.parse_coordinate(value)[:2] for value in planned_live})
        == EXPECTED_PLANNED_LIVE_PROMOTION_ROOTS
        and BASE.root_digest(
            {BASE.parse_coordinate(value)[:2] for value in planned_live}
        )
        == EXPECTED_PLANNED_LIVE_PROMOTION_ROOT_SHA256,
        "BF7B potential/current-live promotion partition drifted",
    )
    BASE.require(
        all(
            actual_rows[("pk_msggame", coordinate)].get("runtime_review")
            == "pending"
            for coordinate in planned_live
        )
        and all(
            actual_rows[("pk_msggame", coordinate)].get("runtime_review")
            == "verified"
            for coordinate in already_promoted | renewal_coordinates
        ),
        "current a19 runtime-state partition drifted",
    )
    BASE.require(
        len(selector538_supersession)
        == EXPECTED_SELECTOR538_SUPERSESSION_ROWS
        and BASE.coordinate_digest(selector538_supersession)
        == EXPECTED_SELECTOR538_SUPERSESSION_COORDINATE_SHA256
        and len(selector538_renewal_supersession)
        == EXPECTED_SELECTOR538_RENEWAL_SUPERSESSION_ROWS
        and BASE.coordinate_digest(selector538_renewal_supersession)
        == EXPECTED_SELECTOR538_RENEWAL_SUPERSESSION_COORDINATE_SHA256
        and already_promoted <= selector538_supersession,
        "selector-538 evidence supersession partition drifted",
    )
    for coordinate in selector538_supersession:
        current = actual_rows[("pk_msggame", coordinate)]
        evidence = selector538_evidence[coordinate]
        BASE.require(
            current.get("runtime_vm_verification") == evidence
            and current.get("selector538_chunk0_update_action")
            == evidence.get("action"),
            f"selector-538 integrated evidence drifted: {coordinate}",
        )

    actual_replacements = {
        BASE.parse_coordinate(coordinate): str(row["translation"])
        for (resource, coordinate), row in actual_rows.items()
        if resource == "pk_msggame"
        and isinstance(row.get("translation"), str)
    }
    actual_replacements.update(
        {
            BASE.parse_coordinate(coordinate): str(text)
            for coordinate, text in result["rewrite_map"].items()
        }
    )
    actual_candidate_blob = BASE.BASE_AUDIT.rebuild_packed_with_literals(
        BASE.BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        actual_replacements,
    )
    BASE.require(
        BASE.sha256_bytes(actual_candidate_blob)
        == EXPECTED_ACTUAL_CANDIDATE_SHA256,
        "a19 plus selector-568 chunk-0 candidate drifted",
    )
    result.update(
        {
            "actual_candidate_blob": actual_candidate_blob,
            "actual_predecessor_rows": actual_rows,
            "already_promoted_coordinates": already_promoted,
            "planned_live_promotion_coordinates": planned_live,
            "selector538_evidence": selector538_evidence,
            "selector538_supersession_coordinates":
                selector538_supersession,
            "selector538_renewal_supersession_coordinates":
                selector538_renewal_supersession,
        }
    )
    return result


def build_audit(
    *,
    analysis: Mapping[str, Any],
    predecessor_report: Mapping[str, Any],
    review_public: Mapping[str, Any],
) -> dict[str, Any]:
    report = _BASE_BUILD_AUDIT(
        analysis=analysis,
        predecessor_report=predecessor_report,
        review_public=review_public,
    )
    result = copy.deepcopy(report)
    result["guards"].update(
        {
            "actual_candidate_sha256": EXPECTED_ACTUAL_CANDIDATE_SHA256,
            "actual_predecessor_sha256":
                EXPECTED_ACTUAL_PREDECESSOR_SHA256,
            "bf7b_decision_projection_candidate_sha256":
                EXPECTED_BF7B_DECISION_PROJECTION_CANDIDATE_SHA256,
            "already_promoted_coordinate_sha256":
                EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256,
            "planned_live_promotion_coordinate_sha256":
                EXPECTED_PLANNED_LIVE_PROMOTION_COORDINATE_SHA256,
            "planned_live_promotion_root_sha256":
                EXPECTED_PLANNED_LIVE_PROMOTION_ROOT_SHA256,
            "selector538_evidence_sha256":
                EXPECTED_SELECTOR538_EVIDENCE_SHA256,
            "selector538_supersession_coordinate_sha256":
                EXPECTED_SELECTOR538_SUPERSESSION_COORDINATE_SHA256,
        }
    )
    result["integration_policy"] = {
        "actual_integration_predecessor": "a19_integrated_ledger",
        "already_verified_rows_use_evidence_supersession": True,
        "bf7b_graph_baseline_preserved": True,
        "promotion_count_basis": {
            "actual_planned_live": EXPECTED_PLANNED_LIVE_PROMOTION_ROWS,
            "bf7b_potential": EXPECTED_PROMOTION_ROWS,
        },
    }
    result["proof"].update(
        {
            "actual_live_pending_rows_promoted_only": True,
            "already_promoted_selector538_rows_not_repromoted": True,
            "selector538_evidence_supersession_rows":
                EXPECTED_SELECTOR538_SUPERSESSION_ROWS,
            "selector538_renewal_evidence_supersession_rows":
                EXPECTED_SELECTOR538_RENEWAL_SUPERSESSION_ROWS,
        }
    )
    result["scope"].update(
        {
            "actual_post_layer_pending_rows": EXPECTED_ACTUAL_PENDING_AFTER,
            "actual_predecessor_pending_rows":
                EXPECTED_ACTUAL_PREDECESSOR_PENDING,
            "already_promoted_rows": EXPECTED_ALREADY_PROMOTED_ROWS,
            "bf7b_potential_runtime_promotion_rows":
                EXPECTED_PROMOTION_ROWS,
            "planned_live_runtime_promotion_roots":
                EXPECTED_PLANNED_LIVE_PROMOTION_ROOTS,
            "planned_live_runtime_promotion_rows":
                EXPECTED_PLANNED_LIVE_PROMOTION_ROWS,
            "runtime_promotion_rows_basis": "bf7b_potential",
            "selector538_evidence_supersession_rows":
                EXPECTED_SELECTOR538_SUPERSESSION_ROWS,
        }
    )
    return BASE.HONORIFIC.seal_report(result)


def bf7b_action(*, is_override: bool, is_promotion: bool) -> str:
    if is_promotion:
        return (
            "translation_override_and_runtime_promotion"
            if is_override
            else "runtime_promotion"
        )
    return (
        "translation_override_and_verification_renewal"
        if is_override
        else "verification_renewal"
    )


def build_updated_rows(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    analysis: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rewrite_map = analysis["rewrite_map"]
    promotion_coordinates = analysis["promotion_coordinates"]
    planned_live = analysis["planned_live_promotion_coordinates"]
    already_promoted = analysis["already_promoted_coordinates"]
    renewal_coordinates = analysis["renewal_coordinates"]
    actual_rows = analysis["actual_predecessor_rows"]
    selector538_evidence = analysis["selector538_evidence"]
    selector538_supersession = (
        analysis["selector538_supersession_coordinates"]
    )
    updated_rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    terminal_digest = BASE.coordinate_digest(
        f"0:{terminal}:0" for terminal in TERMINALS
    )
    for coordinate in sorted(
        analysis["update_coordinates"], key=BASE.parse_coordinate
    ):
        bf7b_predecessor = predecessor_rows[("pk_msggame", coordinate)]
        actual_predecessor = actual_rows[("pk_msggame", coordinate)]
        updated = copy.deepcopy(dict(actual_predecessor))
        is_override = coordinate in rewrite_map
        is_promotion = coordinate in promotion_coordinates
        is_live_promotion = coordinate in planned_live
        is_already_promoted = coordinate in already_promoted
        if is_override:
            updated["translation"] = rewrite_map[coordinate]
            REVIEW.CALLER.PREDECESSOR.repair_hard_risks(updated)
            updated[EXACT_OVERRIDE_FIELD] = {
                "automatic_space_inserted": False,
                "control_bytes_preserved": True,
                "private_handoff_hash_bound": True,
                "schema": OVERRIDE_SCHEMA,
                "translation_utf16le_sha256": REVIEW.ENGINE.sha256_text(
                    str(updated["translation"])
                ),
            }
        theoretical_action = bf7b_action(
            is_override=is_override,
            is_promotion=is_promotion,
        )
        if is_live_promotion:
            BASE.require(
                actual_predecessor.get("runtime_review") == "pending",
                f"actual promotion predecessor drifted: {coordinate}",
            )
            updated["runtime_review"] = "verified"
            updated["scope_classification"] = "retranslated"
            updated["layout_review"] = "runtime_verified"
            action = theoretical_action
        elif is_already_promoted:
            BASE.require(
                actual_predecessor.get("runtime_review") == "verified",
                f"already-promoted predecessor drifted: {coordinate}",
            )
            action = (
                "translation_override_and_evidence_supersession"
                if is_override
                else "evidence_supersession"
            )
        else:
            BASE.require(
                coordinate in renewal_coordinates
                and actual_predecessor.get("runtime_review") == "verified",
                f"renewal predecessor drifted: {coordinate}",
            )
            action = theoretical_action

        evidence: dict[str, Any] = {
            "action": action,
            "actual_live_runtime_promotion": is_live_promotion,
            "already_promoted_under_selector538": is_already_promoted,
            "bf7b_action": theoretical_action,
            "bf7b_potential_runtime_promotion": is_promotion,
            "closure_binding": {
                "accepted_assembly_sha256": audit["guards"][
                    "accepted_assembly_sha256"
                ],
                "actual_candidate_sha256":
                    EXPECTED_ACTUAL_CANDIDATE_SHA256,
                "audit_report_file_sha256": audit_file_sha256,
                "audit_report_payload_sha256": audit["guards"][
                    "report_payload_sha256"
                ],
                "bf7b_candidate_sha256": EXPECTED_CANDIDATE_SHA256,
                "decision_coordinate_sha256":
                    EXPECTED_DECISION_COORDINATE_SHA256,
                "handoff_sha256": EXPECTED_HANDOFF_SHA256,
                "review_public_sha256": EXPECTED_REVIEW_PUBLIC_SHA256,
                "selector": SELECTOR,
                "terminal_coordinate_sha256": terminal_digest,
            },
            "coordinate": coordinate,
            "method": METHOD,
            "per_row_game_playback_required": False,
            "predecessor_binding": {
                "actual_checkpoint_sha256":
                    EXPECTED_ACTUAL_PREDECESSOR_SHA256,
                "actual_row_sha256": BASE.canonical_sha256(
                    actual_predecessor
                ),
                "bf7b_checkpoint_sha256":
                    EXPECTED_PREDECESSOR_PRIVATE_SHA256,
                "bf7b_row_sha256": BASE.canonical_sha256(
                    bf7b_predecessor
                ),
            },
            "preexisting_verified_evidence_renewed":
                not is_live_promotion,
            "resource": "pk_msggame",
            "schema": EVIDENCE_SCHEMA,
            "status": "verified",
            "translation_utf16le_sha256": REVIEW.ENGINE.sha256_text(
                str(updated["translation"])
            ),
        }
        if coordinate in selector538_supersession:
            prior = selector538_evidence[coordinate]
            evidence["superseded_evidence_binding"] = {
                "action": prior["action"],
                "evidence_file_sha256": EXPECTED_SELECTOR538_EVIDENCE_SHA256,
                "evidence_row_sha256": BASE.canonical_sha256(prior),
                "method": prior["method"],
                "promotion_report_sha256":
                    EXPECTED_SELECTOR538_PROMOTION_SHA256,
                "schema": prior["schema"],
                "selector": 538,
            }
        updated[BF7B_ACTION_FIELD] = theoretical_action
        updated[UPDATE_ACTION_FIELD] = action
        updated["runtime_vm_verification"] = evidence
        updated_rows.append(updated)
        evidence_rows.append(evidence)
    updated_rows.sort(key=BASE.row_sort_key)
    evidence_rows.sort(
        key=lambda row: BASE.parse_coordinate(str(row["coordinate"]))
    )
    actions = Counter(str(row["action"]) for row in evidence_rows)
    theoretical_actions = Counter(
        str(row["bf7b_action"]) for row in evidence_rows
    )
    BASE.require(
        dict(actions) == EXPECTED_ACTION_COUNTS
        and dict(theoretical_actions) == EXPECTED_BF7B_ACTION_COUNTS,
        "actual/BF7B closure action counts drifted",
    )
    return updated_rows, evidence_rows


def build_promotion(
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    decision_content: str,
    evidence_content: str,
    evidence_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    report = _BASE_BUILD_PROMOTION(
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        decision_content=decision_content,
        evidence_content=evidence_content,
        evidence_rows=evidence_rows,
    )
    result = copy.deepcopy(report)
    result["evidence"].update(
        {
            "actual_predecessor_sha256":
                EXPECTED_ACTUAL_PREDECESSOR_SHA256,
            "already_promoted_coordinate_sha256":
                EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256,
            "planned_live_promotion_coordinate_sha256":
                EXPECTED_PLANNED_LIVE_PROMOTION_COORDINATE_SHA256,
            "selector538_decision_sha256":
                EXPECTED_SELECTOR538_DECISION_SHA256,
            "selector538_evidence_sha256":
                EXPECTED_SELECTOR538_EVIDENCE_SHA256,
            "selector538_promotion_sha256":
                EXPECTED_SELECTOR538_PROMOTION_SHA256,
        }
    )
    result["result"].update(
        {
            "actual_pending_rows_after": EXPECTED_ACTUAL_PENDING_AFTER,
            "actual_pending_rows_before":
                EXPECTED_ACTUAL_PREDECESSOR_PENDING,
            "already_promoted_evidence_supersession_rows":
                EXPECTED_ALREADY_PROMOTED_ROWS,
            "bf7b_pending_rows_after": EXPECTED_PENDING_AFTER,
            "bf7b_pending_rows_before": EXPECTED_PREDECESSOR_PENDING,
            "bf7b_potential_runtime_promotion_rows":
                EXPECTED_PROMOTION_ROWS,
            "planned_live_runtime_promotion_roots":
                EXPECTED_PLANNED_LIVE_PROMOTION_ROOTS,
            "planned_live_runtime_promotion_rows":
                EXPECTED_PLANNED_LIVE_PROMOTION_ROWS,
            "runtime_promotion_rows_basis": "bf7b_potential",
            "selector538_evidence_supersession_rows":
                EXPECTED_SELECTOR538_SUPERSESSION_ROWS,
            "selector538_renewal_evidence_supersession_rows":
                EXPECTED_SELECTOR538_RENEWAL_SUPERSESSION_ROWS,
        }
    )
    return BASE.HONORIFIC.seal_report(result)


def validate_outputs(
    *,
    decision_content: str,
    evidence_content: str,
    audit_content: str,
    promotion_content: str,
    audit: Mapping[str, Any],
    bundle: Mapping[str, Any],
    require_frozen_hashes: bool = True,
) -> None:
    # The private delta is intentionally integration-ready for a19.  Its five
    # supersession rows preserve selector-538 state, so projecting that delta
    # back onto BF7B differs from the pure BF7B review candidate at one
    # non-override coordinate.  All other base closure invariants still apply.
    expected_candidate = BASE.EXPECTED_CANDIDATE_SHA256
    BASE.EXPECTED_CANDIDATE_SHA256 = (
        EXPECTED_BF7B_DECISION_PROJECTION_CANDIDATE_SHA256
    )
    try:
        _BASE_VALIDATE_OUTPUTS(
            decision_content=decision_content,
            evidence_content=evidence_content,
            audit_content=audit_content,
            promotion_content=promotion_content,
            audit=audit,
            bundle=bundle,
            require_frozen_hashes=require_frozen_hashes,
        )
    finally:
        BASE.EXPECTED_CANDIDATE_SHA256 = expected_candidate
    analysis = bundle["analysis"]
    actual_merged = {
        key: copy.deepcopy(dict(row))
        for key, row in analysis["actual_predecessor_rows"].items()
    }
    actual_before = sum(
        row.get("runtime_review") == "pending"
        for row in actual_merged.values()
    )
    for row in bundle["updated_rows"]:
        actual_merged[("pk_msggame", str(row["coordinate"]))] = row
    actual_after = sum(
        row.get("runtime_review") == "pending"
        for row in actual_merged.values()
    )
    actual_promotions = {
        coordinate
        for coordinate in analysis["promotion_coordinates"]
        if analysis["actual_predecessor_rows"][
            ("pk_msggame", coordinate)
        ].get("runtime_review")
        == "pending"
        and actual_merged[("pk_msggame", coordinate)].get("runtime_review")
        == "verified"
    }
    actions = Counter(
        str(row[UPDATE_ACTION_FIELD]) for row in bundle["updated_rows"]
    )
    BASE.require(
        actual_before == EXPECTED_ACTUAL_PREDECESSOR_PENDING
        and actual_after == EXPECTED_ACTUAL_PENDING_AFTER
        and actual_promotions
        == analysis["planned_live_promotion_coordinates"]
        and dict(actions) == EXPECTED_ACTION_COUNTS,
        "actual a19 integration projection drifted",
    )
    updated_by_coordinate = {
        str(row["coordinate"]): row for row in bundle["updated_rows"]
    }
    for coordinate in analysis["already_promoted_coordinates"]:
        row = updated_by_coordinate[coordinate]
        BASE.require(
            row[UPDATE_ACTION_FIELD]
            in {
                "evidence_supersession",
                "translation_override_and_evidence_supersession",
            }
            and row["runtime_review"] == "verified"
            and "superseded_evidence_binding"
            in row["runtime_vm_verification"],
            f"already-promoted evidence was not superseded: {coordinate}",
        )
    for coordinate in analysis["selector538_supersession_coordinates"]:
        BASE.require(
            "superseded_evidence_binding"
            in updated_by_coordinate[coordinate]["runtime_vm_verification"],
            f"selector-538 evidence supersession missing: {coordinate}",
        )
    replacements = {
        BASE.parse_coordinate(coordinate): str(row["translation"])
        for (resource, coordinate), row in actual_merged.items()
        if resource == "pk_msggame"
        and isinstance(row.get("translation"), str)
    }
    actual_candidate = BASE.BASE_AUDIT.rebuild_packed_with_literals(
        BASE.BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        replacements,
    )
    BASE.require(
        BASE.sha256_bytes(actual_candidate)
        == EXPECTED_ACTUAL_CANDIDATE_SHA256
        and bundle["promotion"]["result"][
            "planned_live_runtime_promotion_rows"
        ]
        == EXPECTED_PLANNED_LIVE_PROMOTION_ROWS
        and bundle["promotion"]["result"][
            "bf7b_potential_runtime_promotion_rows"
        ]
        == EXPECTED_PROMOTION_ROWS,
        "actual candidate/promotion report drifted",
    )


patch_base_contract()
BASE.load_review = load_review
BASE.build_analysis = build_analysis
BASE.build_audit = build_audit
BASE.build_updated_rows = build_updated_rows
BASE.build_promotion = build_promotion
BASE.validate_outputs = validate_outputs

ClosureError = BASE.ClosureError
require = BASE.require
sha256_bytes = BASE.sha256_bytes
sha256_file = BASE.sha256_file
canonical_bytes = BASE.canonical_bytes
canonical_json = BASE.canonical_json
canonical_jsonl = BASE.canonical_jsonl
canonical_sha256 = BASE.canonical_sha256
parse_coordinate = BASE.parse_coordinate
coordinate_digest = BASE.coordinate_digest
root_digest = BASE.root_digest
site_digest = BASE.site_digest
row_sort_key = BASE.row_sort_key
load_json_exact = BASE.load_json_exact
load_predecessor = BASE.load_predecessor
grouped_coordinates = BASE.grouped_coordinates
build_candidate = BASE.build_candidate
coordinates_for_roots = BASE.coordinates_for_roots
assert_source_free_report = BASE.assert_source_free_report
contains_body_key = BASE.contains_body_key
build_outputs = BASE.build_outputs
validate_output_paths = BASE.validate_output_paths
parse_args = BASE.parse_args
HONORIFIC = BASE.HONORIFIC
BASE_AUDIT = BASE.BASE_AUDIT
LIVE_STEAM_BASE = BASE.LIVE_STEAM_BASE
LIVE_STEAM_PK = BASE.LIVE_STEAM_PK


def main(argv: Sequence[str] | None = None) -> int:
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
