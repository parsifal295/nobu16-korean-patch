#!/usr/bin/env python3
"""Build the selector-142 single-union closure on frozen post-selector1126."""

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

BASE_BUILDER_PATH = WORKSTREAM / "build_pk_selector1126_consolidated_closure_v1.py"
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector142_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector142_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector142_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1126_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector1126_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector142_chunk{chunk}_review_v1.py"
    for chunk in range(3)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector142_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(3)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector142_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(3)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector142_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(3)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector142_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector142_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector142_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector142_consolidated_closure_promotion.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "AE769DBA9F0BBC1A6E04A663E6DBDE98ADC5DA45CA5CA1A4199DE1B0C3CBCC77"
)
EXPECTED_INPUT_SHA256 = {
    "assignment_builder":
        "AE1428FBF34BA042F1588E89DAA02623752D791BCD498687B9AD8595ED4BD7FF",
    "assignment_private":
        "3F22858009367851ADCFBC99E4620CCD4676043FD22755DBF48A50571B7E4C7E",
    "assignment_public":
        "D0EA381E8491BDD34E7E9D30BFCAA027CCBCA197468EB5AFF6F76B5F4D892438",
    "official_ledger":
        "3198DC9F7A06809636D0C43F5740A65B5D4C50E7226D53AA7C52B7D893EFA06E",
    "predecessor_decisions":
        "E7FE1D70A6DF175C25D3D4D42359983E26075F1962B8F0EB6BD52DC82376EB15",
    "chunk0_builder":
        "C62040CB4437D4FF2ECCF2235D1038826A6E01AC16F427EC7B10D09B284D3B06",
    "chunk0_public":
        "BEBE9154674989ABFA86926A91FAF911DC8EAB5D2646A0C3348046F6D6A23AB5",
    "chunk0_decisions":
        "8CB612B1F881A15E46F5450DE4AC0BAFB1A067531886BF5E80EC7726B6033F92",
    "chunk0_evidence":
        "66DC85B09C88F3C42A659A13AEBB06DF60EAB724675F1DD1376CC73ADFFB78A9",
    "chunk1_builder":
        "1426011D5BDF98CADAA074CF4F721A62F513797C3D7C846B5F63DC326F506CA3",
    "chunk1_public":
        "966B8005C2BE5D271C7AD8D710B0A47018378B8E1CFAF2B37034539FD9FAC161",
    "chunk1_decisions":
        "6C9F52DB04C2FE46CF14D40CD1CED03E4638D2201664F232895990C713798B9D",
    "chunk1_evidence":
        "3668346AF7B6070C1A25529ED0720B2349F0D18EEB8C535E3E26E2F8522307BF",
    "chunk2_builder":
        "E57510C22DED8F050FFDD230DB15966F23C2874455FD459FEB029FA9E878341C",
    "chunk2_public":
        "8B3F493D7BD169B5BF0176F829A92AE03BFEEC4ABD788C3FBF37F9832DE754C2",
    "chunk2_decisions":
        "6F0F575A206F2A2B3E1244E0451556000058B3580A7FF70345EE46F24920FD40",
    "chunk2_evidence":
        "75C32D13199A16F0A887D8D52A37ADE7D6DA989A9A6F508C94943205B0171415",
}

EXPECTED_OWNER_ROWS = 162
EXPECTED_UNION_ROWS = 162
EXPECTED_DECISION_ROOTS = 91
EXPECTED_CHANGED_ROOTS = 85
EXPECTED_PROMOTIONS = 116
EXPECTED_UNION_RENEWALS = 46
EXPECTED_OWNER_RENEWALS = 46
EXPECTED_UNION_OVERRIDES = 101
EXPECTED_OWNER_OVERRIDES = 101
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 61,
    "translation_override_and_runtime_promotion": 55,
    "translation_override_and_verification_renewal": 46,
}
EXPECTED_OWNER_ACTION_COUNTS = EXPECTED_ACTION_COUNTS
EXPECTED_CHUNK_ROWS = (46, 53, 63)
EXPECTED_CHUNK_SITES = (34, 36, 39)
EXPECTED_REVIEWED_SITES = 109
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "4E040FA596394C5378375876510E3A296F66719CB57370AF9AF0445B9F8CD070"
)
EXPECTED_SOURCE_SITES = 115
EXPECTED_SOURCE_SITE_SHA256 = (
    "296259EAF7CB09EEC5B1CF8D978D77071997F4E3E8F5D17789CE4706A40131C8"
)
EXPECTED_SOURCE_ONLY_SITES = 6
EXPECTED_SOURCE_ONLY_SHA256 = (
    "C4F5553FF0AE65E2880C01A09914A138F36F15A887E783EDC9192B6FCB08E40B"
)
EXPECTED_OWNER_OVERLAPS = 0
EXPECTED_OWNER_OVERLAP_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_PREDECESSOR_OVERLAP_SHA256 = EXPECTED_OWNER_OVERLAP_SHA256
EXPECTED_PENDING_BEFORE = 6_761
EXPECTED_PENDING_AFTER = 6_645
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "B25D15DB919FC4E3CF3A68E7C10938F581C233F04DA111F1C8D0ECA0A3F86D62"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "BD38D0EE71B59ADFEB8146760B91E82A7E09604E17B770760F13C94CB32704A5"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "6E3E5CD8A0FF7CC07C69BD9ABDCB2380FFD507D21F528E2A446D57329359F6A8"
)

# Frozen after deterministic bootstrap.
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "E0AD32905438B6E1228F512105B1AE33570B51307FFA5550A1A2E82D8B5D6692",
    "private_evidence":
        "9822F9E413F8F74DD5AA08D7F7626B69143295F22EAF6BAFA569BF0C7FC48FAF",
    "public_coverage":
        "C2E6289A849D7D2ADE417DF818F0CE373017C6F4FB5E398C7F17956933F1FA7A",
    "public_promotion":
        "35D1E186215717B75C781B8A04FF70F3D26714ED3605ED5E0C1BF6BB48F0DE26",
    "final_candidate": EXPECTED_FINAL_CANDIDATE_SHA256,
    "decision_coordinates":
        "719F9CA4F9801104F5255824916307084EDF1FB20D16B1373EB801B3783A759E",
    "promotion_coordinates":
        "18E0612009B06E1C9E7DB613C2A118C647C0073FF43F9C75E9C0EEC6F83D69D9",
    "renewal_coordinates":
        "28366F53ED7F7C6019DBF228458D0CF14D6D6910EB5E91877427BE57ED91C826",
    "override_coordinates":
        "8ED2707A3B3EE4F46788D7CB4DD6C614CD0FC8C68C333EEB67720E9B2264F065",
    "owner_overlap_coordinates": EXPECTED_OWNER_OVERLAP_SHA256,
    "source_only_proof":
        "7B1E83A2402C37259333A6D3FFE39B9CFF59D605FC5CA51FC5F1AE2F55A4C021",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE_WRAPPER = load_module(BASE_BUILDER_PATH, "selector142_closure_base")
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector142_closure_input")
ASSIGNMENT.load_records = ASSIGNMENT.BASE.load_records
BASE = BASE_WRAPPER.BASE

for _name in (
    "ASSIGNMENT_BUILDER_PATH",
    "ASSIGNMENT_PRIVATE_PATH",
    "ASSIGNMENT_PUBLIC_PATH",
    "OFFICIAL_LEDGER_PATH",
    "PREDECESSOR_DECISIONS_PATH",
    "CHUNK_BUILDERS",
    "CHUNK_PUBLIC",
    "CHUNK_DECISIONS",
    "CHUNK_EVIDENCE",
    "PRIVATE_DECISIONS_OUTPUT",
    "PRIVATE_EVIDENCE_OUTPUT",
    "PUBLIC_COVERAGE_OUTPUT",
    "PUBLIC_PROMOTION_OUTPUT",
    "EXPECTED_INPUT_SHA256",
    "EXPECTED_OWNER_ROWS",
    "EXPECTED_UNION_ROWS",
    "EXPECTED_DECISION_ROOTS",
    "EXPECTED_CHANGED_ROOTS",
    "EXPECTED_PROMOTIONS",
    "EXPECTED_UNION_RENEWALS",
    "EXPECTED_OWNER_RENEWALS",
    "EXPECTED_UNION_OVERRIDES",
    "EXPECTED_OWNER_OVERRIDES",
    "EXPECTED_ACTION_COUNTS",
    "EXPECTED_OWNER_ACTION_COUNTS",
    "EXPECTED_CHUNK_ROWS",
    "EXPECTED_CHUNK_SITES",
    "EXPECTED_REVIEWED_SITES",
    "EXPECTED_CANDIDATE_SITE_SHA256",
    "EXPECTED_SOURCE_SITES",
    "EXPECTED_SOURCE_SITE_SHA256",
    "EXPECTED_SOURCE_ONLY_SITES",
    "EXPECTED_SOURCE_ONLY_SHA256",
    "EXPECTED_OWNER_OVERLAPS",
    "EXPECTED_OWNER_OVERLAP_SHA256",
    "EXPECTED_PREDECESSOR_OVERLAPS",
    "EXPECTED_PREDECESSOR_SUPERSESSIONS",
    "EXPECTED_PENDING_BEFORE",
    "EXPECTED_PENDING_AFTER",
    "EXPECTED_OFFICIAL_CANDIDATE_SHA256",
    "EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256",
    "EXPECTED_OUTPUT_SHA256",
):
    setattr(BASE_WRAPPER, _name, globals()[_name])
    setattr(BASE_WRAPPER.BASE_WRAPPER, _name, globals()[_name])
    setattr(BASE_WRAPPER.INNER_WRAPPER, _name, globals()[_name])

BASE_WRAPPER.ASSIGNMENT = ASSIGNMENT
BASE_WRAPPER.BASE_WRAPPER.ASSIGNMENT = ASSIGNMENT
BASE.ASSIGNMENT = ASSIGNMENT
BASE.ENGINE = ASSIGNMENT.ENGINE
BASE.RANKING = ASSIGNMENT.RANKING

ORIGINAL_CONFIGURE_BASE = BASE_WRAPPER.ORIGINAL_CONFIGURE_BASE
ORIGINAL_TRANSFORM_OUTPUTS = BASE_WRAPPER.ORIGINAL_TRANSFORM_OUTPUTS


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.EXPECTED_OUTPUT_SHA256.update(
        {
            "final_candidate": EXPECTED_FINAL_CANDIDATE_SHA256,
            "predecessor_overlap_coordinates":
                EXPECTED_PREDECESSOR_OVERLAP_SHA256,
            "predecessor_supersession_coordinates":
                EXPECTED_PREDECESSOR_OVERLAP_SHA256,
        }
    )
    BASE.METHOD = (
        "post_selector1126_selector142_three_chunk_single_coordinate_union_"
        "with_disjoint_owners_and_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector142-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector142-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector142-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector142-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector142_consolidated_update_action"


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
        and tuple(row["target"]) == (0, 142)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-142 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    outputs = ORIGINAL_TRANSFORM_OUTPUTS(outputs)
    evidence = json.loads(outputs[PRIVATE_EVIDENCE_OUTPUT].decode("ascii"))
    evidence["proof"].pop(
        "chunk_assignments_disjoint_except_identical_terminal_owner_overlap"
    )
    evidence["proof"].pop("identical_terminal_owner_overlap_deduplicated")
    evidence["proof"]["chunk_coordinate_and_root_sets_disjoint"] = True
    outputs[PRIVATE_EVIDENCE_OUTPUT] = BASE.serialized_json(evidence)

    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("ascii"))
    coverage["proof"].pop("all_102_candidate_sites_reviewed")
    coverage["proof"].pop("source_only_12_absent_from_current_and_candidate")
    coverage["proof"].pop(
        "chunk_assignments_disjoint_except_identical_terminal_owner_overlap"
    )
    coverage["proof"].pop("identical_terminal_owner_overlap_deduplicated")
    coverage["proof"]["all_109_candidate_sites_reviewed"] = True
    coverage["proof"]["source_only_6_absent_from_current_and_candidate"] = True
    coverage["proof"]["chunk_coordinate_and_root_sets_disjoint"] = True
    coverage["guards"]["private_evidence_sha256"] = BASE.sha256_bytes(
        outputs[PRIVATE_EVIDENCE_OUTPUT]
    )
    coverage["guards"].pop("payload_without_guard_sha256")
    coverage["guards"]["payload_without_guard_sha256"] = BASE.canonical_sha256(
        coverage
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)

    promotion = json.loads(outputs[PUBLIC_PROMOTION_OUTPUT].decode("ascii"))
    promotion["guards"]["private_evidence_sha256"] = BASE.sha256_bytes(
        outputs[PRIVATE_EVIDENCE_OUTPUT]
    )
    promotion["guards"].pop("payload_without_guard_sha256")
    promotion["guards"]["payload_without_guard_sha256"] = BASE.canonical_sha256(
        promotion
    )
    BASE.assert_source_free(promotion)
    outputs[PUBLIC_PROMOTION_OUTPUT] = BASE.serialized_json(promotion)
    return outputs


BASE_WRAPPER.configure_base = configure_base
BASE_WRAPPER.validate_site_call = validate_site_call
BASE_WRAPPER.transform_outputs = transform_outputs
BASE_WRAPPER.BASE_WRAPPER.configure_base = configure_base
BASE_WRAPPER.BASE_WRAPPER.validate_site_call = validate_site_call
BASE_WRAPPER.BASE_WRAPPER.transform_outputs = transform_outputs
BASE_WRAPPER.INNER_WRAPPER.configure_base = configure_base
BASE_WRAPPER.INNER_WRAPPER.validate_site_call = validate_site_call
BASE_WRAPPER.INNER_WRAPPER.transform_outputs = transform_outputs


def build_outputs() -> dict[Path, bytes]:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector1126 closure base drifted",
    )
    return BASE_WRAPPER.BASE_WRAPPER.build_outputs()


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
                f"selector142 closure output drifted: {path}",
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
