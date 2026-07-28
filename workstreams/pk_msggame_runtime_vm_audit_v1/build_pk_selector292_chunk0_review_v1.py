#!/usr/bin/env python3
"""Validate selector-292 chunk 0 and emit its source-free checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
PUBLIC = WORKSTREAM / "public"

ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector292_assignment_v1.py"
ASSIGNMENT_PATH = TMP / "pk_selector292_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    PUBLIC / "pk_selector292_assignment_coverage.v1.json"
)
PRIVATE_GENERATOR_PATH = (
    TMP / "build_pk_selector292_chunk0_private_review_v1.py"
)
PRIVATE_DECISIONS_PATH = (
    TMP
    / "semantic_overrides"
    / "pk_selector292_chunk0_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    TMP / "pk_selector292_chunk0_review_evidence.private.v1.json"
)
CONTEXT_MANIFEST_PATH = (
    TMP / "pk_selector292_context_inventory.private.v1.json"
)
LAYOUT_MANIFEST_PATH = (
    TMP
    / "pk_selector292_layout_manifest.selector178_chunk1_fast.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    PUBLIC / "pk_selector292_chunk0_review.source_free.v1.json"
)

SCHEMA = "nobu16.kr.pk-selector292-chunk0-review.source-free.v1"
METHOD = (
    "post_selector238_selector292_chunk0_one_root_rewrite_"
    "jp_authoritative_register_history_and_ordinary_branch_review"
)
EXPECTED_SHA256 = {
    "assignment_builder":
        "A1BC5DE2EA3E0CF06984FF97347006936407FF32B72D439B94F7598B0FD3847E",
    "assignment_private":
        "B2FD0DD7B016B20CCAB04CA903643CD158008299BBC9EF8FAA89187A5C9D6372",
    "assignment_public":
        "AAA5F7F7A503A508712AC1E0DB304F04A9152FA1E3CE30D5A53598B1AE3B06DD",
    "context_manifest":
        "2DC02C44C2698F407970BB0291E3023A597D6F9944B330E91A3C4778C621685D",
    "layout_manifest":
        "A19F3696797F141A282826D1E87DEA1D80EF11E0BB55F21EF49EF061CCE0FA99",
    "official_ledger":
        "AC10F7E71CFAD259ABBC08139BE0DB848CF5309578045532A48991F40E0035AB",
    "private_generator":
        "AC99D59020C3EB7694828C8C87A0AE6DE486AF6D120503CACE052C91FFA0F01A",
    "private_decisions":
        "C853D375FCD23CA0C2F64CF1959B1063973240E6196DFCD3A5EC5ABF109FF024",
    "private_evidence":
        "160C3EA06455FD9E9800D68B0C950679C5CF132CB9F58AC1917576ABB981C7DF",
    "official_candidate":
        "9E5C60A451DB7CCA7B046AFD8CFF199CB3665E003CB0C751120478F693D20C24",
    "reviewed_candidate":
        "89760C7C514093A28E24D75AC2E3C3065FC01C6707D84982C08C5AB1DCF9B93F",
    "live_steam":
        "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
}
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 8,
    "translation_override_and_runtime_promotion": 3,
    "translation_override_and_verification_renewal": 1,
}
EXPECTED_COUNTS = {
    "accepted_pending_roots": 3,
    "accepted_pending_rows": 11,
    "accepted_sites": 3,
    "blocked_pending_roots": 2,
    "blocked_pending_rows": 2,
    "blocked_sites": 2,
    "decision_rows": 12,
    "full_layout_recomputed_branches": 0,
    "hard_blocked_roots": 1,
    "non_display_actions": 0,
    "ordinary_attempt_branches": 28,
    "ordinary_verified_branches": 21,
    "promoted_pending_rows": 11,
    "read_only_nonpending_roots": 8,
    "read_only_nonpending_sites": 8,
    "rewrite_attempt_roots": 4,
    "roots": 13,
    "shared_override_rows": 1,
    "sites": 13,
    "source_only_actions": 0,
    "terminal_decision_rows": 0,
    "terminal_read_only_rows": 7,
    "translation_overrides": 4,
}
EXPECTED_DIGESTS = {
    "accepted":
        "A4194AFAD8D21BF331C9EB5DF5C9C1DDF4B7BFC6AD38D98FEEF1D66180A2D01D",
    "assembly":
        "6109A5ECB71DC4B8D20AE3FDD387ACA333632A651FDE0F1213FAFEAAC1CF6753",
    "blocked":
        "A4C847A386A849A75F6F71A816B2C4DB483FC37FA95DE9F907A3016A19220FA4",
    "override":
        "80A28A82FEEAA0B002594E9C876476D0453018D879EEF40609587E5254260E01",
}
EXPECTED_PUBLIC_SHA256: str | None = (
    "78A55FA3CA4FD492AED3520FF14857DCA00AE78A45ABF572DE0965F8085E269D"
)


class ReviewError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")


def serialized(value: Any) -> bytes:
    return canonical_bytes(value) + b"\n"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"object expected: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    require(all(isinstance(row, dict) for row in rows), "JSONL shape drifted")
    return rows


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 3, f"bad coordinate: {value}")
    return parts  # type: ignore[return-value]


def assert_source_free(value: Any) -> None:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            encoded,
        )
        is None,
        "public report contains CJK",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", encoded) is None,
        "public report contains coordinates",
    )


def immutable_inputs(wrapper: Any) -> None:
    paths = {
        ASSIGNMENT_BUILDER_PATH: "assignment_builder",
        ASSIGNMENT_PATH: "assignment_private",
        ASSIGNMENT_PUBLIC_PATH: "assignment_public",
        CONTEXT_MANIFEST_PATH: "context_manifest",
        LAYOUT_MANIFEST_PATH: "layout_manifest",
        wrapper.RANKING_WRAPPER.DEFAULT_LEDGER: "official_ledger",
        PRIVATE_GENERATOR_PATH: "private_generator",
        PRIVATE_DECISIONS_PATH: "private_decisions",
        PRIVATE_EVIDENCE_PATH: "private_evidence",
    }
    for path, key in paths.items():
        require(
            path.is_file() and sha256_file(path) == EXPECTED_SHA256[key],
            f"immutable input drifted: {path}",
        )


def build_report() -> dict[str, Any]:
    wrapper = load_module(
        ASSIGNMENT_BUILDER_PATH, "selector292_chunk0_review_assignment"
    )
    wrapper.configure()
    immutable_inputs(wrapper)
    private_generator = load_module(
        PRIVATE_GENERATOR_PATH, "selector292_chunk0_private_generator"
    )
    decision_bytes, evidence_bytes = private_generator.build_outputs()
    require(
        sha256_bytes(decision_bytes) == EXPECTED_SHA256["private_decisions"]
        and sha256_bytes(evidence_bytes) == EXPECTED_SHA256["private_evidence"],
        "private regeneration drifted",
    )

    assignment = load_json(ASSIGNMENT_PATH)
    evidence = load_json(PRIVATE_EVIDENCE_PATH)
    decisions = load_jsonl(PRIVATE_DECISIONS_PATH)
    chunk = assignment["chunks"][0]
    require(
        (
            chunk["site_count"],
            chunk["root_count"],
            chunk["pending_root_count"],
            chunk["pending_row_upper_bound"],
            chunk["hard_block_root_count"],
            chunk["hard_block_pending_row_count"],
            chunk["rewrite_candidate_root_count"],
            chunk["rewrite_candidate_pending_row_count"],
        )
        == (13, 13, 5, 13, 1, 1, 4, 12),
        "chunk assignment metrics drifted",
    )
    require(
        evidence["schema"]
        == "nobu16.kr.pk-selector292-chunk0-review-evidence.private.v1"
        and evidence["method"] == METHOD
        and evidence["counts"] == EXPECTED_COUNTS
        and evidence["digests"]["accepted_coordinate_sha256"]
        == EXPECTED_DIGESTS["accepted"]
        and evidence["digests"]["blocked_coordinate_sha256"]
        == EXPECTED_DIGESTS["blocked"]
        and evidence["digests"]["override_coordinate_sha256"]
        == EXPECTED_DIGESTS["override"]
        and evidence["digests"]["assembly_manifest_canonical_sha256"]
        == EXPECTED_DIGESTS["assembly"],
        "private evidence drifted",
    )
    proof = evidence["proof"]
    require(
        proof["accepted_ordinary_branches_current_relative_nonexpanding"]
        and proof["accepted_ordinary_branches_grammar_pass"]
        and proof["controls_tokens_and_linebreak_counts_preserved"]
        and proof["jp_semantic_authority"]
        and proof["maximum_rewrite_attempts_per_root"] == 1
        and not proof["full_518_branch_recompute_performed"]
        and proof["nonpending_roots_read_only"]
        and proof["terminal_records_read_only"]
        and proof["terminal_automatic_promotion_count"] == 0
        and proof["source_only_action_count"] == 0
        and not proof["steam_write_performed"],
        "private proof drifted",
    )

    branches = evidence["assembly_manifest"]
    accepted_branches = [
        row
        for row in branches
        if row["grammar_pass"] and row["current_relative_nonexpanding"]
    ]
    require(
        len(branches) == 28
        and len(accepted_branches) == 21
        and all(row["topology_pass"] for row in accepted_branches)
        and len(evidence["blocked_root_reasons"]) == 2,
        "ordinary branch proof drifted",
    )
    action_counts = Counter(str(row["action"]) for row in decisions)
    require(
        len(decisions) == 12
        and action_counts == Counter(EXPECTED_ACTION_COUNTS)
        and sum(
            row["action"] == "translation_override_and_verification_renewal"
            for row in decisions
        )
        == 1
        and all(
            row["fresh_semantic_review"] == "approved"
            and row["historical_factuality_review"] == "approved"
            and row["speaker_tone_review"] == "approved"
            and row["runtime_review"] == "verified"
            and row["root_rewrite_attempt_count"] == 1
            for row in decisions
        ),
        "decision contract drifted",
    )

    terminal_manifest = assignment["shared_terminal_ownership"][
        "terminal_manifest"
    ]
    terminal_coordinates = {
        str(row["coordinate"]) for row in terminal_manifest
    }
    require(
        len(terminal_manifest) == 7
        and sum(row["runtime_review"] == "verified" for row in terminal_manifest)
        == 6
        and sum(row["runtime_review"] == "pending" for row in terminal_manifest)
        == 1
        and all(
            row["read_only"]
            and not row["automatic_status_promotion_authorized"]
            for row in terminal_manifest
        )
        and not terminal_coordinates
        & {str(row["coordinate"]) for row in decisions}
        and assignment["source_only_repair"]["action_count"] == 0
        and len(assignment["source_only_repair"]["sites"]) == 5,
        "protected terminal/source-only scope drifted",
    )

    candidate, current, source, _contexts, _pending = (
        wrapper.ASSIGNMENT.RECORDS.load_records()
    )
    engine = wrapper.ENGINE
    live_path = (
        wrapper.RANKING_WRAPPER.DEFAULT_STEAM_ROOT
        / "MSG_PK"
        / "JP"
        / "msggame.bin"
    )
    steam_before = sha256_file(live_path)
    require(
        steam_before == EXPECTED_SHA256["live_steam"], "Steam input drifted"
    )
    replacements, _ = wrapper.RANKING.load_official_ledger(
        wrapper.RANKING_WRAPPER.DEFAULT_LEDGER
    )
    candidate_blob = engine.rebuild_packed_with_literals(
        live_path.read_bytes(), replacements
    )
    require(
        sha256_bytes(candidate_blob) == EXPECTED_SHA256["official_candidate"],
        "candidate reconstruction drifted",
    )
    overrides = {
        parse_coordinate(str(row["coordinate"])):
            str(row["reviewed_translation"])
        for row in decisions
        if str(row["action"]).startswith("translation_override")
    }
    reviewed_blob = engine.rebuild_packed_with_literals(
        candidate_blob, overrides
    )
    reviewed_sha = sha256_bytes(reviewed_blob)
    require(
        reviewed_sha == EXPECTED_SHA256["reviewed_candidate"],
        "reviewed candidate drifted",
    )
    reviewed = engine.archive_records(
        engine.parse_packed_msggame(reviewed_blob).archive
    )
    for row in decisions:
        coordinate = parse_coordinate(str(row["coordinate"]))
        root = coordinate[:2]
        literal_id = coordinate[2]
        require(
            row["jp_source_utf16le_sha256"]
            == private_generator.sha256_text(
                private_generator.literals(source, root)[literal_id]
            )
            and row["current_ko_utf16le_sha256"]
            == private_generator.sha256_text(
                private_generator.literals(current, root)[literal_id]
            )
            and row["reviewed_translation"]
            == private_generator.literals(reviewed, root)[literal_id],
            "decision lineage drifted",
        )
    reverse_blob = engine.rebuild_packed_with_literals(
        reviewed_blob,
        {
            coordinate:
                private_generator.literals(candidate, coordinate[:2])[
                    coordinate[2]
                ]
            for coordinate in overrides
        },
    )
    require(
        sha256_bytes(reverse_blob) == EXPECTED_SHA256["official_candidate"]
        and sha256_file(live_path) == steam_before,
        "reverse overlay or Steam immutability drifted",
    )

    report = {
        "distribution_policy": {
            "private_dialogue_bodies_stay_below_tmp": True,
            "tracked_builder_contains_dialogue_bodies": False,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_test_contains_dialogue_bodies": False,
        },
        "guards": {
            "assignment_private_sha256":
                EXPECTED_SHA256["assignment_private"],
            "context_manifest_sha256":
                EXPECTED_SHA256["context_manifest"],
            "decision_file_sha256":
                EXPECTED_SHA256["private_decisions"],
            "evidence_file_sha256":
                EXPECTED_SHA256["private_evidence"],
            "layout_manifest_sha256":
                EXPECTED_SHA256["layout_manifest"],
            "official_candidate_sha256":
                EXPECTED_SHA256["official_candidate"],
            "reviewed_candidate_sha256": reviewed_sha,
            "reverse_overlay_sha256":
                EXPECTED_SHA256["official_candidate"],
        },
        "method": METHOD,
        "proof": {
            "accepted_branches_current_relative_nonexpanding": True,
            "accepted_branches_grammar_pass": True,
            "automatic_promotion_count_zero": True,
            "controls_tokens_and_linebreak_counts_preserved": True,
            "full_layout_recompute_performed": False,
            "historical_factuality_reviewed": True,
            "jp_authoritative_other_languages_advisory": True,
            "maximum_rewrite_attempts_per_root": 1,
            "nonpending_roots_read_only": True,
            "prior_and_owned_evidence_read_only": True,
            "source_only_action_count_zero": True,
            "speaker_register_reviewed": True,
            "terminal_rows_read_only": True,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": EXPECTED_COUNTS,
        "schema": SCHEMA,
        "scope": {
            "chunk_id": 0,
            "selector": 292,
            "workload_weight": 343,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    assert_source_free(report)
    return report


def build_output() -> bytes:
    content = serialized(build_report())
    if EXPECTED_PUBLIC_SHA256 is not None:
        require(
            sha256_bytes(content) == EXPECTED_PUBLIC_SHA256,
            "public output drifted",
        )
    return content


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--bootstrap", action="store_true")
    args = parser.parse_args(argv)
    content = build_output()
    if args.write or args.bootstrap:
        DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PUBLIC_OUTPUT.write_bytes(content)
    else:
        require(
            DEFAULT_PUBLIC_OUTPUT.is_file()
            and DEFAULT_PUBLIC_OUTPUT.read_bytes() == content,
            "public output is not frozen",
        )
    print(json.dumps({
        "accepted_pending": 11,
        "blocked_pending": 2,
        "output_sha256": sha256_bytes(content),
        "reviewed_candidate_sha256":
            build_report()["guards"]["reviewed_candidate_sha256"],
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
