#!/usr/bin/env python3
"""Freeze selector-364 chunk 1 as a blocked-only residual checkpoint."""

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
    WORKSTREAM / "build_pk_selector376_chunk1_review_v1.py",
    "selector364_chunk1_review_template",
)
CORE = TEMPLATE.CORE
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector364_assignment_v1.py",
    "selector364_chunk1_review_assignment",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector364_assignment.private.v1.json"
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector364_chunk1_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector364_chunk1_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector364_chunk1_review.source_free.v1.json"
)

METHOD = (
    "post_selector376_zero_closure_selector364_chunk1_blocked_only_"
    "terminal_caller_current_relative_and_overlap_review"
)
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector364-chunk1-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector364-chunk1-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector364-chunk1-review.source-free.v1"
EXPECTED_COUNTS = {
    "accepted_pending_roots": 0,
    "accepted_sites": 0,
    "assembly_branches": 133,
    "blocked_pending_roots": 8,
    "blocked_pending_rows": 20,
    "blocked_sites": 19,
    "decision_rows": 0,
    "owned_overlap_roots": 5,
    "promoted_pending_rows": 0,
    "roots": 19,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 19,
    "translation_overrides": 0,
    "verification_renewal_rows": 0,
}
EXPECTED_ACTION_COUNTS: dict[str, int] = {}
EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "0726F36F1D0259708698AC1721943A40C119CCC0D3DCED8A87C0511497E6DFFE"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "48BC6BDF976BC50A0BDE822504AB6CA4014533859D8B0D51554DDD027C2B9653"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "485D30E2790D091064A93482915AC3DE4FCD1B9413FCD0B4198F442936CC75A3"
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
    "DDCDDD2A1923E132A5E615F47ADEADC518129EB81684B8078DD37D32963FB1E7"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "F60B5D0F62D48303805BAA91F5A4125532B1B2B8322D3D3767998D55C5A230AA"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "66AC1B0C39E3ED7C2995EDB44A76F475BDDB1FFB8FE72923B002CC840EC3A3FE"
)
EXPECTED_CHUNK_DIGESTS = {
    "owned_overlap_root_sha256":
        "A13E7A1481F0AA9EDC059F5DD318E2FB6DAA4273D7679B045FD52BAFEA3A0C41",
    "pending_root_sha256":
        "A2071D5CA26ED21B106FB7F9BC6FC5F1090CB5D81F5B5565A402994FC9CED42A",
    "pending_sha256":
        "B53F7E40DDF4E9D74A202AAF7AAD60837EA98425B41F4AE23EA74F2568E71CD9",
    "root_sha256":
        "F45EB34114A01C8C09F01FE4C14498CBA9DE384B601EA9E96C8E5769A14E9919",
    "site_sha256":
        "92A08B64051B64C8490D3C6C234B578DB7B4B73A10912452FD446B2EC101A7BC",
}
EXPECTED_PRIVATE_DECISIONS_SHA256 = EMPTY_SHA256
EXPECTED_PRIVATE_EVIDENCE_SHA256: str | None = (
    "A32273C4E84D2C614652672F3BA12657527CA32C2CC38677D5F0AC2A38297139"
)
EXPECTED_ASSEMBLY_SHA256: str | None = (
    "11A7D41AF3F8D34A45AB7E8B4443E07EA8CB63103AAA32BAB605935BAF4E3679"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "090A212CB678C3F9FF053DBAE7AFCB77D179157D67E9A6C4D0670F4B28FCE5DF"
)

_CORE_BUILD_REPORT = TEMPLATE._CORE_BUILD_REPORT


def configure_core() -> None:
    CORE.ASSIGNMENT_BUILDER_PATH = (
        WORKSTREAM / "build_pk_selector364_assignment_v1.py"
    )
    CORE.ASSIGNMENT_PATH = ASSIGNMENT_PATH
    CORE.ASSIGNMENT_PUBLIC_PATH = (
        WORKSTREAM / "public" / "pk_selector364_assignment_coverage.v1.json"
    )
    CORE.OFFICIAL_LEDGER_PATH = (
        DIALOGUE_TMP
        / "runtime_vm_integrated.post_selector1162_consolidated_checkpoint.private.v1.jsonl"
    )
    CORE.PRIVATE_DECISIONS_PATH = PRIVATE_DECISIONS_PATH
    CORE.PRIVATE_EVIDENCE_PATH = PRIVATE_EVIDENCE_PATH
    CORE.DEFAULT_PUBLIC_OUTPUT = DEFAULT_PUBLIC_OUTPUT
    CORE.SELECTOR = 364
    CORE.TERMINALS = tuple(range(1699, 1706))
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
    CORE.selected_terminal_roots = TEMPLATE.TEMPLATE.selected_terminal_roots
    CORE._EDGE_CACHE.clear()
    CORE._TERMINAL_CACHE.clear()


def terminal_digest(records: Any) -> tuple[list[int], str]:
    values = [
        CORE.first_literal(records, (0, terminal))
        for terminal in range(1699, 1706)
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
        and chunk["site_count"] == 19
        and chunk["root_count"] == 19
        and chunk["pending_root_count"] == 8
        and chunk["pending_row_upper_bound"] == 20
        and chunk["owned_overlap_root_count"] == 5
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
                "blocked_terminal_caller_current_relative_or_overlap",
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
                "terminal_caller_current_relative_or_overlap_unresolved",
            "root": f"{block_id}:{record_id}",
            "site": site,
        })
    assembly_sha = CORE.canonical_sha256(assembly_manifest)
    CORE.require(
        len(site_reviews) == 19
        and len(assembly_manifest) == 133
        and same_gap_branches == 0,
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
