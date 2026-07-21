#!/usr/bin/env python3
"""Build a read-only Static Patch 007 runtime-event layout ledger.

The workstream deliberately reads the latest private event candidate and the
four direct PC-language witnesses.  It never creates an event candidate and
never writes the Steam installation.  The only writable outputs are reports
under this workstream directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PUBLIC = WORKSTREAM / "public"

MSGEV_RELATIVE = Path("MSG_PK") / "JP" / "msgev.bin"
W101_ROOT = REPO / "tmp" / "pc_event_kanto_quality_wave101_v1" / "candidate-final"
W101_EVENT = W101_ROOT / MSGEV_RELATIVE
W101_AUDIT = W101_ROOT / "audit.v1.json"
W101_MANIFEST = W101_ROOT / "candidate_manifest.v1.json"
W100_ROOT = REPO / "tmp" / "pc_event_ending_regions_quality_wave100_v1" / "candidate-final"
W100_EVENT = W100_ROOT / MSGEV_RELATIVE
W100_MANIFEST = W100_ROOT / "candidate_manifest.v1.json"

DIRECT_CONTEXT_PATHS: Mapping[str, Path] = {
    "jp": Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
        r"\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msgev.bin"
    ),
    "en": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msgev.bin"),
    "sc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msgev.bin"),
    "tc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msgev.bin"),
}

LEDGER_PATH = PUBLIC / "pc_event_runtime_layout_inventory.v1.json"
VALIDATION_PATH = WORKSTREAM / "validation.v1.json"
REPORT_PATH = WORKSTREAM / "REPORT_KO.md"

# Static Patch 007 is the runtime authority for PK event dialogue.  Raw
# G1N-like accounting is retained only as a reproducible conversion basis.
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
EFFECTIVE_LIMIT_PX = 912
RAW_EQUIVALENT_LIMIT_PX = 1_440
MAX_LINES = 4

EXPECTED_TEXT_COUNT = 17_916
EXPECTED_RUNTIME_ROW_COUNT = 1_049
EXPECTED_W101_CHANGED_IDS = (
    3_489,
    3_490,
    3_491,
    3_493,
    3_497,
    3_500,
    3_502,
    3_505,
    3_506,
    3_508,
    3_510,
    3_514,
    3_516,
    3_522,
    3_526,
)
EXPECTED_W101_RUNTIME_CHANGED_IDS = (3_514, 3_522, 3_526)

ESC_RE = re.compile(r"\x1bC[ABCZ]")
BRACKET_TOKEN_RE = re.compile(r"\[[^\[\]\r\n]+\]")
NUMERIC_NAME_TOKEN_RE = re.compile(r"\[([A-Za-z]{1,16})(\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

TOOLS_ROOT = REPO / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


class InventoryError(RuntimeError):
    """Raised for pinned-input or report-invariant drift."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InventoryError(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def relative_or_absolute(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return str(path)


def file_record(path: Path) -> Mapping[str, Any]:
    blob = path.read_bytes()
    return {
        "path": relative_or_absolute(path),
        "sha256": sha256(blob),
        "size": len(blob),
    }


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def normalize_linebreaks(value: str) -> str:
    return LINEBREAK_RE.sub("\n", value)


def is_full_width_visible(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xAC00 <= codepoint <= 0xD7AF
        or 0xF900 <= codepoint <= 0xFAFF
    )


def raw_metrics(display: str) -> Mapping[str, int]:
    full = sum(1 for character in display if is_full_width_visible(character))
    half = len(display) - full
    raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
    return {
        "full_width_character_count": full,
        "half_width_character_count": half,
        "raw_g1n_width_px": raw,
        "effective_width_px": math.ceil(raw * DRAW_FONT_PX / RAW_FULL_WIDTH_PX),
    }


def colour_structure(value: str) -> Mapping[str, Any]:
    in_span = False
    malformed: list[Mapping[str, Any]] = []
    linebreak_inside_colour_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            if ESC_RE.fullmatch(token) is None:
                malformed.append({"offset": cursor, "token": token})
                cursor += 1
                continue
            if token == "\x1bCZ":
                if not in_span:
                    malformed.append({"offset": cursor, "token": token, "reason": "unpaired_close"})
                in_span = False
            else:
                if in_span:
                    malformed.append({"offset": cursor, "token": token, "reason": "nested_open"})
                in_span = True
            cursor += 3
            continue
        if in_span and value[cursor] in "\r\n":
            linebreak_inside_colour_span = True
        cursor += 1
    if in_span:
        malformed.append({"offset": len(value), "token": None, "reason": "unterminated_open"})
    return {
        "structurally_valid": not malformed and not linebreak_inside_colour_span,
        "malformed_esc_sequences": malformed,
        "linebreak_inside_colour_span": linebreak_inside_colour_span,
    }


def text_signature(value: str) -> Mapping[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(value))
    printf_offsets = {match.start() for match in printf_matches}
    controls = [
        f"U+{ord(character):04X}"
        for character in value
        if character not in "\r\n\x1b" and unicodedata.category(character) == "Cc"
    ]
    return {
        "esc_tags": ESC_RE.findall(value),
        "numeric_name_tokens": NUMERIC_NAME_TOKEN_RE.findall(value),
        "bracket_tokens": BRACKET_TOKEN_RE.findall(value),
        "printf_tokens": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1 for offset, character in enumerate(value) if character == "%" and offset not in printf_offsets
        ),
        "other_c0_controls": controls,
        "manual_line_count": len(normalize_linebreaks(value).split("\n")),
        "colour_structure": colour_structure(value),
    }


def cross_language_structure(current: Mapping[str, Any], witness: Mapping[str, Any]) -> Mapping[str, bool]:
    return {
        "esc_tags": current["esc_tags"] == witness["esc_tags"],
        "numeric_name_tokens": current["numeric_name_tokens"] == witness["numeric_name_tokens"],
        "bracket_tokens": current["bracket_tokens"] == witness["bracket_tokens"],
        "printf_tokens": current["printf_tokens"] == witness["printf_tokens"],
        "other_c0_controls": current["other_c0_controls"] == witness["other_c0_controls"],
    }


def profile(packed: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "sha256": sha256(packed),
        "size": len(packed),
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
    }


def load_packed_table(path: Path, label: str) -> tuple[Sequence[str], Mapping[str, Any]]:
    require(path.is_file(), f"{label} is missing: {path}")
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(len(table.texts) == EXPECTED_TEXT_COUNT, f"{label} text-table count drift")
    return table.texts, profile(packed, raw)


def load_json(path: Path) -> Mapping[str, Any]:
    require(path.is_file(), f"JSON source is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), f"JSON root is not an object: {path}")
    return payload


def runtime_row_ids(texts: Sequence[str]) -> tuple[int, ...]:
    return tuple(
        entry_id
        for entry_id, value in enumerate(texts)
        if NUMERIC_NAME_TOKEN_RE.search(value) is not None or PRINTF_RE.search(value) is not None
    )


def load_strict_inputs() -> tuple[Sequence[str], Mapping[str, Any], Sequence[str], Mapping[str, Any], Mapping[str, Any]]:
    manifest = load_json(W101_MANIFEST)
    audit = load_json(W101_AUDIT)
    require(manifest.get("candidate_only") is True, "W101 must remain candidate-only")
    require(audit.get("candidate_only") is True, "W101 audit must remain candidate-only")
    require(manifest.get("resource") == MSGEV_RELATIVE.as_posix(), "W101 resource drift")
    require(tuple(manifest.get("applied_row_ids", ())) == EXPECTED_W101_CHANGED_IDS, "W101 changed-ID scope drift")
    require(tuple(audit.get("coverage", {}).get("applied_row_ids", ())) == EXPECTED_W101_CHANGED_IDS, "W101 audit scope drift")
    require(
        tuple(audit.get("coverage", {}).get("runtime_reservation_ids", ())) == EXPECTED_W101_RUNTIME_CHANGED_IDS,
        "W101 runtime reservation scope drift",
    )
    require(manifest.get("steam_game_resource_written") is False, "W101 must not claim Steam write")
    require(manifest.get("release_published") is False, "W101 must not claim release")
    w101_texts, w101_profile = load_packed_table(W101_EVENT, "W101 strict Korean input")
    require(manifest.get("output") == w101_profile, "W101 manifest output profile drift")
    require(audit.get("output_event_profile") == w101_profile, "W101 audit output profile drift")

    w100_manifest = load_json(W100_MANIFEST)
    require(w100_manifest.get("candidate_only") is True, "W100 must remain candidate-only")
    require(w100_manifest.get("resource") == MSGEV_RELATIVE.as_posix(), "W100 resource drift")
    w100_texts, w100_profile = load_packed_table(W100_EVENT, "W100 strict predecessor")
    require(w100_manifest.get("output") == w100_profile, "W100 manifest output profile drift")
    strict_input = manifest.get("strict_input", {})
    require(strict_input.get("workstream") == W100_ROOT.parent.name, "W101 predecessor workstream drift")
    require(strict_input.get("event_profile") == w100_profile, "W101 predecessor profile drift")

    changed_ids = tuple(
        entry_id
        for entry_id, (before, after) in enumerate(zip(w100_texts, w101_texts, strict=True))
        if before != after
    )
    require(changed_ids == EXPECTED_W101_CHANGED_IDS, "actual W100-to-W101 diff scope drift")
    w100_runtime_ids = runtime_row_ids(w100_texts)
    w101_runtime_ids = runtime_row_ids(w101_texts)
    require(w100_runtime_ids == w101_runtime_ids, "W100-to-W101 runtime scope changed unexpectedly")
    require(len(w101_runtime_ids) == EXPECTED_RUNTIME_ROW_COUNT, "runtime scope row count drift")
    runtime_changed_ids = tuple(entry_id for entry_id in changed_ids if entry_id in set(w101_runtime_ids))
    require(runtime_changed_ids == EXPECTED_W101_RUNTIME_CHANGED_IDS, "W101 runtime changed-ID scope drift")

    strict_info = {
        "workstream": W101_ROOT.parent.name,
        "candidate_relative": relative_or_absolute(W101_ROOT),
        "event_relative": relative_or_absolute(W101_EVENT),
        "event_profile": w101_profile,
        "manifest": file_record(W101_MANIFEST),
        "audit": file_record(W101_AUDIT),
        "candidate_only": True,
        "read_only": True,
        "steam_game_resource_written": False,
        "release_published": False,
    }
    rebase = {
        "predecessor_workstream": W100_ROOT.parent.name,
        "predecessor_candidate_relative": relative_or_absolute(W100_ROOT),
        "predecessor_event_profile": w100_profile,
        "w100_to_w101_changed_ids": list(changed_ids),
        "w100_runtime_row_count": len(w100_runtime_ids),
        "w101_runtime_row_count": len(w101_runtime_ids),
        "runtime_scope_identical": True,
        "runtime_changed_ids": list(runtime_changed_ids),
        "changed_ids_overlap_runtime_scope": bool(runtime_changed_ids),
        "policy": "W101 updated 15 event rows, including three runtime-name rows; all 1,049 runtime rows are remeasured from W101.",
    }
    return w101_texts, strict_info, w100_texts, rebase, audit


def load_direct_contexts(audit: Mapping[str, Any]) -> tuple[Mapping[str, Sequence[str]], Mapping[str, Any]]:
    declared = audit.get("direct_pc_source_resources")
    require(isinstance(declared, dict), "W101 direct-PC resource evidence is missing")
    tables: dict[str, Sequence[str]] = {}
    evidence: dict[str, Any] = {}
    for language in ("jp", "en", "sc", "tc"):
        path = DIRECT_CONTEXT_PATHS[language]
        resolved = path.resolve(strict=True)
        require("switch" not in {part.casefold() for part in resolved.parts}, f"non-PC witness forbidden: {resolved}")
        texts, direct_profile = load_packed_table(path, f"direct PC {language.upper()} witness")
        detail = declared.get(language)
        require(isinstance(detail, dict), f"W101 direct witness declaration missing: {language}")
        require(detail.get("path") == str(path), f"W101 direct witness path drift: {language}")
        require(detail.get("profile") == direct_profile, f"W101 direct witness profile drift: {language}")
        tables[language] = texts
        evidence[language] = {"path": str(path), "profile": direct_profile, "read_only": True}
    return tables, evidence


def plain_name_display(value: str, source_name_id: int) -> str:
    """Return a strictly local Korean name reservation, or raise on ambiguity."""
    structure = colour_structure(value)
    require(structure["structurally_valid"], f"name source has invalid colour structure: {source_name_id}")
    display = ESC_RE.sub("", value)
    require("\n" not in normalize_linebreaks(display), f"name source has line break: {source_name_id}")
    require(BRACKET_TOKEN_RE.search(display) is None, f"name source contains nested bracket token: {source_name_id}")
    require(PRINTF_RE.search(display) is None, f"name source contains printf token: {source_name_id}")
    require(
        not any(unicodedata.category(character) == "Cc" for character in display),
        f"name source contains control: {source_name_id}",
    )
    require(display != "", f"name source is empty: {source_name_id}")
    return display


def name_reservation(token: str, prefix: str, source_name_id: int, current_texts: Sequence[str]) -> Mapping[str, Any]:
    require(0 <= source_name_id < len(current_texts), f"runtime name ID out of range: {token}")
    display = plain_name_display(current_texts[source_name_id], source_name_id)
    metrics = raw_metrics(display)
    return {
        "token": token,
        "prefix": prefix,
        "source_name_id": source_name_id,
        "display_string": display,
        "display_utf16le_sha256": text_hash(display),
        "reserved_raw_g1n_width_px": metrics["raw_g1n_width_px"],
        "reserved_effective_width_px": metrics["effective_width_px"],
        "runtime_proven": False,
        "prefix_semantics_assumed": False,
        "reservation_policy": "same numeric ID in strict Korean MSGEV; full displayed name reserved without inferring prefix behaviour",
    }


def measure_line(entry_id: int, line_number: int, source_line: str, current_texts: Sequence[str]) -> Mapping[str, Any]:
    static_visible: list[str] = []
    resolved_visible: list[str] = []
    template: list[str] = []
    reservations: list[Mapping[str, Any]] = []
    unresolved: list[Mapping[str, Any]] = []
    cursor = 0
    while cursor < len(source_line):
        if source_line[cursor] == "\x1b":
            token = source_line[cursor : cursor + 3]
            if ESC_RE.fullmatch(token) is None:
                unresolved.append({"token": token, "kind": "malformed_esc"})
                template.append("{malformed_esc}")
                cursor += 1
            else:
                cursor += 3
            continue
        numeric = NUMERIC_NAME_TOKEN_RE.match(source_line, cursor)
        if numeric is not None:
            token = numeric.group(0)
            prefix = numeric.group(1)
            source_name_id = int(numeric.group(2))
            reservation = name_reservation(token, prefix, source_name_id, current_texts)
            template.append("{" + token + "}")
            resolved_visible.append(str(reservation["display_string"]))
            reservations.append(reservation)
            cursor = numeric.end()
            continue
        bracket = BRACKET_TOKEN_RE.match(source_line, cursor)
        if bracket is not None:
            token = bracket.group(0)
            template.append("{" + token + "}")
            unresolved.append({"token": token, "kind": "unresolved_bracket_token_or_ui"})
            cursor = bracket.end()
            continue
        printf = PRINTF_RE.match(source_line, cursor)
        if printf is not None:
            token = printf.group(0)
            template.append("{" + token + "}")
            unresolved.append(
                {
                    "token": token,
                    "kind": "printf_runtime_value_without_width_bound",
                    "reason": "No row-local rendered value or safe width upper bound is available; do not infer it.",
                }
            )
            cursor = printf.end()
            continue
        character = source_line[cursor]
        if unicodedata.category(character) == "Cc":
            unresolved.append({"token": f"U+{ord(character):04X}", "kind": "unresolved_control_or_ui"})
            template.append("{control}")
        else:
            static_visible.append(character)
            resolved_visible.append(character)
            template.append(character)
        cursor += 1

    static = raw_metrics("".join(static_visible))
    line: dict[str, Any] = {
        "line_number": line_number,
        "source_line_with_tags_and_tokens": source_line,
        "display_template": "".join(template),
        "static_visible_string": "".join(static_visible),
        "static_full_width_character_count": static["full_width_character_count"],
        "static_half_width_character_count": static["half_width_character_count"],
        "static_raw_g1n_width_px": static["raw_g1n_width_px"],
        "static_effective_width_px": static["effective_width_px"],
        "runtime_name_reservations": reservations,
        "unresolved_runtime_or_ui_tokens": unresolved,
    }
    if unresolved:
        line.update(
            {
                "measurement_status": "unresolved_runtime_or_ui_hold",
                "display_string": None,
                "full_width_character_count": None,
                "half_width_character_count": None,
                "raw_g1n_width_px": None,
                "effective_width_px": None,
                "over_912px": None,
            }
        )
        return line
    display = "".join(resolved_visible)
    measured = raw_metrics(display)
    line.update(
        {
            "measurement_status": "measured_runtime_name_reservation" if reservations else "measured_literal_static_text",
            "display_string": display,
            "full_width_character_count": measured["full_width_character_count"],
            "half_width_character_count": measured["half_width_character_count"],
            "raw_g1n_width_px": measured["raw_g1n_width_px"],
            "effective_width_px": measured["effective_width_px"],
            "over_912px": measured["effective_width_px"] > EFFECTIVE_LIMIT_PX,
        }
    )
    return line


def build_row(entry_id: int, current_texts: Sequence[str], direct_tables: Mapping[str, Sequence[str]]) -> Mapping[str, Any]:
    current_ko = current_texts[entry_id]
    signature = text_signature(current_ko)
    direct = {language: direct_tables[language][entry_id] for language in ("jp", "en", "sc", "tc")}
    direct_signatures = {language: text_signature(value) for language, value in direct.items()}
    lines = [
        measure_line(entry_id, number, source_line, current_texts)
        for number, source_line in enumerate(normalize_linebreaks(current_ko).split("\n"), 1)
    ]
    for line in lines:
        line["row_manual_line_count"] = len(lines)
    has_unresolved = any(line["measurement_status"] == "unresolved_runtime_or_ui_hold" for line in lines)
    line_count_overflow = len(lines) > MAX_LINES
    width_overflow = any(line["over_912px"] is True for line in lines)
    if not signature["colour_structure"]["structurally_valid"]:
        status = "unresolved_token_or_ui_hold"
        status_reason = "invalid_colour_structure"
    elif has_unresolved:
        status = "unresolved_token_or_ui_hold"
        status_reason = "unbounded_runtime_or_ui_token"
    elif line_count_overflow or width_overflow:
        status = "width_or_line_overflow_candidate"
        status_reason = "manual_line_count_exceeds_4" if line_count_overflow else "effective_width_exceeds_912px"
    else:
        status = "pass"
        status_reason = "all_runtime_name_reservations_measured;_each_line_within_912px;manual_line_count_within_4"
    return {
        "entry_id": entry_id,
        "current_ko": current_ko,
        "current_ko_utf16le_sha256": text_hash(current_ko),
        "direct_pc_context_read_only": {
            language: {
                "text": direct[language],
                "utf16le_sha256": text_hash(direct[language]),
                "structure_signature": direct_signatures[language],
                "structure_matches_current_ko": cross_language_structure(signature, direct_signatures[language]),
            }
            for language in ("jp", "en", "sc", "tc")
        },
        "current_ko_structure_signature": signature,
        "manual_line_count": len(lines),
        "maximum_manual_lines": MAX_LINES,
        "manual_line_count_exceeds_4": line_count_overflow,
        "any_line_over_912px": width_overflow if not has_unresolved else None,
        "status": status,
        "status_reason": status_reason,
        "lines": lines,
        "constraints": {
            "runtime_proven_is_false_for_name_reservations": True,
            "prefix_semantics_not_inferred": True,
            "source_language_linebreaks_not_copied": True,
            "sentence_shortening_or_deletion_performed": False,
            "event_candidate_created": False,
        },
    }


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    statuses = Counter(str(row["status"]) for row in rows)
    numeric_rows = sum(bool(row["current_ko_structure_signature"]["numeric_name_tokens"]) for row in rows)
    printf_rows = sum(bool(row["current_ko_structure_signature"]["printf_tokens"]) for row in rows)
    require(numeric_rows == 859, "numeric runtime row count drift")
    require(printf_rows == 190, "printf runtime row count drift")
    require(numeric_rows + printf_rows == EXPECTED_RUNTIME_ROW_COUNT, "runtime class union drift")
    require(
        statuses == Counter({"pass": 859, "unresolved_token_or_ui_hold": 190}),
        f"runtime layout status drift: {dict(statuses)}",
    )
    return {
        "runtime_row_count": len(rows),
        "numeric_name_token_row_count": numeric_rows,
        "printf_runtime_token_row_count": printf_rows,
        "status_counts": dict(sorted(statuses.items())),
        "width_or_line_overflow_candidate_count": statuses["width_or_line_overflow_candidate"],
        "unresolved_token_or_ui_hold_count": statuses["unresolved_token_or_ui_hold"],
        "pass_count": statuses["pass"],
        "runtime_name_reservation_occurrence_count": sum(
            len(line["runtime_name_reservations"])
            for row in rows
            for line in row["lines"]
        ),
        "printf_runtime_token_occurrence_count": sum(
            len(row["current_ko_structure_signature"]["printf_tokens"]) for row in rows
        ),
        "maximum_observed_manual_line_count": max(int(row["manual_line_count"]) for row in rows),
    }


def render_report(ledger: Mapping[str, Any], validation: Mapping[str, Any]) -> str:
    counts = ledger["counts"]
    return "\n".join(
        [
            "# PK 이벤트 런타임 토큰 레이아웃 전수 감사",
            "",
            "## 결론",
            "",
            f"W101 strict 한국어 후보의 런타임 행 **{counts['runtime_row_count']:,}행**을 Static Patch 007 기준으로 전수 계측했습니다.",
            f"인명 숫자 토큰 행 **{counts['numeric_name_token_row_count']:,}행**은 모두 최대 4줄·각 줄 유효폭 912px 이하로 **통과**했습니다.",
            f"폭 또는 줄 수 초과 후보는 **{counts['width_or_line_overflow_candidate_count']:,}행**입니다.",
            f"`%s`/`%d`처럼 실제 런타임 값의 행별 상한을 입증할 수 없는 **{counts['unresolved_token_or_ui_hold_count']:,}행**은 안전하게 hold로 남겼습니다. 이 hold는 레이아웃 통과 판정이 아니라, 값 상한 증거가 없다는 뜻입니다.",
            "",
            "## 기준과 범위",
            "",
            "- PK `MSGEV`만 적용: 30px, 줄 간격 8, 유효폭 912px, 최대 4줄.",
            "- 원본 G1N 기준 폭은 전각 48px/반각 24px이며, 유효폭은 `ceil(raw_g1n_width_px * 30 / 48)`입니다.",
            "- 숫자 인명 토큰은 같은 ID의 strict 한국어 이름 전체 폭을 예약했습니다. prefix의 런타임 의미는 추론하지 않았고 모든 예약은 `runtime_proven=false`입니다.",
            "- JP/EN/SC/TC는 의미·태그·토큰 구조 확인용 읽기 전용 증거입니다. 타 언어의 줄바꿈을 한국어에 이식하지 않았습니다.",
            "",
            "## W100 → W101 재베이스",
            "",
            f"W101의 변경 ID는 {', '.join(map(str, ledger['w100_to_w101_rebase']['w100_to_w101_changed_ids']))}입니다. 이 중 런타임 행은 {', '.join(map(str, ledger['w100_to_w101_rebase']['runtime_changed_ids']))}이며, 해당 3행도 W101 새 문안 기준으로 다시 계측했습니다. W100과 W101의 런타임 행 범위는 동일한 {counts['runtime_row_count']:,}행입니다.",
            "",
            "행별 표시 문자열(확정 불가 hold는 `null`), raw/effective 폭, 전각/반각 수, 줄 수, 912px 초과 여부, 토큰 예약·보류 사유는 `public/pc_event_runtime_layout_inventory.v1.json`에 전부 기록했습니다.",
            "",
            f"검증 상태: **{validation['status']}**. Steam 파일·후보 바이너리·Git·네트워크·릴리스에는 쓰지 않았습니다.",
            "",
        ]
    )


def build_bundle() -> tuple[Mapping[str, Any], Mapping[str, Any], str]:
    current_texts, strict_info, _w100_texts, rebase, audit = load_strict_inputs()
    direct_tables, direct_info = load_direct_contexts(audit)
    ids = runtime_row_ids(current_texts)
    rows = tuple(build_row(entry_id, current_texts, direct_tables) for entry_id in ids)
    counts = summarize_rows(rows)
    ledger = {
        "schema": "nobu16.kr.pc-event-runtime-layout-inventory.v1",
        "read_only": True,
        "event_candidate_created": False,
        "resource": MSGEV_RELATIVE.as_posix(),
        "strict_korean_input": strict_info,
        "w100_to_w101_rebase": rebase,
        "direct_pc_context_evidence": direct_info,
        "scope_selection": {
            "policy": "row contains a numeric runtime-name token [prefix+ID] or a printf runtime token",
            "numeric_name_token_regex": NUMERIC_NAME_TOKEN_RE.pattern,
            "printf_token_regex": PRINTF_RE.pattern,
            "expected_runtime_row_count": EXPECTED_RUNTIME_ROW_COUNT,
            "entry_ids": list(ids),
        },
        "layout_policy": {
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_width_limit_px": EFFECTIVE_LIMIT_PX,
            "raw_equivalent_limit_px": RAW_EQUIVALENT_LIMIT_PX,
            "maximum_manual_lines": MAX_LINES,
            "dynamic_name_reservation_policy": "same numeric ID strict Korean full name; scaled by 30/48; runtime_proven=false; prefix semantics not inferred",
            "source_language_linebreak_copying": "forbidden",
        },
        "counts": counts,
        "rows": rows,
        "steam_game_resource_written": False,
        "transaction_performed": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }
    validation = {
        "schema": "nobu16.kr.pc-event-runtime-layout-inventory-validation.v1",
        "status": "PASS",
        "read_only": True,
        "runtime_row_count": len(rows),
        "status_counts": counts["status_counts"],
        "w100_to_w101_runtime_scope_identical": rebase["runtime_scope_identical"],
        "w101_runtime_changed_ids": rebase["runtime_changed_ids"],
        "output": relative_or_absolute(LEDGER_PATH),
        "steam_game_resource_written": False,
        "transaction_performed": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }
    return ledger, validation, render_report(ledger, validation)


def require_output_path(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = WORKSTREAM.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise InventoryError(f"output escapes workstream: {resolved}") from exc
    require("candidate-final" not in {part.casefold() for part in resolved.parts}, f"candidate output forbidden: {resolved}")
    return resolved


def write_atomic(path: Path, payload: bytes) -> None:
    target = require_output_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = require_output_path(target.with_name(target.name + ".staging"))
    require(not staging.exists(), f"stale staging output: {staging}")
    try:
        staging.write_bytes(payload)
        os.replace(staging, target)
    finally:
        staging.unlink(missing_ok=True)


def write_outputs(bundle: tuple[Mapping[str, Any], Mapping[str, Any], str]) -> Mapping[str, str]:
    ledger, validation, report = bundle
    write_atomic(LEDGER_PATH, canonical_json(ledger))
    write_atomic(VALIDATION_PATH, canonical_json(validation))
    write_atomic(REPORT_PATH, report.encode("utf-8"))
    return {
        "ledger": relative_or_absolute(LEDGER_PATH),
        "validation": relative_or_absolute(VALIDATION_PATH),
        "report": relative_or_absolute(REPORT_PATH),
    }


def verify_outputs(bundle: tuple[Mapping[str, Any], Mapping[str, Any], str]) -> Mapping[str, Any]:
    ledger, validation, report = bundle
    expected = {
        LEDGER_PATH: canonical_json(ledger),
        VALIDATION_PATH: canonical_json(validation),
        REPORT_PATH: report.encode("utf-8"),
    }
    for path, payload in expected.items():
        require(path.is_file(), f"output missing: {path}")
        require(path.read_bytes() == payload, f"nondeterministic output: {path}")
    return {
        "status": "PASS",
        "runtime_row_count": validation["runtime_row_count"],
        "status_counts": validation["status_counts"],
        "steam_game_resource_written": False,
        "event_candidate_created": False,
    }


def source_whitespace_check() -> None:
    for path in (SCRIPT, WORKSTREAM / "test_pc_event_runtime_layout_inventory_v1.py"):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "summary"))
    args = parser.parse_args(argv)
    source_whitespace_check()
    bundle = build_bundle()
    if args.command == "build":
        print(json.dumps(write_outputs(bundle), ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "verify":
        print(json.dumps(verify_outputs(bundle), ensure_ascii=False, sort_keys=True))
        return 0
    _ledger, validation, _report = bundle
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (InventoryError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
