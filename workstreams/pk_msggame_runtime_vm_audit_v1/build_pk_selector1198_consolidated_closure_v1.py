#!/usr/bin/env python3
"""Build the selector-1198 two-chunk closure on frozen post-selector628."""

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

BASE_BUILDER_PATH = WORKSTREAM / "build_pk_selector514_consolidated_closure_core_v1.py"
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector1198_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector1198_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector1198_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector628_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector628_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector1198_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector1198_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector1198_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector1198_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector1198_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector1198_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector1198_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector1198_consolidated_closure_promotion.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "AE64FFC67F3B8424E78026DE82D32D8A176051A4FF8B45C1FDDBB750155DE4A3"
)
EXPECTED_INPUT_SHA256 = {
    "assignment_builder":
        "698AAEB85B9036ABBD4171E41E533EC9A2EDDCF511D9755BF0DD1BF7E60CB0EB",
    "assignment_private":
        "5EE8DB27C71CFA014DBD4EEF454E69A02FF10B0D1EFD82F14E91CEF487CC090A",
    "assignment_public":
        "A20F3757EC0EDC48BC68CD60A844F38E42873D244A2B858DEF3B93679F901A3A",
    "official_ledger":
        "64F57157C47A72E42CBDBDA59C84AA142519CAAF7D4391983CEFD34362640147",
    "predecessor_decisions":
        "009C9D4B7DCE6CE0E7F07D21F827FB4633DF3C01A3BA6D097AC19F04E0CBE2C4",
    "chunk0_builder":
        "197B718A90AF8B7EA1D90E0BA9B4EE8AE625A0588809E07532738B338D1616FA",
    "chunk0_public":
        "793ACC7D31442340BFFDAD8BC6C2D1A3B184C619AC6B0FFA85739289A35F8E36",
    "chunk0_decisions":
        "B12CB46EE9175B2EF889F471B063B5C1235FE02FFE17132F6F756671CBB34E83",
    "chunk0_evidence":
        "84A845EC897B23E09BFB5C55052D8D53D618A36459E304C7C40826177A387862",
    "chunk1_builder":
        "4500E3528C37967014D8992FA86F46DB45806E7C52CD32864EA9EF96B7AA4FA8",
    "chunk1_public":
        "EEC95385EFC742956B08630B0B82FCE8238D9FB90EB99052DA50BAE3F44FEC31",
    "chunk1_decisions":
        "4CD586C905B7D45A03E51B9AA7C99F0C62D9480CEE9DFB3757B2D6F13A014602",
    "chunk1_evidence":
        "B2B7CC75AB60AC917900F716ACBBD9D58C07FE321ECCD13333180FCFC244A89B",
}

EXPECTED_DECISION_ROWS = 27
EXPECTED_DECISION_ROOTS = 11
EXPECTED_PROMOTIONS = 25
EXPECTED_RENEWALS = 2
EXPECTED_OVERRIDES = 6
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 21,
    "translation_override_and_runtime_promotion": 4,
    "translation_override_and_verification_renewal": 2,
}
EXPECTED_CHUNK_ROWS = (8, 19)
EXPECTED_CHUNK_SITES = (23, 23)
EXPECTED_REVIEWED_SITES = 46
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "5D1E5253A7B6CC4683BE71F4A17DDACAB1E6C57715E47859127FA327B888C811"
)
EXPECTED_SOURCE_SITES = 46
EXPECTED_SOURCE_SITE_SHA256 = EXPECTED_CANDIDATE_SITE_SHA256
EXPECTED_SOURCE_ONLY_SITES = 0
EXPECTED_SOURCE_ONLY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_PENDING_BEFORE = 6_489
EXPECTED_PENDING_AFTER = 6_464
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "28267B6928CBDBF3E98FBB8E13A4733947A4EAC6A2BF04812A848C1091F9B186"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "D75600A25C086D41190589DA21C8B389ACD9A9BAD561B920F9BB25F5FB9E5B88"
)

EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "933552574FBFC2322CC17DD35ED106BF24326A006EB85F057E4136C720B6E1B4",
    "private_evidence":
        "BCFA331FDED65EBCACBCC3906D9454A5FB7307DEE5015F2ABB910FF4EFF8D262",
    "public_coverage":
        "EDDE1CBEA959714C9F16B88CB23E442CC5529BE31CF3ED70F806D3361DDA7A01",
    "public_promotion":
        "3F90F0BB36FAAA06162FD805E0BC6DFEF20676F22D395579106964828212067E",
    "final_candidate":
        "74E30E798B82129565518FA04F35DC73220974CFC6E1E7E61BCEC2D8008671DA",
    "decision_coordinates":
        "FE9A7E842B974AC8669153DFAF33657EB79EAC55618C4D79F8ECFF9BB770B1BE",
    "promotion_coordinates":
        "490D8B91BEABD960A6D9DDAB59CD982243779F011B6EF63FB227AFB171D8979C",
    "renewal_coordinates":
        "F908D488BC94E36E6FD0BCC1FA3342744CFC61307404C8B124B9BFD9E1ACCE6B",
    "override_coordinates":
        "62A0D9D5CC458EA5DA8653C87D6886C86C5C1ABE87FF113142B97705C3631E57",
    "predecessor_overlap_coordinates": EXPECTED_SOURCE_ONLY_SHA256,
    "predecessor_supersession_coordinates": EXPECTED_SOURCE_ONLY_SHA256,
    "source_only_proof":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_BUILDER_PATH, "selector1198_closure_base")
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector1198_closure_input")


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
            key: (
                None
                if key in {"public_coverage", "public_promotion"}
                else value
            )
            for key, value in EXPECTED_OUTPUT_SHA256.items()
        },
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.METHOD = (
        "post_selector628_selector1198_two_chunk_single_coordinate_union_"
        "with_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector1198-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector1198-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector1198-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector1198-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector1198_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = "nobu16.kr.pk-selector1198-assignment.private.v1"


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
        and tuple(row["target"]) == (0, 1198)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-1198 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("ascii"))
    proof = coverage["proof"]
    proof.pop("all_230_candidate_sites_reviewed", None)
    proof.pop("source_only_13_absent_from_current_and_candidate", None)
    proof["all_46_candidate_sites_reviewed"] = True
    proof["source_only_sites_empty"] = True
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
                f"selector1198 closure output drifted: {path}",
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
