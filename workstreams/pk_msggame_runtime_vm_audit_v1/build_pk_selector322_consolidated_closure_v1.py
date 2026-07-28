#!/usr/bin/env python3
"""Build the selector-322 two-chunk closure on frozen post-selector742 state."""

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
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector322_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector322_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector322_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector742_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector742_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector322_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector322_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector322_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector322_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector322_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector322_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector322_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector322_consolidated_closure_promotion.v1.json"
)

# Chunk hashes and union results remain deliberately unfrozen until both bounded
# reviewers finish. Known predecessor and assignment inputs are already sealed.
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "6DD14D61DFF734FA574CB174E97F89BD24AB69412CDD8B5FE5931E1BFEC7BB86",
    "assignment_private":
        "0FE780C5A37609CF062AA210212A1CB745D6938E5DA28BA9725AFD3C8DF2D97F",
    "assignment_public":
        "6A6034DC2A4485F254931AA81DEF408FBBEC805C58175B6A1FADB724EA02F364",
    "official_ledger":
        "4AC2CD8969958AA254D0F70F7302E1BC3D273229DBB59A0512FEB27E1786D90B",
    "predecessor_decisions":
        "F0EBDA5FC1154F9568CD802D1AA65BAD4FED0A082A41CC8E20959C3A9C263881",
    "chunk0_builder":
        "13B0E229DE5F315723CEB29E645D01F8B984E463AE4C2E2EC4B97D764C4229A6",
    "chunk0_public":
        "2E4DE94F1A1F228E6EFDF52982EBE25CCCA52E6CAD769724BE9469A4FA538B7A",
    "chunk0_decisions":
        "13AF9393F5DFC0935FA3A9FD8A495ED422DF2A5763A1A2B4509CA99BC44C6721",
    "chunk0_evidence":
        "F6AAE4BA45FE2C5EA7ED674A0D7BBB27DB5205831F5742DB2AB938451DD5BF62",
    "chunk1_builder":
        "27F993FB5F06E314327DCBDEAF1C0EB2390CD456DDDDEBE7CEB7DA822FCEEC08",
    "chunk1_public":
        "D31D0529EDE28566CE2D8D435FA264516FA0D299B753D006CE71F2E8DF9C2269",
    "chunk1_decisions":
        "393BD642B4DD5FBC881461047A33F4510429854F2327E704FCB971B5895502A0",
    "chunk1_evidence":
        "2FFA605B5FFAC27AE78FA8AB7CF49FAFDA3DAFF98182575845C949672851E8B3",
}

EXPECTED_CHUNK_ROWS = (17, 11)
EXPECTED_CHUNK_SITES = (42, 43)
EXPECTED_DECISION_ROWS = 28
EXPECTED_DECISION_ROOTS = 13
EXPECTED_PROMOTIONS = 25
EXPECTED_RENEWALS = 3
EXPECTED_OVERRIDES = 12
EXPECTED_ACTION_COUNTS: dict[str, int] = {
    "runtime_promotion": 16,
    "translation_override_and_runtime_promotion": 9,
    "translation_override_and_verification_renewal": 3,
}
EXPECTED_PENDING_BEFORE = 6_335
EXPECTED_PENDING_AFTER = 6_310
EXPECTED_REVIEWED_SITES = 85
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "E2E30CDE0A542E9265C4FAB36BE0C2701B74D84EF588EE52A8DA2CE5E3A3177F"
)
EXPECTED_SOURCE_SITES = 94
EXPECTED_SOURCE_SITE_SHA256 = (
    "D516F208DEA77BA8148385870722FF41092B1C2D4AC6EAF533CC3DE6B8D28595"
)
EXPECTED_SOURCE_ONLY_SITES = 9
EXPECTED_SOURCE_ONLY_SHA256 = (
    "93CE5ED3ED53ACF06FEDA71F84A2F24F86A4E419112BC68AFD5D37E80264EC7A"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "BCA693F86DEE850F95996243CB5FFA3DBA56A4F58750800FFE8253F9FC2ACFBB"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "D9A52A500BD6E60D3B35574E1890BFC128151A9328A5CAE8B1C4CFBEAB087E9B"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "F7992DD09D0955EC49B2CFD4419D1B53F29857E58510F4382C0514DEA83AF80B",
    "private_evidence":
        "9642374CCA6ECEC2D478AFD8970A6106F576431C44705E095FAE1D8F04E4883F",
    "public_coverage":
        "2DE91D13ECE1E9AA8C47FE79C3BBBA9C1653131C9F56E1A517B86A8315F1885E",
    "public_promotion":
        "4F2DBE92BE6ADBA9EFA80A0A00A7C12E165EE61A1C31616E369FCBACC2EE1930",
    "final_candidate":
        "D0739EBB2E00B9034071165D00CA0D5E08D5F30A6400C8FF38CDA2867BA0203E",
    "decision_coordinates":
        "1169E96A368BD9E0362D4370CE828D65140ECB0189B99F2B667D771EE89282EB",
    "promotion_coordinates":
        "5F971848A7D1BB9D1197BA0D1C13B71F01F02D023E27EC5CAD8E88150C073AED",
    "renewal_coordinates":
        "BF7195E809B3E53F4E18E35CF7C9D282CC2D242E03AC8D803ACAEDD034549701",
    "override_coordinates":
        "39AC2461307157E7B837CC457B33B00BDA7FF54C8638BD945807E46F86008B51",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "B3502277F407BB7ACFBC694363F643DD169A1BAE8B21779274E9558075329E6C",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


WRAPPER = load_module(BASE_WRAPPER_PATH, "selector322_closure_base_wrapper")
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector322_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = WRAPPER.configure_base


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.METHOD = (
        "post_selector742_selector322_two_chunk_single_coordinate_union_"
        "with_targeted_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector322-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector322-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector322-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector322-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector322_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = "nobu16.kr.pk-selector322-assignment.private.v1"


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
        and tuple(row["target"]) == (0, 322)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-322 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("utf-8"))
    proof = coverage["proof"]
    proof.pop("all_230_candidate_sites_reviewed", None)
    proof.pop("source_only_13_absent_from_current_and_candidate", None)
    proof["all_85_candidate_sites_reviewed"] = True
    proof["confirmed_non_display_rows_untouched"] = True
    proof["seven_terminal_records_unchanged"] = True
    proof["source_only_9_absent_from_current_and_candidate"] = True
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
    confirmed = {
        (str(row["resource"]), str(row["coordinate"]))
        for row in official
        if row.get("scope_classification") == "confirmed_non_display"
    }
    decision_keys = {
        (str(row["resource"]), str(row["coordinate"])) for row in decisions
    }
    terminal_roots = {(0, record_id) for record_id in range(1650, 1657)}
    decision_roots = {
        tuple(map(int, coordinate.split(":")[:2]))
        for _resource, coordinate in decision_keys
    }
    BASE.require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed,
        "selector322 touched the confirmed-non-display universe",
    )
    BASE.require(
        not decision_roots & terminal_roots,
        "selector322 decision union changed one of its seven terminals",
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
        "selector322 chunk inputs are not frozen yet",
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
        "selector322 exact union constants are not frozen yet",
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
                f"selector322 closure output drifted: {path}",
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
