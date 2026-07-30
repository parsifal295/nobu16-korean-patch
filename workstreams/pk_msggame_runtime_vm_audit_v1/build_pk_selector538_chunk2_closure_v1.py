#!/usr/bin/env python3
"""Build the independent selector-538 chunk-2 runtime closure layer.

The frozen post-selector-1066 checkpoint is the predecessor. Dialogue bodies
and exact overrides remain private below ``tmp``; only source-free coverage
and promotion reports are tracked. Shared integration code, progress, and
Steam remain read only.
"""

from __future__ import annotations

import copy
import importlib.util
import sys
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
ENGINE_PATH = WORKSTREAM / "build_pk_selector538_chunk1_closure_v1.py"
REVIEW_BUILDER_PATH = WORKSTREAM / "build_pk_selector538_chunk2_review_v1.py"
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
PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family538_chunk2_analysis.private.v1.json"
)
REVIEW_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk2_review_proposal.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk2_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk2_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector538_chunk2_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector538_chunk2_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = "nobu16.kr.pk-selector538-chunk2-closure-coverage.v1"
PROMOTION_SCHEMA = "nobu16.kr.pk-selector538-chunk2-closure-promotion.v1"
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector538-chunk2-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = "nobu16.kr.pk-selector538-chunk2-exact-override.v1"
METHOD = "reversed_vm_pk_selector538_chunk2_independent_closure"
UPDATE_ACTION_FIELD = "selector538_chunk2_update_action"
EXACT_OVERRIDE_FIELD = "selector538_chunk2_exact_override_evidence"
SELECTOR = 538
TERMINALS = tuple(range(1916, 1923))

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_HANDOFF_SHA256 = (
    "7B01273B3DF0042DF7BF35ABDA1751EAE7B88F6890FD38E6B4C6CF1959CC4574"
)
EXPECTED_REVIEW_PUBLIC_SHA256 = (
    "0EFE7C538E2A966D063400CE551F8858D3A6AC5D4C5508FAC3334731AFFB460F"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_213
EXPECTED_PENDING_AFTER = 8_169
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "E5E46F9814DF6B4DE9E9293EBAF9CF8DDD14B3D48F8D60EDA838BCD1C3FC1266"
)
EXPECTED_REWRITE_ROWS = 30
EXPECTED_KEEP_ROWS = 3
EXPECTED_REJECTED_SITES = 38
EXPECTED_ACCEPTED_SITES = 33
EXPECTED_ACCEPTED_ASSEMBLIES = 231
EXPECTED_PROMOTION_ROWS = 44
EXPECTED_PROMOTION_ROOTS = 25
EXPECTED_REJECTED_PENDING_ROWS = 57
EXPECTED_REJECTED_ROOTS = 38
EXPECTED_REJECTED_PENDING_ROOTS = 32
EXPECTED_RENEWAL_ROWS = 420
EXPECTED_RENEWAL_ROOTS = 204
EXPECTED_DECISION_ROWS = 464
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 340
EXPECTED_SOURCE_AFFECTED_ROOTS = 405
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 36,
    "translation_override_and_runtime_promotion": 8,
    "translation_override_and_verification_renewal": 22,
    "verification_renewal": 398,
}

EXPECTED_REWRITE_COORDINATE_SHA256 = (
    "94C92DFF823518F2156E4C807B7D3B021D8F1E8BC43D06F180B917511331971B"
)
EXPECTED_REWRITE_MAP_SHA256 = (
    "450C186FC755553E7C5C43D4F21701DF49B332254088717B6993412E0440BD2E"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "EB277A871FDD6C9C3EA7DA4A150A35B45B4CBFEF4C5086C05E05B274E83F60CE"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "E01D6C4628787C3BC61DBEA4FABB9FB67A70F47B23F2D9634EA457A4C758A777"
)
EXPECTED_ACCEPTED_ROOT_SHA256 = (
    "DE0C65372DC24CF5A904A79B64260F8E0601CD2C5C82FBC12452C7B3230D1B7E"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "0C740849FBDE1F4D11543471596C8FA5D7B176E97BCD12D8A8F9A99B71C0FB97"
)
EXPECTED_PROMOTION_ROOT_SHA256 = (
    "53909755933D03B691F3FC7CAEBC455316CC61FDF2B0753A89F81ABFF571521C"
)
EXPECTED_REJECTED_COORDINATE_SHA256 = (
    "9FD9765A38202A9AFD1F25C4264BF0418C90C772CE0B19B33FA51554F8F096C4"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "5078C4F351DC1BE4AA17385FBD256A1ECA3A16801B0A41BBDF583F7C2B61F109"
)
EXPECTED_REJECTED_PENDING_ROOT_SHA256 = (
    "982F7CC5A3ED66A9C74CC871BC6C80AC0C1E87189D714C869025C682390AE40B"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "36058C249C73F5B42C0DC7426FA68879F4BDC515F40F9C50B6CFEC07C7FD4D59"
)
EXPECTED_RENEWAL_ROOT_SHA256 = (
    "65AB478BEE4C7F7102084ACDD7D1268C33F5FE93DDA278F69DEB7D59C502AE92"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "D7DDC358689AF3B84C63AC37174552F45A7171492F92DD229C1E7C98369D81C4"
)
EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256 = (
    "8EF7B4ED0FF43FACAB1B4D393D0198CAE3E2C7057A9D29EF3F22E21DB176BC50"
)
EXPECTED_SOURCE_AFFECTED_ROOT_SHA256 = (
    "1958C5972B0E9F1F7606DDD39F41FDCD05CE7A80AC1A7B63E357E3EA51358A64"
)

# Frozen after independently reproducible outputs are generated.
EXPECTED_ACCEPTED_ASSEMBLY_SHA256: str | None = (
    "8B11F02D305F2EB2760392CBD86611BA51BB7184C199679908EFDE2CF2371A8E"
)
EXPECTED_AUDIT_FILE_SHA256: str | None = (
    "5475B552EF7BA70EE1F184263F45BDDC732E1548ED371D6174EC485EA1BAFEBA"
)
EXPECTED_PROMOTION_FILE_SHA256: str | None = (
    "CB4DF5D1307995E5C60D19CF1DD43F95D852901A70E4480B03F22D1B8BD9E871"
)
EXPECTED_DECISION_FILE_SHA256: str | None = (
    "1AFCCCF416F1EFFB04DAA045139E85E16D96668EB4E8F7A8CE41B6362C573BB2"
)
EXPECTED_EVIDENCE_FILE_SHA256: str | None = (
    "C59C7190BF0291B99CF8D4A64AE3276DD36238CAFC90F77F562089927DBC050E"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module(ENGINE_PATH, "pk_selector538_chunk2_closure_engine_v1")
REVIEW = load_module(REVIEW_BUILDER_PATH, "pk_selector538_chunk2_closure_review_v1")
CLOSURE = ENGINE.BASE

_CONTRACT = {
    "REVIEW": REVIEW,
    "CALLER": REVIEW.CALLER,
    "HONORIFIC": REVIEW.CALLER.HONORIFIC,
    "CROSS": REVIEW.CALLER.CROSS,
    "BASE_AUDIT": REVIEW.BASE_AUDIT,
    "ENGINE": REVIEW.CALLER.ENGINE,
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
    "EXACT_OVERRIDE_FIELD": EXACT_OVERRIDE_FIELD,
    "SELECTOR": SELECTOR,
    "TERMINALS": TERMINALS,
}
for _name in (
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
    _CONTRACT[_name] = globals()[_name]
for _name, _value in _CONTRACT.items():
    setattr(ENGINE, _name, _value)
ENGINE.patch_base_contract()


def load_review() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    CLOSURE.require(
        CLOSURE.sha256_file(PRIVATE_HANDOFF_PATH) == EXPECTED_HANDOFF_SHA256,
        "private chunk-2 handoff drifted",
    )
    public = CLOSURE.load_json_exact(
        REVIEW_PUBLIC_PATH,
        EXPECTED_REVIEW_PUBLIC_SHA256,
    )
    assignment, chunk = REVIEW.load_assignment()
    world = REVIEW.ENGINE.load_world()
    handoff = REVIEW.load_json_exact(PRIVATE_HANDOFF_PATH)
    validated = REVIEW.ENGINE.validate_private_handoff(
        handoff,
        assignment=assignment,
        chunk=chunk,
        world=world,
    )
    result = public.get("result", {})
    proof = public.get("proof", {})
    CLOSURE.require(
        public.get("schema") == REVIEW.PUBLIC_SCHEMA
        and public.get("status") == "PASS"
        and result.get("accepted_site_count") == EXPECTED_ACCEPTED_SITES
        and result.get("rewrite_coordinate_count") == EXPECTED_REWRITE_ROWS
        and result.get("keep_coordinate_count") == EXPECTED_KEEP_ROWS
        and result.get("reject_coordinate_count") == EXPECTED_REJECTED_SITES
        and result.get("proposal_candidate_sha256")
        == EXPECTED_CANDIDATE_SHA256
        and result.get("runtime_promotion_coordinate_count")
        == EXPECTED_PROMOTION_ROWS
        and result.get("blocked_pending_coordinate_count")
        == EXPECTED_REJECTED_PENDING_ROWS
        and result.get("verification_renewal_coordinate_count")
        == EXPECTED_RENEWAL_ROWS
        and proof.get("accepted_assembly_branches")
        == EXPECTED_ACCEPTED_ASSEMBLIES
        and proof.get("assembly_branches_recorded") == 497
        and proof.get(
            "all_accepted_current_relative_raw_g1n_nonexpanding"
        )
        is True
        and proof.get("all_accepted_register_branches_proven") is True
        and public.get("steam_write_performed") is False,
        "source-free chunk-2 proposal drifted",
    )
    return handoff, public, world, validated


def build_analysis(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    world: Mapping[str, Any],
    handoff: Mapping[str, Any],
    validated: Mapping[str, Any],
) -> dict[str, Any]:
    adapted = copy.deepcopy(dict(handoff))
    for row in adapted["site_reviews"]:
        row["baseline_candidate_right"] = row["reviewed_candidate_right"]
    return ENGINE._BASE_BUILD_ANALYSIS(
        predecessor_rows=predecessor_rows,
        world=world,
        handoff=adapted,
        validated=validated,
    )


def build_audit(
    *,
    analysis: Mapping[str, Any],
    predecessor_report: Mapping[str, Any],
    review_public: Mapping[str, Any],
) -> dict[str, Any]:
    report = ENGINE._BASE_BUILD_AUDIT(
        analysis=analysis,
        predecessor_report=predecessor_report,
        review_public=review_public,
    )
    result = copy.deepcopy(report)
    result["proof"]["rejected_chunk2_pending_rows_unchanged"] = (
        result["proof"].pop("rejected_chunk0_pending_rows_unchanged")
    )
    result["scope"]["chunk_id"] = 2
    return CLOSURE.HONORIFIC.seal_report(result)


def build_updated_rows(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    analysis: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    updated_rows, evidence_rows = ENGINE._BASE_BUILD_UPDATED_ROWS(
        predecessor_rows=predecessor_rows,
        analysis=analysis,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
    )
    for row in updated_rows:
        if "selector538_chunk0_exact_override_evidence" in row:
            row[EXACT_OVERRIDE_FIELD] = row.pop(
                "selector538_chunk0_exact_override_evidence"
            )
    return updated_rows, evidence_rows


CLOSURE.load_review = load_review
CLOSURE.build_analysis = build_analysis
CLOSURE.build_audit = build_audit
CLOSURE.build_updated_rows = build_updated_rows

ClosureError = CLOSURE.ClosureError
require = CLOSURE.require
sha256_bytes = CLOSURE.sha256_bytes
sha256_file = CLOSURE.sha256_file
canonical_bytes = CLOSURE.canonical_bytes
canonical_json = CLOSURE.canonical_json
canonical_jsonl = CLOSURE.canonical_jsonl
canonical_sha256 = CLOSURE.canonical_sha256
parse_coordinate = CLOSURE.parse_coordinate
coordinate_digest = CLOSURE.coordinate_digest
root_digest = CLOSURE.root_digest
site_digest = CLOSURE.site_digest
row_sort_key = CLOSURE.row_sort_key
load_json_exact = CLOSURE.load_json_exact
load_predecessor = CLOSURE.load_predecessor
grouped_coordinates = CLOSURE.grouped_coordinates
build_candidate = CLOSURE.build_candidate
coordinates_for_roots = CLOSURE.coordinates_for_roots
build_promotion = CLOSURE.build_promotion
assert_source_free_report = CLOSURE.assert_source_free_report
contains_body_key = CLOSURE.contains_body_key
build_outputs = CLOSURE.build_outputs
validate_outputs = CLOSURE.validate_outputs
validate_output_paths = CLOSURE.validate_output_paths
parse_args = CLOSURE.parse_args
HONORIFIC = CLOSURE.HONORIFIC
BASE_AUDIT = CLOSURE.BASE_AUDIT
LIVE_STEAM_BASE = CLOSURE.LIVE_STEAM_BASE
LIVE_STEAM_PK = CLOSURE.LIVE_STEAM_PK


def main(argv: Sequence[str] | None = None) -> int:
    return CLOSURE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
