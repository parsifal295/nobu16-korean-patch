#!/usr/bin/env python3
"""Validate selector-292 chunk 1 and emit its source-free checkpoint."""

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
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector292_assignment_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector292_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector292_assignment_coverage.v1.json"
)
CONTEXT_PATH = DIALOGUE_TMP / "pk_selector292_context_inventory.private.v1.json"
LAYOUT_PATH = (
    DIALOGUE_TMP
    / "pk_selector292_layout_manifest.selector178_chunk1_fast.private.v1.json"
)
PRIVATE_GENERATOR_PATH = (
    DIALOGUE_TMP / "pk_selector292_chunk1_review_generator.private.v1.py"
)
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector292_chunk1_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector292_chunk1_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector292_chunk1_review.source_free.v1.json"
)

CHUNK_ID = 1
SELECTOR = 292
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector292-chunk1-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector292-chunk1-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector292-chunk1-review.source-free.v1"
METHOD = (
    "post_selector238_selector292_chunk1_single_pass_jp_authoritative_"
    "semantic_register_and_affected_ordinary_branch_review"
)

EXPECTED_SHA256 = {
    "assignment_builder":
        "A1BC5DE2EA3E0CF06984FF97347006936407FF32B72D439B94F7598B0FD3847E",
    "assignment_private":
        "B2FD0DD7B016B20CCAB04CA903643CD158008299BBC9EF8FAA89187A5C9D6372",
    "assignment_public":
        "AAA5F7F7A503A508712AC1E0DB304F04A9152FA1E3CE30D5A53598B1AE3B06DD",
    "context_private":
        "2DC02C44C2698F407970BB0291E3023A597D6F9944B330E91A3C4778C621685D",
    "layout_private":
        "A19F3696797F141A282826D1E87DEA1D80EF11E0BB55F21EF49EF061CCE0FA99",
    "private_generator":
        "696D61F66B824586449AA0A27219B96E897A3228D573F08E28FA88E00BB9EF34",
    "private_decisions":
        "6B2230F012B400AF9C393E0ADDBA0D7658E349ABC53E7DC49722FB27217C6A95",
    "private_evidence":
        "92F0A300B915AC0EDB01CD00DF1C52DE5F6929BB71CC2F7A86CCA268616296C0",
    "official_ledger":
        "AC10F7E71CFAD259ABBC08139BE0DB848CF5309578045532A48991F40E0035AB",
    "official_candidate":
        "9E5C60A451DB7CCA7B046AFD8CFF199CB3665E003CB0C751120478F693D20C24",
    "reviewed_candidate":
        "FBE33BD69066D1F6139A08D8E15A03541FB91CB12DB9D82BBB93426361ADA9C4",
    "live_steam":
        "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
    "terminal_candidate":
        "F18978DBB58A5D8AF1ED4B2266FE2B599C98A038D5A85BDAAC2222FDEB8C51A6",
    "terminal_current":
        "84EE1EB18E39223AA009868B7FB99119073A6DFC7CA8FC899C70C464F8346B47",
    "terminal_source":
        "798B6E4A8099F9FCA1BF5033F8315B17832B8D17178826029B800738EAD905C2",
}
EXPECTED_DIGESTS = {
    "accepted_branches":
        "6EFB010FE52D6485235F1CD3FD3FD242CB00C8FEE669B7D2CE16DFB1C4511F02",
    "affected_branches":
        "2EDF3F59CE0DE2A137C248879C402045EB3165F848832ACA7E9DFD0895DDF7E2",
    "blocked_attempt_branches":
        "1638463049662C62309DE1A4D5E839937E2D7DCD5A0980C1B339BFE0A19E4C3B",
    "decision":
        "D20DB6262E784687BC4EDA784780879380A97164A633CD8F2686D936F62DC8CC",
    "override":
        "555253FFDFDE5E627E222DAADC31418641E55CCA72BB254B3688F0E5B7F24092",
    "promoted":
        "D20DB6262E784687BC4EDA784780879380A97164A633CD8F2686D936F62DC8CC",
}
EXPECTED_COUNTS = {
    "accepted_pending_roots": 3,
    "accepted_pending_rows": 10,
    "accepted_sites": 3,
    "affected_ordinary_branches_computed": 35,
    "affected_ordinary_pass_branches": 33,
    "assigned_roots": 13,
    "assigned_sites": 13,
    "blocked_pending_roots": 3,
    "blocked_pending_rows": 10,
    "blocked_sites": 3,
    "decision_rows": 10,
    "hard_block_reused_branches": 7,
    "non_display_actions": 0,
    "owned_overlap_automatic_promotions": 0,
    "prior_evidence_automatic_promotions": 0,
    "promoted_pending_rows": 10,
    "read_only_nonpending_roots": 7,
    "register_atom_blocked_roots": 2,
    "rewrite_attempt_roots": 5,
    "runtime_only_promotions": 6,
    "source_only_actions": 0,
    "source_only_sites": 5,
    "terminal_decision_rows": 0,
    "terminal_pending_read_only_rows": 1,
    "terminal_verified_read_only_rows": 6,
    "translation_overrides": 4,
}
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 6,
    "translation_override_and_runtime_promotion": 4,
}
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "71A23B62D9B6DC0B32E02163F9B9997743453E55B13840401BB0E506BB915AF5"
)


class ReviewError(ValueError):
    """Raised when a frozen review invariant drifts."""


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


WRAPPER = load_module(
    ASSIGNMENT_BUILDER_PATH, "selector292_chunk1_review_assignment"
)
ASSIGNMENT = WRAPPER.ASSIGNMENT
RANKING = WRAPPER.RANKING
ENGINE = WRAPPER.ENGINE
OFFICIAL_LEDGER_PATH = WRAPPER.RANKING_WRAPPER.DEFAULT_LEDGER
TERMINALS = tuple(WRAPPER.TERMINALS)


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


def serialized(value: Any) -> bytes:
    return canonical_bytes(value) + b"\n"


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return parts


def parse_root(value: str) -> tuple[int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    require(len(parts) == 2, f"invalid root: {value}")
    return parts


def coordinate_digest(values: Iterable[str]) -> str:
    return sha256_bytes(
        "\n".join(sorted(set(values), key=parse_coordinate)).encode("ascii")
    )


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


def literal_text(
    records: Mapping[tuple[int, int], Any], coordinate: str
) -> str:
    block_id, record_id, literal_id = parse_coordinate(coordinate)
    literals = ENGINE.parse_record_literals(records[(block_id, record_id)])
    require(literal_id < len(literals), f"literal absent: {coordinate}")
    return literals[literal_id].text


def terminal_text(
    records: Mapping[tuple[int, int], Any], root: tuple[int, int]
) -> str:
    literals = ENGINE.parse_record_literals(records[root])
    require(len(literals) == 1, f"terminal shape drifted: {root}")
    return literals[0].text


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le", errors="strict"))


def terminal_digest(
    records: Mapping[tuple[int, int], Any],
    terminals: Sequence[tuple[int, int]],
) -> str:
    return sha256_bytes(
        "\0".join(terminal_text(records, root) for root in terminals)
        .encode("utf-8")
    )


def current_relative_pass(
    reviewed_widths: Sequence[int], current_widths: Sequence[int]
) -> bool:
    return (
        len(reviewed_widths) == len(current_widths)
        and all(
            reviewed <= current
            for reviewed, current in zip(reviewed_widths, current_widths)
        )
    )


def site_assembly(
    records: Mapping[tuple[int, int], Any],
    root: tuple[int, int],
    gap_id: int,
    terminal: tuple[int, int],
) -> str:
    literals = ENGINE.parse_record_literals(records[root])
    require(0 < gap_id <= len(literals), f"gap shape drifted: {root}")
    value = literals[gap_id - 1].text + terminal_text(records, terminal)
    if gap_id < len(literals):
        value += literals[gap_id].text
    return value


def branch_manifest(
    *,
    sites: Sequence[str],
    selected: Mapping[tuple[int, int], Any],
    current: Mapping[tuple[int, int], Any],
    terminals: Sequence[tuple[int, int]],
    disposition: str,
) -> list[list[Any]]:
    manifest: list[list[Any]] = []
    for site in sites:
        block_id, record_id, gap_id, _offset = RANKING.site_key(site)
        root = (block_id, record_id)
        for ordinal, terminal in enumerate(terminals):
            reviewed_text = site_assembly(selected, root, gap_id, terminal)
            current_text = site_assembly(current, root, gap_id, terminal)
            reviewed_widths = [
                int(value)
                for value in ASSIGNMENT.HELPER.LEGACY.line_widths(reviewed_text)
            ]
            current_widths = [
                int(value)
                for value in ASSIGNMENT.HELPER.LEGACY.line_widths(current_text)
            ]
            manifest.append([
                site,
                ordinal,
                sha256_bytes(reviewed_text.encode("utf-8")),
                sha256_bytes(current_text.encode("utf-8")),
                reviewed_widths,
                current_widths,
                current_relative_pass(reviewed_widths, current_widths),
                disposition,
            ])
    return manifest


def validate_source_free(value: Any) -> None:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True)
    cjk = re.compile(
        r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
        r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
    )
    require(cjk.search(encoded) is None, "public report contains CJK text")
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", encoded) is None,
        "public report contains exact coordinates",
    )


def validate_inputs() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    list[dict[str, Any]],
]:
    immutable = {
        ASSIGNMENT_BUILDER_PATH: EXPECTED_SHA256["assignment_builder"],
        ASSIGNMENT_PATH: EXPECTED_SHA256["assignment_private"],
        ASSIGNMENT_PUBLIC_PATH: EXPECTED_SHA256["assignment_public"],
        CONTEXT_PATH: EXPECTED_SHA256["context_private"],
        LAYOUT_PATH: EXPECTED_SHA256["layout_private"],
        PRIVATE_GENERATOR_PATH: EXPECTED_SHA256["private_generator"],
        PRIVATE_DECISIONS_PATH: EXPECTED_SHA256["private_decisions"],
        PRIVATE_EVIDENCE_PATH: EXPECTED_SHA256["private_evidence"],
        OFFICIAL_LEDGER_PATH: EXPECTED_SHA256["official_ledger"],
    }
    for path, expected in immutable.items():
        require(
            path.is_file() and sha256_file(path) == expected,
            f"immutable input drifted: {path}",
        )
    return (
        load_json(ASSIGNMENT_PATH),
        load_json(CONTEXT_PATH),
        load_json(LAYOUT_PATH),
        load_json(PRIVATE_EVIDENCE_PATH),
        load_jsonl(PRIVATE_DECISIONS_PATH),
    )


def validate_assignment(
    assignment: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> tuple[
    Mapping[str, Any],
    set[tuple[int, int]],
    set[tuple[int, int]],
    set[tuple[int, int]],
    set[tuple[int, int]],
]:
    chunk = assignment["chunks"][CHUNK_ID]
    require(
        (
            chunk["site_count"],
            chunk["root_count"],
            chunk["pending_root_count"],
            chunk["pending_row_upper_bound"],
            chunk["rewrite_candidate_root_count"],
            chunk["rewrite_candidate_pending_row_count"],
            chunk["hard_block_root_count"],
            chunk["hard_block_pending_row_count"],
            chunk["workload_weight"],
        ) == (13, 13, 6, 20, 5, 16, 1, 4, 342),
        "chunk assignment metrics drifted",
    )
    accepted_coordinates = set(evidence["accepted_pending_coordinates"])
    blocked_coordinates = set(evidence["blocked_pending_coordinates"])
    require(
        accepted_coordinates | blocked_coordinates
        == set(chunk["pending_coordinates"])
        and not accepted_coordinates & blocked_coordinates,
        "pending row partition drifted",
    )
    accepted_roots = {
        parse_coordinate(value)[:2] for value in accepted_coordinates
    }
    blocked_roots = {
        parse_coordinate(value)[:2] for value in blocked_coordinates
    }
    chunk_roots = {parse_root(value) for value in chunk["roots"]}
    read_only_roots = chunk_roots - accepted_roots - blocked_roots
    blocked_reason_roots = {
        parse_root(str(row["root"]))
        for row in evidence["blocked_root_reasons"]
    }
    hard_block_roots = {
        parse_root(str(row["root"]))
        for row in evidence["blocked_root_reasons"]
        if int(row["rewrite_attempt_count"]) == 0
    }
    require(
        len(accepted_roots) == 3
        and len(blocked_roots) == 3
        and len(read_only_roots) == 7
        and blocked_reason_roots == blocked_roots
        and len(hard_block_roots) == 1
        and not accepted_roots & blocked_roots
        and not accepted_roots & read_only_roots
        and not blocked_roots & read_only_roots,
        "root disposition partition drifted",
    )
    require(
        assignment["prior_pending_evidence"][
            "automatic_status_promotion_authorized"
        ] is False
        and assignment["shared_terminal_ownership"][
            "automatic_status_promotion_authorized"
        ] is False
        and assignment["source_only_repair"]["action_count"] == 0
        and len(assignment["source_only_repair"]["sites"]) == 5
        and assignment["review_partition"]["root_rewrite_maximum"] == 1,
        "assignment protection guard drifted",
    )
    return (
        chunk,
        accepted_roots,
        blocked_roots,
        read_only_roots,
        hard_block_roots,
    )


def validate_decisions(
    decisions: Sequence[Mapping[str, Any]],
    evidence: Mapping[str, Any],
    accepted_roots: set[tuple[int, int]],
    blocked_roots: set[tuple[int, int]],
) -> tuple[dict[str, str], set[str]]:
    require(
        len(decisions) == EXPECTED_COUNTS["decision_rows"]
        and Counter(str(row["action"]) for row in decisions)
        == Counter(EXPECTED_ACTION_COUNTS),
        "decision action partition drifted",
    )
    coordinates = {str(row["coordinate"]) for row in decisions}
    require(
        coordinates == set(evidence["accepted_pending_coordinates"])
        and coordinate_digest(coordinates) == EXPECTED_DIGESTS["decision"]
        and not {
            parse_coordinate(value)[:2] for value in coordinates
        } & blocked_roots,
        "decision coordinate partition drifted",
    )
    for row in decisions:
        reviewed_text = str(row["reviewed_translation"])
        require(
            row.get("schema") == PRIVATE_DECISION_SCHEMA
            and row.get("resource") == "pk_msggame"
            and row.get("fresh_semantic_review") == "approved"
            and row.get("historical_factuality_review") == "approved"
            and row.get("speaker_tone_review") == "approved"
            and row.get("runtime_review") == "verified"
            and row.get("layout_review")
            == "current_relative_raw_g1n_nonexpanding"
            and row.get("multilingual_context_role")
            == "en_sc_tc_advisory_jp_authoritative"
            and row.get("root_rewrite_attempt_count") == 1
            and utf16le_sha256(reviewed_text)
            == row.get("reviewed_utf16le_sha256")
            and parse_coordinate(str(row["coordinate"]))[:2]
            in accepted_roots,
            "decision semantic or layout proof drifted",
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
        len(overrides) == 4
        and coordinate_digest(overrides) == EXPECTED_DIGESTS["override"]
        and len(promoted) == 10
        and coordinate_digest(promoted) == EXPECTED_DIGESTS["promoted"],
        "override or promotion partition drifted",
    )
    return overrides, promoted


def validate_evidence(
    evidence: Mapping[str, Any],
    context: Mapping[str, Any],
    layout: Mapping[str, Any],
    accepted_roots: set[tuple[int, int]],
    blocked_roots: set[tuple[int, int]],
) -> None:
    require(
        evidence.get("schema") == PRIVATE_EVIDENCE_SCHEMA
        and evidence.get("method") == METHOD
        and evidence.get("counts") == EXPECTED_COUNTS,
        "private evidence identity or counts drifted",
    )
    proof = evidence["proof"]
    require(
        proof["all_pending_rows_freshly_reviewed"]
        and proof["fresh_review_limited_to_chunk1_pending_rows"]
        and proof["jp_authoritative"]
        and proof["en_sc_tc_advisory_only"]
        and proof["historical_factuality_reviewed"]
        and proof["speaker_tone_reviewed"]
        and proof["all_accepted_branches_current_relative_nonexpanding"]
        and proof["affected_ordinary_branches_computed_once"]
        and not proof["layout_518_branch_recompute_performed"]
        and proof["register_atom_consistency_preserved_by_atomic_block"]
        and not proof["repeat_risk_translation_copied_from_neighbor"]
        and proof["reverse_overlay_recovers_official_candidate"]
        and proof["terminal_records_read_only"]
        and proof["terminal_automatic_promotion_count"] == 0
        and proof["source_only_action_count"] == 0
        and proof["non_display_action_count"] == 0
        and proof["owned_overlap_automatic_promotion_count"] == 0
        and proof["prior_pending_evidence_automatic_promotion_count"] == 0
        and proof["maximum_rewrite_attempts_per_root"] == 1
        and proof["control_gap_change_count"] == 0
        and proof["linebreak_change_count"] == 0
        and not proof["steam_write_performed"],
        "private evidence proof drifted",
    )
    require(
        context["multilingual_authority"]["jp_authoritative"]
        and context["multilingual_authority"]["en_sc_tc_advisory_only"],
        "multilingual authority drifted",
    )
    layout_counts = layout["counts"]
    require(
        layout_counts["total_runtime_assemblies"] == 518
        and layout_counts["terminal_verified_read_only_rows"] == 6
        and layout_counts["terminal_pending_read_only_rows"] == 1
        and layout_counts["terminal_decision_rows"] == 0
        and layout_counts["source_only_sites"] == 5
        and layout_counts["source_only_actions"] == 0
        and not layout["proof"]["root_rewrite_not_performed"]
        is False,
        "reused layout manifest drifted",
    )
    attempted_roots = {
        parse_coordinate(value)[:2]
        for value in evidence["blocked_attempt_overrides"]
    }
    require(
        len(attempted_roots) == 2
        and attempted_roots < blocked_roots
        and any(
            {parse_root(root) for root in atom} == attempted_roots
            for atom in context.get("register_root_atoms", [])
        ) is False,
        "context register data unexpectedly owns review partition",
    )
    register_atoms = [
        {parse_root(root) for root in atom}
        for atom in load_json(ASSIGNMENT_PATH)["register_root_atoms"]
    ]
    require(
        attempted_roots in register_atoms
        and parse_root(
            load_json(ASSIGNMENT_PATH)["register_repeat_risk"]["root"]
        ) in accepted_roots
        and load_json(ASSIGNMENT_PATH)["register_repeat_risk"][
            "automatic_atom_union_authorized"
        ] is False,
        "register atom or repeat-risk guard drifted",
    )


def build_report() -> dict[str, Any]:
    assignment, context, layout, evidence, decisions = validate_inputs()
    (
        chunk,
        accepted_roots,
        blocked_roots,
        read_only_roots,
        hard_block_roots,
    ) = validate_assignment(assignment, evidence)
    validate_evidence(
        evidence, context, layout, accepted_roots, blocked_roots
    )
    overrides, promoted = validate_decisions(
        decisions, evidence, accepted_roots, blocked_roots
    )
    require(
        evidence["digests"]["decision_coordinate_sha256"]
        == EXPECTED_DIGESTS["decision"]
        and evidence["digests"]["override_coordinate_sha256"]
        == EXPECTED_DIGESTS["override"]
        and evidence["digests"]["promoted_coordinate_sha256"]
        == EXPECTED_DIGESTS["promoted"],
        "private coordinate digest drifted",
    )

    candidate, current, source, _contexts, _pending = (
        ASSIGNMENT.RECORDS.load_records()
    )
    live_path = (
        WRAPPER.RANKING_WRAPPER.DEFAULT_STEAM_ROOT
        / "MSG_PK" / "JP" / "msggame.bin"
    )
    steam_before = sha256_file(live_path)
    require(
        steam_before == EXPECTED_SHA256["live_steam"],
        "live Steam archive drifted",
    )
    replacements, _ = RANKING.load_official_ledger(OFFICIAL_LEDGER_PATH)
    candidate_blob = ENGINE.rebuild_packed_with_literals(
        live_path.read_bytes(), replacements
    )
    require(
        sha256_bytes(candidate_blob) == EXPECTED_SHA256["official_candidate"],
        "official candidate reconstruction drifted",
    )
    reviewed_blob = ENGINE.rebuild_packed_with_literals(
        candidate_blob,
        {
            parse_coordinate(coordinate): translation
            for coordinate, translation in overrides.items()
        },
    )
    require(
        sha256_bytes(reviewed_blob) == EXPECTED_SHA256["reviewed_candidate"],
        "reviewed candidate drifted",
    )
    reviewed = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(reviewed_blob).archive
    )
    for row in decisions:
        coordinate = str(row["coordinate"])
        require(
            row["jp_source_utf16le_sha256"]
            == utf16le_sha256(literal_text(source, coordinate))
            and row["current_ko_utf16le_sha256"]
            == utf16le_sha256(literal_text(current, coordinate))
            and row["reviewed_utf16le_sha256"]
            == utf16le_sha256(literal_text(reviewed, coordinate))
            and row["reviewed_translation"]
            == literal_text(reviewed, coordinate),
            "decision text hash proof drifted",
        )
        if row["action"] == "runtime_promotion":
            require(
                literal_text(candidate, coordinate)
                == literal_text(reviewed, coordinate),
                "runtime-only promotion changed translation",
            )
    changed_roots = {
        root for root in candidate if candidate[root].data != reviewed[root].data
    }
    override_roots = {
        parse_coordinate(coordinate)[:2] for coordinate in overrides
    }
    require(
        changed_roots == override_roots
        and len(changed_roots) == 2
        and changed_roots < accepted_roots,
        "changed root set drifted",
    )
    for root in changed_roots:
        before = ENGINE.parse_record_literals(candidate[root])
        after = ENGINE.parse_record_literals(reviewed[root])
        require(
            ENGINE.record_gap_bytes(candidate[root])
            == ENGINE.record_gap_bytes(reviewed[root])
            and len(before) == len(after)
            and all(
                old.text.count("\n") == new.text.count("\n")
                for old, new in zip(before, after)
            ),
            "record control or linebreak drifted",
        )
    reverse_blob = ENGINE.rebuild_packed_with_literals(
        reviewed_blob,
        {
            parse_coordinate(coordinate): literal_text(candidate, coordinate)
            for coordinate in overrides
        },
    )
    require(
        reverse_blob == candidate_blob
        and sha256_bytes(reverse_blob)
        == EXPECTED_SHA256["official_candidate"],
        "reverse overlay drifted",
    )

    terminal_roots = tuple((0, terminal) for terminal in TERMINALS)
    require(
        len(terminal_roots) == 7
        and terminal_digest(candidate, terminal_roots)
        == EXPECTED_SHA256["terminal_candidate"]
        and terminal_digest(current, terminal_roots)
        == EXPECTED_SHA256["terminal_current"]
        and terminal_digest(source, terminal_roots)
        == EXPECTED_SHA256["terminal_source"],
        "read-only terminal text guard drifted",
    )
    terminal_manifest = assignment["shared_terminal_ownership"][
        "terminal_manifest"
    ]
    terminal_coordinates = {str(row["coordinate"]) for row in terminal_manifest}
    require(
        len(terminal_manifest) == 7
        and Counter(str(row["runtime_review"]) for row in terminal_manifest)
        == Counter({"verified": 6, "pending": 1})
        and all(
            row["read_only"]
            and not row["automatic_status_promotion_authorized"]
            for row in terminal_manifest
        )
        and not terminal_coordinates
        & {str(row["coordinate"]) for row in decisions},
        "terminal ownership guard drifted",
    )

    accepted_sites = [
        site
        for site in chunk["sites"]
        if RANKING.site_key(site)[:2] in accepted_roots
    ]
    accepted_manifest = branch_manifest(
        sites=accepted_sites,
        selected=reviewed,
        current=current,
        terminals=terminal_roots,
        disposition="accepted",
    )
    require(
        len(accepted_sites) == 3
        and len(accepted_manifest) == 21
        and all(bool(row[-2]) for row in accepted_manifest)
        and canonical_sha256(accepted_manifest)
        == EXPECTED_DIGESTS["accepted_branches"],
        "accepted affected-branch proof drifted",
    )

    attempt_overrides = {
        parse_coordinate(coordinate): str(translation)
        for coordinate, translation
        in evidence["blocked_attempt_overrides"].items()
    }
    attempt_blob = ENGINE.rebuild_packed_with_literals(
        candidate_blob, attempt_overrides
    )
    attempted = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(attempt_blob).archive
    )
    attempted_roots = {
        coordinate[:2] for coordinate in attempt_overrides
    }
    attempt_sites = [
        site
        for site in chunk["sites"]
        if RANKING.site_key(site)[:2] in attempted_roots
    ]
    blocked_attempt_manifest = branch_manifest(
        sites=attempt_sites,
        selected=attempted,
        current=current,
        terminals=terminal_roots,
        disposition="blocked_after_one_root_attempt",
    )
    failed_sites = Counter(
        str(row[0]) for row in blocked_attempt_manifest if not row[-2]
    )
    require(
        len(attempt_sites) == 2
        and len(blocked_attempt_manifest) == 14
        and sum(bool(row[-2]) for row in blocked_attempt_manifest) == 12
        and sorted(failed_sites.values()) == [1, 1]
        and canonical_sha256(blocked_attempt_manifest)
        == EXPECTED_DIGESTS["blocked_attempt_branches"],
        "blocked root-attempt proof drifted",
    )
    affected_manifest = accepted_manifest + blocked_attempt_manifest
    require(
        len(affected_manifest) == 35
        and sum(bool(row[-2]) for row in affected_manifest) == 33
        and canonical_sha256(affected_manifest)
        == EXPECTED_DIGESTS["affected_branches"],
        "affected branch manifest drifted",
    )

    layout_fields = layout["root_layout_field_order"]
    layout_by_root = {
        parse_root(str(row[0])): dict(zip(layout_fields, row))
        for row in layout["per_root_layout"]
    }
    require(
        len(hard_block_roots) == 1
        and all(
            int(layout_by_root[root]["branch_count"]) == 7
            and bool(layout_by_root[root]["provisional_hard_block"])
            for root in hard_block_roots
        ),
        "reused hard-block layout proof drifted",
    )
    require(
        len(read_only_roots) == EXPECTED_COUNTS["read_only_nonpending_roots"]
        and len(promoted) == EXPECTED_COUNTS["promoted_pending_rows"]
        and sha256_file(live_path) == steam_before,
        "read-only count, promotion count, or Steam immutability drifted",
    )

    report = {
        "distribution_policy": {
            "private_decisions_stay_below_tmp": True,
            "private_evidence_stays_below_tmp": True,
            "private_generator_stays_below_tmp": True,
            "tracked_builder_contains_dialogue_bodies": False,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_test_contains_dialogue_bodies": False,
            "tracked_validator_uses_frozen_private_hashes": True,
        },
        "guards": {
            "accepted_branch_manifest_sha256":
                EXPECTED_DIGESTS["accepted_branches"],
            "action_counts": EXPECTED_ACTION_COUNTS,
            "affected_branch_manifest_sha256":
                EXPECTED_DIGESTS["affected_branches"],
            "assignment_private_sha256":
                EXPECTED_SHA256["assignment_private"],
            "blocked_attempt_branch_manifest_sha256":
                EXPECTED_DIGESTS["blocked_attempt_branches"],
            "context_private_sha256": EXPECTED_SHA256["context_private"],
            "decision_coordinate_sha256": EXPECTED_DIGESTS["decision"],
            "decision_file_sha256": EXPECTED_SHA256["private_decisions"],
            "evidence_file_sha256": EXPECTED_SHA256["private_evidence"],
            "layout_private_sha256": EXPECTED_SHA256["layout_private"],
            "official_candidate_sha256":
                EXPECTED_SHA256["official_candidate"],
            "official_ledger_sha256": EXPECTED_SHA256["official_ledger"],
            "override_coordinate_sha256": EXPECTED_DIGESTS["override"],
            "private_generator_sha256":
                EXPECTED_SHA256["private_generator"],
            "promoted_coordinate_sha256": EXPECTED_DIGESTS["promoted"],
            "reverse_overlay_sha256":
                EXPECTED_SHA256["official_candidate"],
            "reviewed_candidate_sha256":
                EXPECTED_SHA256["reviewed_candidate"],
            "steam_archive_sha256_after": sha256_file(live_path),
            "steam_archive_sha256_before": steam_before,
            "terminal_candidate_sha256":
                EXPECTED_SHA256["terminal_candidate"],
            "terminal_current_sha256": EXPECTED_SHA256["terminal_current"],
            "terminal_source_sha256": EXPECTED_SHA256["terminal_source"],
        },
        "method": METHOD,
        "proof": {
            "accepted_affected_branches_current_relative_nonexpanding": True,
            "affected_ordinary_branches_computed_once": True,
            "all_changed_record_control_gaps_preserved": True,
            "all_literal_linebreak_counts_preserved": True,
            "all_pending_rows_freshly_reviewed": True,
            "blocked_roots_received_no_decisions": True,
            "full_layout_manifest_recomputed": False,
            "hard_block_branch_proof_reused": True,
            "historical_factuality_reviewed": True,
            "jp_authoritative": True,
            "maximum_rewrite_attempts_per_root": 1,
            "non_display_action_count": 0,
            "owned_overlap_automatic_promotion_count": 0,
            "prior_pending_evidence_automatic_promotion_count": 0,
            "register_atom_consistency_preserved_by_atomic_block": True,
            "repeat_risk_translation_copied_from_neighbor": False,
            "reverse_overlay_recovers_official_candidate": True,
            "source_only_action_count": 0,
            "speaker_tone_reviewed": True,
            "terminal_automatic_promotion_count": 0,
            "terminal_rows_read_only": True,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": EXPECTED_COUNTS,
        "schema": PUBLIC_SCHEMA,
        "scope": {
            "chunk_id": CHUNK_ID,
            "selector": SELECTOR,
            "terminal_count": len(TERMINALS),
            "workload_weight": 342,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    validate_source_free(report)
    return report


def build_output() -> bytes:
    return serialized(build_report())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--bootstrap-public", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    content = build_output()
    output_sha256 = sha256_bytes(content)
    if not args.bootstrap_public:
        require(
            EXPECTED_PUBLIC_FILE_SHA256 is not None
            and output_sha256 == EXPECTED_PUBLIC_FILE_SHA256,
            f"public output hash drifted: {output_sha256}",
        )
        require(
            DEFAULT_PUBLIC_OUTPUT.is_file()
            and DEFAULT_PUBLIC_OUTPUT.read_bytes() == content,
            "public artifact drifted",
        )
    print(json.dumps({
        "accepted_pending": EXPECTED_COUNTS["accepted_pending_rows"],
        "affected_branches": EXPECTED_COUNTS[
            "affected_ordinary_branches_computed"
        ],
        "blocked_pending": EXPECTED_COUNTS["blocked_pending_rows"],
        "output_sha256": output_sha256,
        "reviewed_candidate_sha256":
            EXPECTED_SHA256["reviewed_candidate"],
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
