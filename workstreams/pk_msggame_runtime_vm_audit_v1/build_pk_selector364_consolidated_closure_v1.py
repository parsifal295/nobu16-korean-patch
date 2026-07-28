#!/usr/bin/env python3
"""Build the selector-364 two-chunk closure on frozen post-selector1162 state."""

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

BASE_WRAPPER_PATH = (
    WORKSTREAM / "build_pk_selector376_consolidated_closure_v1.py"
)
EXPECTED_BASE_WRAPPER_SHA256 = (
    "736C067922CE6C171E1B807C2332B8E8AB0E0E01946C41927A51DC375BB1F09C"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector364_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector364_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector364_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1162_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector1162_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector364_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector364_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector364_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector364_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector364_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector364_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector364_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector364_consolidated_closure_promotion.v1.json"
)

# Chunk hashes and union results remain deliberately unfrozen until both bounded
# reviewers finish. Known predecessor and assignment inputs are already sealed.
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "0726F36F1D0259708698AC1721943A40C119CCC0D3DCED8A87C0511497E6DFFE",
    "assignment_private":
        "48BC6BDF976BC50A0BDE822504AB6CA4014533859D8B0D51554DDD027C2B9653",
    "assignment_public":
        "485D30E2790D091064A93482915AC3DE4FCD1B9413FCD0B4198F442936CC75A3",
    "official_ledger":
        "A3A5433CCDD5F085AF61BEDB0409B5A02C7CAD162AD4ADE5938B356C988065B4",
    "predecessor_decisions":
        "61E3E983D040461169FC989BB9F54BA67E4031CCF0CF49A411B0FB41CFC8BD37",
    "chunk0_builder":
        "A377270B07C57BD3A111B0FC64026A0AB2073F129F0BA3991798FB71648E2C35",
    "chunk0_public":
        "206EADD38D09E906EC4530B2B0208683FD920F05B57C1095D5C77FC86C528F0D",
    "chunk0_decisions":
        "4FC9F47D2F80B018705D01E854EBC068047C860DAC665ED9E4EA800569DB4733",
    "chunk0_evidence":
        "B332E1F0055552000106EF28BF94A34A9FE2F8F4C8A88EE210BB3DD0385B4803",
    "chunk1_builder":
        "028A58E12553FB45E719BC4890503F8CFF846E09FA15ED5AB864041685B50AED",
    "chunk1_public":
        "090A212CB678C3F9FF053DBAE7AFCB77D179157D67E9A6C4D0670F4B28FCE5DF",
    "chunk1_decisions":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "chunk1_evidence":
        "A32273C4E84D2C614652672F3BA12657527CA32C2CC38677D5F0AC2A38297139",
}

EXPECTED_CHUNK_ROWS = (5, 0)
EXPECTED_CHUNK_SITES = (19, 19)
EXPECTED_DECISION_ROWS = 5
EXPECTED_DECISION_ROOTS = 2
EXPECTED_PROMOTIONS = 5
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 2
EXPECTED_ACTION_COUNTS: dict[str, int] = {
    "runtime_promotion": 3,
    "translation_override_and_runtime_promotion": 2,
}
EXPECTED_PENDING_BEFORE = 6_307
EXPECTED_PENDING_AFTER = 6_302
EXPECTED_REVIEWED_SITES = 38
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "79029DA92407A84927E7F696B37C325A4F42E4C866513957B73C565C6D2C9537"
)
EXPECTED_SOURCE_SITES = 42
EXPECTED_SOURCE_SITE_SHA256 = (
    "120466AB7088A679D248EA503130D45D7272858B6499D9B0E946E5653FEDB92A"
)
EXPECTED_SOURCE_ONLY_SITES = 4
EXPECTED_SOURCE_ONLY_SHA256 = (
    "D217E9475CBA2CC9055EC61AC94DF8463E3EF64B820C4A30884A045CEA43C0AF"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "94FE58C283D696DA36E0F6ADB8339713A0211163EDCD6FD0A92EB5110AE613D2"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "E063AF9F3681DA84315A4596F43EE6ED8F5FC368D4D712A96DD2B1BFEA1031D7"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "19FB86E3D7B129344B42F391F9F8B72CC6ED0D3AFE61A86031A8BFD6EC9E5106",
    "private_evidence":
        "CDA509B7225014678292D1765D0A2DFAFEB73137468E50E585AF4A44DC497689",
    "public_coverage":
        "94F76C8D8BA158A9F50608BAE9254945B27AF7520A5C43FAED0E9DAC002A0B0D",
    "public_promotion":
        "700C3DC088B607319E79510CBE103E7366D2DE7B8FE6183E2D6724776AE405EE",
    "final_candidate":
        "6F3880DF9105F47402378E89E9C1ADE9599C052CAEC6EE3D7CC795333C04C7DE",
    "decision_coordinates":
        "A0B197328C57E3882B759B9023E95764809DCFF6CD5CB8BCB38ABD5B58CE52CB",
    "promotion_coordinates":
        "A0B197328C57E3882B759B9023E95764809DCFF6CD5CB8BCB38ABD5B58CE52CB",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "127F5B99D4ACB221140A599CF2C8B7DB9161502CA0E0A725EC4B23ABF4C6E100",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "3E1C22E24277AF3025E531C5CC60A3DD484AE376DB53ED2859F939A66A276A59",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE_WRAPPER = load_module(BASE_WRAPPER_PATH, "selector364_closure_base_wrapper")
WRAPPER = BASE_WRAPPER.WRAPPER
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector364_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = BASE_WRAPPER.ORIGINAL_CONFIGURE_BASE


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.METHOD = (
        "post_selector1162_selector364_two_chunk_single_coordinate_union_"
        "with_targeted_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector364-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector364-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector364-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector364-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector364_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = "nobu16.kr.pk-selector364-assignment.private.v1"


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
        and tuple(row["target"]) == (0, 364)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-364 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("utf-8"))
    proof = coverage["proof"]
    proof.pop("all_230_candidate_sites_reviewed", None)
    proof.pop("source_only_13_absent_from_current_and_candidate", None)
    proof["all_38_candidate_sites_reviewed"] = True
    proof["confirmed_non_display_rows_untouched"] = True
    proof["seven_terminal_records_unchanged"] = True
    proof["source_only_4_absent_from_current_and_candidate"] = True
    proof["owned_overlap_rows_require_fresh_exact_review"] = True
    coverage["guards"].pop("payload_without_guard_sha256")
    coverage["guards"]["payload_without_guard_sha256"] = BASE.canonical_sha256(
        coverage
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


def validate_wrapper_invariants(outputs: Mapping[Path, bytes]) -> None:
    official = [
        json.loads(line)
        for line in OFFICIAL_LEDGER_PATH.read_text(encoding="utf-8").splitlines()
        if line
    ]
    decisions = [
        json.loads(line)
        for line in outputs[PRIVATE_DECISIONS_OUTPUT]
        .decode("utf-8", errors="strict")
        .splitlines()
        if line
    ]
    chunk_decisions = [
        json.loads(line)
        for path in CHUNK_DECISIONS
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    confirmed = {
        (str(row["resource"]), str(row["coordinate"]))
        for row in official
        if row.get("scope_classification") == "confirmed_non_display"
    }
    decision_keys = {
        (str(row["resource"]), str(row["coordinate"])) for row in decisions
    }
    terminal_roots = {(0, record_id) for record_id in range(1699, 1706)}
    decision_roots = {
        tuple(map(int, coordinate.split(":")[:2]))
        for _resource, coordinate in decision_keys
    }
    BASE.require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed,
        "selector364 touched the confirmed-non-display universe",
    )
    BASE.require(
        not decision_roots & terminal_roots,
        "selector364 decision union changed one of its seven terminals",
    )
    BASE.require(
        all(
            row.get("fresh_semantic_review") == "approved"
            and row.get("runtime_review") == "verified"
            for row in decisions
        ),
        "selector364 closure decisions lack fresh exact review",
    )
    BASE.require(
        all(
            row.get("fresh_semantic_review") == "approved"
            and row.get("runtime_review") == "verified"
            and row.get("predecessor_candidate_sha256")
            == EXPECTED_OFFICIAL_CANDIDATE_SHA256
            and "auto" not in str(row.get("action", "")).lower()
            for row in chunk_decisions
        ),
        "selector364 chunk decisions lack exact predecessor-state review",
    )


for _name, _value in {
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
    "EXPECTED_CONFIRMED_NON_DISPLAY": EXPECTED_CONFIRMED_NON_DISPLAY,
    "EXPECTED_OFFICIAL_CANDIDATE_SHA256": EXPECTED_OFFICIAL_CANDIDATE_SHA256,
    "EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256":
        EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256,
    "EXPECTED_OUTPUT_SHA256": EXPECTED_OUTPUT_SHA256,
    "configure_base": configure_base,
    "validate_site_call": validate_site_call,
    "transform_outputs": transform_outputs,
    "validate_wrapper_invariants": validate_wrapper_invariants,
}.items():
    setattr(WRAPPER, _name, _value)


def build_outputs() -> dict[Path, bytes]:
    BASE.require(
        BASE.sha256_file(BASE_WRAPPER_PATH) == EXPECTED_BASE_WRAPPER_SHA256,
        "selector376 closure wrapper drifted",
    )
    BASE.require(
        all(value is not None for value in EXPECTED_INPUT_SHA256.values()),
        "selector364 chunk inputs are not frozen yet",
    )
    BASE.require(
        all(value >= 0 for value in EXPECTED_CHUNK_ROWS)
        and EXPECTED_DECISION_ROWS >= 0
        and EXPECTED_DECISION_ROOTS >= 0
        and EXPECTED_PROMOTIONS >= 0
        and EXPECTED_RENEWALS >= 0
        and EXPECTED_OVERRIDES >= 0
        and EXPECTED_PENDING_AFTER >= 0
        and EXPECTED_PREDECESSOR_OVERLAPS == 0
        and EXPECTED_PREDECESSOR_SUPERSESSIONS == 0,
        "selector364 exact union constants are not frozen yet",
    )
    return WRAPPER.build_outputs()


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
                f"selector364 closure output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(json.dumps({
        "decision_rows": EXPECTED_DECISION_ROWS,
        "pending_after": EXPECTED_PENDING_AFTER,
        "promotions": EXPECTED_PROMOTIONS,
        "source_only_actions": 0,
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
