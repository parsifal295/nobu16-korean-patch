#!/usr/bin/env python3
"""Audit a conservative PK residual runtime/layout promotion layer.

Tier-A records with complete assembly evidence are considered directly.
Tier-B/C records may join the same safe set only when their missing metadata
can be regenerated from exact source/current/candidate bytes.  A root is
promoted only when its complete final-candidate call/jump closure:

* preserves the pristine PK VM control structure and the current KO gaps;
* reaches no Tier-B/C/D residual record and no blocked exact-reuse row;
* preserves every literal's line count, protected tokens, and whitespace; and
* never expands any corresponding static line beyond the already deployed
  current-Korean line envelope.

The relative-width gate deliberately assumes no absolute ``msggame`` widget
width and does not reuse the PK ``msgev`` 912px rule.  The report is
source-free and this program has no Steam write path.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
FULL_AUDIT_PATH = (
    WORKSTREAM / "build_pk_msggame_full_candidate_runtime_vm_audit_v1.py"
)
EXACT_COVERAGE_PATH = (
    WORKSTREAM
    / "public"
    / "pk_msggame_full_candidate_runtime_vm_coverage.v1.json"
)
DEFAULT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_msggame_residual_runtime_vm_coverage.v1.json"
)

SCHEMA = "nobu16.kr.pk-msggame-residual-runtime-vm-coverage.v1"
EXPECTED_RESIDUAL_ROWS = 10_913
EXPECTED_RESIDUAL_RECORDS = 6_921
EXPECTED_TIER_ROWS = {"A": 7_295, "B": 1_375, "C": 907, "D": 1_336}
EXPECTED_TIER_RECORDS = {"A": 4_244, "B": 869, "C": 844, "D": 964}
EXPECTED_A_SAFE_ROWS = 6_735
EXPECTED_A_SAFE_RECORDS = 3_848
EXPECTED_RECOMPUTED_BC_SAFE_ROWS = 1_785
EXPECTED_RECOMPUTED_BC_SAFE_RECORDS = 1_351
EXPECTED_UNIFIED_SAFE_ROWS = 8_520
EXPECTED_UNIFIED_SAFE_RECORDS = 5_199
EXPECTED_ELIGIBLE_ROWS = 2_945
EXPECTED_ELIGIBLE_RECORDS = 1_949
EXPECTED_RESIDUAL_COORDINATE_SHA256 = (
    "8AF1915EEF84F2ED004DA86428A50C9A29A420DDB68FB00FA3C3E4FD13C96C65"
)
EXPECTED_TIER_A_COORDINATE_SHA256 = (
    "0B7533B42A62AB9295E32113A12682F48508FAE60B33E3CF3E7C1F36C6F140D0"
)
EXPECTED_A_SAFE_COORDINATE_SHA256 = (
    "9B24580A30A211B5D35C32EDE12E2687F597DC82D1DF7C8F607D8BCB250996D1"
)
EXPECTED_RECOMPUTED_BC_SAFE_COORDINATE_SHA256 = (
    "606784B8573A253373FE22CDA1061AAF9EBF3E954C007B175DCA7F5DD1B79F72"
)
EXPECTED_RECOMPUTED_BC_SAFE_RECORD_SHA256 = (
    "08C9F97426B9552CA1295CEF395457B332D33160A5DACACB1924444DAFDD6390"
)
EXPECTED_ELIGIBLE_COORDINATE_SHA256 = (
    "BB4493A6727655F963BECF89FE4B26020CA03EC98479651AFA4A08D1E7107B58"
)
EXPECTED_ELIGIBLE_RECORD_SHA256 = (
    "7950E61F6A6DD07C3B22BA3A589C0F1C730682F130DC76ED335DFC8E3D2C6F6E"
)

HAZARD_FIELDS = frozenset(
    {
        "runtime_morphology_conflict_detected",
        "caller_rewrite_required_before_runtime_approval",
        "future_caller_rewrite_required_before_runtime_approval",
        "current_gap_difference_requires_runtime_audit",
        "runtime_gap_divergence_followup_required",
        "source_runtime_gap_repair_required",
        "followup_runtime_companion_audit_required",
        "spacing_requires_runtime_companion_audit",
        "two_name_particle_spacing_requires_runtime_audit",
        "name_particle_spacing_requires_runtime_audit",
        "resource_amount_particle_requires_runtime_review",
        "particle_cannot_be_safely_moved_into_owned_prefix",
        "plain_da_branch_runtime_pending",
        "plain_da_copula_allomorph_conflict",
        "base_operand_diff_requires_pk_runtime_review",
    }
)
CALL_GRAPH_FIELDS = frozenset(
    {
        "source_and_current_call_graphs_reviewed",
        "live_pk_call_graphs_reviewed",
        "full_root_graph_closure_guarded",
        "all_actual_caller_contexts_guarded",
        "all_actual_caller_left_right_contexts_guarded",
        "all_caller_contexts_guarded",
        "reachable_0143_call_sets_guarded",
    }
)
TOKEN_FIELDS = frozenset(
    {
        "inline_token_hex",
        "inline_runtime_tokens",
        "inline_runtime_controls",
        "inline_name_token_hex",
    }
)
GAP_EQUAL_FIELDS = frozenset(
    {
        "source_current_runtime_gap_equal",
        "source_current_gap_match",
        "source_current_gap_equal",
    }
)


class ResidualAuditError(ValueError):
    """Raised when the conservative residual proof drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ResidualAuditError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FULL_AUDIT = load_module("pk_residual_full_candidate_audit", FULL_AUDIT_PATH)
BASE_AUDIT = FULL_AUDIT.BASE_AUDIT
ENGINE = FULL_AUDIT.ENGINE


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    )


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def parse_coordinate(value: str) -> tuple[int, int, int]:
    return BASE_AUDIT.parse_literal_coordinate(value)


def coordinate_digest(coordinates: Sequence[str]) -> str:
    payload = "".join(
        f"{coordinate}\n"
        for coordinate in sorted(coordinates, key=parse_coordinate)
    )
    return sha256_bytes(payload.encode("ascii"))


def record_digest(records: Sequence[tuple[int, int]]) -> str:
    payload = "".join(
        f"{block_id}:{record_id}\n"
        for block_id, record_id in sorted(set(records))
    )
    return sha256_bytes(payload.encode("ascii"))


def row_hazard(row: Mapping[str, Any]) -> bool:
    evidence = row.get("runtime_assembly_evidence")
    evidence = evidence if isinstance(evidence, dict) else {}
    line_contradiction = (
        row.get("line_count_preserved") is True
        and row.get("line_count_before") != row.get("line_count_after")
    )
    return line_contradiction or any(
        evidence.get(field) is True for field in HAZARD_FIELDS
    )


def evidence_pair_present(
    evidence: Mapping[str, Any],
    field: str,
) -> bool:
    return f"current_{field}" in evidence and f"source_{field}" in evidence


def strong_row(row: Mapping[str, Any]) -> bool:
    evidence = row.get("runtime_assembly_evidence")
    evidence = evidence if isinstance(evidence, dict) else {}
    return (
        row.get("line_count_preserved") is True
        and row.get("line_count_before") == row.get("line_count_after")
        and evidence.get("complete_record_assembly_reviewed") is True
        and bool(evidence.get("current_record_gap_sha256"))
        and bool(evidence.get("source_record_gap_sha256"))
        and any(
            evidence.get(field) is True for field in GAP_EQUAL_FIELDS
        )
        and any(
            evidence_pair_present(evidence, field)
            for field in TOKEN_FIELDS
        )
        and "current_direct_call_operands" in evidence
        and "source_direct_call_operands" in evidence
        and any(
            evidence.get(field) is True for field in CALL_GRAPH_FIELDS
        )
    )


def classify_records(
    residual_rows: Sequence[Mapping[str, Any]],
) -> tuple[
    dict[tuple[int, int], str],
    dict[tuple[int, int], list[Mapping[str, Any]]],
]:
    by_record: defaultdict[
        tuple[int, int], list[Mapping[str, Any]]
    ] = defaultdict(list)
    for row in residual_rows:
        block_id, record_id, _literal_id = parse_coordinate(
            str(row["coordinate"])
        )
        by_record[(block_id, record_id)].append(row)
    tiers: dict[tuple[int, int], str] = {}
    for record, rows in by_record.items():
        if any(row_hazard(row) for row in rows):
            tier = "D"
        elif any(row.get("line_count_preserved") is not True for row in rows):
            tier = "C"
        elif any(not strong_row(row) for row in rows):
            tier = "B"
        else:
            tier = "A"
        tiers[record] = tier
    return tiers, dict(by_record)


def raw_line_widths(value: str) -> tuple[int, ...]:
    widths: list[int] = []
    for line in value.split("\n"):
        width = 0
        for character in line:
            if unicodedata.category(character) == "Cc":
                # Non-layout controls are separately required to match through
                # ``protected_signature`` and do not advance the text cursor.
                continue
            width += (
                48
                if unicodedata.east_asian_width(character) in {"W", "F", "A"}
                else 24
            )
        widths.append(width)
    return tuple(widths)


def build_record_profiles(
    *,
    inputs: Any,
) -> tuple[
    dict[tuple[int, int], dict[str, Any]],
    dict[tuple[int, int], tuple[tuple[int, int], ...]],
]:
    profiles: dict[tuple[int, int], dict[str, Any]] = {}
    edges: dict[tuple[int, int], tuple[tuple[int, int], ...]] = {}
    for record in sorted(inputs.pk_candidate_records):
        source = inputs.pk_source_records.get(record)
        current = inputs.pk_current_records.get(record)
        candidate = inputs.pk_candidate_records.get(record)
        reasons: set[str] = set()
        literal_manifest: list[dict[str, Any]] = []
        decoded_edges: list[tuple[int, int]] = []
        if source is None or current is None or candidate is None:
            reasons.add("record_missing")
        else:
            source_gaps = ENGINE.record_gap_bytes(source)
            current_gaps = ENGINE.record_gap_bytes(current)
            candidate_gaps = ENGINE.record_gap_bytes(candidate)
            if current_gaps != candidate_gaps:
                reasons.add("current_candidate_gap_mismatch")
            try:
                components = BASE_AUDIT.decode_record(candidate)
            except BASE_AUDIT.AuditError:
                components = []
                reasons.add("candidate_decode_failure")
            for component in components:
                if component["kind"] in {"call", "jump"}:
                    target = tuple(component["target"])
                    if target not in inputs.pk_candidate_records:
                        reasons.add("candidate_target_missing")
                    decoded_edges.append(target)
            current_literals = ENGINE.parse_record_literals(current)
            candidate_literals = ENGINE.parse_record_literals(candidate)
            if len(current_literals) != len(candidate_literals):
                reasons.add("literal_count_mismatch")
            else:
                for current_literal, candidate_literal in zip(
                    current_literals,
                    candidate_literals,
                ):
                    current_widths = raw_line_widths(current_literal.text)
                    candidate_widths = raw_line_widths(
                        candidate_literal.text
                    )
                    if len(current_widths) != len(candidate_widths):
                        reasons.add("line_count_mismatch")
                    elif any(
                        candidate_width > current_width
                        for current_width, candidate_width in zip(
                            current_widths,
                            candidate_widths,
                        )
                    ):
                        reasons.add("relative_line_width_expansion")
                    if (
                        ENGINE.protected_signature(current_literal.text)
                        != ENGINE.protected_signature(candidate_literal.text)
                    ):
                        reasons.add("protected_signature_mismatch")
                    literal_manifest.append(
                        {
                            "current_utf16le_sha256":
                            ENGINE.sha256_text(current_literal.text),
                            "candidate_utf16le_sha256":
                            ENGINE.sha256_text(candidate_literal.text),
                            "current_line_widths": list(current_widths),
                            "candidate_line_widths": list(
                                candidate_widths
                            ),
                        }
                    )
            profiles[record] = {
                "source_record_sha256": sha256_bytes(source.data),
                "current_record_sha256": sha256_bytes(current.data),
                "candidate_record_sha256": sha256_bytes(candidate.data),
                "source_gap_sha256": canonical_sha256(
                    [sha256_bytes(gap) for gap in source_gaps]
                ),
                "current_gap_sha256": canonical_sha256(
                    [sha256_bytes(gap) for gap in current_gaps]
                ),
                "candidate_gap_sha256": canonical_sha256(
                    [sha256_bytes(gap) for gap in candidate_gaps]
                ),
                "literal_manifest_sha256": canonical_sha256(
                    literal_manifest
                ),
                "reason_codes": sorted(reasons),
            }
        edges[record] = tuple(decoded_edges)
    return profiles, edges


def recomputed_bc_safe_records(
    *,
    inputs: Any,
    residual_tiers: Mapping[tuple[int, int], str],
    residual_by_record: Mapping[
        tuple[int, int], Sequence[Mapping[str, Any]]
    ],
    profiles: Mapping[tuple[int, int], Mapping[str, Any]],
    exact_statuses: Mapping[tuple[int, int], Sequence[str]],
) -> set[tuple[int, int]]:
    result: set[tuple[int, int]] = set()
    disallowed_profile_reasons = {
        "record_missing",
        "current_candidate_gap_mismatch",
        "candidate_decode_failure",
        "candidate_target_missing",
        "literal_count_mismatch",
        "line_count_mismatch",
        "protected_signature_mismatch",
    }
    for record, tier in residual_tiers.items():
        if tier not in {"B", "C"}:
            continue
        if "blocked" in exact_statuses.get(record, ()):
            continue
        source = inputs.pk_source_records.get(record)
        current = inputs.pk_current_records.get(record)
        candidate = inputs.pk_candidate_records.get(record)
        if source is None or current is None or candidate is None:
            continue
        if not (
            ENGINE.record_gap_bytes(source)
            == ENGINE.record_gap_bytes(current)
            == ENGINE.record_gap_bytes(candidate)
        ):
            continue
        current_literals = ENGINE.parse_record_literals(current)
        candidate_literals = ENGINE.parse_record_literals(candidate)
        if len(current_literals) != len(candidate_literals):
            continue
        if any(
            len(current_literal.text.split("\n"))
            != len(candidate_literal.text.split("\n"))
            for current_literal, candidate_literal in zip(
                current_literals,
                candidate_literals,
            )
        ):
            continue
        if any(
            reason in disallowed_profile_reasons
            for reason in profiles[record]["reason_codes"]
        ):
            continue
        if any(row_hazard(row) for row in residual_by_record[record]):
            continue
        control_guard = FULL_AUDIT.pk_source_candidate_closure_guard(
            record,
            inputs=inputs,
        )
        if control_guard["taints"]:
            continue
        result.add(record)
    coordinates = [
        str(row["coordinate"])
        for record in sorted(result)
        for row in residual_by_record[record]
    ]
    require(
        len(result) == EXPECTED_RECOMPUTED_BC_SAFE_RECORDS
        and len(coordinates) == EXPECTED_RECOMPUTED_BC_SAFE_ROWS
        and coordinate_digest(coordinates)
        == EXPECTED_RECOMPUTED_BC_SAFE_COORDINATE_SHA256
        and record_digest(list(result))
        == EXPECTED_RECOMPUTED_BC_SAFE_RECORD_SHA256,
        "recomputed Tier-B/C safe universe drifted",
    )
    return result


def closure_proof(
    root: tuple[int, int],
    *,
    inputs: Any,
    profiles: Mapping[tuple[int, int], Mapping[str, Any]],
    edges: Mapping[tuple[int, int], Sequence[tuple[int, int]]],
    residual_tiers: Mapping[tuple[int, int], str],
    a_safe_records: set[tuple[int, int]],
    exact_statuses: Mapping[tuple[int, int], Sequence[str]],
) -> dict[str, Any]:
    queue = [root]
    seen: set[tuple[int, int]] = set()
    reasons: Counter[str] = Counter()
    manifest: list[dict[str, Any]] = []
    edge_manifest: list[dict[str, Any]] = []
    while queue:
        record = queue.pop()
        if record in seen:
            continue
        seen.add(record)
        profile = profiles.get(record)
        if profile is None:
            reasons["record_profile_missing"] += 1
            continue
        reasons.update(profile["reason_codes"])
        if (
            record in residual_tiers
            and record not in a_safe_records
        ):
            reasons["unsafe_residual_descendant"] += 1
        if "blocked" in exact_statuses.get(record, ()):
            reasons["blocked_exact_descendant"] += 1
        manifest.append(
            {
                "record": list(record),
                "profile_sha256": canonical_sha256(profile),
            }
        )
        for occurrence, target in enumerate(edges.get(record, ())):
            edge_manifest.append(
                {
                    "source": list(record),
                    "occurrence": occurrence,
                    "target": list(target),
                }
            )
            queue.append(target)
    control_guard = FULL_AUDIT.pk_source_candidate_closure_guard(
        root,
        inputs=inputs,
    )
    if control_guard["taints"]:
        reasons["source_candidate_control_taint"] += 1
    proof = {
        "root": list(root),
        "visited_records": sorted(manifest, key=lambda row: row["record"]),
        "edges": sorted(
            edge_manifest,
            key=lambda row: (
                row["source"],
                row["occurrence"],
                row["target"],
            ),
        ),
        "source_candidate_closure_proof_sha256":
        control_guard["proof_sha256"],
        "reason_codes": sorted(reasons),
    }
    return {
        "status": "promotion_eligible" if not reasons else "blocked",
        "reason_codes": sorted(reasons),
        "visited_record_count": len(seen),
        "proof_sha256": canonical_sha256(proof),
        "source_candidate_closure_proof_sha256":
        control_guard["proof_sha256"],
    }


def effective_source_rows(
    source_rows: Sequence[Mapping[str, Any]],
    *,
    full_metadata: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rows = [copy.deepcopy(dict(row)) for row in source_rows]
    (
        semantic_private_content,
        semantic_public_content,
        semantic_report,
        semantic_row,
    ) = FULL_AUDIT.SEMANTIC_OVERRIDE.build_outputs()
    FULL_AUDIT.SEMANTIC_OVERRIDE.validate_outputs(
        semantic_private_content,
        semantic_public_content,
        semantic_report,
        semantic_row,
    )
    semantic_coordinate = str(semantic_row["coordinate"])
    semantic_matches = [
        index
        for index, row in enumerate(rows)
        if str(row["coordinate"]) == semantic_coordinate
    ]
    require(
        len(semantic_matches) == 1,
        "semantic override coordinate is absent or duplicated",
    )
    rows[semantic_matches[0]] = semantic_row
    reflow_overrides, _reflow_metadata = (
        FULL_AUDIT.REFLOW_OVERRIDE.load_overrides(rows)
    )
    consumed: set[str] = set()
    for index, row in enumerate(rows):
        coordinate = str(row["coordinate"])
        override = reflow_overrides.get(coordinate)
        if override is None:
            continue
        rows[index] = override
        consumed.add(coordinate)
    require(
        consumed == set(reflow_overrides),
        "relative reflow override universe was not fully applied",
    )
    replacement_manifest = [
        {
            "coordinate": str(row["coordinate"]),
            "translation_utf16le_sha256": ENGINE.sha256_text(
                str(row["translation"])
            ),
        }
        for row in rows
        if isinstance(row.get("translation"), str)
    ]
    require(
        canonical_sha256(replacement_manifest)
        == full_metadata["replacement_manifest_sha256"],
        "effective residual replacement manifest drifted",
    )
    return rows


def build_report() -> tuple[dict[str, Any], Any, dict[str, Any]]:
    inputs, full_metadata = FULL_AUDIT.full_candidate_inputs()
    exact_report = json.loads(EXACT_COVERAGE_PATH.read_text(encoding="utf-8"))
    FULL_AUDIT.validate_report(
        exact_report,
        inputs=inputs,
        metadata=full_metadata,
    )
    source_rows, source_metadata = FULL_AUDIT.source_decisions()
    source_rows = effective_source_rows(
        source_rows,
        full_metadata=full_metadata,
    )
    exact_coordinates = set(exact_report["row_adjudications"])
    residual_rows = [
        row
        for row in source_rows
        if row.get("runtime_review") == "pending"
        and str(row["coordinate"]) not in exact_coordinates
    ]
    residual_coordinates = [
        str(row["coordinate"]) for row in residual_rows
    ]
    tiers, residual_by_record = classify_records(residual_rows)
    tier_rows = Counter(
        tiers[parse_coordinate(str(row["coordinate"]))[:2]]
        for row in residual_rows
    )
    tier_records = Counter(tiers.values())
    require(
        len(residual_rows) == EXPECTED_RESIDUAL_ROWS
        and len(residual_by_record) == EXPECTED_RESIDUAL_RECORDS
        and dict(tier_rows) == EXPECTED_TIER_ROWS
        and dict(tier_records) == EXPECTED_TIER_RECORDS
        and coordinate_digest(residual_coordinates)
        == EXPECTED_RESIDUAL_COORDINATE_SHA256,
        "residual classifier universe drifted",
    )
    tier_a_coordinates = [
        str(row["coordinate"])
        for row in residual_rows
        if tiers[parse_coordinate(str(row["coordinate"]))[:2]] == "A"
    ]
    require(
        coordinate_digest(tier_a_coordinates)
        == EXPECTED_TIER_A_COORDINATE_SHA256,
        "Tier-A coordinate universe drifted",
    )
    exact_statuses: defaultdict[
        tuple[int, int], list[str]
    ] = defaultdict(list)
    for coordinate, adjudication in exact_report[
        "row_adjudications"
    ].items():
        exact_statuses[parse_coordinate(coordinate)[:2]].append(
            str(adjudication["status"])
        )
    a_safe_records = {
        record
        for record, tier in tiers.items()
        if tier == "A" and "blocked" not in exact_statuses[record]
    }
    a_safe_coordinates = [
        str(row["coordinate"])
        for record in sorted(a_safe_records)
        for row in residual_by_record[record]
    ]
    require(
        len(a_safe_records) == EXPECTED_A_SAFE_RECORDS
        and len(a_safe_coordinates) == EXPECTED_A_SAFE_ROWS
        and coordinate_digest(a_safe_coordinates)
        == EXPECTED_A_SAFE_COORDINATE_SHA256,
        "final-exact-safe Tier-A universe drifted",
    )
    profiles, edges = build_record_profiles(inputs=inputs)
    recomputed_bc_records = recomputed_bc_safe_records(
        inputs=inputs,
        residual_tiers=tiers,
        residual_by_record=residual_by_record,
        profiles=profiles,
        exact_statuses=exact_statuses,
    )
    unified_safe_records = a_safe_records | recomputed_bc_records
    unified_safe_coordinates = [
        str(row["coordinate"])
        for record in sorted(unified_safe_records)
        for row in residual_by_record[record]
    ]
    require(
        len(unified_safe_records) == EXPECTED_UNIFIED_SAFE_RECORDS
        and len(unified_safe_coordinates) == EXPECTED_UNIFIED_SAFE_ROWS,
        "unified Tier-A/recomputed-B/C safe universe drifted",
    )
    record_proofs: dict[str, dict[str, Any]] = {}
    blocker_counts: Counter[str] = Counter()
    eligible_records: list[tuple[int, int]] = []
    for record in sorted(unified_safe_records):
        proof = closure_proof(
            record,
            inputs=inputs,
            profiles=profiles,
            edges=edges,
            residual_tiers=tiers,
            a_safe_records=unified_safe_records,
            exact_statuses=exact_statuses,
        )
        record_proofs[f"{record[0]}:{record[1]}"] = proof
        if proof["status"] == "promotion_eligible":
            eligible_records.append(record)
        else:
            blocker_counts.update(proof["reason_codes"])
    eligible_coordinates = [
        str(row["coordinate"])
        for record in eligible_records
        for row in residual_by_record[record]
    ]
    require(
        len(eligible_records) == EXPECTED_ELIGIBLE_RECORDS
        and len(eligible_coordinates) == EXPECTED_ELIGIBLE_ROWS
        and coordinate_digest(eligible_coordinates)
        == EXPECTED_ELIGIBLE_COORDINATE_SHA256
        and record_digest(eligible_records)
        == EXPECTED_ELIGIBLE_RECORD_SHA256,
        "conservative residual promotion universe drifted",
    )
    source_rows_by_coordinate = {
        str(row["coordinate"]): row for row in source_rows
    }
    row_adjudications: dict[str, dict[str, Any]] = {}
    row_guards: dict[str, str] = {}
    for coordinate in sorted(
        eligible_coordinates,
        key=parse_coordinate,
    ):
        row = source_rows_by_coordinate[coordinate]
        record = parse_coordinate(coordinate)[:2]
        proof = record_proofs[f"{record[0]}:{record[1]}"]
        guard_payload = {
            "coordinate": coordinate,
            "source_decision_sha256": canonical_sha256(row),
            "translation_utf16le_sha256": ENGINE.sha256_text(
                row["translation"]
            ),
            "record": list(record),
            "record_member_coordinate_sha256": coordinate_digest(
                [
                    str(member["coordinate"])
                    for member in residual_by_record[record]
                ]
            ),
            "record_proof_sha256": proof["proof_sha256"],
            "candidate_record_sha256": profiles[record][
                "candidate_record_sha256"
            ],
            "pk_full_candidate_packed_sha256":
            inputs.artifact_hashes["pk_full_candidate_packed_sha256"],
            "exact_coverage_file_sha256": sha256_bytes(
                EXACT_COVERAGE_PATH.read_bytes()
            ),
            "status": "promotion_eligible",
        }
        guard = canonical_sha256(guard_payload)
        row_guards[coordinate] = guard
        row_adjudications[coordinate] = {
            "status": "promotion_eligible",
            "tier": tiers[record],
            "evidence_origin": (
                "complete_metadata_tier_a"
                if record in a_safe_records
                else "binary_recomputed_tier_bc"
            ),
            "record": list(record),
            "translation_utf16le_sha256":
            guard_payload["translation_utf16le_sha256"],
            "source_decision_sha256":
            guard_payload["source_decision_sha256"],
            "candidate_record_sha256":
            guard_payload["candidate_record_sha256"],
            "record_proof_sha256": proof["proof_sha256"],
            "row_verification_guard_sha256": guard,
            "layout_adjudication":
            "relative_full_closure_line_envelope_nonexpanding",
        }
    report = {
        "schema": SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "scope": {
            "pk_rows": FULL_AUDIT.EXPECTED_PK_ROWS,
            "residual_rows": len(residual_rows),
            "residual_records": len(residual_by_record),
            "tier_rows": dict(sorted(tier_rows.items())),
            "tier_records": dict(sorted(tier_records.items())),
            "tier_a_final_exact_safe_rows": len(a_safe_coordinates),
            "tier_a_final_exact_safe_records": len(a_safe_records),
            "recomputed_tier_bc_safe_rows":
            EXPECTED_RECOMPUTED_BC_SAFE_ROWS,
            "recomputed_tier_bc_safe_records": len(
                recomputed_bc_records
            ),
            "unified_safe_rows": len(unified_safe_coordinates),
            "unified_safe_records": len(unified_safe_records),
            "promotion_eligible_rows": len(eligible_coordinates),
            "promotion_eligible_records": len(eligible_records),
            "blocked_after_conservative_closure_rows":
            len(unified_safe_coordinates) - len(eligible_coordinates),
        },
        "candidate_binding": {
            "pk_full_candidate_packed_sha256":
            inputs.artifact_hashes["pk_full_candidate_packed_sha256"],
            "replacement_manifest_sha256": full_metadata[
                "replacement_manifest_sha256"
            ],
            "source_decision_segment_universe_sha256": source_metadata[
                "source_decision_segment_universe_sha256"
            ],
            "semantic_override_private_sha256": full_metadata[
                "semantic_override_private_sha256"
            ],
            "semantic_override_public_sha256": full_metadata[
                "semantic_override_public_sha256"
            ],
            "exact_coverage_file_sha256": sha256_bytes(
                EXACT_COVERAGE_PATH.read_bytes()
            ),
            "exact_coverage_payload_sha256": exact_report["guards"][
                "report_payload_sha256"
            ],
        },
        "classifier": {
            "record_priority": ["D", "C", "B", "A"],
            "hazard_field_allowlist_sha256": canonical_sha256(
                sorted(HAZARD_FIELDS)
            ),
            "call_graph_field_allowlist_sha256": canonical_sha256(
                sorted(CALL_GRAPH_FIELDS)
            ),
            "token_field_allowlist_sha256": canonical_sha256(
                sorted(TOKEN_FIELDS)
            ),
            "blocked_exact_companion_precedence": True,
            "tier_bc_binary_recomputation": {
                "source_current_candidate_gap_exact": True,
                "actual_line_count_recomputed": True,
                "decoded_target_existence_recomputed": True,
                "source_candidate_closure_recomputed": True,
                "metadata_promotion_flags_trusted": False,
            },
        },
        "layout_contract": {
            "comparison": "candidate line <= current KO corresponding line",
            "raw_g1n_full_width_px": 48,
            "raw_g1n_half_width_px": 24,
            "absolute_msggame_widget_width_assumed": False,
            "pk_msgev_912px_rule_applied": False,
            "complete_call_jump_closure_checked": True,
        },
        "blockers": {
            "reason_root_counts": dict(sorted(blocker_counts.items())),
        },
        "guards": {
            "residual_coordinate_sha256":
            EXPECTED_RESIDUAL_COORDINATE_SHA256,
            "tier_a_coordinate_sha256":
            EXPECTED_TIER_A_COORDINATE_SHA256,
            "tier_a_final_exact_safe_coordinate_sha256":
            EXPECTED_A_SAFE_COORDINATE_SHA256,
            "recomputed_tier_bc_safe_coordinate_sha256":
            EXPECTED_RECOMPUTED_BC_SAFE_COORDINATE_SHA256,
            "recomputed_tier_bc_safe_record_sha256":
            EXPECTED_RECOMPUTED_BC_SAFE_RECORD_SHA256,
            "unified_safe_coordinate_sha256": coordinate_digest(
                unified_safe_coordinates
            ),
            "unified_safe_record_sha256": record_digest(
                list(unified_safe_records)
            ),
            "eligible_coordinate_sha256":
            EXPECTED_ELIGIBLE_COORDINATE_SHA256,
            "eligible_record_sha256":
            EXPECTED_ELIGIBLE_RECORD_SHA256,
            "record_proof_universe_sha256": canonical_sha256(
                record_proofs
            ),
            "row_guard_universe_sha256": canonical_sha256(row_guards),
        },
        "record_proofs": record_proofs,
        "row_adjudications": row_adjudications,
        "promotion": {
            "runtime_promotion_performed": False,
            "layout_promotion_performed": False,
            "eligible_rows_require_separate_bound_overlay": True,
        },
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_translated_dialogue_text": False,
        },
        "steam_write_performed": False,
    }
    unsealed = copy.deepcopy(report)
    report["guards"]["report_payload_sha256"] = canonical_sha256(
        unsealed
    )
    return report, inputs, full_metadata


def validate_report(
    report: Mapping[str, Any],
    *,
    inputs: Any,
    full_metadata: Mapping[str, Any],
) -> None:
    require(
        report.get("schema") == SCHEMA
        and report.get("status") == "PASS"
        and report.get("steam_write_performed") is False,
        "residual report metadata drifted",
    )
    unsealed = copy.deepcopy(dict(report))
    guards = unsealed.get("guards")
    require(isinstance(guards, dict), "residual report guards are absent")
    expected_payload = guards.pop("report_payload_sha256", None)
    require(
        expected_payload == canonical_sha256(unsealed),
        "residual report payload drifted",
    )
    require(
        report["candidate_binding"]["pk_full_candidate_packed_sha256"]
        == inputs.artifact_hashes["pk_full_candidate_packed_sha256"]
        and report["candidate_binding"]["replacement_manifest_sha256"]
        == full_metadata["replacement_manifest_sha256"],
        "residual candidate binding drifted",
    )
    eligible = [
        coordinate
        for coordinate, row in report["row_adjudications"].items()
        if row["status"] == "promotion_eligible"
    ]
    require(
        len(eligible) == EXPECTED_ELIGIBLE_ROWS
        and coordinate_digest(eligible)
        == EXPECTED_ELIGIBLE_COORDINATE_SHA256,
        "residual eligible row universe drifted",
    )


def build_outputs() -> tuple[str, dict[str, Any], Any, dict[str, Any]]:
    report, inputs, full_metadata = build_report()
    validate_report(
        report,
        inputs=inputs,
        full_metadata=full_metadata,
    )
    return canonical_json(report), report, inputs, full_metadata


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    first = build_outputs()
    second = build_outputs()
    require(first[0] == second[0], "two-run residual report drifted")
    content, report, _inputs, _metadata = first
    if args.write:
        ENGINE.atomic_write(args.output, content)
    if args.check:
        require(
            args.output.is_file()
            and args.output.read_text(encoding="utf-8") == content,
            "tracked residual report drifted",
        )
    print(
        "PASS "
        f"residual={report['scope']['residual_rows']} "
        f"eligible={report['scope']['promotion_eligible_rows']} "
        f"blocked={report['scope']['blocked_after_conservative_closure_rows']} "
        f"steam_write={str(report['steam_write_performed']).lower()}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        ResidualAuditError,
        ENGINE.RetranslationError,
        BASE_AUDIT.AuditError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
