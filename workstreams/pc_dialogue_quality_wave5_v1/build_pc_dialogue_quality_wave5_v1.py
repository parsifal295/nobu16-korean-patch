#!/usr/bin/env python3
"""Build the next PC-only dialogue-quality candidate without writing Steam.

Wave 5 is intentionally layered on the pinned Wave 4 output. Every new
change is sourced from a reviewed JSONL audit row: it pins the current Korean
record, checks the matching pristine PC Japanese literal tuple, changes only
listed literals, and removes only listed Japanese 01 43 commands.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
WAVE4_SCRIPT = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave4_v1"
    / "build_pc_dialogue_quality_wave4_v1.py"
)
AUDIT_BASE_SUFFIX_BATCH01 = WORKSTREAM / "audit" / "audit_base_suffix_batch01.jsonl"
AUDIT_BASE_SUFFIX_BATCH02 = WORKSTREAM / "audit" / "audit_base_suffix_batch02.jsonl"
AUDIT_BASE_DANGGA_SAFE_BATCH = WORKSTREAM / "audit" / "audit_base_dangga_safe_batch.jsonl"
AUDIT_RESIDUAL_KOREAN_QUALITY = (
    WORKSTREAM / "audit" / "audit_residual_korean_quality_scan_v1.jsonl"
)
AUDIT_RESIDUAL_KOREAN_QUALITY_HOLDS = (
    WORKSTREAM / "audit" / "audit_residual_korean_quality_scan_hold_v1.jsonl"
)
AUDIT_RESIDUAL_KOREAN_QUALITY_PK_14_226_REVIEW = (
    WORKSTREAM / "audit" / "audit_residual_korean_quality_pk_14_226_review_v2.jsonl"
)
AUDIT_PK_COLON_SAMEPC_DONORS = WORKSTREAM / "audit_pk_colon_samepc_donors.jsonl"
AUDIT_PK_SAMEPK_DONORS = WORKSTREAM / "audit_pk_samepk_donors.jsonl"
AUDIT_PK_RUNTIME_SUFFIX_6547 = WORKSTREAM / "audit_pk_runtime_suffix_6547.jsonl"
AUDIT_PK_RELATION_LOGS = WORKSTREAM / "audit_pk_relation_logs.jsonl"
AUDIT_PK_RUNTIME_PARTICLE_HOLDS = WORKSTREAM / "audit_pk_donor_runtime_particle_holds.jsonl"
AUDIT_PK_DONOR_CONFLICTS = WORKSTREAM / "audit_pk_donor_conflicts_resolved.jsonl"
AUDIT_PK_DONOR_CONFLICT_REVIEW = (
    WORKSTREAM / "audit_pk_donor_conflicts_independent_quality_review_20260718.md"
)
AUDIT_PK_DONOR_CONFLICT_SPACING_REPAIRS = (
    WORKSTREAM / "audit_pk_donor_conflict_spacing_repairs.jsonl"
)
AUDIT_EVENT_LINEBREAKS_PK_STATIC_REPAIR = (
    WORKSTREAM / "audit_event_linebreaks_pk_static_repair_v2.jsonl"
)
AUDIT_EVENT_LINEBREAKS_BASE_HOLDS = (
    WORKSTREAM / "audit_event_linebreaks_base_hold_requirements_v2.jsonl"
)
EVENT_PK_RESOURCE = "MSG_PK/JP/msgev.bin"
EVENT_BASE_RESOURCE = "MSG/JP/ev_strdata.bin"
AUDIT_PK_RUNTIME_PARTICLE_RECLASSIFICATION = (
    WORKSTREAM / "audit_pk_colon_manual_96_runtime_particle_reclassification.json"
)

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, parse_link, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
import validate_g1n_surgical as g1n  # noqa: E402


def load_wave4():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave4", WAVE4_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Wave 4 builder: {WAVE4_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE4 = load_wave4()
DEFAULT_STEAM_ROOT = WAVE4.DEFAULT_STEAM_ROOT
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name / "candidate"
DEFAULT_MANIFEST = REPO / "tmp" / WORKSTREAM.name / "build_manifest.v1.json"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave5.v1"
BASELINE_SHA256 = WAVE4.BASELINE_SHA256
PROFILE_PATHS = WAVE4.PROFILE_PATHS
CHANGED_PATHS = tuple(dict.fromkeys((*WAVE4.CHANGED_PATHS, EVENT_PK_RESOURCE)))
if EVENT_PK_RESOURCE not in PROFILE_PATHS:
    raise RuntimeError(f"Wave 4 profile lacks required event resource: {EVENT_PK_RESOURCE}")

# Pinned from the source-gated release candidate after all Wave 5 audit
# batches below were integrated.  The apply transaction rejects any candidate
# that does not reproduce this full 11-file profile exactly.
TARGET_SHA256: dict[str, str] | None = {
    "MSG/JP/ev_strdata.bin": "25D9C029F93788053720C04BAE0C0A14A1A5983F36C68BC2EC7C46C3340D5834",
    "MSG/JP/msggame.bin": "32247AB97112243E58F8EB5B2930EE8A8AB9DF6A2FE0907A49AE28A255720610",
    "MSG/JP/strdata.bin": "10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752",
    "MSG_PK/JP/msgev.bin": "134F6356B194AE319125D369A23EBDA11CA8C75FB79EFA7C987D956EDD4CF154",
    "MSG_PK/JP/msggame.bin": "51320EE41C17608BC6DD558B35F5243793BBD74168E51BE8C7F7B65E136B330D",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
EVENT_PK_TARGET_RAW_SHA256 = "FB00108F13CB243E3FB90E27B5C67C00CED8BB0931CB2F6D0E02DFFC0DC3AB98"
EVENT_PK_TARGET_PACKED_SHA256 = "134F6356B194AE319125D369A23EBDA11CA8C75FB79EFA7C987D956EDD4CF154"
EVENT_PK_LOGICAL_SIZE_DELTA = -4
RESIDUAL_KOREAN_QUALITY_AUDIT_SHA256 = (
    "0362E214C97B0435745FDCF89536D28026BDC9A210C54915FEED64D1FF5AAFB3"
)
RESIDUAL_KOREAN_QUALITY_HOLDS_SHA256 = (
    "69D4F1B6E4F182E9AD1C2D5A32C0E48A34B7985D146F402F81BC491A35534755"
)
RESIDUAL_KOREAN_QUALITY_PK_14_226_REVIEW_SHA256 = (
    "7A23D4DE2E953D13A1BBA34446A8693F6DD5C85457B3119807855FEDB0D4B660"
)


class Wave5Error(ValueError):
    """A Wave 5 audit, source, or byte-preservation contract failed."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def parse_coordinate(value: str) -> tuple[int, int]:
    try:
        block, record = value.split(":", 1)
        return int(block), int(record)
    except (AttributeError, ValueError) as exc:
        raise Wave5Error(f"invalid coordinate: {value!r}") from exc


def read_jsonl(path: Path) -> tuple[dict[str, Any], ...]:
    if not path.is_file():
        raise Wave5Error(f"missing Wave 5 audit data: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise Wave5Error(f"{path}:{line_number} is not JSON") from exc
        if not isinstance(row, dict):
            raise Wave5Error(f"{path}:{line_number} must contain an object")
        rows.append(row)
    if not rows:
        raise Wave5Error(f"no audit rows in {path}")
    return tuple(rows)


def read_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise Wave5Error(f"missing Wave 5 audit data: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Wave5Error(f"{path} is not JSON") from exc
    if not isinstance(value, dict):
        raise Wave5Error(f"{path} must contain an object")
    return value


EVENT_LINEBREAK_RE = re.compile(r"\r\n|\r|\n")
EVENT_RUNTIME_BRACKET_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
EVENT_RUNTIME_TOKEN_RE = re.compile(r"\[([A-Za-z]{1,16})(\d+)\]")
EVENT_ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
EVENT_WIDE_SCRIPT_RE = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]"
)


def event_text_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def event_protected_contract(value: str) -> dict[str, Any]:
    invariant = common.message_invariants(value)
    return {
        "printf": invariant["printf"],
        "unknown_percent_count": invariant["unknown_percent_count"],
        "esc": invariant["esc"],
        "controls": invariant["controls"],
        "pua": invariant["pua"],
        "runtime_brackets": EVENT_RUNTIME_BRACKET_RE.findall(value),
    }


def event_line_count(value: str) -> int:
    return 1 + len(EVENT_LINEBREAK_RE.findall(value))


def event_nonwhitespace_skeleton(value: str) -> str:
    return "".join(character for character in value if not character.isspace())


def require_event_coordinate(row: dict[str, Any], expected_resource: str) -> int:
    coordinate = row.get("coordinate")
    if not isinstance(coordinate, dict):
        raise Wave5Error("event-linebreak coordinate is invalid")
    if coordinate.get("resource") != expected_resource or coordinate.get("index_base") != 0:
        raise Wave5Error("event-linebreak coordinate resource/index is invalid")
    record_id = coordinate.get("record_id")
    if not isinstance(record_id, int) or record_id < 0:
        raise Wave5Error("event-linebreak record ID is invalid")
    return record_id


def require_event_text_contract(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise Wave5Error(f"{label} text contract is invalid")
    literal = value.get("literal")
    if not isinstance(literal, str):
        raise Wave5Error(f"{label} literal is invalid")
    if value.get("utf16le_sha256") != event_text_sha256(literal):
        raise Wave5Error(f"{label} UTF-16LE hash mismatch")
    linebreak_vector = value.get("linebreak_vector")
    if linebreak_vector != EVENT_LINEBREAK_RE.findall(literal):
        raise Wave5Error(f"{label} line-break vector mismatch")
    if value.get("protected_contract") != event_protected_contract(literal):
        raise Wave5Error(f"{label} protected-token contract mismatch")
    return value


def validate_event_line_width_contract(value: dict[str, Any], label: str) -> None:
    literal = value["literal"]
    actual = value.get("actual_line_width_px")
    reserved = value.get("reserved_line_width_px")
    line_count = event_line_count(literal)
    if (
        not isinstance(actual, list)
        or not isinstance(reserved, list)
        or len(actual) != line_count
        or len(reserved) != line_count
        or not all(isinstance(width, int) and width >= 0 for width in actual)
        or not all(isinstance(width, int) and width > 0 for width in reserved)
    ):
        raise Wave5Error(f"{label} line-width evidence is invalid")
    if any(width > budget for width, budget in zip(actual, reserved)):
        raise Wave5Error(f"{label} measured width exceeds its reserved width")


def require_sha256(value: Any, label: str) -> str:
    result = str(value or "").upper()
    if len(result) != 64 or any(character not in "0123456789ABCDEF" for character in result):
        raise Wave5Error(f"{label} is not a SHA-256 value")
    return result


def validate_event_pk_static_repair_row(row: dict[str, Any]) -> None:
    if row.get("schema") != "nobu16.kr.pc-event-linebreak-static-repair-evidence.v2":
        raise Wave5Error("unexpected PK event-linebreak repair schema")
    if row.get("disposition") != "static_pk_candidate_not_applied":
        raise Wave5Error("unapproved PK event-linebreak repair disposition")
    record_id = require_event_coordinate(row, EVENT_PK_RESOURCE)
    current = require_event_text_contract(row.get("current"), f"PK event {record_id} current")
    replacement = require_event_text_contract(
        row.get("replacement"), f"PK event {record_id} replacement"
    )
    validate_event_line_width_contract(current, f"PK event {record_id} current")
    validate_event_line_width_contract(replacement, f"PK event {record_id} replacement")
    invariants = row.get("invariants")
    if not isinstance(invariants, dict):
        raise Wave5Error(f"PK event {record_id} invariants are invalid")
    if invariants.get("protected_contract_equal") is not True:
        raise Wave5Error(f"PK event {record_id} lacks protected-token equality")
    if event_protected_contract(current["literal"]) != event_protected_contract(replacement["literal"]):
        raise Wave5Error(f"PK event {record_id} changes protected tokens")
    if invariants.get("same_nonwhitespace_skeleton") is not True:
        raise Wave5Error(f"PK event {record_id} lacks skeleton equality")
    if event_nonwhitespace_skeleton(current["literal"]) != event_nonwhitespace_skeleton(
        replacement["literal"]
    ):
        raise Wave5Error(f"PK event {record_id} changes its non-whitespace skeleton")
    if event_line_count(replacement["literal"]) != invariants.get(
        "replacement_line_count"
    ):
        raise Wave5Error(f"PK event {record_id} replacement line count mismatch")
    line_count_max = invariants.get("line_count_max")
    if not isinstance(line_count_max, int) or line_count_max != 3:
        raise Wave5Error(f"PK event {record_id} does not pin the three-line renderer limit")
    if event_line_count(replacement["literal"]) > line_count_max:
        raise Wave5Error(f"PK event {record_id} exceeds its line limit")
    max_reserved_width = invariants.get("replacement_max_reserved_width_px")
    if not isinstance(max_reserved_width, int) or not 0 < max_reserved_width <= 912:
        raise Wave5Error(f"PK event {record_id} lacks the 3x912px width contract")
    if max(replacement["reserved_line_width_px"]) != max_reserved_width:
        raise Wave5Error(f"PK event {record_id} replacement width maximum mismatch")
    profile = row.get("input_profile")
    if not isinstance(profile, dict):
        raise Wave5Error(f"PK event {record_id} input profile is invalid")
    if require_sha256(profile.get("table_packed_sha256"), f"PK event {record_id} table hash") != BASELINE_SHA256[EVENT_PK_RESOURCE]:
        raise Wave5Error(f"PK event {record_id} table input hash differs from Steam baseline")
    require_sha256(profile.get("table_raw_sha256"), f"PK event {record_id} raw table hash")
    require_sha256(profile.get("font_packed_sha256"), f"PK event {record_id} font hash")
    if (
        profile.get("font_resource") != "RES_JP/res_lang.bin"
        or profile.get("font_outer_entry") != 6
        or profile.get("font_table") != 0
    ):
        raise Wave5Error(f"PK event {record_id} font route is invalid")


def validate_event_base_hold_row(row: dict[str, Any]) -> None:
    if row.get("schema") != "nobu16.kr.pc-event-linebreak-base-hold.v2":
        raise Wave5Error("unexpected Base event-linebreak hold schema")
    if row.get("application_eligible") is not False:
        raise Wave5Error("Base event-linebreak hold is not explicitly ineligible")
    if row.get("disposition") != "hold_no_base_ev_strdata_runtime_container_evidence":
        raise Wave5Error("unexpected Base event-linebreak hold disposition")
    record_id = require_event_coordinate(row, EVENT_BASE_RESOURCE)
    source = row.get("base_input")
    if not isinstance(source, dict) or source.get("current_ko_table_packed_sha256") != BASELINE_SHA256[
        "MSG/JP/ev_strdata.bin"
    ]:
        raise Wave5Error(f"Base event {record_id} input hash differs from Steam baseline")
    requirements = row.get("qa_requirements")
    if not isinstance(requirements, list) or not requirements:
        raise Wave5Error(f"Base event {record_id} has no real-game QA requirements")


def plans_from_suffix_audit(row: dict[str, Any]):
    if row.get("schema") != "nobu16.kr.pc-dialogue-quality-wave5.audit.v1":
        raise Wave5Error(f"unexpected audit schema at {row.get('coordinate')!r}")
    if row.get("status") not in {
        "high_confidence_static_suffix",
        "high_confidence_runtime_safe",
        "high_confidence_semantic_and_suffix",
        "high_confidence_static_suffix_family",
    }:
        raise Wave5Error(f"unapproved audit status at {row.get('coordinate')!r}")
    coordinates = row.get("coordinates")
    if coordinates is None:
        coordinates = [row.get("coordinate")]
    if not isinstance(coordinates, list) or not coordinates:
        raise Wave5Error(f"invalid coordinates at {row.get('coordinate')!r}")
    parsed_coordinates = tuple(parse_coordinate(str(value)) for value in coordinates)
    current = row.get("current_ko_literals")
    replacement = row.get("replacement_literals")
    if not isinstance(current, list) or not isinstance(replacement, list) or len(current) != len(replacement):
        raise Wave5Error(f"{parsed_coordinates[0]} literal tuple is invalid")
    changes = tuple(
        WAVE4.change(index, expected, result)
        for index, (expected, result) in enumerate(zip(current, replacement))
        if expected != result
    )
    if not changes:
        raise Wave5Error(f"{parsed_coordinates[0]} has no literal change")
    remove = row.get("remove")
    if not isinstance(remove, list) or not remove:
        raise Wave5Error(f"{parsed_coordinates[0]} has no exact removed command")
    removed = tuple(
        WAVE4.remove_command(int(item["offset"]), str(item["hex"]))
        for item in remove
    )
    current_hash = str(row.get("current_record_sha256", "")).upper()
    output_hash = str(row.get("output_record_sha256", "")).upper()
    if len(current_hash) != 64 or len(output_hash) != 64:
        raise Wave5Error(f"{parsed_coordinates[0]} lacks a full record hash")
    source_literals = row.get("pc_jp_literals")
    if not isinstance(source_literals, list):
        raise Wave5Error(f"{parsed_coordinates[0]} lacks PC Japanese literals")
    return tuple(
        (
            WAVE4.plan(block_id, record_id, current_hash, changes, remove_commands=removed),
            tuple(source_literals),
            output_hash,
        )
        for block_id, record_id in parsed_coordinates
    )


def plan_from_base_dangga_audit(row: dict[str, Any]):
    if row.get("schema") != "nobu16.kr.pc-dialogue-quality-wave5.audit.v1":
        raise Wave5Error(f"unexpected dangga audit schema at {row.get('coordinate')!r}")
    if row.get("status") != "high_confidence_dangga_literal":
        raise Wave5Error(f"unapproved dangga audit status at {row.get('coordinate')!r}")
    if row.get("resource") != "MSG/JP/msggame.bin":
        raise Wave5Error(f"dangga audit resource is invalid at {row.get('coordinate')!r}")
    coordinate = parse_coordinate(str(row.get("coordinate")))
    current = require_literal_tuple(row, "current_ko_literals", coordinate)
    replacement = require_literal_tuple(row, "replacement_literals", coordinate)
    if len(current) != len(replacement):
        raise Wave5Error(f"{coordinate} dangga literal count changed")
    changes = tuple(
        WAVE4.change(index, expected, result)
        for index, (expected, result) in enumerate(zip(current, replacement))
        if expected != result
    )
    if len(changes) != 1 or row.get("literal_change_count") != 1:
        raise Wave5Error(f"{coordinate} dangga audit must make exactly one literal change")
    current_hash = str(row.get("current_record_sha256", "")).upper()
    output_hash = str(row.get("output_record_sha256", "")).upper()
    if len(current_hash) != 64 or len(output_hash) != 64:
        raise Wave5Error(f"{coordinate} dangga audit lacks a full record hash")
    source_literals = require_literal_tuple(row, "pc_jp_literals", coordinate)
    source_label = str(row.get("source", ""))
    if "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4" not in source_label:
        raise Wave5Error(f"{coordinate} dangga audit does not pin the pristine PC Japanese source")
    current_opaque = str(row.get("current_opaque_hex", "")).upper()
    output_opaque = str(row.get("asserted_output_opaque_hex", "")).upper()
    if not current_opaque or current_opaque != output_opaque:
        raise Wave5Error(f"{coordinate} dangga audit opaque bytes are invalid")
    if row.get("asserted_output_opaque_preserved") is not True:
        raise Wave5Error(f"{coordinate} dangga audit lacks opaque preservation assertion")
    if row.get("opaque_policy") != "Preserve every opaque byte byte-for-byte; no commands are removed or rewritten.":
        raise Wave5Error(f"{coordinate} dangga audit opaque policy is invalid")
    if row.get("manual_line_count_after") not in {1, 2, 3}:
        raise Wave5Error(f"{coordinate} dangga audit has an unsafe line count")
    return WAVE4.plan(coordinate[0], coordinate[1], current_hash, changes), source_literals, output_hash, row


def opaque_schema(record) -> tuple[str, ...]:
    return tuple(span.hex().upper() for _offset, span in WAVE4.opaque_spans(record))


def require_literal_tuple(row: dict[str, Any], key: str, coordinate: tuple[int, int]) -> tuple[str, ...]:
    value = row.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise Wave5Error(f"{coordinate} lacks a literal tuple in {key}")
    return tuple(value)


def require_opaque_schema(row: dict[str, Any], key: str, coordinate: tuple[int, int]) -> tuple[str, ...]:
    value = row.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise Wave5Error(f"{coordinate} lacks an opaque schema in {key}")
    return tuple(item.upper() for item in value)


def plan_from_pk_donor_audit(row: dict[str, Any]):
    kind = row.get("kind")
    if kind not in {"colon_samepc_base_donor", "same_pk_exact_donor"}:
        raise Wave5Error(f"unapproved PK donor kind: {kind!r}")
    if row.get("resource") != "MSG_PK/JP/msggame.bin":
        raise Wave5Error(f"PK donor resource is invalid at {row.get('coordinate')!r}")
    coordinate = parse_coordinate(str(row.get("coordinate")))
    current = require_literal_tuple(row, "current_literals", coordinate)
    output = require_literal_tuple(row, "asserted_output_literals", coordinate)
    if len(current) != len(output):
        raise Wave5Error(f"{coordinate} PK donor literal count changed")
    changes = tuple(
        WAVE4.change(index, expected, replacement)
        for index, (expected, replacement) in enumerate(zip(current, output))
        if expected != replacement
    )
    if not changes:
        raise Wave5Error(f"{coordinate} PK donor has no literal change")
    expected_hash = str(row.get("current_record_sha256", "")).upper()
    output_hash = str(row.get("asserted_output_record_sha256", "")).upper()
    if len(expected_hash) != 64 or len(output_hash) != 64:
        raise Wave5Error(f"{coordinate} PK donor lacks a record hash")
    if row.get("asserted_target_opaque_preserved") is not True:
        raise Wave5Error(f"{coordinate} PK donor lacks opaque preservation assertion")
    target_schema = require_opaque_schema(row, "target_current_opaque_schema", coordinate)
    output_schema = require_opaque_schema(row, "asserted_output_opaque_schema", coordinate)
    if target_schema != output_schema:
        raise Wave5Error(f"{coordinate} PK donor changes opaque schema")
    return (
        WAVE4.plan(coordinate[0], coordinate[1], expected_hash, changes),
        row,
        output_hash,
    )


def plan_from_pk_runtime_suffix_audit(row: dict[str, Any]):
    if row.get("kind") != "runtime_suffix_pc_precedent_repair":
        raise Wave5Error(f"unapproved PK runtime suffix kind: {row.get('kind')!r}")
    if row.get("resource") != "MSG_PK/JP/msggame.bin":
        raise Wave5Error(f"PK runtime suffix resource is invalid at {row.get('coordinate')!r}")
    coordinate = parse_coordinate(str(row.get("coordinate")))
    current = require_literal_tuple(row, "current_literals", coordinate)
    proposed = require_literal_tuple(row, "proposed_literals", coordinate)
    if len(current) != len(proposed):
        raise Wave5Error(f"{coordinate} PK runtime suffix literal count changed")
    changes = tuple(
        WAVE4.change(index, expected, replacement)
        for index, (expected, replacement) in enumerate(zip(current, proposed))
        if expected != replacement
    )
    if not changes:
        raise Wave5Error(f"{coordinate} PK runtime suffix has no literal change")
    removed_raw = row.get("remove_commands")
    if not isinstance(removed_raw, list) or not removed_raw:
        raise Wave5Error(f"{coordinate} PK runtime suffix has no removed command")
    removed = tuple(
        WAVE4.remove_command(int(item["offset"], 16), str(item["hex"]))
        for item in removed_raw
    )
    expected_hash = str(row.get("current_record_sha256", "")).upper()
    output_hash = str(row.get("asserted_output_record_sha256", "")).upper()
    if len(expected_hash) != 64 or len(output_hash) != 64:
        raise Wave5Error(f"{coordinate} PK runtime suffix lacks a record hash")
    return (
        WAVE4.plan(
            coordinate[0],
            coordinate[1],
            expected_hash,
            changes,
            remove_commands=removed,
        ),
        row,
        output_hash,
    )


def plan_from_pk_relation_log_audit(row: dict[str, Any]):
    if row.get("kind") != "manual_relation_log_literal_repair":
        raise Wave5Error(f"unapproved PK relation-log kind: {row.get('kind')!r}")
    if row.get("resource") != "MSG_PK/JP/msggame.bin":
        raise Wave5Error(f"PK relation-log resource is invalid at {row.get('coordinate')!r}")
    if row.get("change_scope") != "literal-only; no 0143/runtime opcode removal":
        raise Wave5Error(f"PK relation-log change scope is invalid at {row.get('coordinate')!r}")
    coordinate = parse_coordinate(str(row.get("coordinate")))
    current = require_literal_tuple(row, "current_literals", coordinate)
    proposed = require_literal_tuple(row, "proposed_literals", coordinate)
    asserted_output = require_literal_tuple(row, "asserted_output_literals", coordinate)
    if proposed != asserted_output:
        raise Wave5Error(f"{coordinate} relation-log proposal/output literal mismatch")
    if len(current) != len(proposed):
        raise Wave5Error(f"{coordinate} relation-log literal count changed")
    changes = tuple(
        WAVE4.change(index, expected, replacement)
        for index, (expected, replacement) in enumerate(zip(current, proposed))
        if expected != replacement
    )
    if not changes:
        raise Wave5Error(f"{coordinate} relation-log has no literal change")
    expected_hash = str(row.get("current_record_sha256", "")).upper()
    output_hash = str(row.get("asserted_output_record_sha256", "")).upper()
    if len(expected_hash) != 64 or len(output_hash) != 64:
        raise Wave5Error(f"{coordinate} relation-log lacks a full record hash")
    if row.get("asserted_target_opaque_preserved") is not True:
        raise Wave5Error(f"{coordinate} relation-log lacks opaque preservation assertion")
    current_schema = require_opaque_schema(row, "current_opaque_schema", coordinate)
    output_schema = require_opaque_schema(row, "asserted_output_opaque_schema", coordinate)
    if current_schema != output_schema:
        raise Wave5Error(f"{coordinate} relation-log changes opaque schema")
    pristine_jp = require_literal_tuple(row, "pristine_pc_jp_literals", coordinate)
    if not pristine_jp:
        raise Wave5Error(f"{coordinate} relation-log lacks pristine PC Japanese literals")
    if not isinstance(row.get("resolution_note"), str) or not row["resolution_note"].strip():
        raise Wave5Error(f"{coordinate} relation-log lacks a resolution note")
    return WAVE4.plan(coordinate[0], coordinate[1], expected_hash, changes), row, output_hash


def validate_pk_runtime_particle_holds_against_donors(
    rows: tuple[dict[str, Any], ...],
    raw_donors: dict[tuple[int, int], dict[str, Any]],
) -> None:
    for row in rows:
        if row.get("schema") != "nobu16.kr.pc-dialogue-quality-wave5.runtime-particle-hold.v1":
            raise Wave5Error(f"unexpected PK runtime particle hold schema at {row.get('coordinate')!r}")
        if row.get("resource") != "MSG_PK/JP/msggame.bin":
            raise Wave5Error(f"PK runtime particle hold resource is invalid at {row.get('coordinate')!r}")
        coordinate = parse_coordinate(str(row.get("coordinate")))
        if row.get("eligible_for_steam_application") is not False:
            raise Wave5Error(f"PK runtime particle hold must be Steam-ineligible: {coordinate}")
        categories = row.get("hold_categories")
        evidence = row.get("runtime_suffix_evidence")
        if not isinstance(categories, list) or not categories or not all(
            isinstance(value, str) for value in categories
        ):
            raise Wave5Error(f"PK runtime particle hold lacks categories: {coordinate}")
        if not isinstance(evidence, list) or not evidence or not all(
            isinstance(value, dict) for value in evidence
        ):
            raise Wave5Error(f"PK runtime particle hold lacks runtime evidence: {coordinate}")
        donor = raw_donors.get(coordinate)
        if donor is None:
            raise Wave5Error(f"PK runtime particle hold has no source donor: {coordinate}")
        if row.get("candidate_kind") != donor.get("kind"):
            raise Wave5Error(f"PK runtime particle hold donor kind changed: {coordinate}")
        if str(row.get("current_record_sha256", "")).upper() != str(
            donor.get("current_record_sha256", "")
        ).upper():
            raise Wave5Error(f"PK runtime particle hold input hash changed: {coordinate}")
        if str(row.get("asserted_output_record_sha256", "")).upper() != str(
            donor.get("asserted_output_record_sha256", "")
        ).upper():
            raise Wave5Error(f"PK runtime particle hold donor output hash changed: {coordinate}")
        if require_literal_tuple(row, "current_literals", coordinate) != require_literal_tuple(
            donor, "current_literals", coordinate
        ):
            raise Wave5Error(f"PK runtime particle hold current literals changed: {coordinate}")
        if require_literal_tuple(row, "asserted_output_literals", coordinate) != require_literal_tuple(
            donor, "asserted_output_literals", coordinate
        ):
            raise Wave5Error(f"PK runtime particle hold donor output literals changed: {coordinate}")
        if require_opaque_schema(row, "target_current_opaque_schema", coordinate) != require_opaque_schema(
            donor, "target_current_opaque_schema", coordinate
        ):
            raise Wave5Error(f"PK runtime particle hold opaque schema changed: {coordinate}")
        override = row.get("relation_repair_override")
        relation_row = PK_RELATION_LOG_ROWS_BY_COORDINATE.get(coordinate)
        if relation_row is None:
            if override is not None:
                raise Wave5Error(f"unexpected relation override in runtime particle hold: {coordinate}")
            continue
        if not isinstance(override, dict) or override.get("available") is not True:
            raise Wave5Error(f"relation override is not explicit for runtime particle hold: {coordinate}")
        if override.get("audit_file") != AUDIT_PK_RELATION_LOGS.name:
            raise Wave5Error(f"relation override audit file is invalid: {coordinate}")
        if override.get("requires_explicit_plan_precedence") is not True:
            raise Wave5Error(f"relation override precedence is not explicit: {coordinate}")
        if str(override.get("asserted_output_record_sha256", "")).upper() != str(
            relation_row.get("asserted_output_record_sha256", "")
        ).upper():
            raise Wave5Error(f"relation override output hash is invalid: {coordinate}")


def plans_from_pk_conflict_spacing_repair(
    row: dict[str, Any], conflict_rows: dict[tuple[int, int], dict[str, Any]]
):
    if row.get("schema") != "nobu16.kr.pc-dialogue-quality-wave5.pk-donor-conflict-spacing-repair.v1":
        raise Wave5Error(f"unexpected PK conflict repair schema at {row.get('coordinates')!r}")
    if row.get("status") != "candidate_after_spacing_repair_requires_runtime_ui_qa":
        raise Wave5Error(f"unapproved PK conflict repair status at {row.get('coordinates')!r}")
    if row.get("source_conflict_audit_sha256") != sha256_bytes(AUDIT_PK_DONOR_CONFLICTS.read_bytes()):
        raise Wave5Error("PK conflict repair source audit hash mismatch")
    if row.get("independent_review_sha256") != sha256_bytes(AUDIT_PK_DONOR_CONFLICT_REVIEW.read_bytes()):
        raise Wave5Error("PK conflict repair independent-review hash mismatch")
    coordinates_raw = row.get("coordinates")
    if not isinstance(coordinates_raw, list) or not coordinates_raw:
        raise Wave5Error("PK conflict repair coordinates are invalid")
    coordinates = tuple(parse_coordinate(str(value)) for value in coordinates_raw)
    replacement = require_literal_tuple(row, "replacement_literals", coordinates[0])
    output_hash = str(row.get("asserted_output_record_sha256", "")).upper()
    if len(output_hash) != 64:
        raise Wave5Error(f"{coordinates[0]} conflict repair lacks an output hash")
    line_count = row.get("manual_line_count")
    if line_count not in {1, 2, 3}:
        raise Wave5Error(f"{coordinates[0]} conflict repair line count is invalid")
    output = []
    for coordinate in coordinates:
        conflict = conflict_rows.get(coordinate)
        if conflict is None:
            raise Wave5Error(f"PK conflict repair is not backed by a conflict row: {coordinate}")
        if conflict.get("kind") != "manual_naturalization_resolves_divergent_donors":
            raise Wave5Error(f"PK conflict repair has an unapproved conflict kind: {coordinate}")
        if conflict.get("resource") != "MSG_PK/JP/msggame.bin":
            raise Wave5Error(f"PK conflict repair resource is invalid: {coordinate}")
        if conflict.get("pc_jp_literal_tuple_match") is not True or conflict.get(
            "pc_jp_opaque_schema_match"
        ) is not True:
            raise Wave5Error(f"PK conflict repair lacks PC JP equivalence: {coordinate}")
        if conflict.get("asserted_target_opaque_preserved") is not True:
            raise Wave5Error(f"PK conflict repair lacks opaque preservation: {coordinate}")
        current = require_literal_tuple(conflict, "current_literals", coordinate)
        if len(current) != len(replacement):
            raise Wave5Error(f"PK conflict repair literal count changed: {coordinate}")
        changes = tuple(
            WAVE4.change(index, expected, result)
            for index, (expected, result) in enumerate(zip(current, replacement))
            if expected != result
        )
        if not changes:
            raise Wave5Error(f"PK conflict repair has no literal change: {coordinate}")
        expected_hash = str(conflict.get("current_record_sha256", "")).upper()
        if len(expected_hash) != 64:
            raise Wave5Error(f"PK conflict repair lacks input hash: {coordinate}")
        output.append((WAVE4.plan(coordinate[0], coordinate[1], expected_hash, changes), conflict, output_hash, row))
    return tuple(output)


RESIDUAL_RESOURCE_BY_LABEL = {
    "Base": "MSG/JP/msggame.bin",
    "PK": "MSG_PK/JP/msggame.bin",
}


def residual_text_sha256(value: str) -> str:
    # The residual audit predates the event JSONL schema and records its
    # literal evidence as UTF-8 SHA-256 (the record-level pins remain raw
    # byte SHA-256).  Keep that distinction explicit here rather than
    # silently treating the two audit formats as interchangeable.
    return sha256_bytes(value.encode("utf-8"))


def residual_visible_line_count(value: str) -> int:
    return len(value.splitlines()) or 1


def residual_excerpt_matches(value: str, excerpt: str) -> bool:
    normalized_value = "".join(character for character in value if not character.isspace())
    cursor = 0
    for fragment in (part for part in excerpt.split("...") if part):
        normalized_fragment = "".join(
            character for character in fragment if not character.isspace()
        )
        found = normalized_value.find(normalized_fragment, cursor)
        if found < 0:
            return False
        cursor = found + len(normalized_fragment)
    return True


def require_residual_opaque_schema(
    row: dict[str, Any], coordinate: tuple[int, int]
) -> tuple[tuple[int, str], ...]:
    value = row.get("opaque_schema")
    if not isinstance(value, list) or not value:
        raise Wave5Error(f"{coordinate} residual opaque schema is invalid")
    result: list[tuple[int, str]] = []
    for item in value:
        if not isinstance(item, dict):
            raise Wave5Error(f"{coordinate} residual opaque schema item is invalid")
        raw_offset = item.get("offset")
        raw_hex = item.get("hex")
        if not isinstance(raw_offset, str) or not isinstance(raw_hex, str):
            raise Wave5Error(f"{coordinate} residual opaque schema item is invalid")
        try:
            offset = int(raw_offset, 0)
            bytes.fromhex(raw_hex)
        except ValueError as exc:
            raise Wave5Error(f"{coordinate} residual opaque schema item is malformed") from exc
        result.append((offset, raw_hex.upper()))
    if len({offset for offset, _value in result}) != len(result):
        raise Wave5Error(f"{coordinate} residual opaque schema has duplicate offsets")
    return tuple(result)


def residual_opaque_bytes_from_schema(
    row: dict[str, Any], coordinate: tuple[int, int]
) -> bytes:
    return b"".join(
        bytes.fromhex(value) for _offset, value in require_residual_opaque_schema(row, coordinate)
    )


def load_residual_korean_quality_audit() -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    if sha256_bytes(AUDIT_RESIDUAL_KOREAN_QUALITY.read_bytes()) != RESIDUAL_KOREAN_QUALITY_AUDIT_SHA256:
        raise Wave5Error("residual Korean-quality audit hash mismatch")
    if (
        sha256_bytes(AUDIT_RESIDUAL_KOREAN_QUALITY_HOLDS.read_bytes())
        != RESIDUAL_KOREAN_QUALITY_HOLDS_SHA256
    ):
        raise Wave5Error("residual Korean-quality hold audit hash mismatch")
    rows = read_jsonl(AUDIT_RESIDUAL_KOREAN_QUALITY)
    metadata_rows = tuple(row for row in rows if row.get("record_type") == "metadata")
    candidate_rows = tuple(row for row in rows if row.get("record_type") != "metadata")
    if len(metadata_rows) != 1 or not candidate_rows:
        raise Wave5Error("residual Korean-quality audit metadata/candidate shape is invalid")
    metadata = metadata_rows[0]
    if metadata.get("schema") != "pc_dialogue_quality_residual_scan_v1":
        raise Wave5Error("residual Korean-quality audit schema is invalid")
    basis = metadata.get("basis")
    if not isinstance(basis, dict):
        raise Wave5Error("residual Korean-quality audit basis is invalid")
    expected_basis = {
        "wave4_base_output_sha256": WAVE4.TARGET_SHA256["MSG/JP/msggame.bin"],
        "wave4_pk_output_sha256": WAVE4.TARGET_SHA256["MSG_PK/JP/msggame.bin"],
        "pristine_pc_jp_base_sha256": WAVE4.WAVE3.PRISTINE_SOURCES[
            "MSG/JP/msggame.bin"
        ][1],
        "pristine_pc_jp_pk_sha256": WAVE4.WAVE3.PRISTINE_SOURCES[
            "MSG_PK/JP/msggame.bin"
        ][1],
    }
    if basis != expected_basis:
        raise Wave5Error("residual Korean-quality audit PC-source basis differs")
    if metadata.get("line_count_method") != "visible physical lines: len(text.splitlines()) or 1":
        raise Wave5Error("residual Korean-quality audit line-count method differs")
    if metadata.get("opaque_policy") != "All opaque spans are preserved byte-for-byte; replacement changes static literal payloads only.":
        raise Wave5Error("residual Korean-quality audit opaque policy differs")
    if (
        sha256_bytes(AUDIT_RESIDUAL_KOREAN_QUALITY_PK_14_226_REVIEW.read_bytes())
        != RESIDUAL_KOREAN_QUALITY_PK_14_226_REVIEW_SHA256
    ):
        raise Wave5Error("residual Korean-quality PK 14:226 review hash mismatch")
    review_rows = read_jsonl(AUDIT_RESIDUAL_KOREAN_QUALITY_PK_14_226_REVIEW)
    if len(review_rows) != 1:
        raise Wave5Error("residual Korean-quality PK 14:226 review count differs")
    review = review_rows[0]
    if (
        review.get("supersedes_audit_sha256") != RESIDUAL_KOREAN_QUALITY_AUDIT_SHA256
        or review.get("supersedes_coordinate") != "14:226"
        or review.get("resource") != "PK"
        or review.get("coordinate") != "14:226"
        or not isinstance(review.get("review"), str)
    ):
        raise Wave5Error("residual Korean-quality PK 14:226 review provenance differs")
    original_target_rows = tuple(
        row
        for row in candidate_rows
        if row.get("resource") == "PK" and row.get("coordinate") == "14:226"
    )
    if len(original_target_rows) != 1:
        raise Wave5Error("residual Korean-quality original PK 14:226 row differs")
    effective_candidate_rows = tuple(
        row for row in candidate_rows if row not in original_target_rows
    ) + review_rows
    if len(effective_candidate_rows) != len(candidate_rows):
        raise Wave5Error("residual Korean-quality review changed candidate count")
    coordinates: set[tuple[str, tuple[int, int]]] = set()
    for row in effective_candidate_rows:
        if (
            row.get("schema") != "pc_dialogue_quality_residual_scan_v1"
            or row.get("status") != "high_confidence_static_candidate"
        ):
            raise Wave5Error("residual Korean-quality candidate status/schema is invalid")
        label = row.get("resource")
        if label not in RESIDUAL_RESOURCE_BY_LABEL:
            raise Wave5Error("residual Korean-quality candidate resource is invalid")
        coordinate = parse_coordinate(str(row.get("coordinate")))
        key = (str(label), coordinate)
        if key in coordinates:
            raise Wave5Error(f"residual Korean-quality audit has duplicate coordinate: {key}")
        coordinates.add(key)
        require_sha256(row.get("current_record_sha256"), f"{coordinate} residual current hash")
        require_sha256(row.get("output_record_sha256"), f"{coordinate} residual output hash")
        require_sha256(row.get("pristine_pc_jp_record_sha256"), f"{coordinate} residual PC JP hash")
        if row.get("opaque_schema_preserved") is not True or row.get("has_0143_opcode") is not False:
            raise Wave5Error(f"{coordinate} residual opaque/0143 policy is invalid")
        require_residual_opaque_schema(row, coordinate)
        changes = row.get("literal_changes")
        if not isinstance(changes, list) or not changes:
            raise Wave5Error(f"{coordinate} residual literal changes are invalid")
    holds = read_jsonl(AUDIT_RESIDUAL_KOREAN_QUALITY_HOLDS)
    if len(holds) != 4:
        raise Wave5Error("residual Korean-quality hold count differs")
    for row in holds:
        if row.get("schema") != "pc_dialogue_quality_residual_scan_v1" or row.get("status") != "hold":
            raise Wave5Error("residual Korean-quality hold status/schema is invalid")
    return effective_candidate_rows, holds


def materialize_residual_korean_quality_plans(
    relative: str, wave4_resource: bytes
) -> tuple[tuple[Any, dict[str, Any], str], ...]:
    label = next(
        (candidate for candidate, value in RESIDUAL_RESOURCE_BY_LABEL.items() if value == relative),
        None,
    )
    if label is None:
        raise Wave5Error(f"unexpected residual Korean-quality resource: {relative}")
    source_path, source_hash = WAVE4.WAVE3.PRISTINE_SOURCES[relative]
    if WAVE4.WAVE3.sha256_path(source_path) != source_hash:
        raise Wave5Error(f"residual Korean-quality PC JP source hash differs: {relative}")
    source_records = WAVE4.records_by_coordinate(source_path.read_bytes())
    records = WAVE4.records_by_coordinate(wave4_resource)
    result: list[tuple[Any, dict[str, Any], str]] = []
    for row in RESIDUAL_KOREAN_QUALITY_ROWS:
        if row["resource"] != label:
            continue
        coordinate = parse_coordinate(str(row["coordinate"]))
        record = records.get(coordinate)
        source = source_records.get(coordinate)
        if record is None or source is None:
            raise Wave5Error(f"residual Korean-quality record is absent: {relative} {coordinate}")
        if sha256_bytes(record.data) != require_sha256(
            row["current_record_sha256"], f"{coordinate} residual current hash"
        ):
            raise Wave5Error(f"residual Korean-quality current record hash changed: {coordinate}")
        if sha256_bytes(source.data) != require_sha256(
            row["pristine_pc_jp_record_sha256"], f"{coordinate} residual PC JP hash"
        ):
            raise Wave5Error(f"residual Korean-quality PC JP record hash changed: {coordinate}")
        actual_opaque = tuple(
            (offset, span.hex().upper()) for offset, span in WAVE4.opaque_spans(record)
        )
        if actual_opaque != require_residual_opaque_schema(row, coordinate):
            raise Wave5Error(f"residual Korean-quality opaque schema changed: {coordinate}")
        if WAVE4.opaque_commands(record):
            raise Wave5Error(f"residual Korean-quality record contains 0143: {coordinate}")
        current_literals = {
            literal.literal_id: literal.text for literal in WAVE4.parse_record_literals(record)
        }
        source_literals = {
            literal.literal_id: literal.text for literal in WAVE4.parse_record_literals(source)
        }
        plans = []
        for change_row in row["literal_changes"]:
            if not isinstance(change_row, dict) or not isinstance(change_row.get("literal_id"), int):
                raise Wave5Error(f"{coordinate} residual literal-change shape is invalid")
            literal_id = change_row["literal_id"]
            current = current_literals.get(literal_id)
            source_literal = source_literals.get(literal_id)
            if current is None or source_literal is None:
                raise Wave5Error(f"{coordinate} residual literal slot is absent: {literal_id}")
            expected_current = change_row.get("current_literal")
            current_hash = change_row.get("current_literal_sha256")
            if not isinstance(expected_current, str) and not isinstance(current_hash, str):
                raise Wave5Error(f"{coordinate} residual current literal lacks exact evidence")
            if isinstance(expected_current, str) and current != expected_current:
                raise Wave5Error(f"{coordinate} residual current literal changed: {literal_id}")
            if isinstance(current_hash, str) and residual_text_sha256(current) != require_sha256(
                current_hash, f"{coordinate} residual current literal hash"
            ):
                raise Wave5Error(f"{coordinate} residual current literal hash changed: {literal_id}")
            source_literal_expected = change_row.get("pc_jp_literal")
            source_literal_hash = change_row.get("pc_jp_literal_sha256")
            source_excerpt = change_row.get("pc_jp_literal_excerpt")
            if not any(
                isinstance(value, str)
                for value in (source_literal_expected, source_literal_hash, source_excerpt)
            ):
                raise Wave5Error(f"{coordinate} residual PC JP literal evidence is absent")
            if isinstance(source_literal_expected, str) and source_literal != source_literal_expected:
                raise Wave5Error(f"{coordinate} residual PC JP literal changed: {literal_id}")
            if isinstance(source_literal_hash, str) and residual_text_sha256(source_literal) != require_sha256(
                source_literal_hash, f"{coordinate} residual PC JP literal hash"
            ):
                raise Wave5Error(f"{coordinate} residual PC JP literal hash changed: {literal_id}")
            if isinstance(source_excerpt, str) and not residual_excerpt_matches(source_literal, source_excerpt):
                raise Wave5Error(f"{coordinate} residual PC JP excerpt changed: {literal_id}")
            replacement = change_row.get("replacement_literal")
            if not isinstance(replacement, str):
                replacement = current
                replacements = change_row.get("exact_replacements")
                if not isinstance(replacements, list) or not replacements:
                    raise Wave5Error(f"{coordinate} residual replacements are invalid: {literal_id}")
                for item in replacements:
                    if not isinstance(item, dict):
                        raise Wave5Error(f"{coordinate} residual replacement is invalid: {literal_id}")
                    before = item.get("from")
                    after = item.get("to")
                    if not isinstance(before, str) or not before or not isinstance(after, str) or not after:
                        raise Wave5Error(f"{coordinate} residual replacement is invalid: {literal_id}")
                    if replacement.count(before) < 1:
                        raise Wave5Error(
                            f"{coordinate} residual replacement source is absent: {literal_id}"
                        )
                    # A single audited literal can contain the same role label
                    # more than once.  The record and output hashes below pin
                    # the complete intended result, while this replacement is
                    # still restricted to that one literal slot.
                    replacement = replacement.replace(before, after)
            if not replacement or "\x00" in replacement or replacement == current:
                raise Wave5Error(f"{coordinate} residual replacement is invalid: {literal_id}")
            replacement_hash = change_row.get("replacement_literal_sha256")
            if isinstance(replacement_hash, str) and residual_text_sha256(replacement) != require_sha256(
                replacement_hash, f"{coordinate} residual replacement literal hash"
            ):
                raise Wave5Error(
                    f"{coordinate} residual replacement literal hash changed: {literal_id}"
                )
            if residual_visible_line_count(current) != change_row.get("line_count_before"):
                raise Wave5Error(f"{coordinate} residual current line count changed: {literal_id}")
            if residual_visible_line_count(replacement) != change_row.get("line_count_after"):
                raise Wave5Error(f"{coordinate} residual output line count changed: {literal_id}")
            plans.append(WAVE4.change(literal_id, current, replacement))
        if len({plan.literal_id for plan in plans}) != len(plans):
            raise Wave5Error(f"{coordinate} residual literal changes are duplicated")
        result.append(
            (
                WAVE4.plan(
                    coordinate[0],
                    coordinate[1],
                    require_sha256(row["current_record_sha256"], f"{coordinate} residual current hash"),
                    tuple(plans),
                ),
                row,
                require_sha256(row["output_record_sha256"], f"{coordinate} residual output hash"),
            )
        )
    if not result:
        raise Wave5Error(f"residual Korean-quality audit has no rows for {relative}")
    return tuple(result)


def rebuild_residual_korean_quality_resource(
    packed: bytes,
    items: tuple[tuple[Any, dict[str, Any], str], ...],
    relative: str,
    base_records: dict[tuple[int, int], Any],
) -> bytes:
    """Apply explicitly audited static help/UI literals without a 3-line cap.

    Wave 4's generic quality builder rightly rejects long dialogue records.
    These residual entries are different: each existing manual line is kept,
    the per-literal before/after line counts are pinned in the audit, and only
    static UI/help labels are changed.  This local path retains every byte and
    topology check from the generic builder while refusing 0143 removal.
    """
    plans = tuple(item[0] for item in items)
    coordinates = [plan.coordinate for plan in plans]
    if len(coordinates) != len(set(coordinates)):
        raise Wave5Error(f"residual Korean-quality plans are duplicated: {relative}")
    before = WAVE4.records_by_coordinate(packed)
    replacements: dict[tuple[int, int], bytes] = {}
    opaque_contracts: dict[tuple[int, int], bytes] = {}
    rows = {plan.coordinate: row for plan, row, _output in items}
    for plan in plans:
        if plan.remove_commands:
            raise Wave5Error(f"residual Korean-quality plan removes opaque commands: {plan.coordinate}")
        record = before.get(plan.coordinate)
        if record is None:
            raise Wave5Error(f"residual Korean-quality record is absent: {plan.coordinate}")
        if sha256_bytes(record.data) != plan.expected_sha256:
            raise Wave5Error(f"residual Korean-quality input record changed: {plan.coordinate}")
        WAVE4.assert_anchor(base_records, plan)
        literals = {literal.literal_id: literal.text for literal in WAVE4.parse_record_literals(record)}
        literal_replacements: dict[int, str] = {}
        for change in plan.changes:
            if literals.get(change.literal_id) != change.expected_text:
                raise Wave5Error(
                    f"residual Korean-quality current literal changed: {plan.coordinate}/{change.literal_id}"
                )
            if change.expected_text == change.replacement or "\x00" in change.replacement:
                raise Wave5Error(
                    f"residual Korean-quality replacement is invalid: {plan.coordinate}/{change.literal_id}"
                )
            literal_replacements[change.literal_id] = change.replacement
        if len(literal_replacements) != len(plan.changes):
            raise Wave5Error(f"residual Korean-quality literal changes are duplicated: {plan.coordinate}")
        opaque_contracts[plan.coordinate] = WAVE4.opaque_bytes(record)
        replacements[plan.coordinate] = WAVE4.rebuild_quality_record(
            record, plan, literal_replacements
        )
    rebuilt = WAVE4.rebuild_packed_msggame(packed, replacements)
    after = WAVE4.records_by_coordinate(rebuilt)
    if set(after) != set(before):
        raise Wave5Error(f"residual Korean-quality record topology changed: {relative}")
    for coordinate, original in before.items():
        if after[coordinate].data != replacements.get(coordinate, original.data):
            raise Wave5Error(f"residual Korean-quality rebuilt-record mismatch: {coordinate}")
    for plan, row, output_hash in items:
        record = after[plan.coordinate]
        if sha256_bytes(record.data) != output_hash:
            raise Wave5Error(f"residual Korean-quality output record hash changed: {plan.coordinate}")
        if WAVE4.opaque_bytes(record) != opaque_contracts[plan.coordinate]:
            raise Wave5Error(f"residual Korean-quality opaque bytes changed: {plan.coordinate}")
        literals = {literal.literal_id: literal.text for literal in WAVE4.parse_record_literals(record)}
        for change_row in row["literal_changes"]:
            literal_id = change_row["literal_id"]
            replacement = next(
                change.replacement for change in plan.changes if change.literal_id == literal_id
            )
            if literals.get(literal_id) != replacement:
                raise Wave5Error(
                    f"residual Korean-quality output literal changed: {plan.coordinate}/{literal_id}"
                )
            if residual_visible_line_count(replacement) != change_row["line_count_after"]:
                raise Wave5Error(
                    f"residual Korean-quality output line count changed: {plan.coordinate}/{literal_id}"
                )
    return rebuilt


RESIDUAL_KOREAN_QUALITY_ROWS, RESIDUAL_KOREAN_QUALITY_HOLD_ROWS = (
    load_residual_korean_quality_audit()
)
if len(RESIDUAL_KOREAN_QUALITY_ROWS) != 16:
    raise Wave5Error("residual Korean-quality candidate count differs")
RESIDUAL_KOREAN_QUALITY_COORDINATES = {
    (row["resource"], parse_coordinate(str(row["coordinate"])))
    for row in RESIDUAL_KOREAN_QUALITY_ROWS
}

BASE_AUDIT_ROWS = read_jsonl(AUDIT_BASE_SUFFIX_BATCH01) + read_jsonl(AUDIT_BASE_SUFFIX_BATCH02)
BASE_AUDIT_ITEMS = tuple(
    item
    for row in BASE_AUDIT_ROWS
    for item in plans_from_suffix_audit(row)
)
BASE_DANGGA_AUDIT_ROWS = read_jsonl(AUDIT_BASE_DANGGA_SAFE_BATCH)
BASE_DANGGA_AUDIT_ITEMS = tuple(
    plan_from_base_dangga_audit(row) for row in BASE_DANGGA_AUDIT_ROWS
)
BASE_DANGGA_ROWS_BY_COORDINATE = {
    plan.coordinate: item[2] for plan, *item in BASE_DANGGA_AUDIT_ITEMS
}
if len(BASE_DANGGA_ROWS_BY_COORDINATE) != len(BASE_DANGGA_AUDIT_ITEMS):
    raise Wave5Error("Base dangga audit has duplicate coordinates")
BASE_EXTRA_PLANS = tuple(item[0] for item in BASE_AUDIT_ITEMS) + tuple(
    item[0] for item in BASE_DANGGA_AUDIT_ITEMS
)
BASE_EXPECTED_JP_LITERALS = {
    plan.coordinate: item[0] for plan, *item in BASE_AUDIT_ITEMS
}
BASE_EXPECTED_JP_LITERALS.update(
    {plan.coordinate: item[0] for plan, *item in BASE_DANGGA_AUDIT_ITEMS}
)
BASE_EXPECTED_OUTPUT_RECORD_SHA256 = {
    plan.coordinate: item[1] for plan, *item in BASE_AUDIT_ITEMS
}
BASE_EXPECTED_OUTPUT_RECORD_SHA256.update(
    {plan.coordinate: item[1] for plan, *item in BASE_DANGGA_AUDIT_ITEMS}
)
PK_COLON_DONOR_AUDIT_ROWS = read_jsonl(AUDIT_PK_COLON_SAMEPC_DONORS)
PK_SAMEPK_RAW_ROWS = read_jsonl(AUDIT_PK_SAMEPK_DONORS)
PK_RELATION_LOG_AUDIT_ROWS = read_jsonl(AUDIT_PK_RELATION_LOGS)
PK_RELATION_LOG_COORDINATES = {
    parse_coordinate(str(row.get("coordinate"))) for row in PK_RELATION_LOG_AUDIT_ROWS
}
if len(PK_RELATION_LOG_COORDINATES) != len(PK_RELATION_LOG_AUDIT_ROWS):
    raise Wave5Error("PK relation-log audit has duplicate coordinates")
PK_RELATION_LOG_AUDIT_ITEMS = tuple(
    plan_from_pk_relation_log_audit(row) for row in PK_RELATION_LOG_AUDIT_ROWS
)
PK_RELATION_LOG_ROWS_BY_COORDINATE = {
    plan.coordinate: item[0] for plan, *item in PK_RELATION_LOG_AUDIT_ITEMS
}
PK_RELATION_LOG_EXPECTED_OUTPUT_RECORD_SHA256 = {
    plan.coordinate: item[1] for plan, *item in PK_RELATION_LOG_AUDIT_ITEMS
}
PK_RUNTIME_PARTICLE_HOLD_AUDIT_ROWS = read_jsonl(AUDIT_PK_RUNTIME_PARTICLE_HOLDS)
PK_RUNTIME_PARTICLE_HOLD_COORDINATES = {
    parse_coordinate(str(row.get("coordinate"))) for row in PK_RUNTIME_PARTICLE_HOLD_AUDIT_ROWS
}
if len(PK_RUNTIME_PARTICLE_HOLD_COORDINATES) != len(PK_RUNTIME_PARTICLE_HOLD_AUDIT_ROWS):
    raise Wave5Error("PK runtime particle hold audit has duplicate coordinates")
PK_RUNTIME_PARTICLE_RECLASSIFICATION = read_json_object(
    AUDIT_PK_RUNTIME_PARTICLE_RECLASSIFICATION
)
if (
    PK_RUNTIME_PARTICLE_RECLASSIFICATION.get("schema")
    != "nobu16.kr.pc-dialogue-quality-wave5.pk-colon-runtime-particle-reclassification.v1"
):
    raise Wave5Error("unexpected PK runtime particle reclassification schema")
if PK_RUNTIME_PARTICLE_RECLASSIFICATION.get("source_audit_sha256", "").upper() != sha256_bytes(
    (WORKSTREAM / "audit_pk_colon_manual_96.jsonl").read_bytes()
):
    raise Wave5Error("PK runtime particle reclassification source audit hash mismatch")
PK_RUNTIME_PARTICLE_RECLASSIFICATION_ROWS = PK_RUNTIME_PARTICLE_RECLASSIFICATION.get("records")
if not isinstance(PK_RUNTIME_PARTICLE_RECLASSIFICATION_ROWS, list) or not all(
    isinstance(row, dict) for row in PK_RUNTIME_PARTICLE_RECLASSIFICATION_ROWS
):
    raise Wave5Error("PK runtime particle reclassification records are invalid")
PK_RUNTIME_PARTICLE_RECLASSIFICATION_BY_COORDINATE = {
    parse_coordinate(str(row.get("coordinate"))): row
    for row in PK_RUNTIME_PARTICLE_RECLASSIFICATION_ROWS
}
if len(PK_RUNTIME_PARTICLE_RECLASSIFICATION_BY_COORDINATE) != len(
    PK_RUNTIME_PARTICLE_RECLASSIFICATION_ROWS
):
    raise Wave5Error("PK runtime particle reclassification has duplicate coordinates")
for coordinate, row in PK_RUNTIME_PARTICLE_RECLASSIFICATION_BY_COORDINATE.items():
    if row.get("eligible_for_steam_application") is not False:
        raise Wave5Error(
            f"PK runtime particle reclassification must be explicitly Steam-ineligible: {coordinate}"
        )
    if not isinstance(row.get("final_application_status"), str):
        raise Wave5Error(f"PK runtime particle reclassification lacks final status: {coordinate}")
PK_COLON_DONOR_ROWS_BY_COORDINATE = {
    parse_coordinate(str(row.get("coordinate"))): row for row in PK_COLON_DONOR_AUDIT_ROWS
}
PK_COLON_DONOR_COORDINATES = set(PK_COLON_DONOR_ROWS_BY_COORDINATE)
PK_ALL_DONOR_COORDINATES = PK_COLON_DONOR_COORDINATES | {
    parse_coordinate(str(row.get("coordinate"))) for row in PK_SAMEPK_RAW_ROWS
}
PK_RUNTIME_PARTICLE_DONOR_HOLD_COORDINATES = {
    coordinate
    for coordinate in PK_RUNTIME_PARTICLE_RECLASSIFICATION_BY_COORDINATE
    if coordinate in PK_ALL_DONOR_COORDINATES
}
PK_SAMEPK_CONFLICT_ROWS = tuple(
    row
    for row in PK_SAMEPK_RAW_ROWS
    if (
        parse_coordinate(str(row.get("coordinate"))) in PK_COLON_DONOR_COORDINATES
        and str(row.get("asserted_output_record_sha256", "")).upper()
        != str(
            PK_COLON_DONOR_ROWS_BY_COORDINATE[
                parse_coordinate(str(row.get("coordinate")))
            ].get("asserted_output_record_sha256", "")
        ).upper()
    )
)
PK_SAMEPK_CONFLICT_COORDINATES = {
    parse_coordinate(str(row.get("coordinate"))) for row in PK_SAMEPK_CONFLICT_ROWS
}
PK_CONFLICT_AUDIT_ROWS = read_jsonl(AUDIT_PK_DONOR_CONFLICTS)
PK_CONFLICT_ROWS_BY_COORDINATE = {
    parse_coordinate(str(row.get("coordinate"))): row for row in PK_CONFLICT_AUDIT_ROWS
}
if len(PK_CONFLICT_ROWS_BY_COORDINATE) != len(PK_CONFLICT_AUDIT_ROWS):
    raise Wave5Error("PK donor conflict audit has duplicate coordinates")
PK_CONFLICT_REPAIR_AUDIT_ROWS = read_jsonl(AUDIT_PK_DONOR_CONFLICT_SPACING_REPAIRS)
PK_CONFLICT_REPAIR_ITEMS = tuple(
    item
    for row in PK_CONFLICT_REPAIR_AUDIT_ROWS
    for item in plans_from_pk_conflict_spacing_repair(row, PK_CONFLICT_ROWS_BY_COORDINATE)
)
PK_CONFLICT_REPAIR_ROWS_BY_COORDINATE = {
    plan.coordinate: item[2] for plan, *item in PK_CONFLICT_REPAIR_ITEMS
}
if len(PK_CONFLICT_REPAIR_ROWS_BY_COORDINATE) != len(PK_CONFLICT_REPAIR_ITEMS):
    raise Wave5Error("PK donor conflict repair audit has duplicate coordinates")
PK_CONFLICT_REPAIR_EXPECTED_OUTPUT_RECORD_SHA256 = {
    plan.coordinate: item[1] for plan, *item in PK_CONFLICT_REPAIR_ITEMS
}
PK_CONFLICT_REPAIR_COORDINATES = set(PK_CONFLICT_REPAIR_ROWS_BY_COORDINATE)
if PK_CONFLICT_REPAIR_COORDINATES != PK_SAMEPK_CONFLICT_COORDINATES:
    raise Wave5Error("PK donor conflict repair coordinates do not exactly cover donor conflicts")
if (4, 76) in PK_CONFLICT_REPAIR_COORDINATES:
    raise Wave5Error("PK 4:76 linebreak hold must not enter the conflict repair plan")
PK_LINEBREAK_HOLD_COORDINATES = {(4, 76)}
PK_JP_RUNTIME_CONTROL_HOLD_COORDINATES = {
    (6, 1545),
    (6, 1560),
    (6, 1635),
    (6, 3369),
    (6, 3377),
    (6, 3429),
    (6, 3584),
    (6, 3696),
    (6, 3697),
}
PK_UNRESOLVED_DONOR_COORDINATES = (
    PK_SAMEPK_CONFLICT_COORDINATES
    | PK_LINEBREAK_HOLD_COORDINATES
    | PK_JP_RUNTIME_CONTROL_HOLD_COORDINATES
    | PK_RUNTIME_PARTICLE_DONOR_HOLD_COORDINATES
)
PK_SAMEPK_CROSSCHECK_ROWS = tuple(
    row
    for row in PK_SAMEPK_RAW_ROWS
    if (
        parse_coordinate(str(row.get("coordinate"))) in PK_COLON_DONOR_COORDINATES
        and parse_coordinate(str(row.get("coordinate"))) not in PK_SAMEPK_CONFLICT_COORDINATES
    )
)
PK_SAMEPK_EXTRA_ROWS = tuple(
    row
    for row in PK_SAMEPK_RAW_ROWS
    if parse_coordinate(str(row.get("coordinate"))) not in PK_COLON_DONOR_COORDINATES
)
PK_RAW_DONOR_ROWS_BY_COORDINATE = dict(PK_COLON_DONOR_ROWS_BY_COORDINATE)
for _row in PK_SAMEPK_EXTRA_ROWS:
    _coordinate = parse_coordinate(str(_row.get("coordinate")))
    if _coordinate in PK_RAW_DONOR_ROWS_BY_COORDINATE:
        raise Wave5Error(f"duplicate raw PK donor coordinate: {_coordinate}")
    PK_RAW_DONOR_ROWS_BY_COORDINATE[_coordinate] = _row
validate_pk_runtime_particle_holds_against_donors(
    PK_RUNTIME_PARTICLE_HOLD_AUDIT_ROWS, PK_RAW_DONOR_ROWS_BY_COORDINATE
)
PK_RUNTIME_PARTICLE_RELATION_OVERRIDE_COORDINATES = {
    parse_coordinate(str(row.get("coordinate")))
    for row in PK_RUNTIME_PARTICLE_HOLD_AUDIT_ROWS
    if row.get("relation_repair_override") is not None
}
if PK_RUNTIME_PARTICLE_RELATION_OVERRIDE_COORDINATES != (
    PK_RUNTIME_PARTICLE_HOLD_COORDINATES & PK_RELATION_LOG_COORDINATES
):
    raise Wave5Error("runtime particle relation overrides do not cover every relation-log hold")
PK_RUNTIME_PARTICLE_GENERIC_DONOR_HOLD_COORDINATES = (
    PK_RUNTIME_PARTICLE_HOLD_COORDINATES - PK_RUNTIME_PARTICLE_RELATION_OVERRIDE_COORDINATES
)
PK_UNRESOLVED_DONOR_COORDINATES |= PK_RUNTIME_PARTICLE_GENERIC_DONOR_HOLD_COORDINATES
PK_DONOR_AUDIT_ROWS = (
    tuple(
        row
        for row in PK_COLON_DONOR_AUDIT_ROWS
        if (
            parse_coordinate(str(row.get("coordinate"))) not in PK_UNRESOLVED_DONOR_COORDINATES
            and parse_coordinate(str(row.get("coordinate"))) not in PK_RELATION_LOG_COORDINATES
        )
    )
    + tuple(
        row
        for row in PK_SAMEPK_EXTRA_ROWS
        if (
            parse_coordinate(str(row.get("coordinate"))) not in PK_UNRESOLVED_DONOR_COORDINATES
            and parse_coordinate(str(row.get("coordinate"))) not in PK_RELATION_LOG_COORDINATES
        )
    )
)
PK_DONOR_AUDIT_ITEMS = tuple(plan_from_pk_donor_audit(row) for row in PK_DONOR_AUDIT_ROWS)
PK_DONOR_ROWS_BY_COORDINATE = {
    plan.coordinate: item[0] for plan, *item in PK_DONOR_AUDIT_ITEMS
}
PK_DONOR_EXPECTED_OUTPUT_RECORD_SHA256 = {
    plan.coordinate: item[1] for plan, *item in PK_DONOR_AUDIT_ITEMS
}
PK_RUNTIME_SUFFIX_AUDIT_ROWS = read_jsonl(AUDIT_PK_RUNTIME_SUFFIX_6547)
PK_RUNTIME_SUFFIX_AUDIT_ITEMS = tuple(
    plan_from_pk_runtime_suffix_audit(row) for row in PK_RUNTIME_SUFFIX_AUDIT_ROWS
)
PK_RUNTIME_SUFFIX_ROWS_BY_COORDINATE = {
    plan.coordinate: item[0] for plan, *item in PK_RUNTIME_SUFFIX_AUDIT_ITEMS
}
PK_RUNTIME_SUFFIX_EXPECTED_OUTPUT_RECORD_SHA256 = {
    plan.coordinate: item[1] for plan, *item in PK_RUNTIME_SUFFIX_AUDIT_ITEMS
}
PK_EXTRA_PLANS = tuple(item[0] for item in PK_DONOR_AUDIT_ITEMS) + tuple(
    item[0] for item in PK_RELATION_LOG_AUDIT_ITEMS
) + tuple(item[0] for item in PK_CONFLICT_REPAIR_ITEMS) + tuple(
    item[0] for item in PK_RUNTIME_SUFFIX_AUDIT_ITEMS
)
PK_EXPECTED_OUTPUT_RECORD_SHA256 = {
    **PK_DONOR_EXPECTED_OUTPUT_RECORD_SHA256,
    **PK_RELATION_LOG_EXPECTED_OUTPUT_RECORD_SHA256,
    **PK_CONFLICT_REPAIR_EXPECTED_OUTPUT_RECORD_SHA256,
    **PK_RUNTIME_SUFFIX_EXPECTED_OUTPUT_RECORD_SHA256,
}

PK_EVENT_STATIC_REPAIR_AUDIT_ROWS = read_jsonl(AUDIT_EVENT_LINEBREAKS_PK_STATIC_REPAIR)
for _event_row in PK_EVENT_STATIC_REPAIR_AUDIT_ROWS:
    validate_event_pk_static_repair_row(_event_row)
PK_EVENT_STATIC_REPAIR_ROWS_BY_ID = {
    require_event_coordinate(row, EVENT_PK_RESOURCE): row for row in PK_EVENT_STATIC_REPAIR_AUDIT_ROWS
}
if len(PK_EVENT_STATIC_REPAIR_ROWS_BY_ID) != len(PK_EVENT_STATIC_REPAIR_AUDIT_ROWS):
    raise Wave5Error("PK event-linebreak repair audit has duplicate record IDs")
PK_EVENT_STATIC_REPAIR_IDS = tuple(sorted(PK_EVENT_STATIC_REPAIR_ROWS_BY_ID))
if PK_EVENT_STATIC_REPAIR_IDS != (5492, 6668):
    raise Wave5Error("PK event-linebreak repair set must be exactly 5492 and 6668")

BASE_EVENT_LINEBREAK_HOLD_AUDIT_ROWS = read_jsonl(AUDIT_EVENT_LINEBREAKS_BASE_HOLDS)
for _event_row in BASE_EVENT_LINEBREAK_HOLD_AUDIT_ROWS:
    validate_event_base_hold_row(_event_row)
BASE_EVENT_LINEBREAK_HOLD_ROWS_BY_ID = {
    require_event_coordinate(row, EVENT_BASE_RESOURCE): row
    for row in BASE_EVENT_LINEBREAK_HOLD_AUDIT_ROWS
}
if len(BASE_EVENT_LINEBREAK_HOLD_ROWS_BY_ID) != len(BASE_EVENT_LINEBREAK_HOLD_AUDIT_ROWS):
    raise Wave5Error("Base event-linebreak hold audit has duplicate record IDs")
BASE_EVENT_LINEBREAK_HOLD_IDS = tuple(sorted(BASE_EVENT_LINEBREAK_HOLD_ROWS_BY_ID))
if BASE_EVENT_LINEBREAK_HOLD_IDS != (4657, 4781, 6233, 6668, 7475, 16397):
    raise Wave5Error("Base event-linebreak holds do not match the reviewed set")
if EVENT_BASE_RESOURCE in CHANGED_PATHS:
    raise Wave5Error("Base event-linebreak holds must not enter the Wave 5 change set")


def validate_samepk_crosscheck_set() -> None:
    for row in PK_SAMEPK_CROSSCHECK_ROWS:
        if row.get("kind") != "same_pk_exact_donor":
            raise Wave5Error(f"unexpected same-PK crosscheck kind: {row.get('kind')!r}")
        coordinate = parse_coordinate(str(row.get("coordinate")))
        primary = PK_DONOR_ROWS_BY_COORDINATE.get(coordinate)
        if primary is None:
            raise Wave5Error(f"same-PK crosscheck has no same-PC primary plan: {coordinate}")
        if require_literal_tuple(row, "asserted_output_literals", coordinate) != require_literal_tuple(
            primary, "asserted_output_literals", coordinate
        ):
            raise Wave5Error(f"same-PK crosscheck output differs from primary plan: {coordinate}")
        if str(row.get("asserted_output_record_sha256", "")).upper() != str(
            primary.get("asserted_output_record_sha256", "")
        ).upper():
            raise Wave5Error(f"same-PK crosscheck record hash differs from primary plan: {coordinate}")


def require_span_contract(row: dict[str, Any], key: str, coordinate: tuple[int, int]) -> tuple[tuple[int, str], ...]:
    value = row.get(key)
    if not isinstance(value, list) or not value:
        raise Wave5Error(f"{coordinate} lacks opaque span contract in {key}")
    result: list[tuple[int, str]] = []
    for item in value:
        if not isinstance(item, dict) or "offset" not in item or "hex" not in item:
            raise Wave5Error(f"{coordinate} has malformed opaque span in {key}")
        result.append((int(str(item["offset"]), 0), str(item["hex"]).upper()))
    return tuple(result)


def opaque_span_contract(record) -> tuple[tuple[int, str], ...]:
    return tuple((offset, span.hex().upper()) for offset, span in WAVE4.opaque_spans(record))


def validate_pk_runtime_suffix_contracts(wave4_pk: bytes) -> None:
    source_path, _source_hash = WAVE4.WAVE3.PRISTINE_SOURCES["MSG_PK/JP/msggame.bin"]
    source_records = WAVE4.records_by_coordinate(source_path.read_bytes())
    records = WAVE4.records_by_coordinate(wave4_pk)
    for plan in (item[0] for item in PK_RUNTIME_SUFFIX_AUDIT_ITEMS):
        coordinate = plan.coordinate
        row = PK_RUNTIME_SUFFIX_ROWS_BY_COORDINATE[coordinate]
        record = records.get(coordinate)
        source = source_records.get(coordinate)
        if record is None or source is None:
            raise Wave5Error(f"PK runtime suffix record is absent: {coordinate}")
        if sha256_bytes(record.data) != plan.expected_sha256:
            raise Wave5Error(f"PK runtime suffix input hash changed: {coordinate}")
        assert_literals(
            record,
            require_literal_tuple(row, "current_literals", coordinate),
            f"PK runtime suffix {coordinate}",
        )
        assert_literals(
            source,
            require_literal_tuple(row, "pristine_pc_jp_literals", coordinate),
            f"PC JP runtime suffix {coordinate}",
        )
        if opaque_span_contract(record) != require_span_contract(
            row, "current_opaque_spans", coordinate
        ):
            raise Wave5Error(f"PK runtime suffix opaque spans changed: {coordinate}")
        if row.get("global_removal_prohibited") is not True:
            raise Wave5Error(f"PK runtime suffix lacks global-removal prohibition: {coordinate}")


def validate_pk_relation_log_contracts(wave4_pk: bytes) -> None:
    source_path, _source_hash = WAVE4.WAVE3.PRISTINE_SOURCES["MSG_PK/JP/msggame.bin"]
    source_records = WAVE4.records_by_coordinate(source_path.read_bytes())
    records = WAVE4.records_by_coordinate(wave4_pk)
    for plan in (item[0] for item in PK_RELATION_LOG_AUDIT_ITEMS):
        coordinate = plan.coordinate
        row = PK_RELATION_LOG_ROWS_BY_COORDINATE[coordinate]
        record = records.get(coordinate)
        source = source_records.get(coordinate)
        if record is None or source is None:
            raise Wave5Error(f"PK relation-log record is absent: {coordinate}")
        if sha256_bytes(record.data) != plan.expected_sha256:
            raise Wave5Error(f"PK relation-log input hash changed: {coordinate}")
        assert_literals(
            record,
            require_literal_tuple(row, "current_literals", coordinate),
            f"PK relation-log {coordinate}",
        )
        assert_schema(
            record,
            require_opaque_schema(row, "current_opaque_schema", coordinate),
            f"PK relation-log {coordinate}",
        )
        assert_literals(
            source,
            require_literal_tuple(row, "pristine_pc_jp_literals", coordinate),
            f"PC JP relation-log {coordinate}",
        )


def validate_pk_conflict_repair_contracts(wave4_pk: bytes) -> None:
    source_path, _source_hash = WAVE4.WAVE3.PRISTINE_SOURCES["MSG_PK/JP/msggame.bin"]
    source_records = WAVE4.records_by_coordinate(source_path.read_bytes())
    records = WAVE4.records_by_coordinate(wave4_pk)
    for plan in (item[0] for item in PK_CONFLICT_REPAIR_ITEMS):
        coordinate = plan.coordinate
        conflict = PK_CONFLICT_ROWS_BY_COORDINATE[coordinate]
        repair = PK_CONFLICT_REPAIR_ROWS_BY_COORDINATE[coordinate]
        record = records.get(coordinate)
        source = source_records.get(coordinate)
        if record is None or source is None:
            raise Wave5Error(f"PK conflict repair record is absent: {coordinate}")
        if sha256_bytes(record.data) != plan.expected_sha256:
            raise Wave5Error(f"PK conflict repair input hash changed: {coordinate}")
        assert_literals(
            record,
            require_literal_tuple(conflict, "current_literals", coordinate),
            f"PK conflict repair {coordinate}",
        )
        assert_schema(
            record,
            require_opaque_schema(conflict, "target_current_opaque_schema", coordinate),
            f"PK conflict repair {coordinate}",
        )
        assert_literals(
            source,
            require_literal_tuple(conflict, "pristine_pc_jp_target_literals", coordinate),
            f"PC JP conflict repair {coordinate}",
        )
        assert_schema(
            source,
            require_opaque_schema(conflict, "pristine_pc_jp_target_opaque_schema", coordinate),
            f"PC JP conflict repair {coordinate}",
        )
        if WAVE4.opaque_commands(record):
            raise Wave5Error(f"PK conflict repair has unresolved 0143 commands: {coordinate}")
        checked_codepoints = conflict.get("font_checked_codepoints")
        if coordinate == (6, 1491):
            if checked_codepoints != ["U+2014"] or "\u2014" not in "".join(
                require_literal_tuple(repair, "replacement_literals", coordinate)
            ):
                raise Wave5Error("PK conflict repair U+2014 evidence is invalid")
        elif checked_codepoints != []:
            raise Wave5Error(f"PK conflict repair has unexpected font evidence: {coordinate}")


def validate_pk_relation_log_font_support(steam_root: Path) -> None:
    font_rows = tuple(
        (coordinate, row)
        for coordinate, row in PK_RELATION_LOG_ROWS_BY_COORDINATE.items()
        if "\u2014" in "".join(require_literal_tuple(row, "proposed_literals", coordinate))
    )
    if not font_rows:
        return
    supports: list[dict[str, Any]] = []
    for coordinate, row in font_rows:
        support = row.get("font_support")
        if not isinstance(support, dict):
            raise Wave5Error(f"{coordinate} relation-log em dash lacks font support evidence")
        if support.get("resource") != "RES_JP/res_lang.bin":
            raise Wave5Error(f"{coordinate} relation-log font resource is invalid")
        if support.get("selected_codepoint") != "U+2014" or support.get("selected_advance") != 48:
            raise Wave5Error(f"{coordinate} relation-log em dash support is invalid")
        if support.get("rejected_codepoint") != "U+2013":
            raise Wave5Error(f"{coordinate} relation-log rejected-glyph evidence is invalid")
        expected_hash = str(support.get("sha256", "")).upper()
        if len(expected_hash) != 64:
            raise Wave5Error(f"{coordinate} relation-log font hash is invalid")
        supports.append(support)
    hashes = {str(support["sha256"]).upper() for support in supports}
    if len(hashes) != 1:
        raise Wave5Error("relation-log font support rows disagree on the active font hash")
    font_path = WAVE4.require_under(
        steam_root, steam_root / "RES_JP" / "res_lang.bin", "relation-log font"
    )
    if WAVE4.WAVE3.sha256_path(font_path) != hashes.pop():
        raise Wave5Error("active relation-log font hash changed")
    try:
        archive = parse_link(font_path.read_bytes())
        _header, raw = decompress_wrapper(archive.entries[6].data)
    except (IndexError, ValueError) as exc:
        raise Wave5Error("active relation-log font cannot be unpacked") from exc
    with tempfile.TemporaryDirectory(prefix="nobu16_wave5_relation_font_") as directory:
        g1n_path = Path(directory) / "relation_font.g1n"
        g1n_path.write_bytes(raw)
        parsed = g1n.parse_g1n(g1n_path)
    if parsed.structural_errors or not parsed.tables:
        raise Wave5Error("active relation-log font structure differs")
    table = parsed.tables[0]
    em_dash_ordinal = table.mapping[0x2014] if 0x2014 < len(table.mapping) else 0
    en_dash_ordinal = table.mapping[0x2013] if 0x2013 < len(table.mapping) else 0
    if em_dash_ordinal == 0 or em_dash_ordinal >= len(table.records):
        raise Wave5Error("active relation-log font lacks U+2014")
    if table.records[em_dash_ordinal].advance != 48:
        raise Wave5Error("active relation-log font has an unexpected U+2014 advance")
    if en_dash_ordinal != 0:
        raise Wave5Error("active relation-log font unexpectedly maps rejected U+2013")


def validate_event_pk_font_support(steam_root: Path) -> Any:
    profiles = tuple(row["input_profile"] for row in PK_EVENT_STATIC_REPAIR_AUDIT_ROWS)
    expected_hashes = {
        require_sha256(profile.get("font_packed_sha256"), "PK event font hash")
        for profile in profiles
    }
    if len(expected_hashes) != 1:
        raise Wave5Error("PK event-linebreak rows disagree on the active font hash")
    font_path = WAVE4.require_under(
        steam_root, steam_root / "RES_JP" / "res_lang.bin", "PK event-linebreak font"
    )
    if WAVE4.WAVE3.sha256_path(font_path) != expected_hashes.pop():
        raise Wave5Error("active PK event-linebreak font hash changed")
    try:
        archive = parse_link(font_path.read_bytes())
        _header, raw = decompress_wrapper(archive.entries[6].data)
    except (IndexError, ValueError) as exc:
        raise Wave5Error("active PK event-linebreak font cannot be unpacked") from exc
    with tempfile.TemporaryDirectory(prefix="nobu16_wave5_event_font_") as directory:
        g1n_path = Path(directory) / "event_font.g1n"
        g1n_path.write_bytes(raw)
        parsed = g1n.parse_g1n(g1n_path)
    if parsed.structural_errors or not parsed.tables:
        raise Wave5Error("active PK event-linebreak font structure differs")
    table = parsed.tables[0]

    def advance(character: str) -> int:
        codepoint = ord(character)
        if codepoint >= len(table.mapping):
            raise Wave5Error(
                f"PK event-linebreak glyph is outside the active font: U+{codepoint:04X}"
            )
        ordinal = table.mapping[codepoint]
        if ordinal == 0:
            if EVENT_WIDE_SCRIPT_RE.fullmatch(character) is not None:
                return 48
            raise Wave5Error(f"PK event-linebreak glyph is absent: U+{codepoint:04X}")
        if ordinal >= len(table.records):
            raise Wave5Error(
                f"PK event-linebreak glyph ordinal is outside the active font: U+{codepoint:04X}"
            )
        record = table.records[ordinal]
        if record.width != record.advance or record.advance not in (24, 48):
            raise Wave5Error(
                f"PK event-linebreak glyph metric is invalid: U+{codepoint:04X}"
            )
        return record.advance

    if (advance("가"), advance(" "), advance("…")) != (48, 24, 48):
        raise Wave5Error("active PK event-linebreak font sample metrics differ")
    return advance


def event_visible_line_width(value: str, advance: Any) -> int:
    width = 0
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            if EVENT_ESC_RE.fullmatch(token) is None:
                raise Wave5Error("PK event-linebreak text has a malformed ESC token")
            cursor += 3
            continue
        character = value[cursor]
        if unicodedata.category(character) == "Cc":
            raise Wave5Error(
                f"PK event-linebreak visible text has a control: U+{ord(character):04X}"
            )
        width += advance(character)
        cursor += 1
    return width


def event_runtime_reservations(
    row: dict[str, Any], table: Any, advance: Any
) -> dict[str, int]:
    expected = row["invariants"].get("runtime_reservations")
    if not isinstance(expected, list) or not all(isinstance(item, dict) for item in expected):
        raise Wave5Error("PK event-linebreak runtime reservation evidence is invalid")
    claimed: dict[str, int] = {}
    for item in expected:
        token = item.get("token")
        width = item.get("reserved_full_name_width_px")
        if not isinstance(token, str) or not isinstance(width, int) or width <= 0:
            raise Wave5Error("PK event-linebreak runtime reservation entry is invalid")
        if token in claimed:
            raise Wave5Error("PK event-linebreak runtime reservation is duplicated")
        match = EVENT_RUNTIME_TOKEN_RE.fullmatch(token)
        if match is None:
            raise Wave5Error("PK event-linebreak runtime reservation token is invalid")
        source_id = int(match.group(2))
        if source_id >= table.string_count:
            raise Wave5Error("PK event-linebreak runtime name ID is out of range")
        measured = event_visible_line_width(table.texts[source_id], advance)
        if measured != width:
            raise Wave5Error(
                f"PK event-linebreak runtime reservation differs at {token}: {measured} != {width}"
            )
        claimed[token] = width
    all_tokens = set(EVENT_RUNTIME_BRACKET_RE.findall(row["current"]["literal"]))
    all_tokens.update(EVENT_RUNTIME_BRACKET_RE.findall(row["replacement"]["literal"]))
    if set(claimed) != all_tokens:
        raise Wave5Error("PK event-linebreak runtime reservation set differs from its literals")
    return claimed


def event_measure_text_widths(value: str, advance: Any, reservations: dict[str, int]) -> tuple[list[int], list[int]]:
    actual: list[int] = []
    reserved: list[int] = []
    for line in EVENT_LINEBREAK_RE.sub("\n", value).split("\n"):
        visible = event_visible_line_width(line, advance)
        projected = visible
        for token in EVENT_RUNTIME_BRACKET_RE.findall(line):
            if token not in reservations:
                raise Wave5Error(f"PK event-linebreak runtime reservation is absent: {token}")
            projected += max(0, reservations[token] - event_visible_line_width(token, advance))
        actual.append(visible)
        reserved.append(projected)
    return actual, reserved


def validate_event_text_measurements(
    row: dict[str, Any], table: Any, advance: Any, text_contract: dict[str, Any], label: str
) -> None:
    reservations = event_runtime_reservations(row, table, advance)
    actual, reserved = event_measure_text_widths(text_contract["literal"], advance, reservations)
    if actual != text_contract["actual_line_width_px"]:
        raise Wave5Error(f"{label} actual width differs from audit")
    if reserved != text_contract["reserved_line_width_px"]:
        raise Wave5Error(f"{label} reserved width differs from audit")
    if len(reserved) > row["invariants"]["line_count_max"] or max(reserved, default=0) > 912:
        raise Wave5Error(f"{label} exceeds the PK 3x912px renderer contract")


def validate_event_pk_source_table(
    source_event: bytes, steam_root: Path
) -> tuple[Any, bytes, Any, Any]:
    if sha256_bytes(source_event) != BASELINE_SHA256[EVENT_PK_RESOURCE]:
        raise Wave5Error("PK event-linebreak source packed hash differs from Steam baseline")
    advance = validate_event_pk_font_support(steam_root)
    try:
        header, raw = decompress_wrapper(source_event)
        table = parse_message_table(raw)
    except ValueError as exc:
        raise Wave5Error("PK event-linebreak source table cannot be unpacked") from exc
    expected_raw_hashes = {
        require_sha256(row["input_profile"].get("table_raw_sha256"), "PK event raw table hash")
        for row in PK_EVENT_STATIC_REPAIR_AUDIT_ROWS
    }
    if len(expected_raw_hashes) != 1 or sha256_bytes(raw) != expected_raw_hashes.pop():
        raise Wave5Error("PK event-linebreak source raw table hash differs from audit")
    if rebuild_message_table(table, table.texts) != raw:
        raise Wave5Error("PK event-linebreak source table is not byte-exact on parse/rebuild")
    for record_id, row in PK_EVENT_STATIC_REPAIR_ROWS_BY_ID.items():
        if record_id >= table.string_count:
            raise Wave5Error(f"PK event-linebreak record is out of range: {record_id}")
        current = row["current"]
        if table.texts[record_id] != current["literal"]:
            raise Wave5Error(f"PK event-linebreak current literal changed: {record_id}")
        if event_text_sha256(table.texts[record_id]) != current["utf16le_sha256"]:
            raise Wave5Error(f"PK event-linebreak current text hash changed: {record_id}")
        validate_event_text_measurements(
            row, table, advance, current, f"PK event-linebreak current {record_id}"
        )
        validate_event_text_measurements(
            row, table, advance, row["replacement"], f"PK event-linebreak replacement {record_id}"
        )
    return header, raw, table, advance


def rebuild_wave5_pk_events(source_event: bytes, steam_root: Path) -> bytes:
    header, raw, table, advance = validate_event_pk_source_table(source_event, steam_root)
    texts = list(table.texts)
    for record_id, row in PK_EVENT_STATIC_REPAIR_ROWS_BY_ID.items():
        texts[record_id] = row["replacement"]["literal"]
    candidate_raw = rebuild_message_table(table, texts)
    candidate = recompress_wrapper(candidate_raw, header)
    try:
        candidate_header, roundtrip_raw = decompress_wrapper(candidate)
        candidate_table = parse_message_table(roundtrip_raw)
    except ValueError as exc:
        raise Wave5Error("PK event-linebreak candidate cannot be unpacked") from exc
    if candidate_header.prefix != header.prefix or roundtrip_raw != candidate_raw:
        raise Wave5Error("PK event-linebreak candidate wrapper round-trip differs")
    if rebuild_message_table(candidate_table, candidate_table.texts) != candidate_raw:
        raise Wave5Error("PK event-linebreak candidate table is not byte-exact on parse/rebuild")
    if candidate_table.string_count != table.string_count:
        raise Wave5Error("PK event-linebreak candidate string count changed")
    if (
        candidate_table.logical_size != table.logical_size + EVENT_PK_LOGICAL_SIZE_DELTA
        or len(candidate_raw) != len(raw) + EVENT_PK_LOGICAL_SIZE_DELTA
    ):
        raise Wave5Error("PK event-linebreak candidate logical-size delta differs")
    for record_id, (before_offset, after_offset) in enumerate(
        zip(table.string_offsets, candidate_table.string_offsets)
    ):
        expected_delta = 0 if record_id <= 5492 else -2 if record_id <= 6668 else -4
        if after_offset - before_offset != expected_delta:
            raise Wave5Error(f"PK event-linebreak candidate offset delta differs: {record_id}")
    changed_ids = {
        record_id
        for record_id, (before, after) in enumerate(zip(table.texts, candidate_table.texts))
        if before != after
    }
    if changed_ids != set(PK_EVENT_STATIC_REPAIR_IDS):
        raise Wave5Error(
            f"PK event-linebreak candidate changed unexpected texts: {sorted(changed_ids)}"
        )
    for record_id, row in PK_EVENT_STATIC_REPAIR_ROWS_BY_ID.items():
        replacement = row["replacement"]
        actual = candidate_table.texts[record_id]
        if actual != replacement["literal"]:
            raise Wave5Error(f"PK event-linebreak candidate literal mismatch: {record_id}")
        if event_text_sha256(actual) != replacement["utf16le_sha256"]:
            raise Wave5Error(f"PK event-linebreak candidate text hash mismatch: {record_id}")
        if event_protected_contract(actual) != replacement["protected_contract"]:
            raise Wave5Error(f"PK event-linebreak candidate token contract mismatch: {record_id}")
        if event_line_count(actual) > row["invariants"]["line_count_max"]:
            raise Wave5Error(f"PK event-linebreak candidate exceeds three lines: {record_id}")
        validate_event_text_measurements(
            row, candidate_table, advance, replacement, f"PK event-linebreak candidate {record_id}"
        )
    if sha256_bytes(candidate_raw) != EVENT_PK_TARGET_RAW_SHA256:
        raise Wave5Error("PK event-linebreak candidate raw output hash differs")
    if sha256_bytes(candidate) != EVENT_PK_TARGET_PACKED_SHA256:
        raise Wave5Error("PK event-linebreak candidate packed output hash differs")
    return candidate


def validate_plan_sets() -> None:
    WAVE4.validate_plan_set(BASE_EXTRA_PLANS, "MSG/JP/msggame.bin")
    WAVE4.validate_plan_set(PK_EXTRA_PLANS, "MSG_PK/JP/msggame.bin")
    validate_samepk_crosscheck_set()
    original_coordinates = {plan.coordinate for plan in WAVE4.BASE_PLANS}
    duplicate = original_coordinates & {plan.coordinate for plan in BASE_EXTRA_PLANS}
    if duplicate:
        raise Wave5Error(f"Wave 5 Base plans overlap Wave 4: {sorted(duplicate)}")
    original_pk_coordinates = {plan.coordinate for plan in WAVE4.PK_PLANS}
    duplicate_pk = original_pk_coordinates & {plan.coordinate for plan in PK_EXTRA_PLANS}
    if duplicate_pk:
        raise Wave5Error(f"Wave 5 PK plans overlap Wave 4: {sorted(duplicate_pk)}")
    planned_pk = {plan.coordinate for plan in PK_EXTRA_PLANS}
    relation_as_donor = set(PK_DONOR_ROWS_BY_COORDINATE) & PK_RELATION_LOG_COORDINATES
    if relation_as_donor:
        raise Wave5Error(
            "relation-log replacements still have generic donor plans: "
            f"{sorted(relation_as_donor)}"
        )
    unresolved_pk = (
        planned_pk - PK_CONFLICT_REPAIR_COORDINATES
    ) & PK_UNRESOLVED_DONOR_COORDINATES
    if unresolved_pk:
        raise Wave5Error(f"unresolved PK donor rows entered the plan set: {sorted(unresolved_pk)}")
    applied_runtime_particle_holds = planned_pk & PK_RUNTIME_PARTICLE_GENERIC_DONOR_HOLD_COORDINATES
    if applied_runtime_particle_holds:
        raise Wave5Error(
            "runtime-particle hold rows entered the plan set: "
            f"{sorted(applied_runtime_particle_holds)}"
        )
    missing_relation_overrides = PK_RUNTIME_PARTICLE_RELATION_OVERRIDE_COORDINATES - planned_pk
    if missing_relation_overrides:
        raise Wave5Error(
            "explicit relation-log overrides are missing from the plan set: "
            f"{sorted(missing_relation_overrides)}"
        )
    applied_reclassified = planned_pk & set(PK_RUNTIME_PARTICLE_RECLASSIFICATION_BY_COORDINATE)
    if applied_reclassified:
        raise Wave5Error(
            "Steam-ineligible PK runtime particle rows entered the plan set: "
            f"{sorted(applied_reclassified)}"
        )


def validate_direct_pc_sources(steam_root: Path) -> dict[str, str]:
    source_hashes = WAVE4.validate_source_coordinates(steam_root)
    source_path, expected_file_hash = WAVE4.WAVE3.PRISTINE_SOURCES["MSG/JP/msggame.bin"]
    actual_file_hash = WAVE4.WAVE3.sha256_path(source_path)
    if actual_file_hash != expected_file_hash:
        raise Wave5Error("pristine Base PC Japanese source hash changed")
    source_records = WAVE4.records_by_coordinate(source_path.read_bytes())
    for plan in BASE_EXTRA_PLANS:
        source = source_records.get(plan.coordinate)
        if source is None:
            raise Wave5Error(f"PC Base Japanese source lacks {plan.coordinate}")
        actual_literals = tuple(item.text for item in WAVE4.parse_record_literals(source))
        expected_literals = BASE_EXPECTED_JP_LITERALS[plan.coordinate]
        if actual_literals != expected_literals:
            raise Wave5Error(
                f"PC Base Japanese literals changed at {plan.coordinate}: "
                f"expected {expected_literals!r}, got {actual_literals!r}"
            )
    return source_hashes


def assert_literals(record, expected: tuple[str, ...], label: str) -> None:
    actual = tuple(item.text for item in WAVE4.parse_record_literals(record))
    if actual != expected:
        raise Wave5Error(f"{label} literal tuple mismatch: expected {expected!r}, got {actual!r}")


def assert_schema(record, expected: tuple[str, ...], label: str) -> None:
    actual = opaque_schema(record)
    if actual != expected:
        raise Wave5Error(f"{label} opaque schema mismatch: expected {expected!r}, got {actual!r}")


def validate_base_dangga_contracts(wave4_base: bytes) -> None:
    records = WAVE4.records_by_coordinate(wave4_base)
    for plan in (item[0] for item in BASE_DANGGA_AUDIT_ITEMS):
        coordinate = plan.coordinate
        row = BASE_DANGGA_ROWS_BY_COORDINATE[coordinate]
        record = records.get(coordinate)
        if record is None:
            raise Wave5Error(f"Base dangga record is absent: {coordinate}")
        if sha256_bytes(record.data) != plan.expected_sha256:
            raise Wave5Error(f"Base dangga input hash changed: {coordinate}")
        assert_literals(
            record,
            require_literal_tuple(row, "current_ko_literals", coordinate),
            f"Base dangga {coordinate}",
        )
        if WAVE4.opaque_bytes(record).hex().upper() != str(row["current_opaque_hex"]).upper():
            raise Wave5Error(f"Base dangga opaque bytes changed: {coordinate}")
        if WAVE4.rendered_literal_line_count(record) != row.get("manual_line_count_before"):
            raise Wave5Error(f"Base dangga input line count changed: {coordinate}")


def validate_pk_donor_contracts(wave4_base: bytes, wave4_pk: bytes) -> None:
    base_source_path, _base_source_hash = WAVE4.WAVE3.PRISTINE_SOURCES["MSG/JP/msggame.bin"]
    pk_source_path, _pk_source_hash = WAVE4.WAVE3.PRISTINE_SOURCES["MSG_PK/JP/msggame.bin"]
    base_jp = WAVE4.records_by_coordinate(base_source_path.read_bytes())
    pk_jp = WAVE4.records_by_coordinate(pk_source_path.read_bytes())
    base_records = WAVE4.records_by_coordinate(wave4_base)
    pk_records = WAVE4.records_by_coordinate(wave4_pk)
    for plan in (item[0] for item in PK_DONOR_AUDIT_ITEMS):
        coordinate = plan.coordinate
        row = PK_DONOR_ROWS_BY_COORDINATE[coordinate]
        target = pk_records.get(coordinate)
        target_jp = pk_jp.get(coordinate)
        if target is None or target_jp is None:
            raise Wave5Error(f"PK donor target is absent: {coordinate}")
        if sha256_bytes(target.data) != plan.expected_sha256:
            raise Wave5Error(f"PK donor target hash changed: {coordinate}")
        assert_literals(target, require_literal_tuple(row, "current_literals", coordinate), f"PK target {coordinate}")
        assert_schema(target, require_opaque_schema(row, "target_current_opaque_schema", coordinate), f"PK target {coordinate}")
        assert_literals(
            target_jp,
            require_literal_tuple(row, "pristine_pc_jp_target_literals", coordinate),
            f"PC JP target {coordinate}",
        )
        assert_schema(
            target_jp,
            require_opaque_schema(row, "pristine_pc_jp_target_opaque_schema", coordinate),
            f"PC JP target {coordinate}",
        )
        if row.get("pristine_pc_jp_literal_tuple_match") is not True:
            raise Wave5Error(f"PK donor has no PC JP literal equivalence: {coordinate}")
        if row.get("pristine_pc_jp_opaque_schema_match") is not True:
            raise Wave5Error(f"PK donor has no PC JP opaque equivalence: {coordinate}")

        if row["kind"] == "colon_samepc_base_donor":
            donor_coordinate = parse_coordinate(str(row.get("base_donor_coordinate")))
            donor = base_records.get(donor_coordinate)
            donor_jp = base_jp.get(donor_coordinate)
            if donor is None or donor_jp is None:
                raise Wave5Error(f"Base donor is absent for PK {coordinate}")
            expected_donor_hash = str(row.get("base_donor_after_wave4_sha256", "")).upper()
            if sha256_bytes(donor.data) != expected_donor_hash:
                raise Wave5Error(f"Base donor hash changed for PK {coordinate}")
            assert_literals(
                donor,
                require_literal_tuple(row, "base_donor_after_wave4_literals", coordinate),
                f"Base donor for PK {coordinate}",
            )
            assert_schema(
                donor,
                require_opaque_schema(row, "base_donor_current_opaque_schema", coordinate),
                f"Base donor for PK {coordinate}",
            )
            assert_literals(
                donor_jp,
                require_literal_tuple(row, "pristine_pc_jp_base_donor_literals", coordinate),
                f"PC JP Base donor for PK {coordinate}",
            )
            assert_schema(
                donor_jp,
                require_opaque_schema(row, "pristine_pc_jp_base_donor_opaque_schema", coordinate),
                f"PC JP Base donor for PK {coordinate}",
            )
        elif row["kind"] == "same_pk_exact_donor":
            donor_coordinate = parse_coordinate(str(row.get("pk_donor_coordinate")))
            donor = pk_records.get(donor_coordinate)
            donor_jp = pk_jp.get(donor_coordinate)
            if donor is None or donor_jp is None:
                raise Wave5Error(f"PK donor is absent for PK {coordinate}")
            expected_donor_hash = str(row.get("pk_donor_record_sha256", "")).upper()
            if sha256_bytes(donor.data) != expected_donor_hash:
                raise Wave5Error(f"PK donor hash changed for PK {coordinate}")
            assert_literals(
                donor,
                require_literal_tuple(row, "pk_donor_literals", coordinate),
                f"PK donor for {coordinate}",
            )
            assert_schema(
                donor,
                require_opaque_schema(row, "pk_donor_current_opaque_schema", coordinate),
                f"PK donor for {coordinate}",
            )
            assert_literals(
                donor_jp,
                require_literal_tuple(row, "pristine_pc_jp_donor_literals", coordinate),
                f"PC JP PK donor for {coordinate}",
            )
            assert_schema(
                donor_jp,
                require_opaque_schema(row, "pristine_pc_jp_donor_opaque_schema", coordinate),
                f"PC JP PK donor for {coordinate}",
            )
        else:
            raise Wave5Error(f"unexpected PK donor kind at {coordinate}")

    for row in PK_SAMEPK_CROSSCHECK_ROWS:
        coordinate = parse_coordinate(str(row.get("coordinate")))
        target = pk_records.get(coordinate)
        target_jp = pk_jp.get(coordinate)
        donor_coordinate = parse_coordinate(str(row.get("pk_donor_coordinate")))
        donor = pk_records.get(donor_coordinate)
        donor_jp = pk_jp.get(donor_coordinate)
        if target is None or target_jp is None or donor is None or donor_jp is None:
            raise Wave5Error(f"same-PK crosscheck record is absent: {coordinate}")
        expected_target_hash = str(row.get("current_record_sha256", "")).upper()
        if sha256_bytes(target.data) != expected_target_hash:
            raise Wave5Error(f"same-PK target hash changed: {coordinate}")
        expected_donor_hash = str(row.get("pk_donor_record_sha256", "")).upper()
        if sha256_bytes(donor.data) != expected_donor_hash:
            raise Wave5Error(f"same-PK donor hash changed: {coordinate}")
        assert_literals(
            target,
            require_literal_tuple(row, "current_literals", coordinate),
            f"same-PK target {coordinate}",
        )
        assert_schema(
            target,
            require_opaque_schema(row, "target_current_opaque_schema", coordinate),
            f"same-PK target {coordinate}",
        )
        assert_literals(
            target_jp,
            require_literal_tuple(row, "pristine_pc_jp_target_literals", coordinate),
            f"PC JP same-PK target {coordinate}",
        )
        assert_schema(
            target_jp,
            require_opaque_schema(row, "pristine_pc_jp_target_opaque_schema", coordinate),
            f"PC JP same-PK target {coordinate}",
        )
        assert_literals(
            donor,
            require_literal_tuple(row, "pk_donor_literals", coordinate),
            f"same-PK donor {coordinate}",
        )
        assert_schema(
            donor,
            require_opaque_schema(row, "pk_donor_current_opaque_schema", coordinate),
            f"same-PK donor {coordinate}",
        )
        assert_literals(
            donor_jp,
            require_literal_tuple(row, "pristine_pc_jp_donor_literals", coordinate),
            f"PC JP same-PK donor {coordinate}",
        )
        assert_schema(
            donor_jp,
            require_opaque_schema(row, "pristine_pc_jp_donor_opaque_schema", coordinate),
            f"PC JP same-PK donor {coordinate}",
        )


def rebuild_wave5_base(source_base: bytes) -> tuple[bytes, bytes, bytes, tuple[Any, ...]]:
    wave3_base = WAVE4.WAVE3.rebuild_static_resource(
        source_base, WAVE4.WAVE3.BASE_PLANS, "MSG/JP/msggame.bin"
    )
    if sha256_bytes(wave3_base) != WAVE4.WAVE3.TARGET_SHA256["MSG/JP/msggame.bin"]:
        raise Wave5Error("in-memory Wave 3 Base output hash mismatch")
    wave4_base_records = WAVE4.records_by_coordinate(wave3_base)
    wave4_base = WAVE4.rebuild_quality_resource(
        wave3_base, WAVE4.BASE_PLANS, "MSG/JP/msggame.bin", wave4_base_records
    )
    validate_base_dangga_contracts(wave4_base)
    wave5_base_records = WAVE4.records_by_coordinate(wave4_base)
    residual_items = materialize_residual_korean_quality_plans(
        "MSG/JP/msggame.bin", wave4_base
    )
    residual_plans = tuple(item[0] for item in residual_items)
    if {plan.coordinate for plan in BASE_EXTRA_PLANS} & {plan.coordinate for plan in residual_plans}:
        raise Wave5Error("residual Korean-quality Base plans overlap existing Wave 5 plans")
    standard_rebuilt = WAVE4.rebuild_quality_resource(
        wave4_base, BASE_EXTRA_PLANS, "MSG/JP/msggame.bin", wave5_base_records
    )
    rebuilt = rebuild_residual_korean_quality_resource(
        standard_rebuilt, residual_items, "MSG/JP/msggame.bin", wave5_base_records
    )
    records = WAVE4.records_by_coordinate(rebuilt)
    expected_output_hashes = dict(BASE_EXPECTED_OUTPUT_RECORD_SHA256)
    expected_output_hashes.update({item[0].coordinate: item[2] for item in residual_items})
    residual_rows = {item[0].coordinate: item[1] for item in residual_items}
    for coordinate, expected_hash in expected_output_hashes.items():
        actual_hash = sha256_bytes(records[coordinate].data)
        if actual_hash != expected_hash:
            raise Wave5Error(
                f"Wave 5 Base audit output mismatch at {coordinate}: "
                f"expected {expected_hash}, got {actual_hash}"
            )
        if coordinate in BASE_DANGGA_ROWS_BY_COORDINATE:
            row = BASE_DANGGA_ROWS_BY_COORDINATE[coordinate]
            if WAVE4.opaque_bytes(records[coordinate]).hex().upper() != str(
                row["asserted_output_opaque_hex"]
            ).upper():
                raise Wave5Error(f"Base dangga opaque bytes changed in output: {coordinate}")
            if WAVE4.rendered_literal_line_count(records[coordinate]) != row.get(
                "manual_line_count_after"
            ):
                raise Wave5Error(f"Base dangga output line count changed: {coordinate}")
        elif coordinate in residual_rows:
            row = residual_rows[coordinate]
            if WAVE4.opaque_bytes(records[coordinate]) != residual_opaque_bytes_from_schema(
                row, coordinate
            ):
                raise Wave5Error(f"Base residual opaque bytes changed: {coordinate}")
    return wave3_base, wave4_base, rebuilt, residual_items


def rebuild_wave5_pk(
    source_pk: bytes, wave3_base: bytes, wave4_base: bytes
) -> tuple[bytes, tuple[Any, ...]]:
    wave3_pk = WAVE4.WAVE3.rebuild_static_resource(
        source_pk, WAVE4.WAVE3.PK_PLANS, "MSG_PK/JP/msggame.bin"
    )
    if sha256_bytes(wave3_pk) != WAVE4.WAVE3.TARGET_SHA256["MSG_PK/JP/msggame.bin"]:
        raise Wave5Error("in-memory Wave 3 PK output hash mismatch")
    base_records = WAVE4.records_by_coordinate(wave3_base)
    wave4_pk = WAVE4.rebuild_quality_resource(
        wave3_pk, WAVE4.PK_PLANS, "MSG_PK/JP/msggame.bin", base_records
    )
    validate_pk_donor_contracts(wave4_base, wave4_pk)
    validate_pk_runtime_suffix_contracts(wave4_pk)
    validate_pk_relation_log_contracts(wave4_pk)
    validate_pk_conflict_repair_contracts(wave4_pk)
    residual_items = materialize_residual_korean_quality_plans(
        "MSG_PK/JP/msggame.bin", wave4_pk
    )
    residual_plans = tuple(item[0] for item in residual_items)
    if {plan.coordinate for plan in PK_EXTRA_PLANS} & {plan.coordinate for plan in residual_plans}:
        raise Wave5Error("residual Korean-quality PK plans overlap existing Wave 5 plans")
    standard_rebuilt = WAVE4.rebuild_quality_resource(
        wave4_pk,
        PK_EXTRA_PLANS,
        "MSG_PK/JP/msggame.bin",
        base_records,
    )
    rebuilt = rebuild_residual_korean_quality_resource(
        standard_rebuilt, residual_items, "MSG_PK/JP/msggame.bin", base_records
    )
    records = WAVE4.records_by_coordinate(rebuilt)
    expected_output_hashes = dict(PK_EXPECTED_OUTPUT_RECORD_SHA256)
    expected_output_hashes.update({item[0].coordinate: item[2] for item in residual_items})
    residual_rows = {item[0].coordinate: item[1] for item in residual_items}
    for coordinate, expected_hash in expected_output_hashes.items():
        actual_hash = sha256_bytes(records[coordinate].data)
        if actual_hash != expected_hash:
            raise Wave5Error(
                f"Wave 5 PK donor output mismatch at {coordinate}: "
                f"expected {expected_hash}, got {actual_hash}"
            )
        if coordinate in PK_DONOR_ROWS_BY_COORDINATE:
            row = PK_DONOR_ROWS_BY_COORDINATE[coordinate]
            assert_schema(
                records[coordinate],
                require_opaque_schema(row, "asserted_output_opaque_schema", coordinate),
                f"Wave 5 PK output {coordinate}",
            )
        elif coordinate in PK_RELATION_LOG_ROWS_BY_COORDINATE:
            row = PK_RELATION_LOG_ROWS_BY_COORDINATE[coordinate]
            assert_schema(
                records[coordinate],
                require_opaque_schema(row, "asserted_output_opaque_schema", coordinate),
                f"Wave 5 PK relation-log output {coordinate}",
            )
        elif coordinate in PK_CONFLICT_REPAIR_ROWS_BY_COORDINATE:
            conflict = PK_CONFLICT_ROWS_BY_COORDINATE[coordinate]
            repair = PK_CONFLICT_REPAIR_ROWS_BY_COORDINATE[coordinate]
            assert_schema(
                records[coordinate],
                require_opaque_schema(conflict, "asserted_output_opaque_schema", coordinate),
                f"Wave 5 PK conflict-repair output {coordinate}",
            )
            if WAVE4.rendered_literal_line_count(records[coordinate]) != repair.get(
                "manual_line_count"
            ):
                raise Wave5Error(f"Wave 5 PK conflict-repair line count changed: {coordinate}")
        elif coordinate in residual_rows:
            row = residual_rows[coordinate]
            if WAVE4.opaque_bytes(records[coordinate]) != residual_opaque_bytes_from_schema(
                row, coordinate
            ):
                raise Wave5Error(f"PK residual opaque bytes changed: {coordinate}")
        else:
            row = PK_RUNTIME_SUFFIX_ROWS_BY_COORDINATE[coordinate]
            if opaque_span_contract(records[coordinate]) != require_span_contract(
                row, "asserted_output_opaque_spans", coordinate
            ):
                raise Wave5Error(f"Wave 5 PK runtime suffix opaque spans changed: {coordinate}")
    return rebuilt, residual_items


def require_under_repo(path: Path, label: str) -> Path:
    return WAVE4.require_under(REPO, path, label)


def build_candidate(
    steam_root: Path,
    output_root: Path,
    manifest_path: Path,
    allow_unpinned_output: bool,
) -> dict[str, object]:
    validate_plan_sets()
    steam_root = steam_root.resolve()
    output_root = require_under_repo(output_root, "candidate output")
    manifest_path = require_under_repo(manifest_path, "manifest output")
    if output_root.exists():
        raise Wave5Error(f"candidate output already exists: {output_root}")
    WAVE4.assert_profile(steam_root, BASELINE_SHA256, "installed input")
    pristine_hashes = validate_direct_pc_sources(steam_root)
    validate_pk_relation_log_font_support(steam_root)

    source_base = (steam_root / "MSG/JP/msggame.bin").read_bytes()
    source_pk = (steam_root / "MSG_PK/JP/msggame.bin").read_bytes()
    source_event_pk = (steam_root / EVENT_PK_RESOURCE).read_bytes()
    wave3_base, wave4_base, final_base, base_residual_items = rebuild_wave5_base(source_base)
    final_pk, pk_residual_items = rebuild_wave5_pk(source_pk, wave3_base, wave4_base)
    final_event_pk = rebuild_wave5_pk_events(source_event_pk, steam_root)

    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(WAVE4.require_under(steam_root, steam_root / relative, "Steam input"), target)
        (stage / "MSG/JP/msggame.bin").write_bytes(final_base)
        (stage / "MSG_PK/JP/msggame.bin").write_bytes(final_pk)
        (stage / EVENT_PK_RESOURCE).write_bytes(final_event_pk)
        output_hashes = WAVE4.profile_hashes(stage)
        if TARGET_SHA256 is None:
            if not allow_unpinned_output:
                raise Wave5Error("Wave 5 output is not pinned; use --allow-unpinned-output only for bootstrap")
        elif output_hashes != TARGET_SHA256:
            raise Wave5Error("candidate target SHA-256 profile mismatch")
        manifest = {
            "schema": MANIFEST_SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave5-v1",
            "input_sha256": BASELINE_SHA256,
            "output_sha256": output_hashes,
            "pinned_output_sha256": TARGET_SHA256,
            "pristine_pc_jp_sha256": pristine_hashes,
            "changed_paths": list(CHANGED_PATHS),
            "base_audit_files": [
                str(AUDIT_BASE_SUFFIX_BATCH01.relative_to(REPO)).replace("\\", "/"),
                str(AUDIT_BASE_SUFFIX_BATCH02.relative_to(REPO)).replace("\\", "/"),
                str(AUDIT_BASE_DANGGA_SAFE_BATCH.relative_to(REPO)).replace("\\", "/"),
                str(AUDIT_RESIDUAL_KOREAN_QUALITY.relative_to(REPO)).replace("\\", "/"),
                str(AUDIT_RESIDUAL_KOREAN_QUALITY_HOLDS.relative_to(REPO)).replace("\\", "/"),
            ],
            "base_plan_count": len(BASE_EXTRA_PLANS) + len(base_residual_items),
            "base_residual_quality_plan_count": len(base_residual_items),
            "base_plans": [
                WAVE4.render_plan(item)
                for item in (*BASE_EXTRA_PLANS, *(entry[0] for entry in base_residual_items))
            ],
            "pk_audit_files": [
                str(AUDIT_PK_COLON_SAMEPC_DONORS.relative_to(REPO)).replace("\\", "/"),
                str(AUDIT_PK_SAMEPK_DONORS.relative_to(REPO)).replace("\\", "/"),
                str(AUDIT_PK_RUNTIME_SUFFIX_6547.relative_to(REPO)).replace("\\", "/"),
                str(AUDIT_PK_RELATION_LOGS.relative_to(REPO)).replace("\\", "/"),
                str(AUDIT_PK_RUNTIME_PARTICLE_HOLDS.relative_to(REPO)).replace("\\", "/"),
                str(AUDIT_PK_DONOR_CONFLICTS.relative_to(REPO)).replace("\\", "/"),
                str(AUDIT_PK_DONOR_CONFLICT_REVIEW.relative_to(REPO)).replace("\\", "/"),
                str(AUDIT_PK_DONOR_CONFLICT_SPACING_REPAIRS.relative_to(REPO)).replace("\\", "/"),
                str(AUDIT_PK_RUNTIME_PARTICLE_RECLASSIFICATION.relative_to(REPO)).replace("\\", "/"),
                str(AUDIT_RESIDUAL_KOREAN_QUALITY_PK_14_226_REVIEW.relative_to(REPO)).replace(
                    "\\", "/"
                ),
            ],
            "pk_plan_count": len(PK_EXTRA_PLANS) + len(pk_residual_items),
            "pk_residual_quality_plan_count": len(pk_residual_items),
            "pk_unresolved_donor_count": len(PK_UNRESOLVED_DONOR_COORDINATES),
            "pk_runtime_particle_reclassified_hold_count": len(
                PK_RUNTIME_PARTICLE_DONOR_HOLD_COORDINATES
            ),
            "pk_runtime_particle_hold_count": len(PK_RUNTIME_PARTICLE_HOLD_COORDINATES),
            "pk_runtime_particle_relation_override_count": len(
                PK_RUNTIME_PARTICLE_RELATION_OVERRIDE_COORDINATES
            ),
            "pk_conflict_repair_plan_count": len(PK_CONFLICT_REPAIR_ITEMS),
            "pk_plans": [
                WAVE4.render_plan(item)
                for item in (*PK_EXTRA_PLANS, *(entry[0] for entry in pk_residual_items))
            ],
            "residual_korean_quality": {
                "candidate_file": str(AUDIT_RESIDUAL_KOREAN_QUALITY.relative_to(REPO)).replace(
                    "\\", "/"
                ),
                "candidate_file_sha256": RESIDUAL_KOREAN_QUALITY_AUDIT_SHA256,
                "candidate_count": len(RESIDUAL_KOREAN_QUALITY_ROWS),
                "hold_file": str(AUDIT_RESIDUAL_KOREAN_QUALITY_HOLDS.relative_to(REPO)).replace(
                    "\\", "/"
                ),
                "hold_file_sha256": RESIDUAL_KOREAN_QUALITY_HOLDS_SHA256,
                "hold_count": len(RESIDUAL_KOREAN_QUALITY_HOLD_ROWS),
                "pk_14_226_review_file": str(
                    AUDIT_RESIDUAL_KOREAN_QUALITY_PK_14_226_REVIEW.relative_to(REPO)
                ).replace("\\", "/"),
                "pk_14_226_review_sha256": RESIDUAL_KOREAN_QUALITY_PK_14_226_REVIEW_SHA256,
            },
            "event_linebreak_audit": {
                "pk_static_repair_file": str(
                    AUDIT_EVENT_LINEBREAKS_PK_STATIC_REPAIR.relative_to(REPO)
                ).replace("\\", "/"),
                "pk_static_repair_count": len(PK_EVENT_STATIC_REPAIR_IDS),
                "pk_static_repair_ids": list(PK_EVENT_STATIC_REPAIR_IDS),
                "base_hold_file": str(
                    AUDIT_EVENT_LINEBREAKS_BASE_HOLDS.relative_to(REPO)
                ).replace("\\", "/"),
                "base_hold_count": len(BASE_EVENT_LINEBREAK_HOLD_IDS),
                "base_hold_ids": list(BASE_EVENT_LINEBREAK_HOLD_IDS),
                "base_changes_applied": 0,
            },
        }
        os.replace(stage, output_root)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return manifest
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="build a source-gated candidate without changing Steam")
    build.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    build.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    build.add_argument("--allow-unpinned-output", action="store_true")
    build.set_defaults(
        func=lambda args: build_candidate(
            args.steam_root, args.output_root, args.manifest, args.allow_unpinned_output
        )
    )
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        outcome = args.func(args)
        print(json.dumps(outcome, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, Wave5Error, WAVE4.QualityError, WAVE4.WAVE3.WaveError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
