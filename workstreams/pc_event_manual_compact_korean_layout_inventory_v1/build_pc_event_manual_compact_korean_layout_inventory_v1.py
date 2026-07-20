#!/usr/bin/env python3
"""Build a read-only current-successor inventory of manual-compact PK event rows.

This workstream is deliberately an audit workstream.  It never creates an
event candidate, never writes the Steam installation, and never performs a
transaction, Git, network, or release operation.  Its only writes are the
tracked JSON/Markdown reports under this workstream directory.
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
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PUBLIC = WORKSTREAM / "public"

SOURCE_LAYOUT = (
    REPO
    / "workstreams"
    / "steam_jp_msgev_full_layout_v2"
    / "public"
    / "msgev_ko_steam_jp_full_layout.v2.json"
)
SOURCE_RESERVATIONS = (
    REPO
    / "workstreams"
    / "steam_jp_msgev_full_layout_v2"
    / "public"
    / "runtime_token_reservations.v1.json"
)
W97_ROOT = REPO / "tmp" / "pc_event_toyotomi_kanpaku_quality_wave97_v1" / "candidate-final"
MSGEV_RELATIVE = Path("MSG_PK") / "JP" / "msgev.bin"
W97_EVENT = W97_ROOT / MSGEV_RELATIVE
W97_AUDIT = W97_ROOT / "audit.v1.json"
W97_MANIFEST = W97_ROOT / "candidate_manifest.v1.json"
STATIC007_3LINE_ROOT = REPO / "tmp" / "pc_event_5777_kanegasaki_static007_3line_v1" / "candidate-final"
STATIC007_3LINE_EVENT = STATIC007_3LINE_ROOT / MSGEV_RELATIVE
STATIC007_3LINE_AUDIT = STATIC007_3LINE_ROOT / "audit.v1.json"
STATIC007_3LINE_MANIFEST = STATIC007_3LINE_ROOT / "candidate_manifest.v1.json"
BATCH01_ROOT = REPO / "tmp" / "pc_event_manual_compact_static007_batch01_v1" / "candidate-final"
BATCH01_EVENT = BATCH01_ROOT / MSGEV_RELATIVE
BATCH01_AUDIT = BATCH01_ROOT / "audit.v1.json"
BATCH01_MANIFEST = BATCH01_ROOT / "candidate_manifest.v1.json"
CURRENT_ROOT = REPO / "tmp" / "pc_event_manual_compact_static007_batch02_v1" / "candidate-final"
CURRENT_EVENT = CURRENT_ROOT / MSGEV_RELATIVE
CURRENT_AUDIT = CURRENT_ROOT / "audit.v1.json"
CURRENT_MANIFEST = CURRENT_ROOT / "candidate_manifest.v1.json"
LEGACY_STATIC_PREFLIGHT_EVENT = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
    r"\steam-jp-v0.10.0-original-font-rollback-v1\originals\MSG_PK\JP\msgev.bin"
)

DIRECT_CONTEXT_PATHS: Mapping[str, Path] = {
    "jp": Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
        r"\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msgev.bin"
    ),
    "en": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msgev.bin"),
    "sc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msgev.bin"),
    "tc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msgev.bin"),
}

INVENTORY_PATH = PUBLIC / "msgev_manual_compact_korean_layout_inventory.v1.json"
BATCHES_PATH = PUBLIC / "msgev_manual_compact_korean_layout_batches.v1.json"
VALIDATION_PATH = WORKSTREAM / "validation.v1.json"
REPORT_PATH = WORKSTREAM / "REPORT_KO.md"

MANUAL_OPERATION = "manual_compact_korean_layout"
MANUAL_NEWLINE_OPERATIONS = frozenset({"reviewed_semantic_compaction", "manual_compaction"})
EXPECTED_ROW_COUNT = 1_553
EXPECTED_ID_RANGE = (3_210, 11_008)
EXPECTED_STRING_COUNT = 17_916

EXPECTED_SOURCE_LAYOUT_SHA256 = "10EE44F4D5F5A871F5DEDB60C6435F4115E698FB1544B898EA421356FAB6BF42"
EXPECTED_RESERVATIONS_SHA256 = "B981C7C456F2DC285721E7E3DB74D2D11456B49B25D5A97BB320F815DFC0A893"
EXPECTED_W97_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "E1810DEA757C5179A8C5631251656CDA83C36425C0699BE95650A6CCFBE4C11F",
    "raw_size": 996_240,
    "sha256": "C5451B9BA726C8D06743E86D8F6ED320E052F6B6065A37D550DE4ACCE3CF4810",
    "size": 1_000_172,
}
EXPECTED_STATIC007_3LINE_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "92B11470E00C7A5004739847D2548286D296B76D4C6016FD1B5E0DDD542EB611",
    "raw_size": 996_276,
    "sha256": "1F7E42E10C0034CD70565993BE3DB311DF3A5356525B6BA14B31987752967745",
    "size": 1_000_208,
}
EXPECTED_BATCH01_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "568D4D514D75A35A6ED9F15841CD682D4795C6563DC0ADBF4A4843EE806034DA",
    "raw_size": 996_420,
    "sha256": "0966577DD40656B46D4276FA49F448F7D44E5A1C7845B814EABC07604B73CFD4",
    "size": 1_000_353,
}
EXPECTED_CURRENT_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "C9F9BD8772C16DC7FC10220AE515FDFAC2C0B3DBF431B8D07A71604982274C05",
    "raw_size": 996_456,
    "sha256": "20050DDFB1F5791A20DF7B05FBA891B654D0486F519410EEE516991368D9C41A",
    "size": 1_000_389,
}
EXPECTED_CURRENT_HISTORICAL_DIFFERENCE_COUNT = 205
EXPECTED_BATCH01_CHANGED_IDS = (3_210, 3_231, 3_232, 3_233, 3_234, 3_239)
EXPECTED_CURRENT_BATCH02_CHANGED_IDS = (3_254, 3_260)
EXPECTED_LEGACY_STATIC_PREFLIGHT_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "EDCF7A9CEBD605BB2275D5A3B92A76E7E2F652B2391554F24C6A8BDD2EF91A08",
    "raw_size": 1_047_944,
    "sha256": "2CA183DA690D45A75702EA0F35C70966786B59E9440B8B8F49BE9652342F81AC",
    "size": 1_052_079,
}
EXPECTED_LEGACY_STATIC_PREFLIGHT_RECOVERY_COUNTS: Mapping[str, int] = {
    "current_same+oldfit": 1_319,
    "current_diff+oldfit": 201,
    "current_same+reflow": 29,
    "current_diff+reflow": 4,
}
EXPECTED_LEGACY_STATIC_PREFLIGHT_REFLOW_IDS = (
    5_164,
    6_654,
    7_308,
    7_610,
    7_611,
    7_734,
    8_449,
    8_513,
    8_696,
    8_818,
    9_049,
    9_083,
    9_140,
    9_141,
    9_169,
    9_228,
    9_326,
    9_338,
    9_340,
    9_523,
    9_540,
    9_541,
    9_624,
    9_683,
    10_136,
    10_183,
    10_314,
    10_334,
    10_343,
    10_463,
    10_595,
    10_625,
    10_744,
)
EXPECTED_DIRECT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    "jp": {
        "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
        "raw_size": 894_800,
        "sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
        "size": 562_226,
    },
    "en": {
        "raw_sha256": "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911",
        "raw_size": 1_878_836,
        "sha256": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
        "size": 762_196,
    },
    "sc": {
        "raw_sha256": "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E",
        "raw_size": 754_708,
        "sha256": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
        "size": 522_177,
    },
    "tc": {
        "raw_sha256": "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6",
        "raw_size": 744_212,
        "sha256": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
        "size": 524_909,
    },
}

# Static patch 007 is authoritative: 30px effective width <= 912px (the raw
# 48/24 equivalent is <= 1440px), with at most four manual lines.  Raw values
# are recorded for review, but the obsolete 960px gate never drives a pass/fail
# decision in this inventory.
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
MAX_LINES = 4
DRAW_FONT_PX = 30
STATIC_PATCH_007_EFFECTIVE_LIMIT_PX = 912
STATIC_PATCH_007_RAW_EQUIVALENT_LIMIT_PX = 1_440

ESC_RE = re.compile(r"\x1bC[ABCZ]")
BRACKET_TOKEN_RE = re.compile(r"\[[^\[\]\r\n]+\]")
NUMERIC_RUNTIME_RE = re.compile(r"\[([A-Za-z]{1,16})(\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
WAVE_RE = re.compile(r"(?:^|_)wave(\d+)(?:_|$)", re.IGNORECASE)


TOOLS_ROOT = REPO / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


class InventoryError(RuntimeError):
    """Raised when a pinned read-only input or generated audit drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InventoryError(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def relative(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def file_record(path: Path) -> Mapping[str, Any]:
    blob = path.read_bytes()
    return {"relative_path": relative(path), "size": len(blob), "sha256": sha256(blob)}


def profile(packed: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "sha256": sha256(packed),
        "size": len(packed),
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
    }


def normalize_linebreaks(value: str) -> str:
    return LINEBREAK_RE.sub("\n", value)


def is_full_width_visible(character: str) -> bool:
    """Use the static-007 raw baseline: Hangul/Hanja are full-width."""
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


def strip_valid_esc_tags(value: str) -> str:
    return ESC_RE.sub("", value)


def colour_structure(value: str) -> Mapping[str, Any]:
    in_span = False
    malformed: list[Mapping[str, Any]] = []
    linebreak_inside = False
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
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
        if in_span and character in "\r\n":
            linebreak_inside = True
        cursor += 1
    if in_span:
        malformed.append({"offset": len(value), "token": None, "reason": "unterminated_open"})
    return {
        "malformed_esc_sequences": malformed,
        "linebreak_inside_colour_tag": linebreak_inside,
        "structurally_valid": not malformed and not linebreak_inside,
    }


def text_signature(value: str) -> Mapping[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(value))
    printf_offsets = {match.start() for match in printf_matches}
    controls: list[str] = []
    pua: list[str] = []
    for offset, character in enumerate(value):
        if character in "\r\n\x1b":
            continue
        if unicodedata.category(character) == "Cc":
            controls.append(f"U+{ord(character):04X}")
        if 0xE000 <= ord(character) <= 0xF8FF:
            pua.append(f"U+{ord(character):04X}")
    return {
        "esc_tags": ESC_RE.findall(value),
        "runtime_bracket_tokens": BRACKET_TOKEN_RE.findall(value),
        "numeric_runtime_tokens": NUMERIC_RUNTIME_RE.findall(value),
        "printf_tokens": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1 for offset, character in enumerate(value) if character == "%" and offset not in printf_offsets
        ),
        "other_c0_controls": controls,
        "pua_codepoints": pua,
        "manual_linebreak_count": len(LINEBREAK_RE.findall(value)),
        "colour_structure": colour_structure(value),
    }


def cross_language_signature_match(current: Mapping[str, Any], context: Mapping[str, Any]) -> Mapping[str, bool]:
    return {
        "esc_tags": current["esc_tags"] == context["esc_tags"],
        "runtime_bracket_tokens": current["runtime_bracket_tokens"] == context["runtime_bracket_tokens"],
        "printf_tokens": current["printf_tokens"] == context["printf_tokens"],
        "other_c0_controls": current["other_c0_controls"] == context["other_c0_controls"],
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_source_entries() -> tuple[Mapping[int, Mapping[str, Any]], Mapping[str, Any]]:
    require(SOURCE_LAYOUT.is_file(), f"manual-layout source is missing: {SOURCE_LAYOUT}")
    require(
        sha256(SOURCE_LAYOUT.read_bytes()) == EXPECTED_SOURCE_LAYOUT_SHA256,
        "manual-layout source hash drift",
    )
    source = load_json(SOURCE_LAYOUT)
    require(source.get("schema") == "nobu16.kr.steam-jp-msgev-full-layout-overlay.v2", "source schema drift")
    entries = source.get("entries")
    require(isinstance(entries, list), "source entries are missing")
    operation_rows = [entry for entry in entries if entry.get("operation") == MANUAL_OPERATION]
    selected = [
        entry
        for entry in operation_rows
        if isinstance(entry.get("newline_operations"), list)
        and len(entry["newline_operations"]) == 1
        and entry["newline_operations"][0] in MANUAL_NEWLINE_OPERATIONS
    ]
    require(
        len(operation_rows) == len(selected) == EXPECTED_ROW_COUNT,
        "manual operation/newline-operation selection drift",
    )
    by_id = {int(entry["id"]): entry for entry in selected}
    require(len(by_id) == EXPECTED_ROW_COUNT, "manual selection contains duplicate IDs")
    ids = tuple(sorted(by_id))
    require((ids[0], ids[-1]) == EXPECTED_ID_RANGE, "manual selection ID range drift")
    require(source.get("selection", {}).get("reviewed_semantic_compaction_count") == 1_552, "source review count drift")
    require(by_id[10_564]["newline_operations"] == ["manual_compaction"], "manual-compaction exception drift")
    return by_id, {
        "file": file_record(SOURCE_LAYOUT),
        "schema": source["schema"],
        "total_entry_count": len(entries),
        "manual_operation": MANUAL_OPERATION,
        "allowed_manual_newline_operations": sorted(MANUAL_NEWLINE_OPERATIONS),
        "selected_row_count": len(selected),
        "selected_id_range": [ids[0], ids[-1]],
        "newline_operation_counts": dict(
            sorted(Counter(entry["newline_operations"][0] for entry in selected).items())
        ),
    }


def load_packed_table(path: Path, label: str, expected: Mapping[str, Any]) -> tuple[Sequence[str], Mapping[str, Any]]:
    require(path.is_file(), f"{label} is missing: {path}")
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    source_profile = profile(packed, raw)
    require(source_profile == expected, f"{label} profile drift")
    require(len(table.texts) == EXPECTED_STRING_COUNT, f"{label} string-table count drift")
    return table.texts, source_profile


def load_w97_predecessor() -> tuple[Sequence[str], Mapping[str, Any]]:
    require(W97_AUDIT.is_file() and W97_MANIFEST.is_file(), "W97 audit/manifest is missing")
    audit = load_json(W97_AUDIT)
    manifest = load_json(W97_MANIFEST)
    require(audit.get("candidate_only") is True, "W97 must remain a private candidate")
    require(manifest.get("candidate_only") is True, "W97 manifest candidate scope drift")
    require(audit.get("output_event_profile") == EXPECTED_W97_PROFILE, "W97 audit profile drift")
    require(manifest.get("output") == EXPECTED_W97_PROFILE, "W97 manifest profile drift")
    texts, source_profile = load_packed_table(W97_EVENT, "strict W97 Korean predecessor", EXPECTED_W97_PROFILE)
    return texts, {
        "candidate_relative": relative(W97_ROOT),
        "event_relative": relative(W97_EVENT),
        "event_profile": source_profile,
        "audit": file_record(W97_AUDIT),
        "manifest": file_record(W97_MANIFEST),
        "read_only": True,
        "steam_game_resource_written": False,
    }


def load_static007_3line_predecessor() -> tuple[Sequence[str], Mapping[str, Any]]:
    """Load and pin the intervening verified 5777 static-007 three-line state."""
    require(
        STATIC007_3LINE_AUDIT.is_file() and STATIC007_3LINE_MANIFEST.is_file(),
        "static-007 5777 audit/manifest is missing",
    )
    audit = load_json(STATIC007_3LINE_AUDIT)
    manifest = load_json(STATIC007_3LINE_MANIFEST)
    require(audit.get("candidate_only") is True, "static-007 5777 must remain a private candidate")
    require(manifest.get("candidate_only") is True, "static-007 5777 manifest candidate scope drift")
    require(
        audit.get("schema") == "nobu16.kr.pc-event-5777-kanegasaki-static007-3line-audit.v1",
        "static-007 5777 audit schema drift",
    )
    require(
        manifest.get("schema") == "nobu16.kr.pc-event-5777-kanegasaki-static007-3line-manifest.v1",
        "static-007 5777 manifest schema drift",
    )
    require(audit.get("output_event_profile") == EXPECTED_STATIC007_3LINE_PROFILE, "static-007 5777 audit profile drift")
    require(manifest.get("output") == EXPECTED_STATIC007_3LINE_PROFILE, "static-007 5777 manifest profile drift")
    require(manifest.get("resource") == MSGEV_RELATIVE.as_posix(), "static-007 5777 resource drift")
    require(manifest.get("changed_row_ids") == [5777], "static-007 5777 changed-row scope drift")
    require(audit.get("actual_changed_row_ids") == [5777], "static-007 5777 audit changed-row scope drift")
    predecessor = manifest.get("predecessor", {})
    require(predecessor.get("workstream") == "pc_event_toyotomi_kanpaku_quality_wave97_v1", "static-007 5777 predecessor drift")
    require(predecessor.get("profile") == EXPECTED_W97_PROFILE, "static-007 5777 predecessor profile drift")
    require(predecessor.get("strict_on_disk") is True, "static-007 5777 must pin its strict predecessor")
    texts, source_profile = load_packed_table(
        STATIC007_3LINE_EVENT,
        "static-007 5777 Korean predecessor",
        EXPECTED_STATIC007_3LINE_PROFILE,
    )
    audit_rows = audit.get("rows")
    require(isinstance(audit_rows, list), "static-007 5777 rows are missing")
    static_row = next((row for row in audit_rows if isinstance(row, dict) and row.get("entry_id") == 5777), None)
    require(isinstance(static_row, dict), "static-007 5777 audit row is missing")
    require(static_row.get("target_ko") == texts[5777], "static-007 5777 target text drift")
    require(static_row.get("target_manual_line_count") == 3, "static-007 5777 must preserve the three-line revision")
    require(len(normalize_linebreaks(texts[5777]).split("\n")) == 3, "static-007 5777 table must preserve three lines")
    return texts, {
        "candidate_relative": relative(STATIC007_3LINE_ROOT),
        "event_relative": relative(STATIC007_3LINE_EVENT),
        "event_profile": source_profile,
        "audit": file_record(STATIC007_3LINE_AUDIT),
        "manifest": file_record(STATIC007_3LINE_MANIFEST),
        "predecessor_workstream": predecessor["workstream"],
        "predecessor_event_profile": predecessor["profile"],
        "read_only": True,
        "steam_game_resource_written": False,
    }


def load_batch01_predecessor(static007_3line_texts: Sequence[str]) -> tuple[Sequence[str], Mapping[str, Any]]:
    """Load and pin batch01, the strict predecessor of the current batch02 state."""
    require(BATCH01_AUDIT.is_file() and BATCH01_MANIFEST.is_file(), "batch01 audit/manifest is missing")
    audit = load_json(BATCH01_AUDIT)
    manifest = load_json(BATCH01_MANIFEST)
    require(audit.get("candidate_only") is True, "batch01 must remain a private candidate")
    require(manifest.get("candidate_only") is True, "batch01 manifest candidate scope drift")
    require(
        audit.get("schema") == "nobu16.kr.pc-event-manual-compact-static007-batch01-audit.v1",
        "batch01 audit schema drift",
    )
    require(
        manifest.get("schema") == "nobu16.kr.pc-event-manual-compact-static007-batch01-manifest.v1",
        "batch01 manifest schema drift",
    )
    require(audit.get("output_event_profile") == EXPECTED_BATCH01_PROFILE, "batch01 audit profile drift")
    require(manifest.get("output") == EXPECTED_BATCH01_PROFILE, "batch01 manifest profile drift")
    require(manifest.get("resource") == MSGEV_RELATIVE.as_posix(), "batch01 resource drift")
    require(tuple(manifest.get("changed_row_ids", ())) == EXPECTED_BATCH01_CHANGED_IDS, "batch01 changed-row scope drift")
    require(tuple(audit.get("actual_changed_row_ids", ())) == EXPECTED_BATCH01_CHANGED_IDS, "batch01 audit changed-row scope drift")
    predecessor = manifest.get("predecessor", {})
    require(predecessor.get("workstream") == STATIC007_3LINE_ROOT.parent.name, "batch01 predecessor drift")
    require(predecessor.get("profile") == EXPECTED_STATIC007_3LINE_PROFILE, "batch01 predecessor profile drift")
    require(predecessor.get("strict_on_disk") is True, "batch01 must pin its strict predecessor")
    texts, source_profile = load_packed_table(BATCH01_EVENT, "batch01 Korean predecessor", EXPECTED_BATCH01_PROFILE)
    actual_changed_ids = tuple(
        entry_id
        for entry_id, (current, predecessor_text) in enumerate(zip(texts, static007_3line_texts, strict=True))
        if current != predecessor_text
    )
    require(actual_changed_ids == EXPECTED_BATCH01_CHANGED_IDS, "batch01 table diff against static-007 predecessor drift")
    require(
        len(normalize_linebreaks(texts[5777]).split("\n")) == 3,
        "batch01 must preserve the static-007 three-line 5777 revision",
    )
    return texts, {
        "candidate_relative": relative(BATCH01_ROOT),
        "event_relative": relative(BATCH01_EVENT),
        "event_profile": source_profile,
        "audit": file_record(BATCH01_AUDIT),
        "manifest": file_record(BATCH01_MANIFEST),
        "predecessor_workstream": predecessor["workstream"],
        "predecessor_event_profile": predecessor["profile"],
        "changed_row_ids_against_static007_3line": list(actual_changed_ids),
        "read_only": True,
        "steam_game_resource_written": False,
    }


def load_current_successor(batch01_texts: Sequence[str]) -> tuple[Sequence[str], Mapping[str, Any]]:
    """Load the authoritative batch02 current Korean state."""
    require(CURRENT_AUDIT.is_file() and CURRENT_MANIFEST.is_file(), "current batch02 audit/manifest is missing")
    audit = load_json(CURRENT_AUDIT)
    manifest = load_json(CURRENT_MANIFEST)
    require(audit.get("candidate_only") is True, "current batch02 must remain a private candidate")
    require(manifest.get("candidate_only") is True, "current batch02 manifest candidate scope drift")
    require(
        audit.get("schema") == "nobu16.kr.pc-event-manual-compact-static007-batch02-audit.v1",
        "current batch02 audit schema drift",
    )
    require(
        manifest.get("schema") == "nobu16.kr.pc-event-manual-compact-static007-batch02-manifest.v1",
        "current batch02 manifest schema drift",
    )
    require(audit.get("output_event_profile") == EXPECTED_CURRENT_PROFILE, "current batch02 audit profile drift")
    require(manifest.get("output") == EXPECTED_CURRENT_PROFILE, "current batch02 manifest profile drift")
    require(manifest.get("resource") == MSGEV_RELATIVE.as_posix(), "current batch02 resource drift")
    require(
        tuple(manifest.get("changed_row_ids", ())) == EXPECTED_CURRENT_BATCH02_CHANGED_IDS,
        "current batch02 changed-row scope drift",
    )
    require(
        tuple(audit.get("actual_changed_row_ids", ())) == EXPECTED_CURRENT_BATCH02_CHANGED_IDS,
        "current batch02 audit changed-row scope drift",
    )
    predecessor = manifest.get("predecessor", {})
    require(predecessor.get("workstream") == BATCH01_ROOT.parent.name, "current batch02 predecessor drift")
    require(predecessor.get("profile") == EXPECTED_BATCH01_PROFILE, "current batch02 predecessor profile drift")
    require(predecessor.get("strict_on_disk") is True, "current batch02 must pin its strict predecessor")
    texts, source_profile = load_packed_table(CURRENT_EVENT, "current batch02 Korean successor", EXPECTED_CURRENT_PROFILE)
    actual_changed_ids = tuple(
        entry_id
        for entry_id, (current, predecessor_text) in enumerate(zip(texts, batch01_texts, strict=True))
        if current != predecessor_text
    )
    require(actual_changed_ids == EXPECTED_CURRENT_BATCH02_CHANGED_IDS, "current batch02 table diff against batch01 predecessor drift")
    require(
        len(normalize_linebreaks(texts[5777]).split("\n")) == 3,
        "current batch02 must preserve the static-007 three-line 5777 revision",
    )
    return texts, {
        "candidate_relative": relative(CURRENT_ROOT),
        "event_relative": relative(CURRENT_EVENT),
        "event_profile": source_profile,
        "audit": file_record(CURRENT_AUDIT),
        "manifest": file_record(CURRENT_MANIFEST),
        "predecessor_workstream": predecessor["workstream"],
        "predecessor_event_profile": predecessor["profile"],
        "changed_row_ids_against_batch01": list(actual_changed_ids),
        "read_only": True,
        "steam_game_resource_written": False,
    }


def load_legacy_static_preflight_table() -> tuple[Sequence[str], Mapping[str, Any]]:
    """Load the original-font-rollback Korean resource for a separate legacy screen."""
    texts, source_profile = load_packed_table(
        LEGACY_STATIC_PREFLIGHT_EVENT,
        "legacy original-font-rollback Korean static preflight",
        EXPECTED_LEGACY_STATIC_PREFLIGHT_PROFILE,
    )
    return texts, {
        "path": str(LEGACY_STATIC_PREFLIGHT_EVENT),
        "event_profile": source_profile,
        "read_only": True,
        "purpose": "non_authoritative_legacy_static_preflight_only",
        "runtime_token_reservations_applied": False,
        "strip_policy": "strip only validated ESC three-byte colour tags; retain existing line breaks and bracket text",
    }


def load_direct_contexts() -> tuple[Mapping[str, Sequence[str]], Mapping[str, Mapping[str, Any]]]:
    tables: dict[str, Sequence[str]] = {}
    evidence: dict[str, Mapping[str, Any]] = {}
    for language in ("jp", "en", "sc", "tc"):
        path = DIRECT_CONTEXT_PATHS[language]
        resolved = path.resolve(strict=True)
        require("switch" not in {part.casefold() for part in resolved.parts}, f"non-PC source forbidden: {resolved}")
        texts, source_profile = load_packed_table(path, f"direct PC {language.upper()} context", EXPECTED_DIRECT_PROFILES[language])
        tables[language] = texts
        evidence[language] = {
            "path": str(path),
            "profile": source_profile,
            "read_only": True,
        }
    return tables, evidence


def plain_display(value: str) -> str:
    """Strip only validated colour tags from a known static reservation display."""
    structure = colour_structure(value)
    require(structure["structurally_valid"], f"reservation display has invalid colour structure: {value!r}")
    display = strip_valid_esc_tags(value)
    require("\n" not in normalize_linebreaks(display), "reservation display unexpectedly has a line break")
    require(not BRACKET_TOKEN_RE.search(display), "reservation display unexpectedly contains a runtime token")
    require(not any(unicodedata.category(character) == "Cc" for character in display), "reservation display has a control")
    return display


def load_runtime_catalog(current_texts: Sequence[str]) -> tuple[Mapping[str, Mapping[str, Any]], Mapping[str, Any]]:
    require(SOURCE_RESERVATIONS.is_file(), f"runtime reservation catalog missing: {SOURCE_RESERVATIONS}")
    require(
        sha256(SOURCE_RESERVATIONS.read_bytes()) == EXPECTED_RESERVATIONS_SHA256,
        "runtime reservation catalog hash drift",
    )
    payload = load_json(SOURCE_RESERVATIONS)
    require(payload.get("schema") == "nobu16.kr.steam-jp-msgev-runtime-token-reservations.v1", "reservation schema drift")
    reservations = payload.get("reservations")
    require(isinstance(reservations, dict), "runtime reservations missing")
    catalog: dict[str, Mapping[str, Any]] = {}
    for token, detail in reservations.items():
        require(isinstance(token, str) and NUMERIC_RUNTIME_RE.fullmatch(token) is not None, f"bad catalog token: {token!r}")
        require(isinstance(detail, dict), f"bad catalog detail: {token}")
        source_name_id = int(detail["source_name_id"])
        require(0 <= source_name_id < len(current_texts), f"catalog source name ID out of range: {token}")
        display = plain_display(current_texts[source_name_id])
        measured = raw_metrics(display)
        documented_raw = int(detail["reserved_full_name_width_px"])
        require(
            measured["raw_g1n_width_px"] == documented_raw,
            f"current successor name width no longer matches catalog reservation: {token}",
        )
        catalog[token] = {
            "token": token,
            "source": "v2_full_name_reservation_catalog",
            "basis": payload["reservation_policy"]["method"],
            "display": display,
            "source_name_id": source_name_id,
            "reserved_raw_g1n_width_px": documented_raw,
            "reserved_effective_width_px": math.ceil(documented_raw * DRAW_FONT_PX / RAW_FULL_WIDTH_PX),
            "runtime_proven": False,
            "scene_limited": False,
            "catalog_source_name_utf16le_sha256": detail["source_name_utf16le_sha256"],
            "current_successor_name_utf16le_sha256": text_hash(current_texts[source_name_id]),
            "catalog_name_hash_matches_current_successor": detail["source_name_utf16le_sha256"]
            == text_hash(current_texts[source_name_id]),
        }
    return catalog, {
        "file": file_record(SOURCE_RESERVATIONS),
        "schema": payload["schema"],
        "reservation_policy": payload["reservation_policy"],
        "catalog_token_count": len(catalog),
    }


def qualification_for_candidate(
    candidate_root: Path,
    workstream_name: str,
    wave: int | None,
    audit: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> str | None:
    if wave is not None and 90 <= wave <= 97:
        return "wave_90_to_wave_97"
    source_policy = audit.get("source_policy", {})
    predecessor = manifest.get("predecessor", {})
    if candidate_root.resolve(strict=False) == STATIC007_3LINE_ROOT.resolve(strict=False):
        return "static007_3line_predecessor"
    if candidate_root.resolve(strict=False) == BATCH01_ROOT.resolve(strict=False):
        return "batch01_predecessor"
    if candidate_root.resolve(strict=False) == CURRENT_ROOT.resolve(strict=False):
        return "current_static007_batch02_successor"
    later_strict = (
        predecessor.get("workstream") == CURRENT_ROOT.parent.name
        and predecessor.get("profile") == EXPECTED_CURRENT_PROFILE
        and predecessor.get("strict_on_disk") is True
        and (
            "strict" in workstream_name.casefold()
            or bool(source_policy.get("strict_input_only"))
        )
    )
    if later_strict:
        return "later_strict_candidate"
    return None


def candidate_sort_key(record: Mapping[str, Any]) -> tuple[int, str]:
    return int(record["sort_order"]), str(record["workstream"])


def discover_candidate_protections(
    current_texts: Sequence[str],
) -> tuple[tuple[Mapping[str, Any], ...], Mapping[int, tuple[Mapping[str, Any], ...]], Mapping[tuple[int, str], Mapping[str, Any]]]:
    """Discover W90–W97, pinned strict chain states, and strict descendants."""
    candidate_records: list[Mapping[str, Any]] = []
    reservations_by_key: dict[tuple[int, str], Mapping[str, Any]] = {}
    reservation_provenance: dict[tuple[int, str], list[Mapping[str, Any]]] = defaultdict(list)

    for root in sorted((REPO / "tmp").glob("pc_event_*/candidate-final"), key=lambda path: path.parent.name.casefold()):
        match = WAVE_RE.search(root.parent.name)
        wave = int(match.group(1)) if match is not None else None
        audit_path = root / "audit.v1.json"
        manifest_path = root / "candidate_manifest.v1.json"
        event_path = root / MSGEV_RELATIVE
        if not (audit_path.is_file() and manifest_path.is_file() and event_path.is_file()):
            if (
                (wave is not None and wave >= 90)
                or root.resolve(strict=False) == STATIC007_3LINE_ROOT.resolve(strict=False)
                or root.resolve(strict=False) == BATCH01_ROOT.resolve(strict=False)
                or root.resolve(strict=False) == CURRENT_ROOT.resolve(strict=False)
            ):
                raise InventoryError(f"incomplete W90+/current candidate evidence: {relative(root)}")
            continue
        audit = load_json(audit_path)
        manifest = load_json(manifest_path)
        qualification = qualification_for_candidate(root, root.parent.name, wave, audit, manifest)
        if qualification is None:
            continue
        require(audit.get("candidate_only") is True and manifest.get("candidate_only") is True, f"candidate scope drift: {root}")
        require(manifest.get("resource") == MSGEV_RELATIVE.as_posix(), f"candidate resource drift: {root}")
        changed_from_manifest = manifest.get("changed_row_ids")
        changed_from_audit = audit.get("coverage", {}).get("changed_row_ids")
        require(isinstance(changed_from_manifest, list), f"candidate changed IDs missing: {root}")
        if changed_from_audit is not None:
            require(changed_from_manifest == changed_from_audit, f"candidate audit/manifest changed-ID drift: {root}")
        changed_ids = tuple(int(entry_id) for entry_id in changed_from_manifest)
        require(len(set(changed_ids)) == len(changed_ids), f"candidate duplicate changed ID: {root}")
        require(all(0 <= entry_id < EXPECTED_STRING_COUNT for entry_id in changed_ids), f"candidate changed ID out of range: {root}")
        sort_order = (
            wave
            if wave is not None
            else 98
            if root.resolve(strict=False) == STATIC007_3LINE_ROOT.resolve(strict=False)
            else 99
            if root.resolve(strict=False) == BATCH01_ROOT.resolve(strict=False)
            else 100
            if root.resolve(strict=False) == CURRENT_ROOT.resolve(strict=False)
            else 99_999
        )
        record = {
            "workstream": root.parent.name,
            "wave": wave,
            "sort_order": sort_order,
            "qualification": qualification,
            "candidate_relative": relative(root),
            "changed_row_count": len(changed_ids),
            "changed_row_ids": list(changed_ids),
            "output_profile": manifest.get("output"),
            "audit_relative": relative(audit_path),
            "manifest_relative": relative(manifest_path),
            "steam_game_resource_written": manifest.get("steam_game_resource_written", False),
            "release_published": manifest.get("release_published", False),
        }
        require(record["steam_game_resource_written"] is False, f"candidate claims a Steam write: {root}")
        require(record["release_published"] is False, f"candidate claims publication: {root}")
        candidate_records.append(record)

        # Scene-limited reservation evidence is valid only for a row whose
        # audited target still equals the current successor.  It is never
        # promoted to a global token rule.
        for audit_row in audit.get("rows", []):
            if not isinstance(audit_row, dict):
                continue
            entry_id = audit_row.get("entry_id")
            target = audit_row.get("target_ko")
            if not isinstance(entry_id, int) or not isinstance(target, str):
                continue
            if not (0 <= entry_id < len(current_texts)) or target != current_texts[entry_id]:
                continue
            for reservation in audit_row.get("runtime_reservations", []):
                if not isinstance(reservation, dict):
                    continue
                token = reservation.get("token")
                display = reservation.get("display")
                raw = reservation.get("reserved_raw_g1n_width_px")
                if not isinstance(token, str) or not isinstance(display, str) or not isinstance(raw, int):
                    raise InventoryError(f"malformed scene reservation: {root}:{entry_id}")
                measured = raw_metrics(plain_display(display))["raw_g1n_width_px"]
                require(measured == raw, f"scene reservation width drift: {root}:{entry_id}:{token}")
                key = (entry_id, token)
                candidate_detail = {
                    "token": token,
                    "source": "matching_scene_limited_candidate_audit",
                    "candidate_workstream": root.parent.name,
                    "candidate_wave": wave,
                    "display": plain_display(display),
                    "source_name_id": reservation.get("source_slot_id"),
                    "reserved_raw_g1n_width_px": raw,
                    "reserved_effective_width_px": math.ceil(raw * DRAW_FONT_PX / RAW_FULL_WIDTH_PX),
                    "runtime_proven": bool(reservation.get("runtime_proven", False)),
                    "scene_limited": bool(reservation.get("scene_limited", True)),
                    "basis": reservation.get("basis"),
                }
                previous = reservations_by_key.get(key)
                if previous is not None:
                    require(
                        (previous["display"], previous["reserved_raw_g1n_width_px"])
                        == (candidate_detail["display"], candidate_detail["reserved_raw_g1n_width_px"]),
                        f"conflicting candidate reservation evidence: {key}",
                    )
                reservations_by_key[key] = candidate_detail
                reservation_provenance[key].append(
                    {"workstream": root.parent.name, "wave": wave, "audit_relative": relative(audit_path)}
                )

    candidate_records.sort(key=candidate_sort_key)
    require(
        any(record["workstream"] == "pc_event_toyotomi_kanpaku_quality_wave97_v1" for record in candidate_records),
        "W97 candidate protection record missing",
    )
    require(
        any(record["workstream"] == STATIC007_3LINE_ROOT.parent.name for record in candidate_records),
        "static-007 5777 candidate protection record missing",
    )
    require(
        any(record["workstream"] == BATCH01_ROOT.parent.name for record in candidate_records),
        "batch01 candidate protection record missing",
    )
    require(
        any(record["workstream"] == CURRENT_ROOT.parent.name for record in candidate_records),
        "current static-007 batch02 candidate protection record missing",
    )
    protection_by_id: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for record in candidate_records:
        for entry_id in record["changed_row_ids"]:
            protection_by_id[int(entry_id)].append(
                {
                    "workstream": record["workstream"],
                    "wave": record["wave"],
                    "qualification": record["qualification"],
                    "candidate_relative": record["candidate_relative"],
                }
            )
    reservation_result: dict[tuple[int, str], Mapping[str, Any]] = {}
    for key, detail in reservations_by_key.items():
        reservation_result[key] = {**detail, "provenance": reservation_provenance[key]}
    return tuple(candidate_records), {entry_id: tuple(records) for entry_id, records in protection_by_id.items()}, reservation_result


def resolve_runtime_token(
    entry_id: int,
    token: str,
    catalog: Mapping[str, Mapping[str, Any]],
    scene_overrides: Mapping[tuple[int, str], Mapping[str, Any]],
) -> Mapping[str, Any] | None:
    override = scene_overrides.get((entry_id, token))
    if override is not None:
        return override
    return catalog.get(token)


def measure_line(
    entry_id: int,
    line_number: int,
    source: str,
    catalog: Mapping[str, Mapping[str, Any]],
    scene_overrides: Mapping[tuple[int, str], Mapping[str, Any]],
) -> Mapping[str, Any]:
    static_visible: list[str] = []
    resolved_visible: list[str] = []
    template: list[str] = []
    reservations: list[Mapping[str, Any]] = []
    unresolved: list[str] = []
    cursor = 0
    while cursor < len(source):
        if source[cursor] == "\x1b":
            token = source[cursor : cursor + 3]
            if ESC_RE.fullmatch(token) is not None:
                cursor += 3
                continue
            # Structural status is reported separately.  Keep a malformed ESC
            # out of the visible width rather than pretending it is a glyph.
            cursor += 1
            continue
        bracket = BRACKET_TOKEN_RE.match(source, cursor)
        if bracket is not None:
            token = bracket.group(0)
            template.append("{" + token + "}")
            reservation = resolve_runtime_token(entry_id, token, catalog, scene_overrides)
            if reservation is None:
                unresolved.append(token)
            else:
                resolved_visible.append(str(reservation["display"]))
                reservations.append(reservation)
            cursor = bracket.end()
            continue
        character = source[cursor]
        if unicodedata.category(character) != "Cc":
            static_visible.append(character)
            resolved_visible.append(character)
            template.append(character)
        cursor += 1

    static_text = "".join(static_visible)
    static = raw_metrics(static_text)
    result: dict[str, Any] = {
        "line_number": line_number,
        "source_line_with_tags_and_tokens": source,
        "display_template": "".join(template),
        "static_visible_string": static_text,
        "static_full_width_character_count": static["full_width_character_count"],
        "static_half_width_character_count": static["half_width_character_count"],
        "static_raw_g1n_width_px": static["raw_g1n_width_px"],
        "static_effective_width_px": static["effective_width_px"],
        "runtime_reservations": reservations,
        "unresolved_runtime_tokens": unresolved,
    }
    if unresolved:
        result.update(
            {
                "measurement_status": "unresolved_runtime_hold",
                "visible_string": None,
                "full_width_character_count": None,
                "half_width_character_count": None,
                "raw_g1n_width_px": None,
                "effective_width_px": None,
                "over_static_patch_007_raw_1440px": None,
                "over_static_patch_007_effective_912px": None,
                "static_patch_007_effective_912_pass": None,
            }
        )
        return result

    visible = "".join(resolved_visible)
    measured = raw_metrics(visible)
    result.update(
        {
            "measurement_status": (
                "scene_limited_reservation" if reservations and any(item["scene_limited"] for item in reservations)
                else "catalog_reservation" if reservations else "literal_static_text"
            ),
            "visible_string": visible,
            "full_width_character_count": measured["full_width_character_count"],
            "half_width_character_count": measured["half_width_character_count"],
            "raw_g1n_width_px": measured["raw_g1n_width_px"],
            "effective_width_px": measured["effective_width_px"],
            "over_static_patch_007_raw_1440px": measured["raw_g1n_width_px"] > STATIC_PATCH_007_RAW_EQUIVALENT_LIMIT_PX,
            "over_static_patch_007_effective_912px": measured["effective_width_px"] > STATIC_PATCH_007_EFFECTIVE_LIMIT_PX,
            "static_patch_007_effective_912_pass": measured["effective_width_px"] <= STATIC_PATCH_007_EFFECTIVE_LIMIT_PX,
        }
    )
    return result


def layout_summary(
    entry_id: int,
    current_ko: str,
    catalog: Mapping[str, Mapping[str, Any]],
    scene_overrides: Mapping[tuple[int, str], Mapping[str, Any]],
) -> Mapping[str, Any]:
    normalized = normalize_linebreaks(current_ko)
    lines = [
        measure_line(entry_id, number, line, catalog, scene_overrides)
        for number, line in enumerate(normalized.split("\n"), 1)
    ]
    structure = colour_structure(current_ko)
    has_unresolved = any(metric["measurement_status"] == "unresolved_runtime_hold" for metric in lines)
    patch007_results = [metric["static_patch_007_effective_912_pass"] for metric in lines]
    line_count_pass = len(lines) <= MAX_LINES
    patch007_pass = None if any(result is None for result in patch007_results) else all(patch007_results)
    if not structure["structurally_valid"]:
        status = "structural_colour_tag_hold"
    elif not line_count_pass:
        status = "manual_line_count_exceeds_4"
    elif has_unresolved:
        status = "unresolved_runtime_reservation_hold"
    elif patch007_pass is False:
        status = "static_patch_007_effective_912_exceeds"
    else:
        status = "human_semantic_retranslation_reflow_required"
    return {
        "manual_line_count": len(lines),
        "max_manual_lines": MAX_LINES,
        "manual_line_count_pass": line_count_pass,
        "all_static_patch_007_effective_912_pass": patch007_pass,
        "has_unresolved_runtime_token": has_unresolved,
        "status": status,
        "lines": lines,
    }


def legacy_static_preflight(historical_ko: str) -> Mapping[str, Any]:
    """Measure the separate original-font-rollback static screen without reservations.

    This intentionally retains existing line breaks and treats bracket text as
    literal characters.  It is a recovery-context comparison only; it never
    replaces the current static-patch-007 runtime-token-reserved assessment.
    """
    normalized = normalize_linebreaks(historical_ko)
    lines: list[Mapping[str, Any]] = []
    for line_number, source_line in enumerate(normalized.split("\n"), 1):
        visible = strip_valid_esc_tags(source_line)
        measured = raw_metrics(visible)
        lines.append(
            {
                "line_number": line_number,
                "source_line_with_esc_tags": source_line,
                "visible_string": visible,
                **measured,
                "over_raw_1440px": measured["raw_g1n_width_px"] > STATIC_PATCH_007_RAW_EQUIVALENT_LIMIT_PX,
            }
        )
    line_count_pass = len(lines) <= MAX_LINES
    raw_1440_pass = all(not line["over_raw_1440px"] for line in lines)
    oldfit = line_count_pass and raw_1440_pass
    return {
        "historical_ko": historical_ko,
        "historical_ko_utf16le_sha256": text_hash(historical_ko),
        "line_count": len(lines),
        "line_count_pass": line_count_pass,
        "all_raw_1440_pass": raw_1440_pass,
        "classification": "oldfit" if oldfit else "reflow",
        "runtime_token_reservations_applied": False,
        "lines": lines,
    }


def group_contiguous_ids(ids: Iterable[int]) -> tuple[tuple[int, ...], ...]:
    batches: list[tuple[int, ...]] = []
    active: list[int] = []
    for entry_id in sorted(ids):
        if active and entry_id != active[-1] + 1:
            batches.append(tuple(active))
            active = []
        active.append(entry_id)
    if active:
        batches.append(tuple(active))
    return tuple(batches)


def layout_attention_ids(row: Mapping[str, Any]) -> Mapping[str, bool]:
    layout = row["manual_layout"]
    return {
        "unresolved_runtime_hold": layout["has_unresolved_runtime_token"],
        "manual_line_count_attention": layout["manual_line_count_pass"] is False,
        "static_patch_007_effective_attention": layout["all_static_patch_007_effective_912_pass"] is False,
    }


def build_batches(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    rows_by_id = {int(row["entry_id"]): row for row in rows}
    groups = group_contiguous_ids(rows_by_id)
    batches: list[Mapping[str, Any]] = []
    for ordinal, ids in enumerate(groups, 1):
        protected_ids = [entry_id for entry_id in ids if rows_by_id[entry_id]["candidate_protection"]["do_not_overwrite"]]
        unresolved = [entry_id for entry_id in ids if layout_attention_ids(rows_by_id[entry_id])["unresolved_runtime_hold"]]
        line_attention = [
            entry_id for entry_id in ids if layout_attention_ids(rows_by_id[entry_id])["manual_line_count_attention"]
        ]
        patch007_attention = [
            entry_id for entry_id in ids if layout_attention_ids(rows_by_id[entry_id])["static_patch_007_effective_attention"]
        ]
        current_differs_from_historical_compact = [
            entry_id for entry_id in ids if rows_by_id[entry_id]["current_differs_from_historical_compact"]
        ]
        if protected_ids:
            priority_bucket = "P0_preserve_strict_candidate_rows"
            priority_score = -1
            planning_action = "do_not_overwrite; split locked IDs out before any human-authored successor candidate"
            candidate_eligible = False
        elif line_attention or patch007_attention:
            priority_bucket = "P1_runtime_or_line_structure_attention"
            priority_score = 400 + 20 * len(line_attention) + 10 * len(patch007_attention) + len(ids)
            planning_action = "human semantic retranslation/reflow with runtime-layout review"
            candidate_eligible = True
        elif unresolved:
            priority_bucket = "P2_runtime_reservation_evidence_attention"
            priority_score = 200 + 20 * len(unresolved) + len(ids)
            planning_action = "human semantic retranslation/reflow after obtaining row-local runtime-token evidence"
            candidate_eligible = True
        else:
            priority_bucket = "P3_standard_human_semantic_retranslation_reflow"
            priority_score = 100 + min(len(ids), 10) + (10 if current_differs_from_historical_compact else 0)
            planning_action = "human semantic non-shortened retranslation/reflow"
            candidate_eligible = True
        batches.append(
            {
                "batch_id": f"MC-{ordinal:04d}",
                "entry_id_start": ids[0],
                "entry_id_end": ids[-1],
                "entry_count": len(ids),
                "entry_ids": list(ids),
                "priority_bucket": priority_bucket,
                "priority_score": priority_score,
                "planning_action": planning_action,
                "candidate_eligible_only_after_human_review": candidate_eligible,
                "candidate_protected_ids": protected_ids,
                "unresolved_runtime_hold_ids": unresolved,
                "manual_line_count_attention_ids": line_attention,
                "static_patch_007_effective_attention_ids": patch007_attention,
                "current_differs_from_historical_compact_ids": current_differs_from_historical_compact,
            }
        )
    recommended = sorted(
        (batch for batch in batches if batch["candidate_eligible_only_after_human_review"]),
        key=lambda batch: (-int(batch["priority_score"]), int(batch["entry_id_start"])),
    )
    priority_plan = [
        {
            "priority_rank": rank,
            "batch_id": batch["batch_id"],
            "entry_id_start": batch["entry_id_start"],
            "entry_id_end": batch["entry_id_end"],
            "entry_count": batch["entry_count"],
            "priority_bucket": batch["priority_bucket"],
            "planning_action": batch["planning_action"],
            "candidate_protected_ids": batch["candidate_protected_ids"],
            "manual_line_count_attention_ids": batch["manual_line_count_attention_ids"],
            "static_patch_007_effective_attention_ids": batch["static_patch_007_effective_attention_ids"],
            "unresolved_runtime_hold_ids": batch["unresolved_runtime_hold_ids"],
        }
        for rank, batch in enumerate(recommended, 1)
    ]
    return {
        "schema": "nobu16.kr.pc-event-manual-compact-korean-layout-batches.v1",
        "contiguous_scene_batch_count": len(batches),
        "batch_size_distribution": {
            str(size): count for size, count in sorted(Counter(batch["entry_count"] for batch in batches).items())
        },
        "batches": batches,
        "prioritized_batch_plan": priority_plan,
        "earliest_recommended_batches": priority_plan[:12],
        "policy": {
            "every_row_requires_human_semantic_non_shortened_retranslation_reflow": True,
            "global_linebreak_strip_forbidden": True,
            "automatic_decompaction_forbidden": True,
            "strict_candidate_changed_rows_must_not_be_overwritten": True,
        },
    }


def build_row(
    source_entry: Mapping[str, Any],
    batch_id: str,
    current_texts: Sequence[str],
    w97_predecessor_texts: Sequence[str],
    legacy_static_preflight_texts: Sequence[str],
    direct_tables: Mapping[str, Sequence[str]],
    catalog: Mapping[str, Mapping[str, Any]],
    scene_overrides: Mapping[tuple[int, str], Mapping[str, Any]],
    protections: Mapping[int, tuple[Mapping[str, Any], ...]],
) -> Mapping[str, Any]:
    entry_id = int(source_entry["id"])
    current_ko = current_texts[entry_id]
    w97_predecessor_ko = w97_predecessor_texts[entry_id]
    require(current_ko != "", f"empty current Korean row in manual inventory: {entry_id}")
    require(w97_predecessor_ko != "", f"empty W97 predecessor Korean row in manual inventory: {entry_id}")
    direct = {language: direct_tables[language][entry_id] for language in ("jp", "en", "sc", "tc")}
    require(all(value != "" for value in direct.values()), f"empty direct-PC witness in manual inventory: {entry_id}")
    current_signature = text_signature(current_ko)
    direct_signatures = {language: text_signature(value) for language, value in direct.items()}
    candidate_changes = list(protections.get(entry_id, ()))
    current_differs_from_historical_compact = current_ko != source_entry["ko"]
    legacy_preflight = legacy_static_preflight(legacy_static_preflight_texts[entry_id])
    legacy_recovery_category = (
        f"current_{'diff' if current_differs_from_historical_compact else 'same'}+"
        f"{legacy_preflight['classification']}"
    )
    return {
        "entry_id": entry_id,
        "scene_batch_id": batch_id,
        "current_ko": current_ko,
        "current_ko_utf16le_sha256": text_hash(current_ko),
        "w97_historical_predecessor_ko": w97_predecessor_ko,
        "w97_historical_predecessor_ko_utf16le_sha256": text_hash(w97_predecessor_ko),
        "current_differs_from_w97_historical_predecessor": current_ko != w97_predecessor_ko,
        "source_manual_compact_ko": source_entry["ko"],
        "source_manual_compact_ko_utf16le_sha256": source_entry["target_utf16le_sha256"],
        "current_differs_from_historical_compact": current_differs_from_historical_compact,
        "current_matches_historical_compact": not current_differs_from_historical_compact,
        "source_manual_compact_layout": {
            "operation": source_entry["operation"],
            "newline_operations": source_entry["newline_operations"],
            "source_line_breaks": source_entry["source_line_breaks"],
            "source_target_line_widths_px": source_entry["target_line_widths_px"],
            "source_target_reserved_line_widths_px": source_entry["target_reserved_line_widths_px"],
            "source_preimage_utf16le_sha256": source_entry["preimage_utf16le_sha256"],
            "source_protected_signature": source_entry["protected_signature"],
        },
        "direct_pc": {
            language: {
                "text": direct[language],
                "utf16le_sha256": text_hash(direct[language]),
            }
            for language in ("jp", "en", "sc", "tc")
        },
        "tags_tokens": {
            "current_ko": current_signature,
            "direct_pc": direct_signatures,
            "current_matches_direct_pc": {
                language: cross_language_signature_match(current_signature, direct_signatures[language])
                for language in ("jp", "en", "sc", "tc")
            },
        },
        "manual_layout": layout_summary(entry_id, current_ko, catalog, scene_overrides),
        "legacy_static_preflight": {
            **legacy_preflight,
            "recovery_category": legacy_recovery_category,
            "non_authoritative": True,
        },
        "required_human_action": {
            "state": "needs_human_semantic_non_shortened_retranslation_reflow",
            "semantic_retranslation_required": True,
            "non_shortened_required": True,
            "manual_reflow_required": True,
            "global_linebreak_strip_forbidden": True,
            "automatic_decompaction_forbidden": True,
            "automatic_text_mutation_forbidden": True,
        },
        "candidate_protection": {
            "changed_by_protected_candidate_chain": bool(candidate_changes),
            "do_not_overwrite": bool(candidate_changes),
            "changed_by_candidates": candidate_changes,
            "safe_handling": (
                "preserve this row; only a separately reviewed successor candidate may touch it after explicit human approval"
                if candidate_changes
                else "no automatic edit; a future candidate still requires human semantic non-shortened retranslation/reflow"
            ),
        },
    }


def count_layout(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, int]:
    return {
        "unresolved_runtime_hold_rows": sum(row["manual_layout"]["has_unresolved_runtime_token"] for row in rows),
        "manual_line_count_attention_rows": sum(
            row["manual_layout"]["manual_line_count_pass"] is False for row in rows
        ),
        "static_patch_007_effective_attention_rows": sum(
            row["manual_layout"]["all_static_patch_007_effective_912_pass"] is False for row in rows
        ),
    }


def summarize_legacy_static_preflight(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    category_counts = Counter(str(row["legacy_static_preflight"]["recovery_category"]) for row in rows)
    reflow_ids = [
        int(row["entry_id"])
        for row in rows
        if row["legacy_static_preflight"]["classification"] == "reflow"
    ]
    require(
        dict(sorted(category_counts.items())) == dict(EXPECTED_LEGACY_STATIC_PREFLIGHT_RECOVERY_COUNTS),
        "legacy original-font-rollback recovery categories drift",
    )
    require(
        tuple(reflow_ids) == EXPECTED_LEGACY_STATIC_PREFLIGHT_REFLOW_IDS,
        "legacy original-font-rollback static reflow IDs drift",
    )
    return {
        "non_authoritative": True,
        "recovery_category_counts": dict(sorted(category_counts.items())),
        "static_reflow_row_count": len(reflow_ids),
        "static_reflow_ids": reflow_ids,
        "policy": "legacy static preflight only; current runtime-token-reserved static-patch-007 layout is authoritative",
    }


def build_bundle() -> tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any], str]:
    source_entries, source_info = load_source_entries()
    w97_predecessor_texts, w97_predecessor_info = load_w97_predecessor()
    static007_3line_texts, static007_3line_info = load_static007_3line_predecessor()
    batch01_texts, batch01_info = load_batch01_predecessor(static007_3line_texts)
    current_texts, current_info = load_current_successor(batch01_texts)
    legacy_static_preflight_texts, legacy_static_preflight_info = load_legacy_static_preflight_table()
    direct_tables, direct_info = load_direct_contexts()
    catalog, catalog_info = load_runtime_catalog(current_texts)
    candidates, protections, scene_overrides = discover_candidate_protections(current_texts)

    ids = tuple(sorted(source_entries))
    groups = group_contiguous_ids(ids)
    batch_id_by_entry = {
        entry_id: f"MC-{ordinal:04d}"
        for ordinal, group in enumerate(groups, 1)
        for entry_id in group
    }
    rows = tuple(
        build_row(
            source_entries[entry_id],
            batch_id_by_entry[entry_id],
            current_texts,
            w97_predecessor_texts,
            legacy_static_preflight_texts,
            direct_tables,
            catalog,
            scene_overrides,
            protections,
        )
        for entry_id in ids
    )
    batches = build_batches(rows)
    protected_rows = [row for row in rows if row["candidate_protection"]["do_not_overwrite"]]
    layout_counts = count_layout(rows)
    status_counts = Counter(row["manual_layout"]["status"] for row in rows)
    current_historical_difference_count = sum(row["current_differs_from_historical_compact"] for row in rows)
    require(
        current_historical_difference_count == EXPECTED_CURRENT_HISTORICAL_DIFFERENCE_COUNT,
        "current static-007 successor historical-compact difference count drift",
    )
    legacy_static_preflight_summary = summarize_legacy_static_preflight(rows)
    unresolved_tokens = Counter(
        token
        for row in rows
        for line in row["manual_layout"]["lines"]
        for token in line["unresolved_runtime_tokens"]
    )

    inventory = {
        "schema": "nobu16.kr.pc-event-manual-compact-korean-layout-inventory.v1",
        "read_only": True,
        "event_candidate_created": False,
        "resource": MSGEV_RELATIVE.as_posix(),
        "source_inventory": source_info,
        "current_successor": current_info,
        "batch01_predecessor": batch01_info,
        "static007_3line_predecessor": static007_3line_info,
        "w97_historical_predecessor": w97_predecessor_info,
        "legacy_static_preflight_source": legacy_static_preflight_info,
        "direct_pc_context": direct_info,
        "runtime_reservation_evidence": {
            **catalog_info,
            "matching_scene_limited_override_count": len(scene_overrides),
            "policy": "Use a matching scene-limited audit reservation only for that exact current-successor-matching row/token; otherwise use the v2 full-name catalog; unresolved nonnumeric brackets stay on hold.",
        },
        "layout_policy": {
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "max_lines": MAX_LINES,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "static_patch_007_runtime_effective_limit_px": STATIC_PATCH_007_EFFECTIVE_LIMIT_PX,
            "static_patch_007_raw_equivalent_limit_px": STATIC_PATCH_007_RAW_EQUIVALENT_LIMIT_PX,
            "dynamic_reservation_effective_width_formula": "ceil(reserved_raw_g1n_width_px * 30 / 48)",
        },
        "human_semantic_policy": {
            "every_row_requires_human_semantic_non_shortened_retranslation_reflow": True,
            "global_linebreak_strip_forbidden": True,
            "automatic_decompaction_forbidden": True,
            "direct_pc_jp_en_sc_tc_are_read_only_context_witnesses": True,
        },
        "candidate_protection_scope": {
            "candidate_count": len(candidates),
            "candidates": candidates,
            "manual_inventory_rows_already_changed": len(protected_rows),
            "manual_inventory_changed_ids": [row["entry_id"] for row in protected_rows],
            "policy": "Rows changed by W90–W97, the pinned Static 007 3-line predecessor, batch01, the current batch02 successor, or a completed strict descendant are locked against overwrite by this planning inventory.",
        },
        "counts": {
            "row_count": len(rows),
            "contiguous_scene_batch_count": batches["contiguous_scene_batch_count"],
            "current_differs_from_historical_compact_count": current_historical_difference_count,
            "candidate_protected_row_count": len(protected_rows),
            "layout_status_counts": dict(sorted(status_counts.items())),
            **layout_counts,
            "legacy_static_preflight": legacy_static_preflight_summary,
            "unresolved_runtime_token_occurrences": sum(unresolved_tokens.values()),
            "unresolved_runtime_tokens": dict(sorted(unresolved_tokens.items())),
        },
        "rows": rows,
        "steam_game_resource_written": False,
        "transaction_performed": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }
    batches_output = {
        **batches,
        "read_only": True,
        "source_inventory_relative": relative(SOURCE_LAYOUT),
        "current_successor_candidate_relative": relative(CURRENT_ROOT),
        "batch01_predecessor_candidate_relative": relative(BATCH01_ROOT),
        "static007_3line_predecessor_candidate_relative": relative(STATIC007_3LINE_ROOT),
        "w97_historical_predecessor_candidate_relative": relative(W97_ROOT),
        "row_count": len(rows),
        "steam_game_resource_written": False,
        "transaction_performed": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }
    validation = {
        "schema": "nobu16.kr.pc-event-manual-compact-korean-layout-inventory-validation.v1",
        "status": "PASS",
        "read_only": True,
        "row_count": len(rows),
        "id_range": [ids[0], ids[-1]],
        "contiguous_scene_batch_count": batches["contiguous_scene_batch_count"],
        "candidate_protected_row_count": len(protected_rows),
        "current_differs_from_historical_compact_count": current_historical_difference_count,
        **layout_counts,
        "legacy_static_preflight": legacy_static_preflight_summary,
        "outputs": {
            "inventory": relative(INVENTORY_PATH),
            "batches": relative(BATCHES_PATH),
            "report": relative(REPORT_PATH),
        },
        "steam_game_resource_written": False,
        "transaction_performed": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }
    report = render_report(inventory, batches_output, validation)
    return inventory, batches_output, validation, report


def render_report(inventory: Mapping[str, Any], batches: Mapping[str, Any], validation: Mapping[str, Any]) -> str:
    counts = inventory["counts"]
    first = batches["earliest_recommended_batches"]
    legacy = counts["legacy_static_preflight"]
    lines = [
        "# 수동 압축 한국어 이벤트 레이아웃 전수 인벤토리",
        "",
        "## 결론",
        "",
        f"`manual_compact_korean_layout` + 수동 개행 작업 대상은 **{counts['row_count']:,}행** "
        f"(ID {validation['id_range'][0]}–{validation['id_range'][1]})이며, 연속 ID 기준 장면 배치는 "
        f"**{counts['contiguous_scene_batch_count']:,}개**입니다.",
        "현재 한국어는 `pc_event_manual_compact_static007_batch02_v1`을 읽기 전용 기준으로 사용합니다. 이 기준은 5777의 검증된 Static 007 3줄 상태, 3210·3231–3234·3239의 batch01 복원, 3254·3260의 batch02 복원을 포함하며, W97은 역사적 엄격 전임으로 보존합니다. Steam 게임 파일·트랜잭션·Git·네트워크·릴리스에는 쓰지 않습니다.",
        "",
        "모든 행은 사람의 의미 검토를 거친 **축약 없는 재번역 및 수동 재개행** 대상입니다. 일괄 줄바꿈 삭제나 자동 decompact는 금지합니다.",
        "",
        "## 측정 원칙",
        "",
        f"- 원본 G1N 기준 전각 {RAW_FULL_WIDTH_PX}px / 반각 {RAW_HALF_WIDTH_PX}px를 기록하고, 유효 표시폭은 `ceil(raw_g1n_width_px * 30 / 48)`로 계산합니다.",
        f"- Static patch 007의 실제 런타임 판단은 유효폭 {STATIC_PATCH_007_EFFECTIVE_LIMIT_PX}px 이하(원본 G1N 동등값 {STATIC_PATCH_007_RAW_EQUIVALENT_LIMIT_PX}px)/최대 {MAX_LINES}줄입니다.",
        "- 동적 이름 토큰은 일치하는 장면 전용 후보 감사 근거가 있으면 그 행에만 적용하고, 그 외에는 v2 전체 이름 상한을 사용했습니다. `[bu]`류 비수치 토큰은 폭을 추정하지 않고 hold로 남깁니다.",
        "",
        "## 현재 결과",
        "",
        f"- W90–W97, Static 007 3줄 전임, batch01, 현재 batch02 또는 완료된 strict 후속 후보가 이미 바꾼 보호 행: **{counts['candidate_protected_row_count']}행** (덮어쓰기 금지)",
        f"- 런타임 토큰 폭 근거 hold 행: **{counts['unresolved_runtime_hold_rows']}행**",
        f"- Static patch 007 유효폭 912px 주의 행: **{counts['static_patch_007_effective_attention_rows']}행**",
        f"- v2 역사적 수동 압축 오버레이와 현재 batch02 기준 문구가 다른 행: **{counts['current_differs_from_historical_compact_count']}행**",
        f"- 별도 legacy static preflight(원본-font-rollback, 비권위적) reflow 행: **{legacy['static_reflow_row_count']}행**",
        "",
        "보호 행도 재검토 대상이지만, 이 인벤토리의 후속 작업이 기존 엄격 후보 변경을 덮어써서는 안 됩니다. 새 후보에서 다루려면 명시적인 사람 승인과 행 단위 차이 검사가 필요합니다.",
        "",
        "## 우선 추천 배치",
        "",
        "아래 순서는 기계 번역 순서가 아니라, 사람 검토를 위한 위험 우선 순위입니다. 각 배치의 모든 문장은 축약 없이 의미를 다시 대조하고, 태그·토큰·종결자·의미 단위를 보존해야 합니다.",
        "",
        "| 순위 | 배치 | ID 범위 | 분류 | 주의 |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for item in first:
        attention = []
        if item["manual_line_count_attention_ids"]:
            attention.append("line count " + ",".join(map(str, item["manual_line_count_attention_ids"])))
        if item["static_patch_007_effective_attention_ids"]:
            attention.append("Static007 width " + ",".join(map(str, item["static_patch_007_effective_attention_ids"])))
        if item["unresolved_runtime_hold_ids"]:
            attention.append("token hold " + ",".join(map(str, item["unresolved_runtime_hold_ids"])))
        note = "; ".join(attention) if attention else "사람 의미·수동 reflow"
        id_range = (
            str(item["entry_id_start"])
            if item["entry_id_start"] == item["entry_id_end"]
            else f"{item['entry_id_start']}–{item['entry_id_end']}"
        )
        lines.append(
            f"| {item['priority_rank']} | {item['batch_id']} | {id_range} | {item['priority_bucket']} | {note} |"
        )
    lines.extend(
        [
            "",
            "## 안전한 후보 체인",
            "",
            "1. 이 인벤토리에서 보호되지 않은 한 배치만 선택하고, JP/EN/SC/TC 직접 PC 문맥과 현재 batch02 한국어 기준을 사람이 대조합니다.",
            "2. 한국어 문장을 삭제·축약하지 말고 태그, 색상 span, 런타임 토큰, printf, 종결자를 그대로 보존한 새 문안과 수동 줄바꿈을 만듭니다.",
            "3. 새 빌더는 현재 batch02 후보(또는 바로 앞에서 검증된 사설 후속 후보)를 엄격한 읽기 전용 입력으로 pin하고, 자기 `tmp/<새_워크스트림>/candidate-final`에만 씁니다.",
            "4. 빌더 감사에는 행별 직접 PC 4언어 문맥, raw/effective 폭, 동적 토큰 예약, 정확한 diff ID, 전임/출력 프로필을 기록합니다.",
            "5. 다음 후보는 직전 검증 후보만 전임으로 삼고, 이 인벤토리의 보호 ID와 기존 변경 ID의 교집합이 비어 있음을 검사합니다. Steam 적용·트랜잭션·릴리스는 명시 승인 전까지 하지 않습니다.",
            "",
            "세부 행별 원문, 직접 PC 4언어 문맥, 태그/토큰, 줄별 폭, 보호 근거는 `public/msgev_manual_compact_korean_layout_inventory.v1.json`에 있습니다. 연속 장면 배치와 전체 우선순위는 `public/msgev_manual_compact_korean_layout_batches.v1.json`에 있습니다.",
            "",
        ]
    )
    return "\n".join(lines)


def require_output_path(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = WORKSTREAM.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise InventoryError(f"output escapes this workstream: {resolved}") from exc
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


def write_outputs(bundle: tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any], str]) -> Mapping[str, str]:
    inventory, batches, validation, report = bundle
    write_atomic(INVENTORY_PATH, canonical_json(inventory))
    write_atomic(BATCHES_PATH, canonical_json(batches))
    write_atomic(VALIDATION_PATH, canonical_json(validation))
    write_atomic(REPORT_PATH, report.encode("utf-8"))
    return {
        "inventory": relative(INVENTORY_PATH),
        "batches": relative(BATCHES_PATH),
        "validation": relative(VALIDATION_PATH),
        "report": relative(REPORT_PATH),
    }


def verify_outputs(bundle: tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any], str]) -> Mapping[str, Any]:
    inventory, batches, validation, report = bundle
    expected = {
        INVENTORY_PATH: canonical_json(inventory),
        BATCHES_PATH: canonical_json(batches),
        VALIDATION_PATH: canonical_json(validation),
        REPORT_PATH: report.encode("utf-8"),
    }
    for path, payload in expected.items():
        require(path.is_file(), f"output missing: {path}")
        require(path.read_bytes() == payload, f"output differs from deterministic read-only build: {path}")
    return {
        "status": "PASS",
        "row_count": validation["row_count"],
        "contiguous_scene_batch_count": validation["contiguous_scene_batch_count"],
        "candidate_protected_row_count": validation["candidate_protected_row_count"],
        "outputs": {"inventory": relative(INVENTORY_PATH), "batches": relative(BATCHES_PATH), "report": relative(REPORT_PATH)},
        "steam_game_resource_written": False,
        "transaction_performed": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (SCRIPT, WORKSTREAM / "test_pc_event_manual_compact_korean_layout_inventory_v1.py"):
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
    _inventory, _batches, validation, _report = bundle
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (InventoryError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
