#!/usr/bin/env python3
"""Freeze selector-376 chunk 1 as a blocked-only residual checkpoint."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


TEMPLATE = load_module(
    WORKSTREAM / "build_pk_selector1162_chunk1_review_v1.py",
    "selector376_chunk1_review_template",
)
CORE = TEMPLATE.CORE
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector376_assignment_v1.py",
    "selector376_chunk1_review_assignment",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector376_assignment.private.v1.json"
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector376_chunk1_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector376_chunk1_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector376_chunk1_review.source_free.v1.json"
)

METHOD = (
    "post_selector1162_selector376_chunk1_blocked_only_"
    "terminal_caller_same_gap_current_relative_and_overlap_review"
)
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector376-chunk1-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector376-chunk1-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector376-chunk1-review.source-free.v1"
EXPECTED_COUNTS = {
    "accepted_pending_roots": 0,
    "accepted_sites": 0,
    "assembly_branches": 154,
    "blocked_pending_roots": 12,
    "blocked_pending_rows": 23,
    "blocked_sites": 22,
    "decision_rows": 0,
    "owned_overlap_roots": 2,
    "promoted_pending_rows": 0,
    "roots": 20,
    "same_gap_branches": 14,
    "shared_override_rows": 0,
    "sites": 22,
    "translation_overrides": 0,
    "verification_renewal_rows": 0,
}
EXPECTED_ACTION_COUNTS: dict[str, int] = {}
EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "0E5776587F048804617A39D53BB1F9F675E73563E92F698AE1585292EEE6F759"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "B91E0CAA8134AB1B7868B79BA93C739BAF76D8EDB478A6F1E81DD254BA4D1858"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "046738E8E977A7929A5171136120F8C0AEFE4B61B3E7AC56ED5BA850018D6F0C"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "A3A5433CCDD5F085AF61BEDB0409B5A02C7CAD162AD4ADE5938B356C988065B4"
)
EXPECTED_CANDIDATE_SHA256 = (
    "94FE58C283D696DA36E0F6ADB8339713A0211163EDCD6FD0A92EB5110AE613D2"
)
EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "774BEEDD3F93621B53E747DD45C75AC8325CABA27813E73DA64BB4B267761E76"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "32A5832BBCEF5EC49BD3710787A6CFA001D23220AF64DC6918FBEAA31E0741D6"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = EXPECTED_TERMINAL_CANDIDATE_SHA256
EXPECTED_CHUNK_DIGESTS = {
    "owned_overlap_root_sha256":
        "F74249C7AF8F5357670E9BF66A1CC4D0879520E96CC73BD865F098465222EEEB",
    "pending_root_sha256":
        "2ECCC190CB2CA4E68991B589EE310B05A565280E8F95155493F2C02E5700EA4C",
    "pending_sha256":
        "B938F348EA4207364B78F45F5C3FDD1998F5C7A59BEC87D565E3F89D1D87E6A9",
    "root_sha256":
        "0A46CAD9FB20B48A9D795DEF7A41AA8A942AB566A130A376366DB2D9F6B5F94C",
    "site_sha256":
        "99F97D0CF6E5DF6E8BA5E8155EB55D7953C0B73EA752647050F0B57A4755A236",
}
EXPECTED_PRIVATE_DECISIONS_SHA256 = EMPTY_SHA256
EXPECTED_PRIVATE_EVIDENCE_SHA256: str | None = (
    "62DC532D4C8CE8764CBF2D0F59DC57F9572697B90657E56C7AD6BE550056E2E2"
)
EXPECTED_ASSEMBLY_SHA256: str | None = (
    "5705C2DD91925588683C988066701D980530E3EBCEA23C1044583CBC46E9C3B3"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "D107D1D309AE5A3F431DB9DB1A0BC85AC94272465C8DCF18A63B418322B101C1"
)

_CORE_BUILD_REPORT = TEMPLATE._CORE_BUILD_REPORT


def configure_core() -> None:
    CORE.ASSIGNMENT_BUILDER_PATH = (
        WORKSTREAM / "build_pk_selector376_assignment_v1.py"
    )
    CORE.ASSIGNMENT_PATH = ASSIGNMENT_PATH
    CORE.ASSIGNMENT_PUBLIC_PATH = (
        WORKSTREAM / "public" / "pk_selector376_assignment_coverage.v1.json"
    )
    CORE.OFFICIAL_LEDGER_PATH = (
        DIALOGUE_TMP
        / "runtime_vm_integrated.post_selector1162_consolidated_checkpoint.private.v1.jsonl"
    )
    CORE.PRIVATE_DECISIONS_PATH = PRIVATE_DECISIONS_PATH
    CORE.PRIVATE_EVIDENCE_PATH = PRIVATE_EVIDENCE_PATH
    CORE.DEFAULT_PUBLIC_OUTPUT = DEFAULT_PUBLIC_OUTPUT
    CORE.SELECTOR = 376
    CORE.TERMINALS = tuple(range(1713, 1720))
    CORE.CHUNK_ID = 1
    CORE.PRIVATE_DECISION_SCHEMA = PRIVATE_DECISION_SCHEMA
    CORE.PRIVATE_EVIDENCE_SCHEMA = PRIVATE_EVIDENCE_SCHEMA
    CORE.PUBLIC_SCHEMA = PUBLIC_SCHEMA
    CORE.METHOD = METHOD
    CORE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
        EXPECTED_ASSIGNMENT_BUILDER_SHA256
    )
    CORE.EXPECTED_ASSIGNMENT_SHA256 = EXPECTED_ASSIGNMENT_SHA256
    CORE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
        EXPECTED_ASSIGNMENT_PUBLIC_SHA256
    )
    CORE.EXPECTED_OFFICIAL_LEDGER_SHA256 = EXPECTED_OFFICIAL_LEDGER_SHA256
    CORE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
        EXPECTED_PRIVATE_DECISIONS_SHA256
    )
    CORE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = EXPECTED_PRIVATE_EVIDENCE_SHA256
    CORE.EXPECTED_CANDIDATE_SHA256 = EXPECTED_CANDIDATE_SHA256
    CORE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = EXPECTED_CANDIDATE_SHA256
    CORE.EXPECTED_LIVE_STEAM_SHA256 = EXPECTED_LIVE_STEAM_SHA256
    CORE.EXPECTED_PUBLIC_FILE_SHA256 = EXPECTED_PUBLIC_FILE_SHA256
    CORE.EXPECTED_COUNTS = EXPECTED_COUNTS
    CORE.EXPECTED_ACTION_COUNTS = EXPECTED_ACTION_COUNTS
    CORE.EXPECTED_DIGESTS = {
        "assembly": EXPECTED_ASSEMBLY_SHA256,
        "decision": EMPTY_SHA256,
        "override": EMPTY_SHA256,
        "promoted": EMPTY_SHA256,
    }
    CORE.ASSIGN = ASSIGN
    CORE.ENGINE = ASSIGN.ENGINE
    CORE.RANKING = ASSIGN.RANKING
    CORE.selected_terminal_roots = TEMPLATE.selected_terminal_roots
    CORE._EDGE_CACHE.clear()
    CORE._TERMINAL_CACHE.clear()


def terminal_digest(records: Any) -> tuple[list[int], str]:
    values = [
        CORE.first_literal(records, (0, terminal))
        for terminal in range(1713, 1720)
    ]
    multiplicities = sorted(values.count(value) for value in set(values))
    return multiplicities, CORE.sha256_bytes(
        "\n".join(values).encode("utf-8")
    )


def build_private_payload() -> tuple[bytes, bytes, dict[str, Any]]:
    configure_core()
    assignment = json.loads(ASSIGNMENT_PATH.read_text(encoding="utf-8"))
    chunk = assignment["chunks"][1]
    CORE.require(
        chunk["chunk_id"] == 1
        and chunk["site_count"] == 22
        and chunk["root_count"] == 20
        and chunk["pending_root_count"] == 12
        and chunk["pending_row_upper_bound"] == 23
        and chunk["owned_overlap_root_count"] == 2
        and {
            key: chunk[key] for key in EXPECTED_CHUNK_DIGESTS
        } == EXPECTED_CHUNK_DIGESTS,
        "chunk scope drifted",
    )
    candidate, current, source, contexts, _pending = ASSIGN.load_records()
    candidate_multiplicities, candidate_terminal_sha = terminal_digest(
        candidate
    )
    current_multiplicities, current_terminal_sha = terminal_digest(current)
    source_multiplicities, source_terminal_sha = terminal_digest(source)
    CORE.require(
        candidate_multiplicities == [1, 2, 4]
        and current_multiplicities == [1, 2, 4]
        and source_multiplicities == [1, 2, 4]
        and candidate_terminal_sha == EXPECTED_TERMINAL_CANDIDATE_SHA256
        and current_terminal_sha == EXPECTED_TERMINAL_CURRENT_SHA256
        and source_terminal_sha == EXPECTED_TERMINAL_SOURCE_SHA256,
        "terminal family drifted",
    )
    graph = CORE.graph_edges_cached(candidate)
    chunk_sites = set(chunk["sites"])
    site_reviews: list[dict[str, Any]] = []
    assembly_manifest: list[list[Any]] = []
    same_gap_branches = 0
    blocked: list[dict[str, Any]] = []
    for assignment_row in assignment["site_assignments"]:
        site = str(assignment_row["site"])
        if site not in chunk_sites:
            continue
        block_id, record_id, gap_id, _offset = CORE.RANKING.site_key(site)
        root = (block_id, record_id)
        targets = [
            f"{int(edge['target'][0])}:{int(edge['target'][1])}"
            for edge in graph[root]
            if int(edge["gap_id"]) == gap_id
        ]
        assemblies: list[dict[str, Any]] = []
        for ordinal in range(7):
            reviewed_assembly = CORE.gap_assembly(
                records=candidate,
                source=source,
                root=root,
                gap_id=gap_id,
                ordinal=ordinal,
            )
            current_assembly = CORE.gap_assembly(
                records=current,
                source=source,
                root=root,
                gap_id=gap_id,
                ordinal=ordinal,
            )
            reviewed_lines = CORE.BASE.line_metrics(reviewed_assembly)
            current_lines = CORE.BASE.line_metrics(current_assembly)
            width_pass = CORE.BASE.current_relative_nonexpanding(
                reviewed_lines, current_lines
            )
            same_gap_branches += int(len(targets) > 1)
            assemblies.append({
                "current_assembly": current_assembly,
                "current_lines": current_lines,
                "current_relative_raw_g1n_nonexpanding": width_pass,
                "grammar_and_spacing_proven": False,
                "line_count_match": len(reviewed_lines) == len(current_lines),
                "ordinal": ordinal,
                "reviewed_assembly": reviewed_assembly,
                "reviewed_lines": reviewed_lines,
                "same_gap_targets": targets,
            })
            assembly_manifest.append([
                int(assignment_row["ordinal"]),
                site,
                ordinal,
                CORE.sha256_bytes(reviewed_assembly.encode("utf-8")),
                CORE.sha256_bytes(current_assembly.encode("utf-8")),
                len(reviewed_lines) == len(current_lines),
                width_pass,
                False,
            ])
        multilingual = {}
        for language, records in {
            "en": contexts["en"],
            "jp": source,
            "sc": contexts["sc"],
            "tc": contexts["tc"],
        }.items():
            available = root in records
            joined = ""
            if available:
                joined = "\n".join(
                    literal.text
                    for literal in CORE.ENGINE.parse_record_literals(
                        records[root]
                    )
                )
            multilingual[language] = {
                "available": available,
                "joined_utf8_sha256": CORE.sha256_bytes(
                    joined.encode("utf-8")
                ),
            }
        site_reviews.append({
            "assemblies": assemblies,
            "decision":
                "blocked_terminal_caller_same_gap_current_relative_or_overlap",
            "historical_factuality_reviewed": True,
            "multilingual_context": multilingual,
            "ordinal": int(assignment_row["ordinal"]),
            "root": f"{block_id}:{record_id}",
            "site": site,
            "speaker_tone_reviewed": True,
        })
        blocked.append({
            "pending_coordinates": [
                coordinate
                for coordinate in chunk["pending_coordinates"]
                if coordinate.startswith(f"{block_id}:{record_id}:")
            ],
            "reason":
                "terminal_caller_same_gap_current_relative_or_overlap_unresolved",
            "root": f"{block_id}:{record_id}",
            "site": site,
        })
    assembly_sha = CORE.canonical_sha256(assembly_manifest)
    CORE.require(
        len(site_reviews) == 22
        and len(assembly_manifest) == 154
        and same_gap_branches == 14,
        "blocked-only scope drifted",
    )
    evidence = {
        "assembly_manifest": assembly_manifest,
        "blocked": blocked,
        "counts": EXPECTED_COUNTS,
        "digests": {
            "assembly_canonical_sha256": assembly_sha,
            "decision_coordinate_sha256": EMPTY_SHA256,
            "override_coordinate_sha256": EMPTY_SHA256,
            "promoted_coordinate_sha256": EMPTY_SHA256,
            "reviewed_candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "reverse_overlay_sha256": EXPECTED_CANDIDATE_SHA256,
            "terminal_candidate_sha256":
                EXPECTED_TERMINAL_CANDIDATE_SHA256,
            "terminal_current_sha256": EXPECTED_TERMINAL_CURRENT_SHA256,
            "terminal_source_sha256": EXPECTED_TERMINAL_SOURCE_SHA256,
        },
        "inputs": {
            "assignment_sha256": EXPECTED_ASSIGNMENT_SHA256,
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "official_ledger_sha256": EXPECTED_OFFICIAL_LEDGER_SHA256,
        },
        "method": METHOD,
        "privacy": {
            "contains_commercial_source_text": True,
            "stays_below_tmp": True,
        },
        "schema": PRIVATE_EVIDENCE_SCHEMA,
        "site_reviews": site_reviews,
    }
    return b"", CORE.serialized(evidence), evidence


def build_report() -> dict[str, Any]:
    report = _CORE_BUILD_REPORT()
    report["guards"].update({
        "assignment_public_sha256": EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        "official_ledger_sha256": EXPECTED_OFFICIAL_LEDGER_SHA256,
        "terminal_candidate_sha256": EXPECTED_TERMINAL_CANDIDATE_SHA256,
        "terminal_current_sha256": EXPECTED_TERMINAL_CURRENT_SHA256,
        "terminal_source_sha256": EXPECTED_TERMINAL_SOURCE_SHA256,
    })
    report["proof"].update({
        "decision_rows_empty": True,
        "promotion_rows_empty": True,
        "shared_override_rows_empty": True,
        "terminal_variant_multiplicities": [1, 2, 4],
        "translation_override_rows_empty": True,
        "verification_renewal_rows_empty": True,
    })
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--bootstrap-private", action="store_true")
    parser.add_argument("--bootstrap-public", action="store_true")
    args = parser.parse_args(argv)
    decisions, evidence, payload = build_private_payload()
    if args.bootstrap_private:
        PRIVATE_DECISIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        PRIVATE_DECISIONS_PATH.write_bytes(decisions)
        PRIVATE_EVIDENCE_PATH.write_bytes(evidence)
        print(json.dumps({
            "assembly_sha256":
                payload["digests"]["assembly_canonical_sha256"],
            "evidence_sha256": CORE.sha256_bytes(evidence),
            "status": "PASS",
        }, sort_keys=True))
        return 0
    CORE.require(
        PRIVATE_DECISIONS_PATH.read_bytes() == decisions
        and PRIVATE_EVIDENCE_PATH.read_bytes() == evidence,
        "private artifact drifted",
    )
    configure_core()
    if args.bootstrap_public:
        report = build_report()
        content = CORE.serialized(report)
        DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PUBLIC_OUTPUT.write_bytes(content)
        print(json.dumps({
            "output_sha256": CORE.sha256_bytes(content),
            "status": "PASS",
        }, sort_keys=True))
        return 0
    return CORE.main(["--check"] if args.check else [])


configure_core()
CORE.build_report = build_report
coordinate_digest = CORE.coordinate_digest
load_decisions = CORE.load_decisions
serialized = CORE.serialized
sha256_file = CORE.sha256_file
ReviewError = CORE.ReviewError


if __name__ == "__main__":
    raise SystemExit(main())
