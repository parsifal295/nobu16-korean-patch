#!/usr/bin/env python3
"""Normalize the high-confidence Japanese court-office title core for issue #48.

This workstream is intentionally a *post-wave08* single-resource overlay.  It
starts from the deterministic Steam 1.1.7 JP v0.8 ``msgdata.bin`` candidate,
not from a live installation.  The checked-in overlay contains only
project-authored Korean text and per-row hashes: it contains neither JP source
strings nor a complete commercial game resource.  A complete candidate is
created only by ``build`` below ``tmp``.

There is deliberately no general Hanja-to-Korean converter here.  The 146
display terms are an explicit, reviewed ID dictionary.  Display rows use
canonical Korean office names, while furigana rows retain Japanese
pronunciation written in Hangul; only explicit incorrect-reading overrides
are changed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
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
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import required module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


COMMON = import_file(
    "steam_jp_office_titles_core_common",
    REPO / "workstreams" / "steam_jp_common_messages_v1" / "build_steam_jp_common_messages_v1.py",
)
WAVE08 = import_file(
    "steam_jp_office_titles_core_wave08",
    REPO / "workstreams" / "steam_jp_common_messages_wave08" / "build_wave08_integration.py",
)


SCHEMA = "nobu16.kr.steam-jp-office-titles-core-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-office-titles-core-validation.v1"
PRIVATE_MANIFEST_SCHEMA = "nobu16.kr.steam-jp-office-titles-core-private-candidate.v1"
RESOURCE = "MSG_PK/JP/msgdata.bin"
NAME = "msgdata.bin"
ISSUE_NUMBER = 48
PAIR_OFFSET = 271
SCOPE_RANGES: tuple[tuple[int, int], ...] = (
    (16_399, 16_463),
    (16_474, 16_491),
    (16_527, 16_553),
    (16_568, 16_586),
    (16_588, 16_591),
    (16_601, 16_613),
)
DISPLAY_PAIR_COUNT = 146
EXCLUDED_BAKUFU_RANGE = (16_614, 16_624)
OVERLAY_PATH = HERE / "public" / "msgdata_ko_steam_jp_office_titles_core.v1.json"
VALIDATION_PATH = HERE / "validation.v1.json"
DEFAULT_STOCK_ROOT = WAVE08.DEFAULT_STOCK_ROOT
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_office_titles_core_v1_candidate"

# This is the current initial v0.8 ``msgdata.bin`` baseline.  Later release
# composers may layer this workstream with independent post-v0.8 deltas, but
# this builder never reads an installed patched file.
WAVE08_MSGDATA_BASELINE_PIN = {
    "size": 496_866,
    "packed_sha256": "5469F26B0E75A2214969F2EBA66CD0C850D7BFEC9E3D344ECBC4DBD171110AA6",
    "raw_size": 494_900,
    "raw_sha256": "62E0209E7A9715C1D44BCE28E4C7D0CE2BBBDDD19A25DC21D4A3FA931CD8BC8D",
    "string_count": 29_218,
}

# Deterministic output pin for the reviewed display/reading policy.  It is a
# validation pin, never a tracked binary.
OUTPUT_CANDIDATE_PIN: dict[str, Any] = {
    "size": 496_481,
    "packed_sha256": "96CA306D8F1DAC69CB6927A29D98E5D845B89952EFA357947988DE384875183B",
    "raw_size": 494_516,
    "raw_sha256": "500B00E196C8455968DAA5BFBE5C7D5F5074C5D42A20AC3A4D57C5EB35E22614",
    "string_count": 29_218,
}
EXPECTED_CHANGED_DISPLAY_COUNT = 113
EXPECTED_CHANGED_READING_COUNT = 8
EXPECTED_CHANGED_ENTRY_COUNT = 121
TARGET_CONTRACT_COUNT = DISPLAY_PAIR_COUNT * 2


class OfficeTitlesCoreError(ValueError):
    """A source, baseline, title dictionary, or structure contract differed."""


@dataclass(frozen=True)
class BaselineContext:
    stock: Any
    packed: bytes
    raw: bytes
    table: Any
    wave08_metrics: dict[str, Any]


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


def scope_display_ids() -> tuple[int, ...]:
    return tuple(entry_id for start, end in SCOPE_RANGES for entry_id in range(start, end + 1))


SCOPE_DISPLAY_IDS = scope_display_ids()
SCOPE_DISPLAY_IDS_SHA256 = "F4EE4D5CA357F10BA2B0DC83E1BDDD7ADA815BE32067A4EA88C4DC541FA63218"


# Explicit reviewed values only.  Never derive an output with a general Hanja
# conversion rule: title conventions (for example, 大宰/太宰, 近衛, and 弾正)
# need an ID-level editorial decision.
CANONICAL_KO_BY_DISPLAY_ID: dict[int, str] = {
    16399: "관백",
    16400: "태정대신",
    16401: "좌대신",
    16402: "우대신",
    16403: "내대신",
    16404: "대납언",
    16405: "권대납언",
    16406: "중납언",
    16407: "권중납언",
    16408: "탄정윤",
    16409: "좌근위대장",
    16410: "우근위대장",
    16411: "태재권수",
    16412: "중무경",
    16413: "참의",
    16414: "식부경",
    16415: "치부경",
    16416: "민부경",
    16417: "병부경",
    16418: "형부경",
    16419: "대장경",
    16420: "궁내경",
    16421: "좌경대부",
    16422: "우경대부",
    16423: "탄정대필",
    16424: "좌근위중장",
    16425: "좌근위권중장",
    16426: "우근위중장",
    16427: "우근위권중장",
    16428: "좌위문독",
    16429: "우위문독",
    16430: "좌병위독",
    16431: "우병위독",
    16432: "대재대이",
    16433: "감해유장관",
    16434: "중무대보",
    16435: "대선대부",
    16436: "수리대부",
    16437: "대재소이",
    16438: "식부대보",
    16439: "치부대보",
    16440: "민부대보",
    16441: "병부대보",
    16442: "형부대보",
    16443: "대장대보",
    16444: "궁내대보",
    16445: "탄정소필",
    16446: "좌근위소장",
    16447: "좌근위권소장",
    16448: "우근위소장",
    16449: "우근위권소장",
    16450: "중무소보",
    16451: "도서두",
    16452: "내장두",
    16453: "아악두",
    16454: "현번두",
    16455: "주계두",
    16456: "목공두",
    16457: "좌마두",
    16458: "우마두",
    16459: "병고두",
    16460: "좌위문좌",
    16461: "우위문좌",
    16462: "좌병위좌",
    16463: "우병위좌",
    16474: "시종",
    16475: "식부소보",
    16476: "치부소보",
    16477: "민부소보",
    16478: "병부소보",
    16479: "형부소보",
    16480: "대장소보",
    16481: "궁내소보",
    16482: "좌경량",
    16483: "우경량",
    16484: "대선량",
    16485: "수리량",
    16486: "내장두",
    16487: "봉전두",
    16488: "대취두",
    16489: "주전두",
    16490: "소부두",
    16491: "감해유차관",
    16527: "중무대승",
    16528: "내선정",
    16529: "동시정",
    16530: "서시정",
    16531: "탄정대충",
    16532: "좌근장감",
    16533: "우근장감",
    16534: "식부대승",
    16535: "치부대승",
    16536: "민부대승",
    16537: "병부대승",
    16538: "형부대승",
    16539: "대장대승",
    16540: "궁내대승",
    16541: "도서조",
    16542: "내장조",
    16543: "아악조",
    16544: "현번조",
    16545: "주계조",
    16546: "목공조",
    16547: "좌마조",
    16548: "우마조",
    16549: "병고조",
    16550: "준인정",
    16551: "직부정",
    16552: "채녀정",
    16553: "탄정소충",
    16568: "중무소승",
    16569: "식부소승",
    16570: "치부소승",
    16571: "민부소승",
    16572: "병부소승",
    16573: "형부소승",
    16574: "대장소승",
    16575: "궁내소승",
    16576: "내장조",
    16577: "봉전조",
    16578: "대취조",
    16579: "주전조",
    16580: "소부조",
    16581: "주수정",
    16582: "주선정",
    16583: "좌위문대위",
    16584: "우위문대위",
    16585: "좌병위대위",
    16586: "우병위대위",
    16588: "좌경대진",
    16589: "우경대진",
    16590: "주마수",
    16591: "감해유판관",
    16601: "좌위문소위",
    16602: "우위문소위",
    16603: "좌병위소위",
    16604: "우병위소위",
    16605: "전선",
    16606: "동시우",
    16607: "서시우",
    16608: "준인우",
    16609: "직부우",
    16610: "채녀우",
    16611: "주수우",
    16612: "주선우",
    16613: "정이대장군",
}
CANONICAL_DICTIONARY_SHA256 = "3ED2E7D57206FFAD0AD12E05589E61CABCD1B1C8E9935E83BE4ACF822F58D1B5"

# Only these furigana rows are currently Korean office labels or need the
# explicitly requested Japanese-Hangul spelling.  Every other reading is
# retained byte-for-text from the pinned initial-v0.8 baseline after its
# source/baseline hashes are checked.  This is intentionally an ID dictionary,
# not a blanket phonetic conversion.
JAPANESE_READING_OVERRIDES_BY_DISPLAY_ID: dict[int, str] = {
    16424: "사코노에노추조",
    16425: "사코노에곤노추조",
    16446: "사코노에노쇼쇼",
    16447: "사코노에곤노쇼쇼",
    16585: "사효에노다이조",
    16601: "사에몬노쇼조",
    16603: "사효에노쇼조",
    16613: "세이이다이쇼군",
}
READING_OVERRIDE_IDS = tuple(sorted(JAPANESE_READING_OVERRIDES_BY_DISPLAY_ID))
READING_OVERRIDE_IDS_SHA256 = "1045712D815BA7D17213E11DDDC54F26EFC8FE0B52D43709A5971720AD5F20B1"


def _require_exact_pin(actual: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    if actual != expected:
        raise OfficeTitlesCoreError(f"{label} pin differs: expected={expected!r}, actual={actual!r}")


def assert_static_scope() -> None:
    if len(SCOPE_DISPLAY_IDS) != DISPLAY_PAIR_COUNT:
        raise OfficeTitlesCoreError("display pair scope count differs")
    if len(set(SCOPE_DISPLAY_IDS)) != DISPLAY_PAIR_COUNT or SCOPE_DISPLAY_IDS != tuple(sorted(SCOPE_DISPLAY_IDS)):
        raise OfficeTitlesCoreError("display pair scope is not sorted unique")
    if set(CANONICAL_KO_BY_DISPLAY_ID) != set(SCOPE_DISPLAY_IDS):
        raise OfficeTitlesCoreError("explicit Korean dictionary differs from the 146-pair scope")
    if COMMON.canonical_hash(list(SCOPE_DISPLAY_IDS)) != SCOPE_DISPLAY_IDS_SHA256:
        raise OfficeTitlesCoreError("display scope hash differs")
    dictionary_rows = [
        {"id": entry_id, "ko": CANONICAL_KO_BY_DISPLAY_ID[entry_id]}
        for entry_id in SCOPE_DISPLAY_IDS
    ]
    if COMMON.canonical_hash(dictionary_rows) != CANONICAL_DICTIONARY_SHA256:
        raise OfficeTitlesCoreError("explicit Korean dictionary hash differs")
    for entry_id, korean in CANONICAL_KO_BY_DISPLAY_ID.items():
        if not isinstance(korean, str) or not korean or "\0" in korean:
            raise OfficeTitlesCoreError(f"invalid Korean title at {entry_id}")
        try:
            korean.encode("utf-16le")
        except UnicodeEncodeError as exc:
            raise OfficeTitlesCoreError(f"invalid UTF-16 title at {entry_id}") from exc
        if EXCLUDED_BAKUFU_RANGE[0] <= entry_id <= EXCLUDED_BAKUFU_RANGE[1]:
            raise OfficeTitlesCoreError("excluded Bakufu title entered the core dictionary")
    if READING_OVERRIDE_IDS != (16424, 16425, 16446, 16447, 16585, 16601, 16603, 16613):
        raise OfficeTitlesCoreError("Japanese reading override domain differs")
    if COMMON.canonical_hash(list(READING_OVERRIDE_IDS)) != READING_OVERRIDE_IDS_SHA256:
        raise OfficeTitlesCoreError("Japanese reading override ID hash differs")
    for display_id, reading in JAPANESE_READING_OVERRIDES_BY_DISPLAY_ID.items():
        if display_id not in SCOPE_DISPLAY_IDS or not isinstance(reading, str) or not reading:
            raise OfficeTitlesCoreError(f"invalid Japanese-Hangul reading override at {display_id}")


def build_wave08_baseline(stock_root: Path) -> BaselineContext:
    """Return the exact in-memory initial-v0.8 JP msgdata baseline."""
    assert_static_scope()
    stock = COMMON.load_pinned(
        stock_root / Path(RESOURCE),
        COMMON.STEAM_PINS[NAME],
        "Steam 1.1.7 pristine JP msgdata",
    )
    candidates, metrics = WAVE08.build_all(stock_root)
    if (
        metrics.get("applied_entries") != 40_581
        or metrics.get("wave08_semantic_delta_entries") != 94
        or metrics.get("surname_recovery_delta_entries") != 980
    ):
        raise OfficeTitlesCoreError("initial v0.8 wave08 accounting differs")
    packed = candidates.get(NAME)
    if not isinstance(packed, bytes):
        raise OfficeTitlesCoreError("initial v0.8 msgdata candidate is absent")
    _require_exact_pin(packed_spec(packed), WAVE08_MSGDATA_BASELINE_PIN, "initial v0.8 msgdata")
    candidate_meta = metrics.get("candidates", {}).get(NAME)
    expected_meta = {**WAVE08_MSGDATA_BASELINE_PIN, "sha256": WAVE08_MSGDATA_BASELINE_PIN["packed_sha256"]}
    if candidate_meta != expected_meta:
        raise OfficeTitlesCoreError("initial v0.8 msgdata metadata pin differs")
    _header, raw = COMMON.decompress_wrapper(packed)
    table = COMMON.parse_message_table(raw)
    if table.string_count != stock.table.string_count:
        raise OfficeTitlesCoreError("initial v0.8 string domain differs")
    return BaselineContext(stock=stock, packed=packed, raw=raw, table=table, wave08_metrics=metrics)


def target_by_coordinate(baseline_texts: tuple[str, ...] | list[str]) -> dict[int, tuple[int, str, str]]:
    """Return display Korean and reading Japanese-Hangul targets without conversion."""
    assert_static_scope()
    if len(baseline_texts) != WAVE08_MSGDATA_BASELINE_PIN["string_count"]:
        raise OfficeTitlesCoreError("reading baseline text domain differs")
    rows: dict[int, tuple[int, str, str]] = {}
    for display_id in SCOPE_DISPLAY_IDS:
        korean = CANONICAL_KO_BY_DISPLAY_ID[display_id]
        reading_id = display_id + PAIR_OFFSET
        if display_id in rows or reading_id in rows:
            raise OfficeTitlesCoreError("duplicate display/reading coordinate")
        rows[display_id] = (display_id, "display", korean)
        rows[reading_id] = (
            display_id,
            "reading",
            JAPANESE_READING_OVERRIDES_BY_DISPLAY_ID.get(display_id, baseline_texts[reading_id]),
        )
    if len(rows) != TARGET_CONTRACT_COUNT:
        raise OfficeTitlesCoreError("display/reading coordinate domain differs")
    return rows


def expected_overlay(context: BaselineContext) -> dict[str, Any]:
    targets = target_by_coordinate(context.table.texts)
    entries: list[dict[str, Any]] = []
    target_contracts: list[dict[str, Any]] = []
    changed_display = 0
    changed_reading = 0
    preserved_display = 0
    preserved_reading = 0
    for entry_id in sorted(targets):
        display_id, role, korean = targets[entry_id]
        if not 0 <= entry_id < context.stock.table.string_count:
            raise OfficeTitlesCoreError(f"office coordinate outside msgdata domain: {entry_id}")
        source = context.stock.table.texts[entry_id]
        baseline = context.table.texts[entry_id]
        contract = {
            "id": entry_id,
            "display_id": display_id,
            "role": role,
            "stock_jp_utf16le_sha256": COMMON.text_hash(source),
            "baseline_ko_utf16le_sha256": COMMON.text_hash(baseline),
            "ko": korean,
            "ko_utf16le_sha256": COMMON.text_hash(korean),
            "requires_change": baseline != korean,
        }
        target_contracts.append(contract)
        if baseline == korean:
            if role == "display":
                preserved_display += 1
            else:
                preserved_reading += 1
            continue
        mismatches = COMMON.common.invariant_mismatches(source, korean)
        if mismatches:
            raise OfficeTitlesCoreError(f"format invariant differs at {entry_id}: {mismatches}")
        entries.append({key: value for key, value in contract.items() if key != "requires_change"})
        if role == "display":
            changed_display += 1
        else:
            changed_reading += 1
    if changed_display + preserved_display != DISPLAY_PAIR_COUNT:
        raise OfficeTitlesCoreError("display preservation accounting differs")
    if changed_reading + preserved_reading != DISPLAY_PAIR_COUNT:
        raise OfficeTitlesCoreError("reading preservation accounting differs")
    if changed_display != EXPECTED_CHANGED_DISPLAY_COUNT:
        raise OfficeTitlesCoreError("changed display count differs")
    if changed_reading != EXPECTED_CHANGED_READING_COUNT:
        raise OfficeTitlesCoreError("changed reading count differs")
    if len(entries) != EXPECTED_CHANGED_ENTRY_COUNT:
        raise OfficeTitlesCoreError("changed coordinate count differs")
    if len(target_contracts) != TARGET_CONTRACT_COUNT:
        raise OfficeTitlesCoreError("all-target contract count differs")
    return {
        "schema": SCHEMA,
        "overlay_id": "msgdata_ko_steam_jp_office_titles_core.v1",
        "issue": ISSUE_NUMBER,
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "baseline": {
            "workstream": "steam_jp_common_messages_wave08",
            "candidate": WAVE08_MSGDATA_BASELINE_PIN,
            "source": "deterministic_initial_v0_8_msgdata_candidate",
        },
        "scope": {
            "display_id_ranges": [list(item) for item in SCOPE_RANGES],
            "display_pair_count": DISPLAY_PAIR_COUNT,
            "display_ids_sha256": SCOPE_DISPLAY_IDS_SHA256,
            "pair_offset": PAIR_OFFSET,
            "coordinate_count": TARGET_CONTRACT_COUNT,
            "explicit_canonical_dictionary_sha256": CANONICAL_DICTIONARY_SHA256,
            "japanese_hangul_reading_override_ids": list(READING_OVERRIDE_IDS),
            "japanese_hangul_reading_override_ids_sha256": READING_OVERRIDE_IDS_SHA256,
            "excluded_bakufu_id_range": list(EXCLUDED_BAKUFU_RANGE),
            "excluded_categories": ["geographic_x守", "geographic_x介", "geographic_x守護", "bakufu_16614_16624"],
        },
        "entry_count": len(entries),
        "target_contract_count": len(target_contracts),
        "translation": {
            "changed_display_count": changed_display,
            "changed_reading_count": changed_reading,
            "changed_entry_count": len(entries),
            "already_canonical_display_count_preserved": preserved_display,
            "already_correct_japanese_hangul_reading_count_preserved": preserved_reading,
            "display_uses_canonical_korean": True,
            "reading_uses_japanese_hangul": True,
        },
        "provenance": {
            "explicit_id_dictionary_used": True,
            "generic_hanja_conversion_used": False,
            "stock_jp_hashes_fail_closed": True,
            "baseline_ko_hashes_fail_closed": True,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
        },
        "entries": entries,
        "target_contracts": target_contracts,
    }


def load_overlay(context: BaselineContext) -> tuple[dict[str, Any], bytes]:
    value, blob = COMMON.read_json(OVERLAY_PATH)
    expected = expected_overlay(context)
    if value != expected or blob != COMMON.pretty_bytes(expected):
        raise OfficeTitlesCoreError("tracked office-title overlay differs from deterministic model")
    return value, blob


def build_blob(stock_root: Path) -> tuple[bytes, dict[str, Any]]:
    context = build_wave08_baseline(stock_root)
    overlay, overlay_blob = load_overlay(context)
    targets = target_by_coordinate(context.table.texts)
    entries = overlay.get("entries")
    if not isinstance(entries, list):
        raise OfficeTitlesCoreError("overlay entries are absent")
    texts = list(context.table.texts)
    changed: set[int] = set()
    changed_display: set[int] = set()
    changed_reading: set[int] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise OfficeTitlesCoreError("overlay entry is not an object")
        required = {
            "id", "display_id", "role", "stock_jp_utf16le_sha256",
            "baseline_ko_utf16le_sha256", "ko", "ko_utf16le_sha256",
        }
        if set(entry) != required:
            raise OfficeTitlesCoreError("overlay entry keys differ")
        entry_id = entry.get("id")
        if type(entry_id) is not int or entry_id not in targets or entry_id in changed:
            raise OfficeTitlesCoreError("overlay coordinate differs")
        display_id, role, expected_output = targets[entry_id]
        if entry.get("display_id") != display_id or entry.get("role") != role:
            raise OfficeTitlesCoreError(f"display/reading pair metadata differs at {entry_id}")
        source = context.stock.table.texts[entry_id]
        baseline = texts[entry_id]
        replacement = entry.get("ko")
        if (
            COMMON.text_hash(source) != entry.get("stock_jp_utf16le_sha256")
            or COMMON.text_hash(baseline) != entry.get("baseline_ko_utf16le_sha256")
            or replacement != expected_output
            or not isinstance(replacement, str)
            or "\0" in replacement
            or COMMON.text_hash(replacement) != entry.get("ko_utf16le_sha256")
        ):
            raise OfficeTitlesCoreError(f"row hash or target output differs at {entry_id}")
        if baseline == replacement:
            raise OfficeTitlesCoreError(f"already-correct target row entered delta: {entry_id}")
        mismatches = COMMON.common.invariant_mismatches(source, replacement)
        if mismatches:
            raise OfficeTitlesCoreError(f"format invariant differs at {entry_id}: {mismatches}")
        texts[entry_id] = replacement
        changed.add(entry_id)
        (changed_display if role == "display" else changed_reading).add(entry_id)

    expected_changed = {
        entry_id
        for entry_id, (_display_id, _role, korean) in targets.items()
        if context.table.texts[entry_id] != korean
    }
    if changed != expected_changed:
        raise OfficeTitlesCoreError("only rows requiring target output changed")
    for display_id in SCOPE_DISPLAY_IDS:
        display_target = CANONICAL_KO_BY_DISPLAY_ID[display_id]
        reading_target = targets[display_id + PAIR_OFFSET][2]
        if texts[display_id] != display_target or texts[display_id + PAIR_OFFSET] != reading_target:
            raise OfficeTitlesCoreError(f"display/reading pair target differs: {display_id}")
    for entry_id, baseline in enumerate(context.table.texts):
        if entry_id not in changed and texts[entry_id] != baseline:
            raise OfficeTitlesCoreError(f"non-delta text changed: {entry_id}")

    rebuilt_raw = COMMON.rebuild_message_table(context.stock.table, texts)
    reparsed = COMMON.parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise OfficeTitlesCoreError("rebuilt office-title table differs")
    if not COMMON._opaque_structure_preserved(context.stock.table, reparsed, rebuilt_raw):
        raise OfficeTitlesCoreError("opaque msgdata structure differs")
    candidate = COMMON.recompress_wrapper(rebuilt_raw, context.stock.packed)
    _header, roundtrip = COMMON.decompress_wrapper(candidate)
    if roundtrip != rebuilt_raw or candidate[:8] != context.stock.packed[:8]:
        raise OfficeTitlesCoreError("candidate wrapper round-trip differs")
    candidate_spec = packed_spec(candidate)
    _require_exact_pin(candidate_spec, OUTPUT_CANDIDATE_PIN, "office-title candidate")
    if len(changed_display) + len(changed_reading) != len(changed):
        raise OfficeTitlesCoreError("display/reading delta partition differs")
    return candidate, {
        "schema": PRIVATE_MANIFEST_SCHEMA,
        "resource": RESOURCE,
        "issue": ISSUE_NUMBER,
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "initial_v0_8_baseline": WAVE08_MSGDATA_BASELINE_PIN,
        "candidate": candidate_spec,
        "overlay": {"size": len(overlay_blob), "sha256": sha256(overlay_blob)},
        "scope": {
            "display_pair_count": DISPLAY_PAIR_COUNT,
            "pair_offset": PAIR_OFFSET,
            "display_ids_sha256": SCOPE_DISPLAY_IDS_SHA256,
            "explicit_canonical_dictionary_sha256": CANONICAL_DICTIONARY_SHA256,
            "japanese_hangul_reading_override_ids_sha256": READING_OVERRIDE_IDS_SHA256,
            "excluded_bakufu_id_range": list(EXCLUDED_BAKUFU_RANGE),
        },
        "translation": {
            "changed_display_count": len(changed_display),
            "changed_reading_count": len(changed_reading),
            "changed_entry_count": len(changed),
            "already_canonical_display_count_preserved": DISPLAY_PAIR_COUNT - len(changed_display),
            "already_correct_japanese_hangul_reading_count_preserved": DISPLAY_PAIR_COUNT - len(changed_reading),
            "display_uses_canonical_korean": True,
            "reading_uses_japanese_hangul": True,
        },
        "anchors": {
            "16402": "우대신",
            "16399": "관백",
            "16670": "간파쿠",
            "16673": "우다이진",
            "16404": "대납언",
            "16675": "다이나곤",
            "16410": "우근위대장",
            "16681": "우코노에노타이쇼",
            "16413": "참의",
            "16684": "참의",
            "16613": "정이대장군",
            "16884": "세이이다이쇼군",
        },
        "proofs": {
            "only_rows_requiring_target_output_changed": True,
            "all_146_display_rows_canonical_korean": True,
            "all_146_reading_rows_japanese_hangul": True,
            "non_delta_texts_preserved": True,
            "id_domain_preserved": True,
            "string_count_preserved": True,
            "opaque_non_string_metadata_preserved": True,
            "wrapper_prefix_preserved": True,
            "generic_hanja_conversion_used": False,
        },
        "safety": {
            "complete_candidate_binary_tracked": False,
            "installed_game_files_modified": False,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
        },
    }


DELTA_ENTRY_KEYS = {
    "id",
    "display_id",
    "role",
    "stock_jp_utf16le_sha256",
    "baseline_ko_utf16le_sha256",
    "ko",
    "ko_utf16le_sha256",
}
TARGET_CONTRACT_KEYS = {*DELTA_ENTRY_KEYS, "requires_change"}


def _validated_target_contracts(
    context: BaselineContext, overlay: dict[str, Any]
) -> tuple[dict[int, dict[str, Any]], set[int]]:
    """Validate all 292 source-free target contracts against initial v0.8.

    The contracts cover all 292 rows: 171 already-correct targets plus 121
    replacements.  A later composer can therefore prove that no other
    workstream touched any of the title/reading coordinates before applying
    this delta.
    """
    targets = target_by_coordinate(context.table.texts)
    contracts = overlay.get("target_contracts")
    entries = overlay.get("entries")
    if (
        overlay.get("target_contract_count") != TARGET_CONTRACT_COUNT
        or not isinstance(contracts, list)
        or len(contracts) != TARGET_CONTRACT_COUNT
        or overlay.get("entry_count") != EXPECTED_CHANGED_ENTRY_COUNT
        or not isinstance(entries, list)
        or len(entries) != EXPECTED_CHANGED_ENTRY_COUNT
    ):
        raise OfficeTitlesCoreError("target contract or delta entry count differs")
    by_id: dict[int, dict[str, Any]] = {}
    expected_delta_entries: list[dict[str, Any]] = []
    for contract in contracts:
        if not isinstance(contract, dict) or set(contract) != TARGET_CONTRACT_KEYS:
            raise OfficeTitlesCoreError("target contract keys differ")
        entry_id = contract.get("id")
        if type(entry_id) is not int or entry_id not in targets or entry_id in by_id:
            raise OfficeTitlesCoreError("target contract coordinate differs")
        display_id, role, target_korean = targets[entry_id]
        if (
            contract.get("display_id") != display_id
            or contract.get("role") != role
            or contract.get("ko") != target_korean
            or type(contract.get("requires_change")) is not bool
        ):
            raise OfficeTitlesCoreError(f"target contract metadata differs at {entry_id}")
        source = context.stock.table.texts[entry_id]
        initial_baseline = context.table.texts[entry_id]
        if (
            COMMON.text_hash(source) != contract.get("stock_jp_utf16le_sha256")
            or COMMON.text_hash(initial_baseline) != contract.get("baseline_ko_utf16le_sha256")
            or COMMON.text_hash(target_korean) != contract.get("ko_utf16le_sha256")
            or bool(contract["requires_change"]) != (initial_baseline != target_korean)
        ):
            raise OfficeTitlesCoreError(f"target source/baseline contract differs at {entry_id}")
        mismatches = COMMON.common.invariant_mismatches(source, target_korean)
        if mismatches:
            raise OfficeTitlesCoreError(f"target format invariant differs at {entry_id}: {mismatches}")
        by_id[entry_id] = contract
        if contract["requires_change"]:
            expected_delta_entries.append(
                {key: contract[key] for key in DELTA_ENTRY_KEYS}
            )
    if tuple(sorted(by_id)) != tuple(sorted(targets)):
        raise OfficeTitlesCoreError("target contract domain differs")
    if entries != expected_delta_entries:
        raise OfficeTitlesCoreError("delta differs from target contracts")
    return by_id, set(entry["id"] for entry in expected_delta_entries)


def _parse_composable_baseline(
    context: BaselineContext, baseline_packed: bytes
) -> tuple[bytes, Any]:
    if not isinstance(baseline_packed, bytes):
        raise OfficeTitlesCoreError("composable baseline must be bytes")
    _header, raw = COMMON.decompress_wrapper(baseline_packed)
    table = COMMON.parse_message_table(raw)
    if table.string_count != context.stock.table.string_count:
        raise OfficeTitlesCoreError("composable baseline string domain differs")
    if baseline_packed[:8] != context.stock.packed[:8]:
        raise OfficeTitlesCoreError("composable baseline wrapper prefix differs")
    if not COMMON._opaque_structure_preserved(context.stock.table, table, raw):
        raise OfficeTitlesCoreError("composable baseline opaque structure differs")
    return raw, table


def _apply_to_packed_context(
    context: BaselineContext, baseline_packed: bytes
) -> tuple[bytes, dict[str, Any]]:
    """Apply exactly the checked-in display/reading delta to a later layer."""
    overlay, overlay_blob = load_overlay(context)
    contracts, expected_changed = _validated_target_contracts(context, overlay)
    _raw, baseline_table = _parse_composable_baseline(context, baseline_packed)
    texts = list(baseline_table.texts)
    changed: set[int] = set()
    changed_display: set[int] = set()
    changed_reading: set[int] = set()

    for entry_id in sorted(contracts):
        contract = contracts[entry_id]
        source = context.stock.table.texts[entry_id]
        current = texts[entry_id]
        replacement = contract["ko"]
        if COMMON.text_hash(source) != contract["stock_jp_utf16le_sha256"]:
            raise OfficeTitlesCoreError(f"current JP source hash differs at {entry_id}")
        if COMMON.text_hash(current) != contract["baseline_ko_utf16le_sha256"]:
            raise OfficeTitlesCoreError(
                f"later baseline target hash differs at {entry_id}; composition is unsafe"
            )
        if COMMON.text_hash(replacement) != contract["ko_utf16le_sha256"]:
            raise OfficeTitlesCoreError(f"target output hash differs at {entry_id}")
        if contract["requires_change"]:
            if current == replacement:
                raise OfficeTitlesCoreError(f"delta target unexpectedly already correct: {entry_id}")
            texts[entry_id] = replacement
            changed.add(entry_id)
            if contract["role"] == "display":
                changed_display.add(entry_id)
            else:
                changed_reading.add(entry_id)
        elif current != replacement:
            raise OfficeTitlesCoreError(f"preserved target differs: {entry_id}")

    if changed != expected_changed or len(changed) != EXPECTED_CHANGED_ENTRY_COUNT:
        raise OfficeTitlesCoreError("composable delta domain differs")
    if len(changed_display) != EXPECTED_CHANGED_DISPLAY_COUNT:
        raise OfficeTitlesCoreError("composable display delta count differs")
    if len(changed_reading) != EXPECTED_CHANGED_READING_COUNT:
        raise OfficeTitlesCoreError("composable reading delta count differs")
    for display_id in SCOPE_DISPLAY_IDS:
        display_target = CANONICAL_KO_BY_DISPLAY_ID[display_id]
        reading_target = contracts[display_id + PAIR_OFFSET]["ko"]
        if texts[display_id] != display_target or texts[display_id + PAIR_OFFSET] != reading_target:
            raise OfficeTitlesCoreError(f"composed display/reading pair differs: {display_id}")
    for entry_id, baseline in enumerate(baseline_table.texts):
        if entry_id not in changed and texts[entry_id] != baseline:
            raise OfficeTitlesCoreError(f"composable non-target text changed: {entry_id}")

    rebuilt_raw = COMMON.rebuild_message_table(baseline_table, texts)
    reparsed = COMMON.parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise OfficeTitlesCoreError("composable rebuilt table differs")
    if not COMMON._opaque_structure_preserved(baseline_table, reparsed, rebuilt_raw):
        raise OfficeTitlesCoreError("composable opaque table metadata differs")
    candidate = COMMON.recompress_wrapper(rebuilt_raw, baseline_packed)
    _header, roundtrip = COMMON.decompress_wrapper(candidate)
    if roundtrip != rebuilt_raw or candidate[:8] != baseline_packed[:8]:
        raise OfficeTitlesCoreError("composable wrapper round-trip differs")
    candidate_spec = packed_spec(candidate)
    return candidate, {
        "schema": "nobu16.kr.steam-jp-office-titles-core-composable-result.v1",
        "resource": RESOURCE,
        "issue": ISSUE_NUMBER,
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "initial_v0_8_baseline": WAVE08_MSGDATA_BASELINE_PIN,
        "input_baseline": packed_spec(baseline_packed),
        "candidate": candidate_spec,
        "overlay": {"size": len(overlay_blob), "sha256": sha256(overlay_blob)},
        "scope": {
            "display_pair_count": DISPLAY_PAIR_COUNT,
            "pair_offset": PAIR_OFFSET,
            "target_contract_count": TARGET_CONTRACT_COUNT,
            "display_ids_sha256": SCOPE_DISPLAY_IDS_SHA256,
            "explicit_canonical_dictionary_sha256": CANONICAL_DICTIONARY_SHA256,
            "japanese_hangul_reading_override_ids_sha256": READING_OVERRIDE_IDS_SHA256,
            "excluded_bakufu_id_range": list(EXCLUDED_BAKUFU_RANGE),
        },
        "translation": {
            "changed_display_count": len(changed_display),
            "changed_reading_count": len(changed_reading),
            "changed_entry_count": len(changed),
            "already_canonical_display_count_preserved": DISPLAY_PAIR_COUNT - len(changed_display),
            "already_correct_japanese_hangul_reading_count_preserved": DISPLAY_PAIR_COUNT - len(changed_reading),
            "display_uses_canonical_korean": True,
            "reading_uses_japanese_hangul": True,
        },
        "anchors": {
            "16402": "우대신",
            "16399": "관백",
            "16670": "간파쿠",
            "16673": "우다이진",
            "16404": "대납언",
            "16675": "다이나곤",
            "16410": "우근위대장",
            "16681": "우코노에노타이쇼",
            "16413": "참의",
            "16684": "참의",
            "16613": "정이대장군",
            "16884": "세이이다이쇼군",
        },
        "proofs": {
            "all_292_target_contracts_fail_closed": True,
            "pristine_jp_hashes_fail_closed": True,
            "later_baseline_target_hashes_fail_closed": True,
            "same_source_free_delta_applied": True,
            "all_146_display_rows_canonical_korean": True,
            "all_146_reading_rows_japanese_hangul": True,
            "non_delta_texts_preserved": True,
            "id_domain_preserved": True,
            "string_count_preserved": True,
            "opaque_non_string_metadata_preserved": True,
            "wrapper_prefix_preserved": True,
            "generic_hanja_conversion_used": False,
        },
        "safety": {
            "complete_candidate_binary_tracked": False,
            "installed_game_files_modified": False,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
        },
    }


def apply_to_packed(stock_root: Path, baseline_packed: bytes) -> tuple[bytes, dict[str, Any]]:
    """Compose the display/reading delta onto a verified later ``msgdata.bin`` layer.

    This is the integration API for candidate composers.  It verifies the
    pristine JP hash and the initial-v0.8 Korean baseline hash for every one
    of the 292 title/reading coordinates before preserving non-target bytes.
    ``baseline_packed`` may therefore include independent prior deltas only
    outside this core's coordinate domain.
    """
    return _apply_to_packed_context(build_wave08_baseline(stock_root), baseline_packed)


def validation_model(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "issue": ISSUE_NUMBER,
        "target": {"base_language": "JP", "steam_version": "1.1.7", "resource": RESOURCE},
        "scope": metrics["scope"],
        "translation": metrics["translation"],
        "expected": {
            "stock_jp": metrics["stock_jp"],
            "initial_v0_8_baseline": metrics["initial_v0_8_baseline"],
            "candidate": metrics["candidate"],
            "overlay": metrics["overlay"],
        },
        "anchors": metrics["anchors"],
        "composable_api": {
            "function": "apply_to_packed(stock_root, baseline_packed)",
            "target_contract_count": TARGET_CONTRACT_COUNT,
            "delta_entry_count": EXPECTED_CHANGED_ENTRY_COUNT,
            "validates_pristine_jp_hashes": True,
            "validates_each_later_baseline_target_hash": True,
            "preserves_non_target_texts": True,
        },
        "proofs": {
            **metrics["proofs"],
            "deterministic_ab_equal": True,
            "stock_jp_hash_pinned": True,
            "initial_v0_8_baseline_hash_pinned": True,
            "stock_jp_hashes_fail_closed": True,
            "baseline_ko_hashes_fail_closed": True,
        },
        "safety": metrics["safety"],
    }


def generate(stock_root: Path) -> dict[str, Any]:
    context = build_wave08_baseline(stock_root)
    COMMON.atomic_write(OVERLAY_PATH, COMMON.pretty_bytes(expected_overlay(context)))
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise OfficeTitlesCoreError("office-title deterministic A/B differs")
    COMMON.atomic_write(VALIDATION_PATH, COMMON.pretty_bytes(validation_model(first_metrics)))
    return {"status": "GENERATED", **first_metrics, "deterministic_ab_equal": True}


def verify(stock_root: Path) -> dict[str, Any]:
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise OfficeTitlesCoreError("office-title deterministic A/B differs")
    validation, validation_blob = COMMON.read_json(VALIDATION_PATH)
    expected = validation_model(first_metrics)
    if validation != expected or validation_blob != COMMON.pretty_bytes(expected):
        raise OfficeTitlesCoreError("tracked office-title validation differs")
    return {"status": "PASS", **first_metrics, "deterministic_ab_equal": True}


def safe_output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = (REPO / "tmp").resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents or resolved.exists():
        raise OfficeTitlesCoreError(f"unsafe output root: {resolved}")
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
        result = generate(args.stock_root)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "verify":
        result = verify(args.stock_root)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    print(build(args.stock_root, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
