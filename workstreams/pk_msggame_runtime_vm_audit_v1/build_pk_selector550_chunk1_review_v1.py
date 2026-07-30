#!/usr/bin/env python3
"""Validate selector-550 chunk 1 and emit its source-free checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector550_assignment_v1.py"
BASE_REVIEW_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector1174_chunk0_review_v1.py"
)
ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector550_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector550_assignment_coverage.v1.json"
)
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector610_consolidated_checkpoint.private.v1.jsonl"
)
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector550_chunk1_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector550_chunk1_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector550_chunk1_review.source_free.v1.json"
)

SELECTOR = 550
TERMINALS = tuple(range(1930, 1937))
CHUNK_ID = 1
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector550-chunk1-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector550-chunk1-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector550-chunk1-review.source-free.v1"
METHOD = (
    "post_selector610_selector550_chunk1_fresh_semantic_seven_branch_"
    "same_gap_and_current_relative_review"
)

EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "4ACE71CD3A28331AD22F6E865F77463B6A9B6A8B4D7A3679097F2EF3BB33895C"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "A692CAAEFAB77ED85DE5A07F775694ABFDDC1407E01AC158C2C1C4FC861EDFBF"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "A98C40EB3414E5F4DC21C264E091761A54C59F90771902A2B611EF13E90D13A8"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "0218C3D198C9930C8920ED8DAEB2DDD85987878035AC59DD5ECC8179D38DE12B"
)
EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "A719F73ECFFD5299DD4FA8B35D2A49D4E4325F050D740E1EBFE9222F73784B06"
)
EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "C64109153CD26F3A920065E0E2A5358C40A77D1D93A4E91E9226AC0489C42A45"
)
EXPECTED_CANDIDATE_SHA256 = (
    "F80EA5958757F097885279BAB53A8456758BB99B1CE47E214FE0F54AB7152807"
)
EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "2AB31CE43D49619ECA6252425121C6342E98DD5B8A5CF42568FCC7A199CE2909"
)
EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PUBLIC_FILE_SHA256 = (
    "9E5A603F6B9E0FB8B93F7EBEDBDC8F55C6F99A517D5BF490E1A4CB486076AF8B"
)
EXPECTED_COUNTS = {
    "accepted_pending_roots": 19,
    "accepted_sites": 38,
    "assembly_branches": 392,
    "blocked_pending_roots": 8,
    "blocked_pending_rows": 16,
    "blocked_sites": 18,
    "decision_rows": 80,
    "promoted_pending_rows": 46,
    "roots": 54,
    "same_gap_branches": 14,
    "sites": 56,
    "translation_overrides": 47,
}
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 33,
    "translation_override_and_runtime_promotion": 13,
    "translation_override_and_verification_renewal": 34,
}
EXPECTED_DIGESTS = {
    "assembly": "C48F9F4E264A7487EC25D9AAA48EBFD4ED7CEF6649894898AD06435967FB7393",
    "decision": "3A7B0DB5B0BD8449A440C9EDA21C5626CB3969ABE2B3904C5CB5B53D1ECE5D60",
    "override": "041A71356A17338EE355E44BDED314222B1E07DE9717CAB88420C0A4E3621478",
    "promoted": "37BB4BFD0C0648C995E9C9C9EFF65D036C23CB8C3F95269EA64297D95A1398EF",
}


class ReviewError(ValueError):
    """Raised when a frozen chunk review invariant drifts."""


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


ASSIGN = load_module(ASSIGNMENT_BUILDER_PATH, "selector550_chunk1_assignment")
BASE = load_module(BASE_REVIEW_BUILDER_PATH, "selector550_chunk1_base")
ENGINE = ASSIGN.ENGINE
RANKING = ASSIGN.RANKING


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return parts


def coordinate_digest(values: Iterable[str]) -> str:
    return sha256_bytes(
        "\n".join(sorted(set(values), key=parse_coordinate)).encode("ascii")
    )


def literal_text(
    records: Mapping[tuple[int, int], Any], coordinate: str
) -> str:
    block_id, record_id, literal_id = parse_coordinate(coordinate)
    literals = ENGINE.parse_record_literals(records[(block_id, record_id)])
    require(literal_id < len(literals), f"literal is absent: {coordinate}")
    return literals[literal_id].text


def first_literal(
    records: Mapping[tuple[int, int], Any], root: tuple[int, int]
) -> str:
    literals = ENGINE.parse_record_literals(records[root])
    require(len(literals) == 1, f"terminal literal shape drifted: {root}")
    return literals[0].text


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le", errors="strict"))


def record_gap_sha256(record: Any) -> str:
    return BASE.record_gap_sha256(record)


_EDGE_CACHE: dict[int, Mapping[tuple[int, int], Sequence[Mapping[str, Any]]]] = {}
_TERMINAL_CACHE: dict[
    tuple[int, int, int], tuple[tuple[int, int], ...]
] = {}


def graph_edges_cached(
    records: Mapping[tuple[int, int], Any],
) -> Mapping[tuple[int, int], Sequence[Mapping[str, Any]]]:
    key = id(records)
    if key not in _EDGE_CACHE:
        _EDGE_CACHE[key] = RANKING.graph_edges(records)
    return _EDGE_CACHE[key]


def selected_terminal_roots(
    records: Mapping[tuple[int, int], Any],
    source: Mapping[tuple[int, int], Any],
    selector: int,
) -> tuple[tuple[int, int], ...]:
    cache_key = (id(records), id(source), selector)
    if cache_key in _TERMINAL_CACHE:
        return _TERMINAL_CACHE[cache_key]
    if selector == SELECTOR:
        result = tuple((0, terminal) for terminal in TERMINALS)
    else:
        shape = RANKING.family_shape(
            graph_edges_cached(records),
            graph_edges_cached(source),
            (0, selector),
        )
        result = tuple(sorted(shape["candidate_leaves"]))
        require(len(result) == 7, f"selector {selector} is not seven-way")
    _TERMINAL_CACHE[cache_key] = result
    return result


def gap_assembly(
    *,
    records: Mapping[tuple[int, int], Any],
    source: Mapping[tuple[int, int], Any],
    root: tuple[int, int],
    gap_id: int,
    ordinal: int,
) -> str:
    literals = ENGINE.parse_record_literals(records[root])
    require(0 < gap_id <= len(literals), f"invalid gap {root}:{gap_id}")
    edges = [
        edge
        for edge in graph_edges_cached(records)[root]
        if int(edge["gap_id"]) == gap_id
    ]
    result = literals[gap_id - 1].text
    for edge in sorted(edges, key=lambda row: int(row["offset"])):
        selector = int(edge["target"][1])
        terminals = selected_terminal_roots(records, source, selector)
        result += first_literal(records, terminals[ordinal])
    if gap_id < len(literals):
        result += literals[gap_id].text
    return result


def load_decisions() -> list[dict[str, Any]]:
    require(
        sha256_file(PRIVATE_DECISIONS_PATH)
        == EXPECTED_PRIVATE_DECISIONS_SHA256,
        "private decisions drifted",
    )
    rows = [
        json.loads(line)
        for line in PRIVATE_DECISIONS_PATH.read_text(
            encoding="utf-8"
        ).splitlines()
        if line
    ]
    require(
        len(rows) == EXPECTED_COUNTS["decision_rows"]
        and all(row["schema"] == PRIVATE_DECISION_SCHEMA for row in rows),
        "private decision shape drifted",
    )
    require(
        dict(sorted(Counter(row["action"] for row in rows).items()))
        == EXPECTED_ACTION_COUNTS,
        "private decision action counts drifted",
    )
    require(
        coordinate_digest(str(row["coordinate"]) for row in rows)
        == EXPECTED_DIGESTS["decision"],
        "private decision coordinate set drifted",
    )
    return rows


def build_report() -> dict[str, Any]:
    immutable = {
        ASSIGNMENT_BUILDER_PATH: EXPECTED_ASSIGNMENT_BUILDER_SHA256,
        ASSIGNMENT_PATH: EXPECTED_ASSIGNMENT_SHA256,
        ASSIGNMENT_PUBLIC_PATH: EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        OFFICIAL_LEDGER_PATH: EXPECTED_OFFICIAL_LEDGER_SHA256,
        PRIVATE_EVIDENCE_PATH: EXPECTED_PRIVATE_EVIDENCE_SHA256,
    }
    for path, expected in immutable.items():
        require(
            path.is_file() and sha256_file(path) == expected,
            f"immutable input drifted: {path}",
        )
    assignment = json.loads(ASSIGNMENT_PATH.read_text(encoding="utf-8"))
    chunk = assignment["chunks"][CHUNK_ID]
    require(
        chunk["site_count"] == EXPECTED_COUNTS["sites"]
        and chunk["root_count"] == EXPECTED_COUNTS["roots"]
        and chunk["pending_row_upper_bound"]
        == (
            EXPECTED_COUNTS["promoted_pending_rows"]
            + EXPECTED_COUNTS["blocked_pending_rows"]
        ),
        "assignment scope drifted",
    )
    decisions = load_decisions()
    evidence = json.loads(
        PRIVATE_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    require(
        evidence["schema"] == PRIVATE_EVIDENCE_SCHEMA
        and evidence["method"] == METHOD
        and evidence["counts"] == EXPECTED_COUNTS,
        "private evidence header drifted",
    )
    digests = evidence["digests"]
    require(
        digests["assembly_canonical_sha256"] == EXPECTED_DIGESTS["assembly"]
        and digests["decision_coordinate_sha256"]
        == EXPECTED_DIGESTS["decision"]
        and digests["override_coordinate_sha256"]
        == EXPECTED_DIGESTS["override"]
        and digests["promoted_coordinate_sha256"]
        == EXPECTED_DIGESTS["promoted"]
        and digests["reviewed_candidate_sha256"]
        == EXPECTED_REVIEWED_CANDIDATE_SHA256
        and digests["reverse_overlay_sha256"] == EXPECTED_CANDIDATE_SHA256,
        "private evidence digest drifted",
    )

    candidate, current, source, _contexts, _pending = ASSIGN.load_records()
    current_path = (
        ASSIGN.RANKING_WRAPPER.DEFAULT_STEAM_ROOT
        / "MSG_PK" / "JP" / "msggame.bin"
    )
    replacements, _ = RANKING.load_official_ledger(OFFICIAL_LEDGER_PATH)
    candidate_blob = ENGINE.rebuild_packed_with_literals(
        current_path.read_bytes(), replacements
    )
    require(
        sha256_bytes(candidate_blob) == EXPECTED_CANDIDATE_SHA256,
        "official candidate reconstruction drifted",
    )
    overrides = {
        str(row["coordinate"]): str(row["reviewed_translation"])
        for row in decisions
        if str(row["action"]).startswith("translation_override")
    }
    promoted = {
        str(row["coordinate"])
        for row in decisions
        if str(row["action"]).endswith("runtime_promotion")
    }
    require(
        len(overrides) == EXPECTED_COUNTS["translation_overrides"]
        and coordinate_digest(overrides) == EXPECTED_DIGESTS["override"]
        and len(promoted) == EXPECTED_COUNTS["promoted_pending_rows"]
        and coordinate_digest(promoted) == EXPECTED_DIGESTS["promoted"],
        "decision partition drifted",
    )
    reviewed_blob = ENGINE.rebuild_packed_with_literals(
        candidate_blob,
        {
            parse_coordinate(coordinate): translation
            for coordinate, translation in overrides.items()
        },
    )
    require(
        sha256_bytes(reviewed_blob) == EXPECTED_REVIEWED_CANDIDATE_SHA256,
        "reviewed candidate drifted",
    )
    reviewed = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(reviewed_blob).archive
    )
    for row in decisions:
        coordinate = str(row["coordinate"])
        source_text = literal_text(source, coordinate)
        current_text = literal_text(current, coordinate)
        reviewed_text = literal_text(reviewed, coordinate)
        require(
            row["jp_source_utf16le_sha256"] == utf16le_sha256(source_text)
            and row["current_ko_utf16le_sha256"]
            == utf16le_sha256(current_text)
            and row["reviewed_utf16le_sha256"]
            == utf16le_sha256(reviewed_text)
            and row["reviewed_translation"] == reviewed_text
            and row["fresh_semantic_review"] == "approved"
            and row["historical_factuality_review"] == "approved"
            and row["speaker_tone_review"] == "approved"
            and row["runtime_review"] == "verified",
            f"decision proof drifted: {coordinate}",
        )
    changed_roots = {
        root for root in candidate if candidate[root].data != reviewed[root].data
    }
    require(
        changed_roots
        == {parse_coordinate(coordinate)[:2] for coordinate in overrides},
        "changed root set drifted",
    )
    for root in changed_roots:
        before_literals = ENGINE.parse_record_literals(candidate[root])
        after_literals = ENGINE.parse_record_literals(reviewed[root])
        require(
            record_gap_sha256(candidate[root])
            == record_gap_sha256(reviewed[root])
            and len(before_literals) == len(after_literals)
            and all(
                before.text.count("\n") == after.text.count("\n")
                for before, after in zip(before_literals, after_literals)
            ),
            f"encoding or control proof drifted: {root}",
        )
    reverse_blob = ENGINE.rebuild_packed_with_literals(
        reviewed_blob,
        {
            parse_coordinate(coordinate): literal_text(candidate, coordinate)
            for coordinate in overrides
        },
    )
    require(reverse_blob == candidate_blob, "reverse overlay drifted")

    site_reviews = evidence["site_reviews"]
    require(
        len(site_reviews) == EXPECTED_COUNTS["sites"],
        "site review count drifted",
    )
    expected_sites = set(chunk["sites"])
    require(
        {str(review["site"]) for review in site_reviews} == expected_sites,
        "site review scope drifted",
    )
    assembly_manifest: list[list[Any]] = []
    accepted_sites = 0
    same_gap_branches = 0
    for review in site_reviews:
        site = str(review["site"])
        block_id, record_id, gap_id, _offset = RANKING.site_key(site)
        root = (block_id, record_id)
        accepted = not str(review["decision"]).startswith("blocked_")
        accepted_sites += int(accepted)
        branches = review["assemblies"]
        require(len(branches) == 7, f"branch count drifted: {site}")
        for ordinal, branch in enumerate(branches):
            reviewed_assembly = gap_assembly(
                records=reviewed,
                source=source,
                root=root,
                gap_id=gap_id,
                ordinal=ordinal,
            )
            current_assembly = gap_assembly(
                records=current,
                source=source,
                root=root,
                gap_id=gap_id,
                ordinal=ordinal,
            )
            reviewed_lines = BASE.line_metrics(reviewed_assembly)
            current_lines = BASE.line_metrics(current_assembly)
            width_pass = BASE.current_relative_nonexpanding(
                reviewed_lines, current_lines
            )
            require(
                branch["ordinal"] == ordinal
                and branch["reviewed_assembly"] == reviewed_assembly
                and branch["current_assembly"] == current_assembly
                and branch["reviewed_lines"] == reviewed_lines
                and branch["current_lines"] == current_lines
                and branch["grammar_and_spacing_proven"] is accepted
                and (not accepted or width_pass),
                f"assembly proof drifted: {site}:{ordinal}",
            )
            if len(branch["same_gap_targets"]) > 1:
                same_gap_branches += 1
            assignment_ordinal = next(
                int(row["ordinal"])
                for row in assignment["site_assignments"]
                if row["site"] == site
            )
            assembly_manifest.append(
                [
                    assignment_ordinal,
                    site,
                    ordinal,
                    sha256_bytes(reviewed_assembly.encode("utf-8")),
                    sha256_bytes(current_assembly.encode("utf-8")),
                    len(reviewed_lines) == len(current_lines),
                    width_pass,
                    accepted,
                ]
            )
    require(
        accepted_sites == EXPECTED_COUNTS["accepted_sites"]
        and same_gap_branches == EXPECTED_COUNTS["same_gap_branches"]
        and len(assembly_manifest) == EXPECTED_COUNTS["assembly_branches"]
        and canonical_sha256(assembly_manifest) == EXPECTED_DIGESTS["assembly"],
        "assembly disposition drifted",
    )

    live_path = Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
    )
    steam_before = sha256_file(live_path)
    require(
        steam_before == EXPECTED_LIVE_STEAM_SHA256,
        "live Steam archive drifted",
    )
    report = {
        "distribution_policy": {
            "private_decisions_stay_below_tmp": True,
            "private_evidence_stays_below_tmp": True,
            "tracked_builder_contains_dialogue_bodies": False,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_test_contains_dialogue_bodies": False,
            "tracked_validator_uses_frozen_private_hashes": True,
        },
        "guards": {
            "action_counts": EXPECTED_ACTION_COUNTS,
            "assembly_canonical_sha256": EXPECTED_DIGESTS["assembly"],
            "decision_coordinate_sha256": EXPECTED_DIGESTS["decision"],
            "decision_file_sha256": EXPECTED_PRIVATE_DECISIONS_SHA256,
            "evidence_file_sha256": EXPECTED_PRIVATE_EVIDENCE_SHA256,
            "official_candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "override_coordinate_sha256": EXPECTED_DIGESTS["override"],
            "promoted_coordinate_sha256": EXPECTED_DIGESTS["promoted"],
            "reverse_overlay_sha256": EXPECTED_CANDIDATE_SHA256,
            "reviewed_candidate_sha256":
                EXPECTED_REVIEWED_CANDIDATE_SHA256,
            "steam_archive_sha256_after": sha256_file(live_path),
            "steam_archive_sha256_before": steam_before,
        },
        "method": METHOD,
        "proof": {
            "accepted_assemblies_current_relative_raw_g1n_nonexpanding": True,
            "all_assigned_sites_reviewed": True,
            "all_changed_record_control_gaps_preserved": True,
            "all_literal_linebreak_counts_preserved": True,
            "automatic_space_or_grammar_repair_by_vm": False,
            "blocked_unresolved_sites_not_promoted": True,
            "historical_factuality_reviewed": True,
            "opcode_0143_call": True,
            "opcode_014a_jump": True,
            "reverse_overlay_recovers_official_candidate": True,
            "same_gap_selectors_reviewed": True,
            "speaker_tone_reviewed": True,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": EXPECTED_COUNTS,
        "schema": PUBLIC_SCHEMA,
        "scope": {
            "chunk_id": CHUNK_ID,
            "selector": SELECTOR,
            "terminal_count": len(TERMINALS),
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    serialized = json.dumps(report, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            serialized,
        )
        is None,
        "public report contains CJK text",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", serialized) is None,
        "public report contains exact coordinates",
    )
    return report


def serialized(value: Any) -> bytes:
    return canonical_bytes(value) + b"\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_PUBLIC_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(
        args.output.resolve() == DEFAULT_PUBLIC_OUTPUT.resolve(),
        "public output path is fixed",
    )
    report = build_report()
    content = serialized(report)
    output_sha256 = sha256_bytes(content)
    require(
        output_sha256 == EXPECTED_PUBLIC_FILE_SHA256,
        f"public output hash drifted: {output_sha256}",
    )
    if args.check:
        require(
            args.output.is_file() and args.output.read_bytes() == content,
            "public artifact drifted",
        )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(content)
    print(
        json.dumps(
            {
                "accepted_pending": EXPECTED_COUNTS["promoted_pending_rows"],
                "blocked_pending": EXPECTED_COUNTS["blocked_pending_rows"],
                "output_sha256": output_sha256,
                "reviewed_candidate_sha256":
                    EXPECTED_REVIEWED_CANDIDATE_SHA256,
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
