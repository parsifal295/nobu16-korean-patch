#!/usr/bin/env python3
"""Build the selector-376 two-chunk closure on frozen post-selector1162 state."""

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
    WORKSTREAM / "build_pk_selector1090_consolidated_closure_v1.py"
)
EXPECTED_BASE_WRAPPER_SHA256 = (
    "46449314582CFBEFCBCB4BA00EB7B36C83056B8EA0F223E26795350B6A1EDDAE"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector376_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector376_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector376_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1162_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector1162_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector376_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector376_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector376_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector376_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector376_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector376_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector376_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector376_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "0E5776587F048804617A39D53BB1F9F675E73563E92F698AE1585292EEE6F759",
    "assignment_private":
        "B91E0CAA8134AB1B7868B79BA93C739BAF76D8EDB478A6F1E81DD254BA4D1858",
    "assignment_public":
        "046738E8E977A7929A5171136120F8C0AEFE4B61B3E7AC56ED5BA850018D6F0C",
    "official_ledger":
        "A3A5433CCDD5F085AF61BEDB0409B5A02C7CAD162AD4ADE5938B356C988065B4",
    "predecessor_decisions":
        "61E3E983D040461169FC989BB9F54BA67E4031CCF0CF49A411B0FB41CFC8BD37",
    "chunk0_builder":
        "ED5472824E4A0B50FFEFB5BC6B6371E4CC99C72AE4CA9C1974637B41D25F7E73",
    "chunk0_public":
        "B7BBB2D16EBF75D831911F63D0F6C6DE52759AF20F41EE62449B99FC9A65915C",
    "chunk0_decisions":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "chunk0_evidence":
        "3FB3E8D860F530ACE232E3C1A55EA53FA7F46668FBFC7F44A50F9C4F40B890C0",
    "chunk1_builder":
        "40AC5B0E0ABB75F4AA02EAEEE4F1A1D22DA6D9FFDAF15B44E33C50960BB27250",
    "chunk1_public":
        "D107D1D309AE5A3F431DB9DB1A0BC85AC94272465C8DCF18A63B418322B101C1",
    "chunk1_decisions":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "chunk1_evidence":
        "62DC532D4C8CE8764CBF2D0F59DC57F9572697B90657E56C7AD6BE550056E2E2",
}

EXPECTED_CHUNK_ROWS = (0, 0)
EXPECTED_CHUNK_SITES = (19, 22)
EXPECTED_DECISION_ROWS = 0
EXPECTED_DECISION_ROOTS = 0
EXPECTED_PROMOTIONS = 0
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 0
EXPECTED_ACTION_COUNTS: dict[str, int] = {}
EXPECTED_PENDING_BEFORE = 6_307
EXPECTED_PENDING_AFTER = 6_307
EXPECTED_REVIEWED_SITES = 41
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "43B47600DC51A2FF26AB908ACCE2197068C19D6468858BBA308CCA38AC4CA59D"
)
EXPECTED_SOURCE_SITES = 48
EXPECTED_SOURCE_SITE_SHA256 = (
    "D4DE4C95EC1EA1B0AC45A4EEAFAAE5F824CB5EBC0B59E6A8B670EEBBCB8E521F"
)
EXPECTED_SOURCE_ONLY_SITES = 7
EXPECTED_SOURCE_ONLY_SHA256 = (
    "6CF0F59F2443FDAA18AB50E854277387281173EE32389A56FEF10958230D677A"
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
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "private_evidence":
        "76657FB7BCBC2A145D0E2FDBA7C328A5DFB1FDAD05F568FF80C23E2DB888F090",
    "public_coverage":
        "AB0E17C741B5E36F5629A8921223A1A72600FB28BB0F9D23FF8A8A7A12E6D01B",
    "public_promotion":
        "D07D5543EC070AD62E3464D8CA3C4688EF0ACD06219CBB6C7D2FAE00D6AA835A",
    "final_candidate":
        "94FE58C283D696DA36E0F6ADB8339713A0211163EDCD6FD0A92EB5110AE613D2",
    "decision_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "promotion_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "ED7E96A0929E2659C356E4264B1BFBAA9584A5B0938028349369CA54EDA1BCC0",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


WRAPPER = load_module(BASE_WRAPPER_PATH, "selector376_closure_base_wrapper")
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector376_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = WRAPPER.configure_base


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.METHOD = (
        "post_selector1162_selector376_two_chunk_single_coordinate_union_"
        "with_targeted_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector376-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector376-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector376-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector376-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector376_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = "nobu16.kr.pk-selector376-assignment.private.v1"


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
        and tuple(row["target"]) == (0, 376)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-376 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("utf-8"))
    proof = coverage["proof"]
    proof.pop("all_230_candidate_sites_reviewed", None)
    proof.pop("source_only_13_absent_from_current_and_candidate", None)
    proof["all_41_candidate_sites_reviewed"] = True
    proof["confirmed_non_display_rows_untouched"] = True
    proof["seven_terminal_records_unchanged"] = True
    proof["source_only_7_absent_from_current_and_candidate"] = True
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
    terminal_roots = {(0, record_id) for record_id in range(1713, 1720)}
    decision_roots = {
        tuple(map(int, coordinate.split(":")[:2]))
        for _resource, coordinate in decision_keys
    }
    BASE.require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed,
        "selector376 touched the confirmed-non-display universe",
    )
    BASE.require(
        not decision_roots & terminal_roots,
        "selector376 decision union changed one of its seven terminals",
    )
    BASE.require(
        all(
            row.get("fresh_semantic_review") == "approved"
            and row.get("runtime_review") == "verified"
            for row in decisions
        ),
        "selector376 closure decisions lack fresh exact review",
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
        "selector376 chunk decisions lack exact predecessor-state review",
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
        "selector1090 closure wrapper drifted",
    )
    BASE.require(
        all(value is not None for value in EXPECTED_INPUT_SHA256.values()),
        "selector376 chunk inputs are not frozen yet",
    )
    BASE.require(
        all(value >= 0 for value in EXPECTED_CHUNK_ROWS)
        and EXPECTED_DECISION_ROWS >= 0
        and EXPECTED_DECISION_ROOTS >= 0
        and EXPECTED_PROMOTIONS >= 0
        and EXPECTED_RENEWALS >= 0
        and EXPECTED_OVERRIDES >= 0
        and EXPECTED_PENDING_AFTER >= 0
        and EXPECTED_PREDECESSOR_OVERLAPS >= 0
        and EXPECTED_PREDECESSOR_SUPERSESSIONS >= 0,
        "selector376 exact union constants are not frozen yet",
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
                f"selector376 closure output drifted: {path}",
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
