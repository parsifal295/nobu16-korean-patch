#!/usr/bin/env python3
"""Build the selector-1126 single-union closure on frozen post-selector748."""

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

BASE_BUILDER_PATH = WORKSTREAM / "build_pk_selector748_consolidated_closure_v1.py"
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector1126_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector1126_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector1126_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector748_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector748_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector1126_chunk{chunk}_review_v1.py"
    for chunk in range(3)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector1126_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(3)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP
    / f"pk_selector1126_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(3)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector1126_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(3)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector1126_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector1126_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector1126_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector1126_consolidated_closure_promotion.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "FCFFA6BC40D3B39E1FFE6B07ADF407CA3B45F712BE44E865DA51CD8D7C0A7EE9"
)
EXPECTED_INPUT_SHA256 = {
    "assignment_builder":
        "9EFDF4FD9CD8330A97AC59E44B4364F9EE965549FEC24F65C5AA79295EDA6ACE",
    "assignment_private":
        "6E5CC3EB27553DC7ECA4AF5095D3F7AB5FAEDBBC5D260A33D635F8E8F407BEE2",
    "assignment_public":
        "83B6F9CA80DF3400ABEAC5DF6BE8E2335FF97A8F407FAE0854A14BCD70C7BFA3",
    "official_ledger":
        "05D9C79515E8B161CD469FFEC5C340F54BE9BB94BFBA8F725B8DFC025DE49E76",
    "predecessor_decisions":
        "35D4A9DF18F3BFC14866B5EEE52606D5BCF41282D0E400AD2B11284FD3C407AE",
    "chunk0_builder":
        "A2AD9CB32F99B6E66330678F3CE39296C5CB5FF107EF37EDC52FEE34EC419901",
    "chunk0_public":
        "A231BA9BD105695A9F3413A65BEAA3CE3D1615504BB930D84282B90BEA2D4540",
    "chunk0_decisions":
        "75DE26F6C85557CAD3E261E0ACB494F65CCCCB1F986EC4D5531DA946F2FE1B6D",
    "chunk0_evidence":
        "9A3B80F100666B7DA115059E3D1D508220825E48966B6AFAD7D9C455A91DBCA8",
    "chunk1_builder":
        "EBA450D280E9B0CFAAC64040704E51C7BB59D6B1DAF00325261BEB19A43BD807",
    "chunk1_public":
        "9523656C069465E2CFCBBAB349C62B3012FEC7F54416D33D0384C07196FD1479",
    "chunk1_decisions":
        "EE1AD1847FE6D1EF02F907169BF08562699AEA500074011BEEB0C060EBEA590C",
    "chunk1_evidence":
        "B4CE98AE51099EAF185D21999C3979D3902130A632EC31D6E865D0202E2BDF62",
    "chunk2_builder":
        "97090BEAF67D77836523E2D85FFD3A48C7A8CCED9F20DBAF29F90CCA26476AE7",
    "chunk2_public":
        "2378BE997B9FE2FBCA44DF21014BFD12FDDFE0E5FE73BB5154581E4E6DDC8CE3",
    "chunk2_decisions":
        "63D1151625C2F6E050173FF9AC6F11545E1E6DB5D06BEE53FC5D0B3A17403A9F",
    "chunk2_evidence":
        "8A99A6A6F73269848EF3E8A5AE20EBC31EB34EB802A3961D667877943BE64F10",
}

EXPECTED_OWNER_ROWS = 185
EXPECTED_UNION_ROWS = 185
EXPECTED_DECISION_ROOTS = 99
EXPECTED_CHANGED_ROOTS = 99
EXPECTED_PROMOTIONS = 118
EXPECTED_UNION_RENEWALS = 67
EXPECTED_OWNER_RENEWALS = 67
EXPECTED_UNION_OVERRIDES = 140
EXPECTED_OWNER_OVERRIDES = 140
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 45,
    "translation_override_and_runtime_promotion": 73,
    "translation_override_and_verification_renewal": 67,
}
EXPECTED_OWNER_ACTION_COUNTS = EXPECTED_ACTION_COUNTS
EXPECTED_CHUNK_ROWS = (65, 49, 71)
EXPECTED_CHUNK_SITES = (38, 38, 38)
EXPECTED_REVIEWED_SITES = 114
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "4142609E7659D9E077D2648303DE0DC6D0C6717F4A0E22288263614B712D66BA"
)
EXPECTED_SOURCE_SITES = 128
EXPECTED_SOURCE_SITE_SHA256 = (
    "65002AF3AE667557EA1124AC499FD3F2066882C75CB5BC09BF5E8640190B530C"
)
EXPECTED_SOURCE_ONLY_SITES = 14
EXPECTED_SOURCE_ONLY_SHA256 = (
    "8F97365A616918DA6E91CF4EB45A8DE4830305555832F7ED645517370DEFAAD8"
)
EXPECTED_OWNER_OVERLAPS = 0
EXPECTED_OWNER_OVERLAP_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_PREDECESSOR_OVERLAPS = 1
EXPECTED_PREDECESSOR_SUPERSESSIONS = 1
EXPECTED_PREDECESSOR_OVERLAP_SHA256 = (
    "0FC3025F49AFF0789836D81B1B6404FBF72C3F99196B58E7040B3F92F0A5B67F"
)
EXPECTED_PENDING_BEFORE = 6_879
EXPECTED_PENDING_AFTER = 6_761
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "903B515128E94FE263430FAF7EECC51759A0DD132211F3C3047E5DAA6D16D9A6"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "882781E1F51D963610A492589C19B6FAE09B33BA533D1369C26E9864AA48BAA7"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "B25D15DB919FC4E3CF3A68E7C10938F581C233F04DA111F1C8D0ECA0A3F86D62"
)

# Frozen after deterministic bootstrap.
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "E7FE1D70A6DF175C25D3D4D42359983E26075F1962B8F0EB6BD52DC82376EB15",
    "private_evidence":
        "88F6E0E0115D026359545301B5FD0B65F7D5D34AA2A07B79B2AF24E9956F2CDF",
    "public_coverage":
        "830B0F2EE480EA11AD6FAACE5A18522B56E314A8A673CEC766FA63E6A67A1F81",
    "public_promotion":
        "407906D270337DAFD38DB94A2192B171AA04F0ACE8D9EFEF5425AAEF0C4909F0",
    "final_candidate": EXPECTED_FINAL_CANDIDATE_SHA256,
    "decision_coordinates":
        "0BBBC43125AC65FD7F7EF9A78BA3AB6ACC0D91283F729AA721C0608607578208",
    "promotion_coordinates":
        "AC668CFB8B8220593DA743BFD7547060C0503D118D5A08CDF4085977E8C86C04",
    "renewal_coordinates":
        "B3ECFED0C1DE975316A6B9F400AA3ECEAABB3B19AFE846FB96B95855CA3C7588",
    "override_coordinates":
        "760418C7AFCD2CC5B12A542D5DC35B2A4C528E4CDA329C7C804284A0C4F9957C",
    "owner_overlap_coordinates": EXPECTED_OWNER_OVERLAP_SHA256,
    "source_only_proof":
        "8B82031E3BB66F8428C087E818DDB63E075107EC045D265154EF6D4FA56F84D2",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE_WRAPPER = load_module(BASE_BUILDER_PATH, "selector1126_closure_base")
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector1126_closure_input")
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
INNER_WRAPPER = BASE_WRAPPER.BASE_WRAPPER
for _name in (
    "ASSIGNMENT",
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
    setattr(INNER_WRAPPER, _name, globals()[_name])

ORIGINAL_CONFIGURE_BASE = BASE_WRAPPER.configure_base
ORIGINAL_TRANSFORM_OUTPUTS = BASE_WRAPPER.transform_outputs


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.EXPECTED_OUTPUT_SHA256.update(
        {
            "final_candidate": EXPECTED_OUTPUT_SHA256["final_candidate"],
            "predecessor_overlap_coordinates":
                EXPECTED_PREDECESSOR_OVERLAP_SHA256,
            "predecessor_supersession_coordinates":
                EXPECTED_PREDECESSOR_OVERLAP_SHA256,
        }
    )
    BASE.METHOD = (
        "post_selector748_selector1126_three_chunk_single_coordinate_union_"
        "with_disjoint_owners_predecessor_supersession_and_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector1126-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector1126-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector1126-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector1126-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector1126_consolidated_update_action"


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
        and tuple(row["target"]) == (0, 1126)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-1126 site drifted: {site}")


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
    coverage["proof"]["all_114_candidate_sites_reviewed"] = True
    coverage["proof"]["source_only_14_absent_from_current_and_candidate"] = True
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
INNER_WRAPPER.configure_base = configure_base
INNER_WRAPPER.validate_site_call = validate_site_call
INNER_WRAPPER.transform_outputs = transform_outputs


def build_outputs() -> dict[Path, bytes]:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector748 closure base drifted",
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
                f"selector1126 closure output drifted: {path}",
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
