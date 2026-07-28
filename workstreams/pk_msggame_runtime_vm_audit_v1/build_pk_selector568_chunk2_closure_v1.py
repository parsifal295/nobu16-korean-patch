#!/usr/bin/env python3
"""Build the independent selector-568 chunk-2 runtime closure layer."""

from __future__ import annotations

import copy
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
REVIEW_BUILDER_PATH = WORKSTREAM / "build_pk_selector568_chunk2_review_v1.py"

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
ACTUAL_PREDECESSOR_PATH = PREDECESSOR_PRIVATE_PATH
PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family568_chunk2_analysis.private.v1.json"
)
REVIEW_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector568_chunk2_review_proposal.v1.json"
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
    WORKSTREAM / "public" / "pk_selector568_chunk2_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector568_chunk2_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector568_chunk2_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector568_chunk2_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = "nobu16.kr.pk-selector568-chunk2-closure-coverage.v1"
PROMOTION_SCHEMA = "nobu16.kr.pk-selector568-chunk2-closure-promotion.v1"
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector568-chunk2-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = "nobu16.kr.pk-selector568-chunk2-exact-override.v1"
METHOD = "reversed_vm_pk_selector568_chunk2_independent_closure"
UPDATE_ACTION_FIELD = "selector568_chunk2_update_action"
BF7B_ACTION_FIELD = "selector568_chunk2_bf7b_action"
EXACT_OVERRIDE_FIELD = "selector568_chunk2_exact_override_evidence"
SELECTOR = 568
TERMINALS = tuple(range(1951, 1958))

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_ACTUAL_PREDECESSOR_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_HANDOFF_SHA256 = (
    "C2235C1BBF2E12D1A9E8466BBB77A0AC3BD1FE87B8EE9238F32D27F24AA3AB37"
)
EXPECTED_REVIEW_PUBLIC_SHA256 = (
    "EE379364FF07A9080E3CFCBB0D6804BB3213EDFF7213C14D37F4A6C46236DE1B"
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
EXPECTED_PENDING_AFTER = 8_163
EXPECTED_ACTUAL_PREDECESSOR_PENDING = 8_213
EXPECTED_ACTUAL_PENDING_AFTER = 8_163
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "D6F95943EA08B02533D8541EF28B3E0F584E79E0CBA2A49D30B5B84D2D48B409"
)
EXPECTED_ACTUAL_CANDIDATE_SHA256 = (
    "D6F95943EA08B02533D8541EF28B3E0F584E79E0CBA2A49D30B5B84D2D48B409"
)
EXPECTED_BF7B_DECISION_PROJECTION_CANDIDATE_SHA256 = (
    "D6F95943EA08B02533D8541EF28B3E0F584E79E0CBA2A49D30B5B84D2D48B409"
)
EXPECTED_REWRITE_ROWS = 51
EXPECTED_KEEP_ROWS = 9
EXPECTED_REJECTED_SITES = 18
EXPECTED_ACCEPTED_SITES = 60
EXPECTED_ACCEPTED_ASSEMBLIES = 420
EXPECTED_PROMOTION_ROWS = 50
EXPECTED_PROMOTION_ROOTS = 28
EXPECTED_PLANNED_LIVE_PROMOTION_ROWS = 50
EXPECTED_PLANNED_LIVE_PROMOTION_ROOTS = 28
EXPECTED_ALREADY_PROMOTED_ROWS = 0
EXPECTED_REJECTED_PENDING_ROWS = 36
EXPECTED_REJECTED_ROOTS = 18
EXPECTED_REJECTED_PENDING_ROOTS = 16
EXPECTED_RENEWAL_ROWS = 261
EXPECTED_RENEWAL_ROOTS = 142
EXPECTED_DECISION_ROWS = 311
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 281
EXPECTED_SOURCE_AFFECTED_ROOTS = 291
EXPECTED_SELECTOR538_SUPERSESSION_ROWS = 0
EXPECTED_SELECTOR538_RENEWAL_SUPERSESSION_ROWS = 0
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 34,
    "translation_override_and_runtime_promotion": 16,
    "translation_override_and_verification_renewal": 35,
    "verification_renewal": 226,
}
EXPECTED_BF7B_ACTION_COUNTS = dict(EXPECTED_ACTION_COUNTS)

EXPECTED_REWRITE_COORDINATE_SHA256 = (
    "A2234AB61FD1A5B236CF46FC94B8A68A2EEE1DF88A2EC981DD9B9CD23920DEF3"
)
EXPECTED_REWRITE_MAP_SHA256 = (
    "BF7453209AF881B79AE630AC67F1E573280BFD10BCB7E791EB604298B48065E6"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "5194E3E6361BBC9791F18F9B98DC37366EA6933F92689AF4F748210BBE6978B7"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "9D4D52DAE0DCBC38C923836249BEF3528A86D4E8E740D17B2594FEFE9713E1F3"
)
EXPECTED_ACCEPTED_ROOT_SHA256 = (
    "F5389A12EF6C98B456C38BEA56E710220E2EA81DE1F3B37B112ABA20F4A6615A"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "998CAF454BA7AE62242E465391B90ED53810A830D0E1257191F2533AD5067B65"
)
EXPECTED_PROMOTION_ROOT_SHA256 = (
    "A8502147E90313B6F43AFCBE226329AE603BD5A1AFBBFA99CBCF6D6ECD233505"
)
EXPECTED_PLANNED_LIVE_PROMOTION_COORDINATE_SHA256 = (
    "998CAF454BA7AE62242E465391B90ED53810A830D0E1257191F2533AD5067B65"
)
EXPECTED_PLANNED_LIVE_PROMOTION_ROOT_SHA256 = (
    "A8502147E90313B6F43AFCBE226329AE603BD5A1AFBBFA99CBCF6D6ECD233505"
)
EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_REJECTED_COORDINATE_SHA256 = (
    "5353221004B1902876E0E27CF18C0541D1B24DB9001B8450350EF6B40C7284BD"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "CAD70606F1AF2324BEFBCDA21C8581A7AEC60F73C5E21C3A863ACC8F9AE8E871"
)
EXPECTED_REJECTED_PENDING_ROOT_SHA256 = (
    "09C13FAF3E13E711DFD2EA64313EF8FEA80CCC505672345E82DB3EDDCEE5E838"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "B9020FDF90392ACD95869EA9553FB77286A6B7E373403443DB5444D10116DE6C"
)
EXPECTED_RENEWAL_ROOT_SHA256 = (
    "B4A3EAA1B5AB6526921FCC73FCAA6F87BB66758CD2EF8639F141A05522DF9606"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "777B7A43F11BEC0494430679FD2F0DA5C2450CE136D2988399514D7086BD891C"
)
EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256 = (
    "493955409CFECBA5A3B3D93193BDAF0ECB3544A26664919006AC3424EE58E0FA"
)
EXPECTED_SOURCE_AFFECTED_ROOT_SHA256 = (
    "B6A76B74CAEC9C25746B5EA863FAB92C8192DF2A7080FEFA5AD475F22374DFF0"
)
EXPECTED_SELECTOR538_SUPERSESSION_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_SELECTOR538_RENEWAL_SUPERSESSION_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_ACCEPTED_ASSEMBLY_SHA256: str | None = (
    "98DDE71CFCE20D622313A1FE8950797B8A8606D7AF8FC472730DAA582BC3FF8E"
)
EXPECTED_AUDIT_FILE_SHA256: str | None = (
    "15E5D3F4606A6C08A0F48FC481B7AF78686205DAC6DDAEA2E43C0234D395880D"
)
EXPECTED_PROMOTION_FILE_SHA256: str | None = (
    "52D6B7B482A02699956D65A015A12BD750F33958B6CD58B1601F3856404107C2"
)
EXPECTED_DECISION_FILE_SHA256: str | None = (
    "35CDC04F0C93247DFC406BB71AB87714E42619A9CDD22192782458220DD98FB9"
)
EXPECTED_EVIDENCE_FILE_SHA256: str | None = (
    "E65EA5FAAAA9524555F1D14267CD1716404CEF6E7CA69833DB31A496CFE8387A"
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
    "pk_selector568_chunk2_closure_engine_v1",
)
REVIEW = load_module(
    REVIEW_BUILDER_PATH,
    "pk_selector568_chunk2_closure_review_v1",
)
BASE = ENGINE.BASE
REVIEW.ENGINE.sha256_text = REVIEW.CALLER.ENGINE.sha256_text
_BASE_BUILD_AUDIT = ENGINE.build_audit


def patch_contract() -> None:
    values = {
        "REVIEW": REVIEW,
        "PREDECESSOR_PRIVATE_PATH": PREDECESSOR_PRIVATE_PATH,
        "PREDECESSOR_PUBLIC_PATH": PREDECESSOR_PUBLIC_PATH,
        "ACTUAL_PREDECESSOR_PATH": ACTUAL_PREDECESSOR_PATH,
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
        "BF7B_ACTION_FIELD": BF7B_ACTION_FIELD,
        "EXACT_OVERRIDE_FIELD": EXACT_OVERRIDE_FIELD,
    }
    for name in tuple(globals()):
        if name.startswith("EXPECTED_"):
            values[name] = globals()[name]
    for module in (ENGINE, BASE):
        for name, value in values.items():
            setattr(module, name, value)


def load_review():
    BASE.require(
        BASE.sha256_file(PRIVATE_HANDOFF_PATH) == EXPECTED_HANDOFF_SHA256,
        "private selector-568 chunk-2 handoff drifted",
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
        and proof.get("assembly_branches_recorded") == 546
        and proof.get("all_accepted_current_relative_raw_g1n_nonexpanding")
        is True
        and proof.get("all_accepted_register_branches_proven") is True
        and public.get("steam_write_performed") is False,
        "source-free selector-568 chunk-2 proposal drifted",
    )
    return handoff, public, world, validated


def build_audit(**kwargs):
    report = _BASE_BUILD_AUDIT(**kwargs)
    result = copy.deepcopy(report)
    result["integration_policy"]["actual_integration_predecessor"] = (
        "immutable_bf7b_theoretical_checkpoint"
    )
    result["integration_policy"][
        "official_post_selector538_rebase_deferred_to_family_consolidation"
    ] = True
    result["proof"][
        "standalone_layer_is_theoretical_not_official_promotion_claim"
    ] = True
    result["scope"]["chunk_id"] = 2
    return BASE.HONORIFIC.seal_report(result)


patch_contract()
BASE.load_review = load_review
BASE.build_analysis = ENGINE.build_analysis
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
