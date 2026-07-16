#!/usr/bin/env python3
"""Repair the ten remaining Latin/pinyin tactic-reading strings for issue #47.

The input is not a live game file.  It is reconstructed in memory from the
pristine Steam 1.1.7 Japanese resource, wave08, the surname hotfix, and the
clan-label normalization.  The tracked overlay and trace intentionally carry
only IDs, Korean replacements, and UTF-16LE hashes; no commercial Japanese
source text or complete binary is tracked here.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def import_file(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CLAN = import_file(
    "steam_jp_tactics_reading_hotfix_clan",
    REPO
    / "workstreams"
    / "steam_jp_clan_label_normalization_v1"
    / "build_steam_jp_clan_label_normalization_v1.py",
)
COMMON = CLAN.COMMON


SCHEMA = "nobu16.kr.steam-jp-tactics-reading-hotfix-overlay.v1"
TRACE_SCHEMA = "nobu16.kr.steam-jp-tactics-reading-hotfix-jp-trace.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-tactics-reading-hotfix-validation.v1"
PRIVATE_MANIFEST_SCHEMA = "nobu16.kr.steam-jp-tactics-reading-hotfix-private-candidate.v1"
RESOURCE = "MSG_PK/JP/msgdata.bin"
NAME = "msgdata.bin"
ISSUE_NUMBER = 47

OVERLAY_PATH = HERE / "public" / "msgdata_ko_steam_jp_tactics_reading_hotfix_10.v1.json"
TRACE_PATH = HERE / "evidence" / "jp_tactics_reading_hash_anchors.v1.json"
VALIDATION_PATH = HERE / "validation.v1.json"
DEFAULT_STOCK_ROOT = CLAN.DEFAULT_STOCK_ROOT
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_tactics_reading_hotfix_v1_candidate"

CLAN_NORMALIZED_BASELINE_PIN = {
    "size": 497_505,
    "packed_sha256": "E783C492860BDC6229A3A05343635FEB05435D3751BBB2670F691F270DA484B6",
    "raw_size": 495_536,
    "raw_sha256": "7276B55F4E5C95728DA9DFA3372F037FE256587F0761E87BA6C87F75DA8BE597",
    "string_count": 29_218,
}

OUTPUT_CANDIDATE_PIN = {
    "size": 497_384,
    "packed_sha256": "4E0B1009789D6EF3935DA359932D73685447890784796BE3702D50C8D64E4387",
    "raw_size": 495_416,
    "raw_sha256": "B5704A99DEDD87A51409DBFA0772695B3FD3A391B12CD0BCAD9727B1631DBE78",
    "string_count": 29_218,
}

TACTICS_READING_START_ID = 15_485
TACTICS_READING_END_ID = 15_550
EMPTY_READING_IDS = (15_531, 15_532, 15_533, 15_534)
TACTICS_READING_SLOT_COUNT = 62
TACTICS_READING_SLOT_IDS_SHA256 = "C0B82A98607EDAB6EC09CC976B801AB29BC8B323EB3C07689616A2C20A4BB913"

TARGET_READINGS = {
    15_520: "기노사이하이",
    15_521: "케이스노사이",
    15_522: "햐쿠세쓰후토",
    15_524: "쿠로다부시",
    15_525: "무소야리",
    15_526: "유시노코코로자시",
    15_527: "켓시노코로에",
    15_528: "즈이헨류",
    15_529: "텐노토키",
    15_530: "다케다노아카조나에",
}
TARGET_IDS = tuple(TARGET_READINGS)
TARGET_IDS_SHA256 = "E67A422ADE9ECB46246D800F746D66D1FAD853713A51E49722FE4F5EE69626FE"

# These are trace anchors for the pristine Steam JP strings, not JP text.
JP_READING_HASH_ANCHORS = {
    15_520: "0CCB6630DD1B56538996E2498FBE4FE9219EA355C0F32B12A4F7E3313BDF987F",
    15_521: "1D75BED16BD12D9C4E66F1E87704B5120B1B8E032C6CDAB79BA9312B1BFA8EAD",
    15_522: "0BCDE9EC0AC19FAFDF1CDBC3A2478B7A79F76DCB057FF7FFA1042932D2FAF707",
    15_524: "9E47406634144681BCF3C832B56BA1C2D293FA6D0A335A140060C5F8BE00DD32",
    15_525: "6DC84160BB227DFA631684597E76F78E1FA8D2A2653EDBCA981A33B5CF114DE7",
    15_526: "09AC13BC86F629435FD16F9AF29A5D9F78ABF986B702F55C118EF1041851F365",
    15_527: "311FA25BC0ECF5DB5FA50FBB08B9AA9C83D65109235C0269AE5EFF6680F30C78",
    15_528: "23997333FEAD1A9C3284AE888F9C1385614A8F7D5DB258A8328347CE1C209718",
    15_529: "8ADBE6343F6074BA4A698EA8BFC828B957C9331CAB7EB594F93CE7E929EA371C",
    15_530: "23102D1DC5654B742D6CEEB2A9FD9640ABBB28854DADEFC0AB339AB8392CE358",
}

# These fail closed against the exact post-clan Korean baseline without
# exposing its pinyin/romanized text in the tracked workstream.
BASELINE_KO_HASH_ANCHORS = {
    15_520: "B376E02A07F4F7B7CB33A876EFCEB17F7B11FCF7635F1BBFDF5CFDDD559234A3",
    15_521: "252044240BECB878C23B9A3ABCA015E15F832BEC5407A041E3177C8965B078BA",
    15_522: "BBD9E10E59D6F67EA73598236B823F8FB30B3FB08C297ABB09A229652C2EC09C",
    15_524: "6C9E98AAC4128D2E693B1864D446A3D67271F3A1A1E5C7A22D28210B33CC9BDC",
    15_525: "19578B9A2C71BCD34197EC4A8DD3B5009AD5CC1CF478BFD154EF7057E92283C4",
    15_526: "AE5FE8B7F51B587F9BC24E1FE4441645F88D24445A792A9BCD62F2A8EC2CEEEF",
    15_527: "324E0DFAF5BDC73EE751CA287EFC3740D969D8A0BC1D3ED5DF7E7137750A408F",
    15_528: "967F80815A0503ABE2084D12EC03CB140F91C75DF6263DD1B7D25363391D0C4D",
    15_529: "69B0E76D9C4F393D33C117077C3597EA9222E4B2E1E5A1F002D6DE754E0C1F83",
    15_530: "5FB910498751AEE3D0627C9809103DFC88F023E10FC8FE9E869FDB895065BEA6",
}
KOREAN_OUTPUT_HASHES = {
    15_520: "E1DC518C12CA8494FB493A6D5EED4F793A839EB5A6498BF576EC0403E2F1AD1B",
    15_521: "EA38D30B678AEEC6DD3130861375E121CFDF3CC31E1911BFACBF14B132EFBF5A",
    15_522: "BC05D9A4E4548A2F52CB869786AA2AADF55329C77418F118BDB110675ABA62DA",
    15_524: "3101286E6CEC0ACD2C1C7C0A18F4E51ACF46E52581CFDF97B431925FD45BFE4A",
    15_525: "8296D5710CEA816D7623712D6A552F42D795D8A9AC5249ADF6F905B9CFD1A940",
    15_526: "F963ED648E9EBD796BBDB5BD46C425EEE300C0A4B7B6A6FD83561B647F2E9E45",
    15_527: "C53383E20AF900625239B40B80E34FAD8D0E3740C6571E207CA1A131DBF11B1D",
    15_528: "F591021D394360352140794C4B931F505342636B4FBE61EA2B04A6BA5C91682C",
    15_529: "8E5D8EA570138278DD1E7D0A7A79A3EDFBDC8BB207A9CFE5FCE45804F947198A",
    15_530: "7A85C63996BEF66AABBE08ABBFE0E2F64B42C7CEA11781A9FD30A5EAAD061483",
}
LATIN_RE = re.compile(r"[A-Za-z]")


class TacticsReadingHotfixError(ValueError):
    """A source, baseline, overlay, or structure contract differed."""


@dataclass(frozen=True)
class BaselineContext:
    stock: Any
    packed: bytes
    raw: bytes
    table: Any
    clan_metrics: dict[str, Any]


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def packed_spec(packed: bytes) -> dict[str, Any]:
    _header, raw = COMMON.decompress_wrapper(packed)
    table = COMMON.parse_message_table(raw)
    return {
        "size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "string_count": table.string_count,
    }


def require_exact(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise TacticsReadingHotfixError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def active_reading_ids(texts: tuple[str, ...] | list[str]) -> tuple[int, ...]:
    if len(texts) != CLAN_NORMALIZED_BASELINE_PIN["string_count"]:
        raise TacticsReadingHotfixError("msgdata text domain differs")
    expected_empty = tuple(
        entry_id
        for entry_id in range(TACTICS_READING_START_ID, TACTICS_READING_END_ID + 1)
        if not texts[entry_id]
    )
    if expected_empty != EMPTY_READING_IDS:
        raise TacticsReadingHotfixError("tactics reading empty-slot domain differs")
    active = tuple(
        entry_id
        for entry_id in range(TACTICS_READING_START_ID, TACTICS_READING_END_ID + 1)
        if entry_id not in EMPTY_READING_IDS
    )
    if len(active) != TACTICS_READING_SLOT_COUNT:
        raise TacticsReadingHotfixError("tactics reading slot count differs")
    if COMMON.canonical_hash(list(active)) != TACTICS_READING_SLOT_IDS_SHA256:
        raise TacticsReadingHotfixError("tactics reading slot ID hash differs")
    return active


def build_clan_normalized_baseline(stock_root: Path) -> BaselineContext:
    """Rebuild and exact-pin the current post-wave08/surname/clan baseline."""
    stock = COMMON.load_pinned(
        stock_root / Path(RESOURCE),
        COMMON.STEAM_PINS[NAME],
        "Steam 1.1.7 pristine JP msgdata",
    )
    baseline, clan_metrics = CLAN.build_blob(stock_root)
    require_exact(
        packed_spec(baseline),
        CLAN_NORMALIZED_BASELINE_PIN,
        "post-wave08+surname+clan msgdata baseline pin",
    )
    require_exact(
        clan_metrics.get("candidate"),
        CLAN_NORMALIZED_BASELINE_PIN,
        "clan normalizer metadata baseline pin",
    )
    _header, raw = COMMON.decompress_wrapper(baseline)
    table = COMMON.parse_message_table(raw)
    if table.string_count != stock.table.string_count:
        raise TacticsReadingHotfixError("stock and baseline text-domain counts differ")
    return BaselineContext(stock, baseline, raw, table, clan_metrics)


def validate_anchor_domain(context: BaselineContext) -> tuple[int, ...]:
    active = active_reading_ids(context.table.texts)
    if tuple(TARGET_READINGS) != TARGET_IDS or tuple(sorted(TARGET_IDS)) != TARGET_IDS:
        raise TacticsReadingHotfixError("target ID order differs")
    if COMMON.canonical_hash(list(TARGET_IDS)) != TARGET_IDS_SHA256:
        raise TacticsReadingHotfixError("target ID hash differs")
    if not set(TARGET_IDS).issubset(active):
        raise TacticsReadingHotfixError("target enters an inactive tactic-reading slot")
    if set(JP_READING_HASH_ANCHORS) != set(TARGET_IDS):
        raise TacticsReadingHotfixError("JP trace anchor domain differs")
    if set(BASELINE_KO_HASH_ANCHORS) != set(TARGET_IDS):
        raise TacticsReadingHotfixError("baseline Korean anchor domain differs")
    if set(KOREAN_OUTPUT_HASHES) != set(TARGET_IDS):
        raise TacticsReadingHotfixError("Korean output anchor domain differs")
    for entry_id in TARGET_IDS:
        if COMMON.text_hash(context.stock.table.texts[entry_id]) != JP_READING_HASH_ANCHORS[entry_id]:
            raise TacticsReadingHotfixError(f"pristine JP trace hash differs at {entry_id}")
        if COMMON.text_hash(context.table.texts[entry_id]) != BASELINE_KO_HASH_ANCHORS[entry_id]:
            raise TacticsReadingHotfixError(f"post-clan baseline Korean hash differs at {entry_id}")
        if COMMON.text_hash(TARGET_READINGS[entry_id]) != KOREAN_OUTPUT_HASHES[entry_id]:
            raise TacticsReadingHotfixError(f"Korean output hash differs at {entry_id}")
    baseline_latin_ids = tuple(
        entry_id for entry_id in active if LATIN_RE.search(context.table.texts[entry_id])
    )
    if baseline_latin_ids != TARGET_IDS:
        raise TacticsReadingHotfixError("pinyin/Latin tactic-reading slot domain differs")
    return active


def expected_trace(context: BaselineContext) -> dict[str, Any]:
    active = validate_anchor_domain(context)
    return {
        "schema": TRACE_SCHEMA,
        "issue": ISSUE_NUMBER,
        "resource": RESOURCE,
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "baseline": {
            "workstream": "steam_jp_clan_label_normalization_v1",
            "candidate": CLAN_NORMALIZED_BASELINE_PIN,
            "source": "deterministic_wave08_plus_surname_plus_clan_normalization",
        },
        "tactics_reading_domain": {
            "id_range": [TACTICS_READING_START_ID, TACTICS_READING_END_ID],
            "active_slot_count": len(active),
            "active_slot_ids_sha256": TACTICS_READING_SLOT_IDS_SHA256,
            "empty_ids": list(EMPTY_READING_IDS),
            "pinyin_latin_slot_ids": list(TARGET_IDS),
        },
        "entries": [
            {
                "id": entry_id,
                "stock_jp_utf16le_sha256": JP_READING_HASH_ANCHORS[entry_id],
                "baseline_ko_utf16le_sha256": BASELINE_KO_HASH_ANCHORS[entry_id],
                "ko_utf16le_sha256": KOREAN_OUTPUT_HASHES[entry_id],
            }
            for entry_id in TARGET_IDS
        ],
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
    }


def expected_overlay(context: BaselineContext) -> dict[str, Any]:
    validate_anchor_domain(context)
    return {
        "schema": SCHEMA,
        "overlay_id": "msgdata_ko_steam_jp_tactics_reading_hotfix_10.v1",
        "issue": ISSUE_NUMBER,
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "baseline": {
            "workstream": "steam_jp_clan_label_normalization_v1",
            "candidate": CLAN_NORMALIZED_BASELINE_PIN,
            "source": "deterministic_wave08_plus_surname_plus_clan_normalization",
        },
        "tactics_reading_domain": {
            "id_range": [TACTICS_READING_START_ID, TACTICS_READING_END_ID],
            "active_slot_count": TACTICS_READING_SLOT_COUNT,
            "active_slot_ids_sha256": TACTICS_READING_SLOT_IDS_SHA256,
            "pinyin_latin_slot_ids": list(TARGET_IDS),
        },
        "provenance": {
            "jp_hash_trace_fail_closed": True,
            "baseline_ko_hashes_fail_closed": True,
            "current_jp_source_hashes_fail_closed": True,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
        },
        "entry_count": len(TARGET_IDS),
        "entries": [
            {
                "id": entry_id,
                "stock_jp_utf16le_sha256": JP_READING_HASH_ANCHORS[entry_id],
                "baseline_ko_utf16le_sha256": BASELINE_KO_HASH_ANCHORS[entry_id],
                "ko": TARGET_READINGS[entry_id],
                "ko_utf16le_sha256": KOREAN_OUTPUT_HASHES[entry_id],
            }
            for entry_id in TARGET_IDS
        ],
    }


def artifact_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {
        "path": path.relative_to(REPO).as_posix(),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def load_trace(context: BaselineContext) -> tuple[dict[str, Any], bytes]:
    value, blob = COMMON.read_json(TRACE_PATH)
    expected = expected_trace(context)
    if value != expected or blob != COMMON.pretty_bytes(expected):
        raise TacticsReadingHotfixError("tracked JP reading trace differs from deterministic model")
    return value, blob


def load_overlay(context: BaselineContext) -> tuple[dict[str, Any], bytes]:
    value, blob = COMMON.read_json(OVERLAY_PATH)
    expected = expected_overlay(context)
    if value != expected or blob != COMMON.pretty_bytes(expected):
        raise TacticsReadingHotfixError("tracked tactics-reading overlay differs from deterministic model")
    return value, blob


def build_blob(stock_root: Path) -> tuple[bytes, dict[str, Any]]:
    """Return the source-free ten-entry post-clan candidate and diagnostics."""
    context = build_clan_normalized_baseline(stock_root)
    active = validate_anchor_domain(context)
    trace, trace_blob = load_trace(context)
    overlay, overlay_blob = load_overlay(context)
    if trace.get("entries") != [
        {
            "id": entry_id,
            "stock_jp_utf16le_sha256": JP_READING_HASH_ANCHORS[entry_id],
            "baseline_ko_utf16le_sha256": BASELINE_KO_HASH_ANCHORS[entry_id],
            "ko_utf16le_sha256": KOREAN_OUTPUT_HASHES[entry_id],
        }
        for entry_id in TARGET_IDS
    ]:
        raise TacticsReadingHotfixError("JP reading trace entry domain differs")
    entries = overlay.get("entries")
    if overlay.get("entry_count") != len(TARGET_IDS) or not isinstance(entries, list):
        raise TacticsReadingHotfixError("overlay entry count differs")
    if [entry.get("id") if isinstance(entry, dict) else None for entry in entries] != list(TARGET_IDS):
        raise TacticsReadingHotfixError("overlay target ID order differs")

    texts = list(context.table.texts)
    changed: set[int] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise TacticsReadingHotfixError("overlay entry is not an object")
        entry_id = entry.get("id")
        if type(entry_id) is not int or entry_id not in TARGET_IDS:
            raise TacticsReadingHotfixError("overlay target ID differs")
        if COMMON.text_hash(context.stock.table.texts[entry_id]) != entry.get("stock_jp_utf16le_sha256"):
            raise TacticsReadingHotfixError(f"current JP source hash differs at {entry_id}")
        if COMMON.text_hash(texts[entry_id]) != entry.get("baseline_ko_utf16le_sha256"):
            raise TacticsReadingHotfixError(f"baseline Korean hash differs at {entry_id}")
        replacement = entry.get("ko")
        if not isinstance(replacement, str) or "\0" in replacement:
            raise TacticsReadingHotfixError(f"Korean replacement differs at {entry_id}")
        if replacement != TARGET_READINGS[entry_id]:
            raise TacticsReadingHotfixError(f"Korean replacement text differs at {entry_id}")
        if COMMON.text_hash(replacement) != entry.get("ko_utf16le_sha256"):
            raise TacticsReadingHotfixError(f"Korean replacement hash differs at {entry_id}")
        if LATIN_RE.search(replacement):
            raise TacticsReadingHotfixError(f"Latin alphabet remains in target reading {entry_id}")
        texts[entry_id] = replacement
        changed.add(entry_id)

    if changed != set(TARGET_IDS):
        raise TacticsReadingHotfixError("tactics-reading delta domain differs")
    if any(LATIN_RE.search(texts[entry_id]) for entry_id in active):
        raise TacticsReadingHotfixError("Latin alphabet remains in active tactic-reading slots")

    rebuilt_raw = COMMON.rebuild_message_table(context.table, texts)
    reparsed = COMMON.parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise TacticsReadingHotfixError("rebuilt tactics-reading table differs")
    if not COMMON._opaque_structure_preserved(context.table, reparsed, rebuilt_raw):
        raise TacticsReadingHotfixError("candidate opaque table metadata differs")
    for entry_id, baseline_text in enumerate(context.table.texts):
        if entry_id not in changed and reparsed.texts[entry_id] != baseline_text:
            raise TacticsReadingHotfixError(f"non-target text changed at {entry_id}")

    candidate = COMMON.recompress_wrapper(rebuilt_raw, context.packed)
    _header, roundtrip = COMMON.decompress_wrapper(candidate)
    if roundtrip != rebuilt_raw or candidate[:8] != context.packed[:8]:
        raise TacticsReadingHotfixError("candidate wrapper round-trip or prefix differs")
    candidate_spec = packed_spec(candidate)
    require_exact(candidate_spec, OUTPUT_CANDIDATE_PIN, "tactics-reading diagnostic candidate pin")
    return candidate, {
        "schema": PRIVATE_MANIFEST_SCHEMA,
        "resource": RESOURCE,
        "issue": ISSUE_NUMBER,
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "post_clan_baseline": CLAN_NORMALIZED_BASELINE_PIN,
        "candidate": candidate_spec,
        "trace": {"size": len(trace_blob), "sha256": sha256(trace_blob)},
        "overlay": {"size": len(overlay_blob), "sha256": sha256(overlay_blob)},
        "tactics_reading_delta_count": len(changed),
        "target_ids_sha256": TARGET_IDS_SHA256,
        "active_tactics_reading_slot_count": len(active),
        "active_tactics_reading_slot_ids_sha256": TACTICS_READING_SLOT_IDS_SHA256,
        "pinyin_latin_slot_ids_eliminated": list(TARGET_IDS),
        "all_active_tactics_reading_slots_no_latin": True,
        "id_domain_preserved": True,
        "string_count_preserved": True,
        "opaque_non_string_metadata_preserved": True,
        "non_target_texts_preserved": True,
        "wrapper_prefix_preserved": True,
        "installed_game_files_modified": False,
        "sc_binary_used": False,
    }


def validation_model(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "issue": ISSUE_NUMBER,
        "resource": RESOURCE,
        "target": {"base_language": "JP", "steam_version": "1.1.7"},
        "tactics_reading_hotfix": {
            "entry_count": len(TARGET_IDS),
            "target_ids_sha256": TARGET_IDS_SHA256,
            "target_ids": list(TARGET_IDS),
            "active_reading_id_range": [TACTICS_READING_START_ID, TACTICS_READING_END_ID],
            "active_reading_slot_count": TACTICS_READING_SLOT_COUNT,
            "active_reading_slot_ids_sha256": TACTICS_READING_SLOT_IDS_SHA256,
            "empty_ids": list(EMPTY_READING_IDS),
        },
        "expected": {
            "stock_jp": metrics["stock_jp"],
            "post_clan_baseline": metrics["post_clan_baseline"],
            "candidate": metrics["candidate"],
            "trace": metrics["trace"],
            "overlay": metrics["overlay"],
        },
        "proofs": {
            "deterministic_ab_equal": True,
            "stock_jp_hash_pinned": True,
            "post_clan_baseline_hash_pinned": True,
            "jp_reading_trace_hashes_fail_closed": True,
            "baseline_ko_hashes_fail_closed": True,
            "all_62_active_tactics_reading_slots_have_no_latin": metrics[
                "all_active_tactics_reading_slots_no_latin"
            ],
            "pinyin_slots_eliminated": metrics["pinyin_latin_slot_ids_eliminated"],
            "target_id_domain_exact": True,
            "non_target_texts_preserved": metrics["non_target_texts_preserved"],
            "string_count_preserved": metrics["string_count_preserved"],
            "opaque_non_string_metadata_preserved": metrics[
                "opaque_non_string_metadata_preserved"
            ],
            "wrapper_prefix_preserved": metrics["wrapper_prefix_preserved"],
        },
        "safety": {
            "complete_candidate_binary_tracked": False,
            "installed_game_files_modified": False,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
        },
    }


def generate(stock_root: Path) -> dict[str, Any]:
    context = build_clan_normalized_baseline(stock_root)
    COMMON.atomic_write(TRACE_PATH, COMMON.pretty_bytes(expected_trace(context)))
    COMMON.atomic_write(OVERLAY_PATH, COMMON.pretty_bytes(expected_overlay(context)))
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise TacticsReadingHotfixError("deterministic A/B tactics-reading build differs")
    COMMON.atomic_write(VALIDATION_PATH, COMMON.pretty_bytes(validation_model(first_metrics)))
    return {"status": "GENERATED", **first_metrics, "deterministic_ab_equal": True}


def verify(stock_root: Path) -> dict[str, Any]:
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise TacticsReadingHotfixError("deterministic A/B tactics-reading build differs")
    validation, blob = COMMON.read_json(VALIDATION_PATH)
    expected = validation_model(first_metrics)
    if validation != expected or blob != COMMON.pretty_bytes(expected):
        raise TacticsReadingHotfixError("tracked tactics-reading validation differs")
    return {"status": "PASS", **first_metrics, "deterministic_ab_equal": True}


def safe_output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = (REPO / "tmp").resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents or resolved.exists():
        raise TacticsReadingHotfixError(f"unsafe or existing output root: {resolved}")
    return resolved


def build(stock_root: Path, output_root: Path) -> Path:
    candidate, metrics = build_blob(stock_root)
    destination = safe_output_root(output_root)
    try:
        target = destination / Path(RESOURCE)
        target.parent.mkdir(parents=True, exist_ok=False)
        target.write_bytes(candidate)
        (destination / "private_manifest.json").write_bytes(COMMON.pretty_bytes(metrics))
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("generate", "verify", "build"):
        child = commands.add_parser(command)
        child.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
        if command == "build":
            child.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    if args.command == "generate":
        print(json.dumps(generate(args.stock_root), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "verify":
        print(json.dumps(verify(args.stock_root), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    print(build(args.stock_root, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
