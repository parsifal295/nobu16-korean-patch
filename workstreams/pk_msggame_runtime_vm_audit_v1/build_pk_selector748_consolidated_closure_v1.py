#!/usr/bin/env python3
"""Build the selector-748 single-union closure on frozen post-selector550."""

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

BASE_BUILDER_PATH = WORKSTREAM / "build_pk_selector550_consolidated_closure_v1.py"
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector748_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector748_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector748_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector550_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector550_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector748_chunk{chunk}_review_v1.py"
    for chunk in range(3)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector748_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(3)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP
    / f"pk_selector748_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(3)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector748_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(3)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector748_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector748_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector748_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector748_consolidated_closure_promotion.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "F7F5FEF832B1C98AD288E3A72BD1A02744B5C14D305B3F901CE8484876C67C26"
)
EXPECTED_INPUT_SHA256 = {
    "assignment_builder":
        "E39ED4738833FB56680E81E5B06A68F04472BABE7279D92CB608A40DB7D17CF5",
    "assignment_private":
        "CE5FBC60D33426695E86FBC8E76205E99917956EE55DBF10375B8933CE91B17E",
    "assignment_public":
        "68615492AC049EF3B87D5840ACDB67A8E05D6E8F2EED63CBC89905A8DF5515B2",
    "official_ledger":
        "F2CB7279F71D33CFA9D73BD4A6DA8E7E90692047F8ECF1D521FD70512D71846E",
    "predecessor_decisions":
        "EAA8AB5A7B71532AC5E95C0C772C990AD05A9B9DFA0D2CCFDB3A813469F0F600",
    "chunk0_builder":
        "FDD2E48321FCDF240587225060A151DAE2CC072FEE7A9BAAD3C1DFAD6C27D7B8",
    "chunk0_public":
        "5B22B5863E673E009E3E200DFF30B47A8E9E29E541C85BE72B466464F423224A",
    "chunk0_decisions":
        "5FF46AC38DE81A7D5485B0FB6F2E489B55BDA5350DBD3A6DC4CB1BDA4464993D",
    "chunk0_evidence":
        "DAF703CC333DC10CAE1F75507F76243CF25CB1D9DACFFB21FE5B1D983E377A13",
    "chunk1_builder":
        "C94C79663403FED100C6D55A3205F85AB0309ABEA4B5AB01D33565FB0D003D59",
    "chunk1_public":
        "B13A18A0115B5B89405BA358967D8100F16FCA66BEACB437C52A5C5F4B6014E3",
    "chunk1_decisions":
        "383D540C26F63C07E495446932D884CB9A3094CF160BB7428A1AB8680BA55A36",
    "chunk1_evidence":
        "DB86BB97C491AB0AFDBE58E99A29B19EFBE1342DDDF23E6A310539F3092B63DF",
    "chunk2_builder":
        "C6F260CA1CABD8A206C18DFA0AFF96055CFA8BF47DF46CEC08ADA12F6CD013C2",
    "chunk2_public":
        "0944B05216AF81013B92D8943315C2FDE152024D8C33E2764FD6A97A0566C138",
    "chunk2_decisions":
        "8007506A3B1A9C5005DCD7A98570A5DF544D6817EE3B1A89B7C6BE0776271003",
    "chunk2_evidence":
        "A64A7DD43C994702E1EDD8601775CB982A11C130DE37CFEC93D759C8C0DB0E23",
}

EXPECTED_OWNER_ROWS = 154
EXPECTED_UNION_ROWS = 147
EXPECTED_DECISION_ROOTS = 72
EXPECTED_CHANGED_ROOTS = 72
EXPECTED_PROMOTIONS = 101
EXPECTED_UNION_RENEWALS = 46
EXPECTED_OWNER_RENEWALS = 46
EXPECTED_UNION_OVERRIDES = 99
EXPECTED_OWNER_OVERRIDES = 106
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 48,
    "translation_override_and_runtime_promotion": 53,
    "translation_override_and_verification_renewal": 46,
}
EXPECTED_OWNER_ACTION_COUNTS = {
    "runtime_promotion": 48,
    "translation_override_and_runtime_promotion": 60,
    "translation_override_and_verification_renewal": 46,
}
EXPECTED_CHUNK_ROWS = (72, 36, 46)
EXPECTED_CHUNK_SITES = (34, 34, 34)
EXPECTED_REVIEWED_SITES = 102
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "D69B1CEAF19B324B5B3D6C29AF16F9890A705BA1E4D9CE8DDD758A4CD9FDFF54"
)
EXPECTED_SOURCE_SITES = 114
EXPECTED_SOURCE_SITE_SHA256 = (
    "AFCF7EB81200064C04D91CAEDD184072B8CCA5672B8DA828573C7CECDA39E143"
)
EXPECTED_SOURCE_ONLY_SITES = 12
EXPECTED_SOURCE_ONLY_SHA256 = (
    "C4E05AF2C8076ED3386680145364D99CF22E76D624047B5A587ED20EB343CF40"
)
EXPECTED_OWNER_OVERLAPS = 7
EXPECTED_OWNER_OVERLAP_SHA256 = (
    "3AF9A924B49358F4AA993E2AF55B03C42CF53F14E202406469F3726BDFD28506"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_PENDING_BEFORE = 6_980
EXPECTED_PENDING_AFTER = 6_879
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "15C3BF1B4CC2E29020E5A8A6F40669555B54EEE57B04C3F7F77DF3AC680CFB93"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "2120F85E7450E58667C784D0ED2035589E1E6674563B94A938545A51B9C573CC"
)

# Frozen after deterministic bootstrap.
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "35D4A9DF18F3BFC14866B5EEE52606D5BCF41282D0E400AD2B11284FD3C407AE",
    "private_evidence":
        "B810947BAC53C9E989535CE95926AD61B3F3D85265B11699F288BC5D6E87D496",
    "public_coverage":
        "6FAD3A50788E7E4FFF2A25171C9461EA77BA5706B9E40E3C09E8F4BAFB95C78E",
    "public_promotion":
        "F253708E1DC1D171D57EA8C6D55A0CEC2E0366E8A614364A2C6F23C493607487",
    "final_candidate":
        "903B515128E94FE263430FAF7EECC51759A0DD132211F3C3047E5DAA6D16D9A6",
    "decision_coordinates":
        "21BED7CD926A5D699ECBE4F240D9CB41085C1A888E021504557730F4B74830E4",
    "promotion_coordinates":
        "CABC471277C98FD744C34251EA5E5FF073D6764B3F20422A6E79AA10E994D4AA",
    "renewal_coordinates":
        "61042C5B2B468EB02DF3A6859D33F5E43B0D43377A24E34131A374556F065294",
    "override_coordinates":
        "B1E7473FA32CA6992E04E80ACAD3F4DC33D2A8761A7A454F897F159256E2A5F6",
    "owner_overlap_coordinates": EXPECTED_OWNER_OVERLAP_SHA256,
    "source_only_proof":
        "2C4F937DEF3F7D71F69805C00FAD5E081DE10C5E2F834D237D611322D52B10B9",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE_WRAPPER = load_module(BASE_BUILDER_PATH, "selector748_closure_base")
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector748_closure_input")
BASE = BASE_WRAPPER.BASE

BASE_WRAPPER.ASSIGNMENT = ASSIGNMENT
BASE_WRAPPER.ASSIGNMENT_BUILDER_PATH = ASSIGNMENT_BUILDER_PATH
BASE_WRAPPER.ASSIGNMENT_PRIVATE_PATH = ASSIGNMENT_PRIVATE_PATH
BASE_WRAPPER.ASSIGNMENT_PUBLIC_PATH = ASSIGNMENT_PUBLIC_PATH
BASE_WRAPPER.OFFICIAL_LEDGER_PATH = OFFICIAL_LEDGER_PATH
BASE_WRAPPER.PREDECESSOR_DECISIONS_PATH = PREDECESSOR_DECISIONS_PATH
BASE_WRAPPER.CHUNK_BUILDERS = CHUNK_BUILDERS
BASE_WRAPPER.CHUNK_PUBLIC = CHUNK_PUBLIC
BASE_WRAPPER.CHUNK_DECISIONS = CHUNK_DECISIONS
BASE_WRAPPER.CHUNK_EVIDENCE = CHUNK_EVIDENCE
BASE_WRAPPER.PRIVATE_DECISIONS_OUTPUT = PRIVATE_DECISIONS_OUTPUT
BASE_WRAPPER.PRIVATE_EVIDENCE_OUTPUT = PRIVATE_EVIDENCE_OUTPUT
BASE_WRAPPER.PUBLIC_COVERAGE_OUTPUT = PUBLIC_COVERAGE_OUTPUT
BASE_WRAPPER.PUBLIC_PROMOTION_OUTPUT = PUBLIC_PROMOTION_OUTPUT
BASE_WRAPPER.EXPECTED_INPUT_SHA256 = EXPECTED_INPUT_SHA256
BASE_WRAPPER.EXPECTED_OWNER_ROWS = EXPECTED_OWNER_ROWS
BASE_WRAPPER.EXPECTED_UNION_ROWS = EXPECTED_UNION_ROWS
BASE_WRAPPER.EXPECTED_DECISION_ROOTS = EXPECTED_DECISION_ROOTS
BASE_WRAPPER.EXPECTED_CHANGED_ROOTS = EXPECTED_CHANGED_ROOTS
BASE_WRAPPER.EXPECTED_PROMOTIONS = EXPECTED_PROMOTIONS
BASE_WRAPPER.EXPECTED_UNION_RENEWALS = EXPECTED_UNION_RENEWALS
BASE_WRAPPER.EXPECTED_OWNER_RENEWALS = EXPECTED_OWNER_RENEWALS
BASE_WRAPPER.EXPECTED_UNION_OVERRIDES = EXPECTED_UNION_OVERRIDES
BASE_WRAPPER.EXPECTED_OWNER_OVERRIDES = EXPECTED_OWNER_OVERRIDES
BASE_WRAPPER.EXPECTED_ACTION_COUNTS = EXPECTED_ACTION_COUNTS
BASE_WRAPPER.EXPECTED_OWNER_ACTION_COUNTS = EXPECTED_OWNER_ACTION_COUNTS
BASE_WRAPPER.EXPECTED_CHUNK_ROWS = EXPECTED_CHUNK_ROWS
BASE_WRAPPER.EXPECTED_CHUNK_SITES = EXPECTED_CHUNK_SITES
BASE_WRAPPER.EXPECTED_REVIEWED_SITES = EXPECTED_REVIEWED_SITES
BASE_WRAPPER.EXPECTED_CANDIDATE_SITE_SHA256 = EXPECTED_CANDIDATE_SITE_SHA256
BASE_WRAPPER.EXPECTED_SOURCE_SITES = EXPECTED_SOURCE_SITES
BASE_WRAPPER.EXPECTED_SOURCE_SITE_SHA256 = EXPECTED_SOURCE_SITE_SHA256
BASE_WRAPPER.EXPECTED_SOURCE_ONLY_SITES = EXPECTED_SOURCE_ONLY_SITES
BASE_WRAPPER.EXPECTED_SOURCE_ONLY_SHA256 = EXPECTED_SOURCE_ONLY_SHA256
BASE_WRAPPER.EXPECTED_OWNER_OVERLAPS = EXPECTED_OWNER_OVERLAPS
BASE_WRAPPER.EXPECTED_OWNER_OVERLAP_SHA256 = EXPECTED_OWNER_OVERLAP_SHA256
BASE_WRAPPER.EXPECTED_PREDECESSOR_OVERLAPS = EXPECTED_PREDECESSOR_OVERLAPS
BASE_WRAPPER.EXPECTED_PREDECESSOR_SUPERSESSIONS = (
    EXPECTED_PREDECESSOR_SUPERSESSIONS
)
BASE_WRAPPER.EXPECTED_PENDING_BEFORE = EXPECTED_PENDING_BEFORE
BASE_WRAPPER.EXPECTED_PENDING_AFTER = EXPECTED_PENDING_AFTER
BASE_WRAPPER.EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    EXPECTED_OFFICIAL_CANDIDATE_SHA256
)
BASE_WRAPPER.EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256
)
BASE_WRAPPER.EXPECTED_OUTPUT_SHA256 = EXPECTED_OUTPUT_SHA256

BASE.ASSIGNMENT = ASSIGNMENT
BASE.ENGINE = ASSIGNMENT.ENGINE
BASE.RANKING = ASSIGNMENT.RANKING

ORIGINAL_CONFIGURE_BASE = BASE_WRAPPER.configure_base
ORIGINAL_TRANSFORM_OUTPUTS = BASE_WRAPPER.transform_outputs


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.EXPECTED_OUTPUT_SHA256["final_candidate"] = (
        EXPECTED_OUTPUT_SHA256["final_candidate"]
    )
    BASE.METHOD = (
        "post_selector550_selector748_three_chunk_single_coordinate_union_"
        "with_identical_shared_terminal_owner_overlap_and_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector748-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector748-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector748-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector748-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector748_consolidated_update_action"


def validate_site_call(
    records: Mapping[tuple[int, int], Any],
    site: str,
    *,
    expected: bool,
) -> None:
    block_id, record_id, gap_id, offset = map(int, site.split(":"))
    rows = [
        row
        for row in BASE.RANKING.LEGACY.record_edges(
            records[(block_id, record_id)]
        )
        if row["kind"] == "C"
        and tuple(row["target"]) == (0, 748)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-748 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    outputs = ORIGINAL_TRANSFORM_OUTPUTS(outputs)
    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("ascii"))
    coverage["proof"].pop("all_169_candidate_sites_reviewed")
    coverage["proof"].pop("source_only_8_absent_from_current_and_candidate")
    coverage["proof"]["all_102_candidate_sites_reviewed"] = True
    coverage["proof"]["source_only_12_absent_from_current_and_candidate"] = True
    coverage["guards"].pop("payload_without_guard_sha256")
    coverage["guards"]["payload_without_guard_sha256"] = BASE.canonical_sha256(
        coverage
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


BASE_WRAPPER.configure_base = configure_base
BASE_WRAPPER.validate_site_call = validate_site_call
BASE_WRAPPER.transform_outputs = transform_outputs


def build_outputs() -> dict[Path, bytes]:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector550 closure base drifted",
    )
    return BASE_WRAPPER.build_outputs()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    outputs = build_outputs()
    if args.check:
        for path, content in outputs.items():
            BASE.require(
                path.is_file() and path.read_bytes() == content,
                f"selector748 closure output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(
        json.dumps(
            {
                "coordinate_union_rows": EXPECTED_UNION_ROWS,
                "owner_decision_rows": EXPECTED_OWNER_ROWS,
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
