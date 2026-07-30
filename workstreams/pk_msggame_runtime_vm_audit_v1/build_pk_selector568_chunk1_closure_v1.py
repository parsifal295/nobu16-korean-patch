#!/usr/bin/env python3
"""Build the independent selector-568 chunk-1 runtime closure layer.

The layer is projected independently onto the immutable BF7B graph baseline
and the a19 integrated ledger.  Exact dialogue bodies and coordinates remain
private below ``tmp``; tracked reports are source-free.
"""

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
BASE_CLOSURE_PATH = WORKSTREAM / "build_pk_selector568_chunk0_closure_v1.py"
REVIEW_BUILDER_PATH = WORKSTREAM / "build_pk_selector568_chunk1_review_v1.py"

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
    DIALOGUE_TMP / "family568_chunk1_analysis.private.v1.json"
)
REVIEW_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector568_chunk1_review_proposal.v1.json"
)
SELECTOR538_DECISION_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector538_family_consolidated_closure_decisions.private.v1.jsonl"
)
SELECTOR538_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector538_family_consolidated_closure_evidence.private.v1.jsonl"
)
SELECTOR538_PROMOTION_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector538_family_consolidated_closure_promotion.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector568_chunk1_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector568_chunk1_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector568_chunk1_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector568_chunk1_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = "nobu16.kr.pk-selector568-chunk1-closure-coverage.v1"
PROMOTION_SCHEMA = "nobu16.kr.pk-selector568-chunk1-closure-promotion.v1"
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector568-chunk1-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = "nobu16.kr.pk-selector568-chunk1-exact-override.v1"
METHOD = "reversed_vm_pk_selector568_chunk1_independent_closure"
UPDATE_ACTION_FIELD = "selector568_chunk1_update_action"
BF7B_ACTION_FIELD = "selector568_chunk1_bf7b_action"
EXACT_OVERRIDE_FIELD = "selector568_chunk1_exact_override_evidence"
SELECTOR = 568
TERMINALS = tuple(range(1951, 1958))

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_ACTUAL_PREDECESSOR_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_HANDOFF_SHA256 = (
    "6EE3B78E55A6A1DC92736EF8392844091D9A3A584D92F610B3911B7C8E33026E"
)
EXPECTED_REVIEW_PUBLIC_SHA256 = (
    "E161B61CBE28D788CC5E0A457F0D5E2D6AFC8CBDE8283C4B96FAF47A7819B7B4"
)
EXPECTED_SELECTOR538_DECISION_SHA256 = (
    "5640EB7FB7E4EA9B32309B7FA280637DA9F26F96CA500BCD4FA9847D997456C0"
)
EXPECTED_SELECTOR538_EVIDENCE_SHA256 = (
    "910C0A59823C2B6B083F58257D6203053738EFEFC2E49E6271D553FF44CAB940"
)
EXPECTED_SELECTOR538_PROMOTION_SHA256 = (
    "6F7DDA159299CC9B1923C14A55B5341CFBDB9E9DB3CADA5D7CB77453EAEF3E85"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_213
EXPECTED_PENDING_AFTER = 8_113
EXPECTED_ACTUAL_PREDECESSOR_PENDING = 7_896
EXPECTED_ACTUAL_PENDING_AFTER = 7_799
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "5376D233785CCFAFF79E4869DF213342151F3BCB34AC8586D723ECDD2887F535"
)
EXPECTED_ACTUAL_CANDIDATE_SHA256 = (
    "3F8313ADF65D664114489CFBDEE9DAB0D507C0F2305C8F4DA26DC210BAFA9E6C"
)
EXPECTED_BF7B_DECISION_PROJECTION_CANDIDATE_SHA256 = (
    "EBADFFEF526B2338C0B9E7BF6B3F0DC898484C1051FA9BF916CA061EB4A1E354"
)
EXPECTED_REWRITE_ROWS = 46
EXPECTED_KEEP_ROWS = 1
EXPECTED_REJECTED_SITES = 20
EXPECTED_ACCEPTED_SITES = 47
EXPECTED_ACCEPTED_ASSEMBLIES = 329
EXPECTED_PROMOTION_ROWS = 100
EXPECTED_PROMOTION_ROOTS = 37
EXPECTED_PLANNED_LIVE_PROMOTION_ROWS = 97
EXPECTED_PLANNED_LIVE_PROMOTION_ROOTS = 36
EXPECTED_ALREADY_PROMOTED_ROWS = 3
EXPECTED_REJECTED_PENDING_ROWS = 31
EXPECTED_REJECTED_ROOTS = 16
EXPECTED_REJECTED_PENDING_ROOTS = 12
EXPECTED_RENEWAL_ROWS = 261
EXPECTED_RENEWAL_ROOTS = 142
EXPECTED_DECISION_ROWS = 361
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 281
EXPECTED_SOURCE_AFFECTED_ROOTS = 291
EXPECTED_SELECTOR538_SUPERSESSION_ROWS = 22
EXPECTED_SELECTOR538_RENEWAL_SUPERSESSION_ROWS = 19
EXPECTED_ACTION_COUNTS = {
    "evidence_supersession": 2,
    "runtime_promotion": 63,
    "translation_override_and_evidence_supersession": 1,
    "translation_override_and_runtime_promotion": 34,
    "translation_override_and_verification_renewal": 11,
    "verification_renewal": 250,
}
EXPECTED_BF7B_ACTION_COUNTS = {
    "runtime_promotion": 65,
    "translation_override_and_runtime_promotion": 35,
    "translation_override_and_verification_renewal": 11,
    "verification_renewal": 250,
}

EXPECTED_REWRITE_COORDINATE_SHA256 = (
    "F4F9BA5BD4F3D7859996C08298D074F4BC70115C36C0FCB9A625E52847D6AF38"
)
EXPECTED_REWRITE_MAP_SHA256 = (
    "289231D236BE175B894F2EC6B9512393B2E82986168FA7BB6D9F2026B3B545D4"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "38C563105477D24BDAF643FF7ED91511DE9AE60D655FC6FBBE61819E3C849A05"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "F8D5DB0866B29A6C838BA6755AB7A6FA40E933C1041568DA53AC73313E7EFF9D"
)
EXPECTED_ACCEPTED_ROOT_SHA256 = (
    "3DC257746F0C17F0D6C166E5A96B7BF8DCB34B20569479A69CB5F46C17285445"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "3206E515A635A0F2423C85B9F22F9449C34DE7AFB3573486234F325115797889"
)
EXPECTED_PROMOTION_ROOT_SHA256 = (
    "FE7C62C007C5593402AA812C5BCF8A5E55321D34206618E1D1EFF0548B4906E6"
)
EXPECTED_PLANNED_LIVE_PROMOTION_COORDINATE_SHA256 = (
    "F0F9C363045793B879CD1FEF16D1F0A08A0A3284775EFE2989656C5CB7729700"
)
EXPECTED_PLANNED_LIVE_PROMOTION_ROOT_SHA256 = (
    "1277C2F2FE30D11D214BF30C1B9D368506B967A86D1EA695B1CE39A88C4FCD1C"
)
EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256 = (
    "8109EF69396AF90569224F826694325564B55FE51377679B703AB02D3B1F8E6D"
)
EXPECTED_REJECTED_COORDINATE_SHA256 = (
    "F4733437116797C88A0D9A903AB07705461AC85B8409A7782EE1258B65ADBD0E"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "FB5AD29FB9F2B07C9AB7B54BEB0861F44B12EE1BFEC1FB4829608E0E30F1B00B"
)
EXPECTED_REJECTED_PENDING_ROOT_SHA256 = (
    "8043127D34372C140B2B28CC501B9E664C2DBFEEEFEF7F5B1F06C6394612FB85"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "B9020FDF90392ACD95869EA9553FB77286A6B7E373403443DB5444D10116DE6C"
)
EXPECTED_RENEWAL_ROOT_SHA256 = (
    "B4A3EAA1B5AB6526921FCC73FCAA6F87BB66758CD2EF8639F141A05522DF9606"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "A9435F74580D74A63DE4BA185FF2998597FB0629C421746A5DE91CC319AAFFEF"
)
EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256 = (
    "493955409CFECBA5A3B3D93193BDAF0ECB3544A26664919006AC3424EE58E0FA"
)
EXPECTED_SOURCE_AFFECTED_ROOT_SHA256 = (
    "B6A76B74CAEC9C25746B5EA863FAB92C8192DF2A7080FEFA5AD475F22374DFF0"
)
EXPECTED_SELECTOR538_SUPERSESSION_COORDINATE_SHA256 = (
    "20FBCE555C64C95CB010CB56E71F531630C9301B93C4B1AC2E142C311DBBC226"
)
EXPECTED_SELECTOR538_RENEWAL_SUPERSESSION_COORDINATE_SHA256 = (
    "1A85CF5FE5F31E5F38BAFF706ADA25BA75F4ABE50112D32752C46752030EA88A"
)
EXPECTED_ACCEPTED_ASSEMBLY_SHA256: str | None = (
    "4B1C3FCD96D154851D628D006FAF7062AF7DA312B26EB55166BAFE80F2547D4B"
)
EXPECTED_AUDIT_FILE_SHA256: str | None = (
    "DE5053AF4C11EFB2987BA139376789ED8B694E4B3323EF65E521966765A612A9"
)
EXPECTED_PROMOTION_FILE_SHA256: str | None = (
    "C5A5F2B8B9EAEE8F14E02C66B02EE1B44F9F776BE7153AF49F02A0D5166163E5"
)
EXPECTED_DECISION_FILE_SHA256: str | None = (
    "B35247D0B6BBC3F392394F9DF3051F8D66E82CDAF71BE1F3235F6260DD310501"
)
EXPECTED_EVIDENCE_FILE_SHA256: str | None = (
    "764BCC8A0E10D1B5FC560917260C2C3027BA79DC94F9D5CBB3994906FC7BD58D"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module(
    BASE_CLOSURE_PATH,
    "pk_selector568_chunk1_closure_engine_v1",
)
REVIEW = load_module(
    REVIEW_BUILDER_PATH,
    "pk_selector568_chunk1_closure_review_v1",
)
BASE = ENGINE.BASE
REVIEW.ENGINE.sha256_text = REVIEW.CALLER.ENGINE.sha256_text
_ORIGINAL_LOAD_ASSIGNMENT = REVIEW.load_assignment
_MISSING = object()
_ORIGINAL_CHUNK0_ACTIONS: dict[str, object] = {}


def patch_contract() -> None:
    values = {
        "REVIEW": REVIEW,
        "ACTUAL_PREDECESSOR_PATH": ACTUAL_PREDECESSOR_PATH,
        "PRIVATE_HANDOFF_PATH": PRIVATE_HANDOFF_PATH,
        "REVIEW_PUBLIC_PATH": REVIEW_PUBLIC_PATH,
        "SELECTOR538_DECISION_PATH": SELECTOR538_DECISION_PATH,
        "SELECTOR538_EVIDENCE_PATH": SELECTOR538_EVIDENCE_PATH,
        "SELECTOR538_PROMOTION_PATH": SELECTOR538_PROMOTION_PATH,
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
        "BF7B_ACTION_FIELD": BF7B_ACTION_FIELD,
        "EXACT_OVERRIDE_FIELD": EXACT_OVERRIDE_FIELD,
    }
    for name in tuple(globals()):
        if name.startswith("EXPECTED_"):
            values[name] = globals()[name]
    for module in (ENGINE, BASE):
        for name, value in values.items():
            setattr(module, name, value)


def load_assignment():
    assignment, chunk = _ORIGINAL_LOAD_ASSIGNMENT()
    graph = assignment["graph_evidence"]
    graph["already_promoted_coordinates"] = sorted(
        set(graph["already_promoted_coordinates"])
        | set(graph["selector538_planned_overlap_coordinates"])
    )
    return assignment, chunk


def load_selector538_family_evidence():
    BASE.require(
        BASE.sha256_file(SELECTOR538_DECISION_PATH)
        == EXPECTED_SELECTOR538_DECISION_SHA256,
        "selector-538 family decision evidence drifted",
    )
    BASE.require(
        BASE.sha256_file(SELECTOR538_EVIDENCE_PATH)
        == EXPECTED_SELECTOR538_EVIDENCE_SHA256,
        "selector-538 family evidence drifted",
    )
    BASE.require(
        BASE.sha256_file(SELECTOR538_PROMOTION_PATH)
        == EXPECTED_SELECTOR538_PROMOTION_SHA256,
        "selector-538 family promotion report drifted",
    )
    rows = ENGINE.load_jsonl_rows(SELECTOR538_EVIDENCE_PATH)
    return {
        coordinate: row
        for (resource, coordinate), row in rows.items()
        if resource == "pk_msggame"
    }


def load_actual_predecessor():
    BASE.require(
        BASE.sha256_file(ACTUAL_PREDECESSOR_PATH)
        == EXPECTED_ACTUAL_PREDECESSOR_SHA256,
        "current integrated ledger drifted",
    )
    rows = ENGINE.load_jsonl_rows(ACTUAL_PREDECESSOR_PATH)
    BASE.require(
        len(rows) == EXPECTED_PREDECESSOR_ROWS
        and sum(
            row.get("runtime_review") == "pending"
            for row in rows.values()
        )
        == EXPECTED_ACTUAL_PREDECESSOR_PENDING,
        "current integrated ledger row/status universe drifted",
    )
    family = load_selector538_family_evidence()
    _ORIGINAL_CHUNK0_ACTIONS.clear()
    for coordinate, evidence in family.items():
        row = rows[("pk_msggame", coordinate)]
        _ORIGINAL_CHUNK0_ACTIONS[coordinate] = row.get(
            "selector538_chunk0_update_action",
            _MISSING,
        )
        row["selector538_chunk0_update_action"] = evidence["action"]
    return rows


def build_analysis(**kwargs):
    result = ENGINE.build_analysis(**kwargs)
    actual_rows = result["actual_predecessor_rows"]
    for coordinate, original in _ORIGINAL_CHUNK0_ACTIONS.items():
        row = actual_rows[("pk_msggame", coordinate)]
        if original is _MISSING:
            row.pop("selector538_chunk0_update_action", None)
        else:
            row["selector538_chunk0_update_action"] = original
    return result


def build_audit(**kwargs):
    report = ENGINE.build_audit(**kwargs)
    report["integration_policy"]["actual_integration_predecessor"] = (
        "post_selector538_family_integrated_ledger"
    )
    report["scope"]["chunk_id"] = 1
    proof = report["proof"]
    proof["rejected_chunk1_pending_rows_unchanged"] = proof.pop(
        "rejected_chunk0_pending_rows_unchanged"
    )
    report["guards"].pop("report_payload_sha256", None)
    return BASE.HONORIFIC.seal_report(report)


def load_review():
    BASE.require(
        BASE.sha256_file(PRIVATE_HANDOFF_PATH) == EXPECTED_HANDOFF_SHA256,
        "private selector-568 chunk-1 handoff drifted",
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
        and result.get("accepted_live_after_selector538_plan_count")
        == EXPECTED_PLANNED_LIVE_PROMOTION_ROWS
        and result.get("blocked_pending_coordinate_count")
        == EXPECTED_REJECTED_PENDING_ROWS
        and proof.get("accepted_assembly_branches")
        == EXPECTED_ACCEPTED_ASSEMBLIES
        and proof.get("assembly_branches_recorded") == 469
        and proof.get("all_accepted_current_relative_raw_g1n_nonexpanding")
        is True
        and proof.get("all_accepted_register_branches_proven") is True
        and public.get("steam_write_performed") is False,
        "source-free selector-568 chunk-1 proposal drifted",
    )
    return handoff, public, world, validated


patch_contract()
REVIEW.load_assignment = load_assignment
ENGINE.load_actual_predecessor = load_actual_predecessor
ENGINE.load_selector538_evidence = load_selector538_family_evidence
BASE.load_review = load_review
BASE.build_analysis = build_analysis
BASE.build_audit = build_audit
BASE.build_updated_rows = ENGINE.build_updated_rows
BASE.build_promotion = ENGINE.build_promotion
BASE.validate_outputs = ENGINE.validate_outputs

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
build_outputs = BASE.build_outputs
validate_outputs = ENGINE.validate_outputs
validate_output_paths = BASE.validate_output_paths
parse_args = BASE.parse_args
HONORIFIC = BASE.HONORIFIC
BASE_AUDIT = BASE.BASE_AUDIT
LIVE_STEAM_BASE = BASE.LIVE_STEAM_BASE
LIVE_STEAM_PK = BASE.LIVE_STEAM_PK


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    validate_output_paths(args)
    (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        bundle,
    ) = build_outputs()
    frozen = all(
        (
            EXPECTED_AUDIT_FILE_SHA256,
            EXPECTED_PROMOTION_FILE_SHA256,
            EXPECTED_DECISION_FILE_SHA256,
            EXPECTED_EVIDENCE_FILE_SHA256,
        )
    )
    validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
        require_frozen_hashes=frozen,
    )
    outputs = {
        args.audit_output: audit_content,
        args.promotion_output: promotion_content,
        args.decision_output: decision_content,
        args.evidence_output: evidence_content,
    }
    if args.check:
        require(frozen, "closure hashes must be frozen before check mode")
        for path, content in outputs.items():
            require(path.is_file(), f"output missing: {path}")
            require(
                path.read_text(encoding="utf-8") == content,
                f"output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    print(
        "PASS "
        f"overrides={EXPECTED_REWRITE_ROWS} "
        f"renewed={EXPECTED_RENEWAL_ROWS} "
        f"promoted={EXPECTED_PLANNED_LIVE_PROMOTION_ROWS} "
        f"pending={EXPECTED_ACTUAL_PENDING_AFTER} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
