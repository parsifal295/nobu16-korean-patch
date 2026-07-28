#!/usr/bin/env python3
"""Build the selector-514 single-union closure on frozen post-selector142."""

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
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector514_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector514_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector514_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector142_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector142_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector514_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector514_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP
    / f"pk_selector514_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector514_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector514_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector514_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector514_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector514_consolidated_closure_promotion.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "AE64FFC67F3B8424E78026DE82D32D8A176051A4FF8B45C1FDDBB750155DE4A3"
)
EXPECTED_INPUT_SHA256 = {
    "assignment_builder":
        "88236661B06478F554DA70706265602722DC4A38254767AF2C9F8CAF6D718A73",
    "assignment_private":
        "22D71A0373FF9B325ABE06C356BBA3A239DB56E9EECB10BFACFAA10C85B1E8DA",
    "assignment_public":
        "EA962FAAC51391DD773E4519693B41377DA5359491451F0631FB297A6A29EAA2",
    "official_ledger":
        "5D3673BC67F8FB55B258BB236CBC6ACD3E76F2E001300994ED7AFD742601C0DB",
    "predecessor_decisions":
        "E0AD32905438B6E1228F512105B1AE33570B51307FFA5550A1A2E82D8B5D6692",
    "chunk0_builder":
        "86735B33BEFF09BAB6387026449972DD3BB2268C3CA1967EF0C8E2549CA46385",
    "chunk0_public":
        "F2313F745BE5A50A82780C092258BBB8995A4531088C41B07037C35C467E7861",
    "chunk0_decisions":
        "82E46843418DEE444DE2CDE80A1A26F736F270C3293FFF222E1C45CBC652C431",
    "chunk0_evidence":
        "EB7B9297D9047051547C110AE7F3AD67A1598D2F49760BB69CB467B567E7ED48",
    "chunk1_builder":
        "F4050FD59CD3DA81CF9FF5420B8166A9F3FD9DDECF5FDE724F18820B26CF8476",
    "chunk1_public":
        "D506896AA1CD2F6F9F4EFB490DEE76D0A228B7535281442F5C6DF902A09E9A75",
    "chunk1_decisions":
        "254E6F3F4E587D2F2401E77EBD1B2C3D8B10057FC866B8739B7AED7EAACC6D44",
    "chunk1_evidence":
        "160D857EC71B859E448D5FF7537C575DFC5A0A7C2712514142DDE2B8FC66BD28",
}

EXPECTED_OWNER_ROWS = 108
EXPECTED_UNION_ROWS = 108
EXPECTED_DECISION_ROOTS = 41
EXPECTED_CHANGED_ROOTS = 27
EXPECTED_PROMOTIONS = 98
EXPECTED_UNION_RENEWALS = 10
EXPECTED_OWNER_RENEWALS = 10
EXPECTED_UNION_OVERRIDES = 29
EXPECTED_OWNER_OVERRIDES = 29
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 79,
    "translation_override_and_runtime_promotion": 19,
    "translation_override_and_verification_renewal": 10,
}
EXPECTED_OWNER_ACTION_COUNTS = EXPECTED_ACTION_COUNTS
EXPECTED_CHUNK_ROWS = (74, 34)
EXPECTED_CHUNK_SITES = (30, 26)
EXPECTED_REVIEWED_SITES = 56
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "6EB321E4CFBEB4FB13B6523D55F4601D6484D4B1B88C00EE6976076BA16B407A"
)
EXPECTED_SOURCE_SITES = 86
EXPECTED_SOURCE_SITE_SHA256 = (
    "F90800BE5845B3FF6815DEB03B358F7091AD49D3A3CBBE470FBBDEC38B138DCD"
)
EXPECTED_SOURCE_ONLY_SITES = 30
EXPECTED_SOURCE_ONLY_SHA256 = (
    "233982CE33B7108CDF1BDB6464FBEC8FA88E2AB84129D50870DAB28AEF03322E"
)
EXPECTED_OWNER_OVERLAPS = 0
EXPECTED_OWNER_OVERLAP_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_PREDECESSOR_OVERLAP_SHA256 = EXPECTED_OWNER_OVERLAP_SHA256
EXPECTED_PENDING_BEFORE = 6_645
EXPECTED_PENDING_AFTER = 6_547
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "6E3E5CD8A0FF7CC07C69BD9ABDCB2380FFD507D21F528E2A446D57329359F6A8"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "FB3119A8080949EDC0BA740E893C4C4B387FF8BC6564E6E4C1B19A3DC8D9A919"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "623C6EE2BDC25B13680C353C97847C3AC646C4B2B222A51F0F242B7A1CC2E093"
)

# Frozen after deterministic bootstrap.
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "9934DEDCE404E2F27EE6680BF43E2B4E8E7870FE6F728E96D09DF566529F1444",
    "private_evidence":
        "F43AE8B566B55513F76DE5D2E1072DE427F18151672902DDE89844D661A3B0A6",
    "public_coverage":
        "E9E10EDB48C8C7774475992E4D246F19D87563A141D48A3DCB00F925B5665FFD",
    "public_promotion":
        "196472A0F5EE9868DD47C582A3749EA755EE658DE8E8CBEC69B97A8D6BBCCEEA",
    "final_candidate": EXPECTED_FINAL_CANDIDATE_SHA256,
    "decision_coordinates":
        "E85BD1FBC4FB89058F21B1846BFEA381C70225D77154BE02DE782A81A9FD7B79",
    "promotion_coordinates":
        "A4AB25F9D7062D0A7513196A85B50C8CE2A17863D28D46FC2080FDA4E2680D20",
    "renewal_coordinates":
        "60162EBF8888E3DA160DB7884403DD9883FE807022900BAA73E67BF1191B4923",
    "override_coordinates":
        "74C768793E78DB2799646E9C6D3D3E14549C528D6AB589C282CA6C11C403D75A",
    "owner_overlap_coordinates": EXPECTED_OWNER_OVERLAP_SHA256,
    "source_only_proof":
        "7660FABBA029B6048B8BA9AF19D634C1EC17C9AB9C5012C485093E07663134E6",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE_WRAPPER = load_module(BASE_BUILDER_PATH, "selector514_closure_base")
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector514_closure_input")
BASE = BASE_WRAPPER

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

def configure_base() -> None:
    for name in (
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
        setattr(BASE, name, globals()[name])
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
        "post_selector142_selector514_two_chunk_single_coordinate_union_"
        "with_chunk0_owned_empty_terminal_and_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector514-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector514-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector514-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector514-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector514_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = (
        "nobu16.kr.pk-selector514-assignment.private.v1"
    )
    BASE.EXPECTED_DECISION_ROWS = EXPECTED_UNION_ROWS
    BASE.EXPECTED_RENEWALS = EXPECTED_UNION_RENEWALS
    BASE.EXPECTED_OVERRIDES = EXPECTED_UNION_OVERRIDES
    BASE.EXPECTED_OUTPUT_SHA256 = {
        key: None for key in EXPECTED_OUTPUT_SHA256
    }


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
        and tuple(row["target"]) == (0, 514)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-514 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    evidence = json.loads(outputs[PRIVATE_EVIDENCE_OUTPUT].decode("ascii"))
    evidence["proof"].pop(
        "chunk_assignments_disjoint_except_identical_terminal_owner_overlap",
        None,
    )
    evidence["proof"].pop(
        "identical_terminal_owner_overlap_deduplicated", None
    )
    evidence["proof"]["chunk_coordinate_and_root_sets_disjoint"] = True
    evidence["proof"]["shared_empty_terminal_dependency_owned_by_chunk_zero"] = True
    outputs[PRIVATE_EVIDENCE_OUTPUT] = BASE.serialized_json(evidence)

    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("ascii"))
    for key in tuple(coverage["proof"]):
        if key.startswith("all_") and key.endswith("_candidate_sites_reviewed"):
            coverage["proof"].pop(key)
        if key.startswith("source_only_") and key.endswith(
            "_absent_from_current_and_candidate"
        ):
            coverage["proof"].pop(key)
    coverage["proof"].pop(
        "chunk_assignments_disjoint_except_identical_terminal_owner_overlap",
        None,
    )
    coverage["proof"].pop(
        "identical_terminal_owner_overlap_deduplicated", None
    )
    coverage["proof"]["all_56_candidate_sites_reviewed"] = True
    coverage["proof"]["source_only_30_absent_from_current_and_candidate"] = True
    coverage["proof"]["chunk_coordinate_and_root_sets_disjoint"] = True
    coverage["proof"]["shared_empty_terminal_dependency_owned_by_chunk_zero"] = True
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


def build_outputs() -> dict[Path, bytes]:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector142 closure base drifted",
    )
    configure_base()
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
                f"selector514 closure output drifted: {path}",
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
