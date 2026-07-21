#!/usr/bin/env python3
"""Build a private Static Patch 007 restoration candidate for six event rows.

The committed 5777 Static Patch 007 candidate is the only Korean input.
Direct PC JP/EN/SC/TC resources are read-only semantic evidence.  This
builder never writes the Steam installation, Git, a release, or the network;
it emits exactly one private candidate below ``tmp``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


MSGEV = "MSG_PK/JP/msgev.bin"
EXPECTED_ROW_COUNT = 17_916
PREDECESSOR_WORKSTREAM = "pc_event_5777_kanegasaki_static007_3line_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_PREDECESSOR_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "92B11470E00C7A5004739847D2548286D296B76D4C6016FD1B5E0DDD542EB611",
    "raw_size": 996_276,
    "sha256": "1F7E42E10C0034CD70565993BE3DB311DF3A5356525B6BA14B31987752967745",
    "size": 1_000_208,
}
# Pinned from the deterministic, strict-predecessor `profile` result.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "568D4D514D75A35A6ED9F15841CD682D4795C6563DC0ADBF4A4843EE806034DA",
    "raw_size": 996_420,
    "sha256": "0966577DD40656B46D4276FA49F448F7D44E5A1C7845B814EABC07604B73CFD4",
    "size": 1_000_353,
}

DIRECT_CONTEXT_PATHS: Mapping[str, Path] = {
    "jp": Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
        r"\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msgev.bin"
    ),
    "en": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msgev.bin"),
    "sc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msgev.bin"),
    "tc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msgev.bin"),
}
EXPECTED_CONTEXT_PROFILES: Mapping[str, Mapping[str, Any]] = {
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

HISTORICAL_OVERLAY_PATH = (
    REPO / "workstreams" / "steam_jp_msgev_full_layout_v2" / "public" / "msgev_ko_steam_jp_full_layout.v2.json"
)
HISTORICAL_OPERATION = "manual_compact_korean_layout"
SCENE_BATCHES: Mapping[str, tuple[int, ...]] = {
    "zentokuji_alliance_context": tuple(range(3_210, 3_215)),
    "kanegasaki_withdrawal_context": tuple(range(3_230, 3_245)),
}
REVIEWED_IDS = tuple(entry_id for batch in SCENE_BATCHES.values() for entry_id in batch)
CHANGED_IDS = (3_210, 3_231, 3_232, 3_233, 3_234, 3_239)
RETAINED_IDS = tuple(entry_id for entry_id in REVIEWED_IDS if entry_id not in CHANGED_IDS)

MAX_LINES = 4
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
RAW_STATIC_PATCH_007_LIMIT_PX = 1_440
DRAW_FONT_PX = 30
EFFECTIVE_STATIC_PATCH_007_LIMIT_PX = 912
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*(?:\d+|\*)?(?:\.(?:\d+|\*))?[hlL]?[diuoxXfFeEgGaAcspn%]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
E = "\x1b"

# Every target retains the direct-PC meaning.  The four-line box is a maximum,
# not a request to split prose mechanically or shorten a sentence.
TARGETS: Mapping[int, str] = {
    3_210: (
        "오늘날 이 회담의 실재를 부정하는 설도 있으나,\n"
        "만일 세 거두가 한자리에 모였다면,\n"
        "그들이 나눈 말의 내용을 상상하는 흥미는 끝이 없다."
    ),
    3_231: (
        "그러나 그것은 위장책에 지나지 않았으며,\n"
        f"진의는 이웃 나라 {E}CC에치젠{E}CZ에 웅거해\n"
        f"{E}CA요시아키{E}CZ와 {E}CA노부나가{E}CZ에게 맞서는 {E}CA아사쿠라 요시카게{E}CZ를\n"
        "견제하는 데 있었다."
    ),
    3_232: (
        f"{E}CC쓰루가{E}CZ에 들어간 {E}CC오다{E}CZ군은 {E}CC가네가사키성{E}CZ을 함락한 뒤,\n"
        f"더 나아가 {E}CC기노메 고개{E}CZ를 넘으려던 바로 그때,\n"
        "정체불명의 진중 위문품이 도착했다."
    ),
    3_233: (
        "양 끝을 끈으로 묶은 자루…… 안에는 팥이 가득 들어 있었다.\n"
        f"보낸 이는 {E}CC고호쿠{E}CZ의 영주 {E}CA아자이 나가마사{E}CZ에게 시집보낸\n"
        f"여동생 {E}CA오이치{E}CZ였다."
    ),
    3_234: (
        "이 자루가 무엇을 뜻하는지, 막료들은 골머리를 앓았다.\n"
        f"난제를 푼 것은 {E}CA기노시타 도키치로 히데요시{E}CZ였다."
    ),
    3_239: (
        f"부부 금슬은 좋았고, {E}CA노부나가{E}CZ 또한 순박한 매제를 아꼈다.\n"
        f"그 {E}CA나가마사{E}CZ에게 하필이면 지금 배신당할 줄이야."
    ),
}
TARGET_LAYOUTS: Mapping[int, tuple[tuple[int, ...], tuple[int, ...]]] = {
    3_210: ((1_080, 792, 1_200), (675, 495, 750)),
    3_231: ((936, 768, 1_200, 456), (585, 480, 750, 285)),
    3_232: ((1_200, 1_032, 816), (750, 645, 510)),
    3_233: ((1_344, 1_248, 432), (840, 780, 270)),
    3_234: ((1_248, 1_104), (780, 690)),
    3_239: ((1_320, 1_104), (825, 690)),
}
RATIONALES: Mapping[int, str] = {
    3_210: "회담의 실재를 부정하는 설, 세 거두의 가정적 회동, 대화 내용을 상상하는 끝없는 흥미를 모두 복원했다.",
    3_231: "隠れ蓑의 위장책과 진의, 에치젠에 웅거한 요시카게를 견제한 목적을 모두 보존했다.",
    3_232: "성 함락 뒤 더 나아가 고개를 넘으려던 바로 그때라는 시간 관계와 진중 위문품을 복원했다.",
    3_233: "양 끝을 묶은 자루 안에 팥이 가득 든 사실과 오이치의 발신자 관계를 빠짐없이 복원했다.",
    3_234: "막료의 고민, 난제 해결, 기노시타 도키치로 히데요시의 전체 이름을 보존했다.",
    3_239: "부부 금슬, 노부나가의 애정, 나가마사에게 하필 지금 배신당한다는 수동적 탄식을 보존했다.",
}
CURRENT_QUALITY_PRESERVED: Mapping[int, tuple[str, ...]] = {
    3_210: ("회담", "세 거두", "가정적 회동"),
    3_231: ("에치젠", "요시아키", "노부나가", "아사쿠라 요시카게"),
    3_232: ("쓰루가", "오다군", "가네가사키성", "기노메 고개"),
    3_233: ("고호쿠", "아자이 나가마사", "오이치"),
    3_234: ("기노시타", "히데요시"),
    3_239: ("노부나가", "나가마사", "매제"),
}


class ManualCompactStatic007Error(RuntimeError):
    """Raised when strict input, evidence, layout, or output drifts."""


@dataclass(frozen=True)
class Bundle:
    event: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    profile: Mapping[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ManualCompactStatic007Error(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def file_spec(path: Path) -> Mapping[str, Any]:
    blob = path.read_bytes()
    return {"path": path.relative_to(REPO).as_posix(), "size": len(blob), "sha256": sha256(blob)}


def profile(event: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "sha256": sha256(event),
        "size": len(event),
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
    }


def parse_table(label: str, event: bytes) -> tuple[Any, bytes, Any]:
    header, raw = decompress_wrapper(event)
    table = parse_message_table(raw)
    require(len(table.texts) == EXPECTED_ROW_COUNT, f"{label} row-count drift: {len(table.texts)}")
    return header, raw, table


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ManualCompactStatic007Error(f"candidate path escapes tmp: {resolved}") from exc
    return resolved


def control_signature(value: str) -> Mapping[str, Any]:
    esc_tokens: list[str] = []
    other_controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == E:
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token at {cursor}")
            esc_tokens.append(token)
            cursor += 3
            continue
        if character not in "\r\n" and unicodedata.category(character) == "Cc":
            other_controls.append(f"U+{ord(character):04X}")
        cursor += 1
    printf = list(PRINTF_RE.finditer(value))
    printf_offsets = {match.start() for match in printf}
    return {
        "esc_tokens": esc_tokens,
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": [match.group(0) for match in printf],
        "unknown_percent_count": sum(
            1 for offset, character in enumerate(value) if character == "%" and offset not in printf_offsets
        ),
        "other_controls": other_controls,
    }


def assert_no_break_inside_tag(value: str) -> None:
    in_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == E:
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token: {token!r}")
            if token == f"{E}CZ":
                require(in_span, "unpaired ESC close")
                in_span = False
            else:
                require(not in_span, "nested ESC span")
                in_span = True
            cursor += 3
            continue
        require(not (in_span and value[cursor] in "\r\n"), "line break inside ESC span")
        cursor += 1
    require(not in_span, "unterminated ESC span")


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


def rendered_display_line(value: str) -> str:
    display: list[str] = []
    cursor = 0
    while cursor < len(value):
        if value[cursor] == E:
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed layout ESC token: {token!r}")
            cursor += 3
            continue
        runtime = RUNTIME_RE.match(value, cursor)
        require(runtime is None, f"unexpected runtime token: {runtime.group(0) if runtime else ''}")
        character = value[cursor]
        require(unicodedata.category(character) != "Cc", f"unexpected visible control U+{ord(character):04X}")
        display.append(character)
        cursor += 1
    return "".join(display)


def line_metrics(value: str) -> tuple[Mapping[str, Any], ...]:
    result: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(LINEBREAK_RE.sub("\n", value).split("\n"), 1):
        display = rendered_display_line(line)
        full = sum(is_full_width_visible(character) for character in display)
        half = len(display) - full
        raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
        effective = (raw * DRAW_FONT_PX + RAW_FULL_WIDTH_PX - 1) // RAW_FULL_WIDTH_PX
        over_raw = raw > RAW_STATIC_PATCH_007_LIMIT_PX
        over_effective = effective > EFFECTIVE_STATIC_PATCH_007_LIMIT_PX
        result.append(
            {
                "line_number": line_number,
                "display_string": display,
                "raw_g1n_width_px": raw,
                "effective_width_px": effective,
                "full_width_character_count": full,
                "half_width_character_count": half,
                "over_raw_1440px": over_raw,
                "over_effective_912px": over_effective,
                "passes_static_patch_007": not over_raw and not over_effective,
            }
        )
    return tuple(result)


def validate_authored_targets() -> None:
    require(tuple(TARGETS) == CHANGED_IDS, "target ID order/scope drift")
    require(set(CHANGED_IDS).isdisjoint(RETAINED_IDS), "changed/retained scope overlap")
    require(tuple(REVIEWED_IDS) == tuple(range(3210, 3215)) + tuple(range(3230, 3245)), "review scope drift")
    for entry_id, target in TARGETS.items():
        require("\x00" not in target, f"embedded terminator: {entry_id}")
        assert_no_break_inside_tag(target)
        signature = control_signature(target)
        require(signature["runtime_tokens"] == [], f"runtime token in target: {entry_id}")
        require(signature["printf_tokens"] == [], f"printf token in target: {entry_id}")
        require(signature["unknown_percent_count"] == 0, f"unknown percent in target: {entry_id}")
        require(signature["other_controls"] == [], f"other control in target: {entry_id}")
        metrics = line_metrics(target)
        expected_raw, expected_effective = TARGET_LAYOUTS[entry_id]
        require(1 <= len(metrics) <= MAX_LINES, f"target line count exceeds max: {entry_id}")
        require(tuple(line["raw_g1n_width_px"] for line in metrics) == expected_raw, f"target raw drift: {entry_id}")
        require(
            tuple(line["effective_width_px"] for line in metrics) == expected_effective,
            f"target effective drift: {entry_id}",
        )
        require(all(line["passes_static_patch_007"] for line in metrics), f"target fails Static Patch 007: {entry_id}")


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"strict predecessor file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict Static007 predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_PREDECESSOR_PROFILE, "strict predecessor packed/raw profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_PREDECESSOR_PROFILE, "predecessor audit profile drift")
    require(manifest.get("output") == EXPECTED_PREDECESSOR_PROFILE, "predecessor manifest profile drift")
    return event, table, raw, predecessor_profile, audit, manifest


def load_direct_contexts() -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
    tables: dict[str, Any] = {}
    profiles: dict[str, Mapping[str, Any]] = {}
    for language, path in DIRECT_CONTEXT_PATHS.items():
        resolved = path.resolve(strict=True)
        require("switch" not in {part.casefold() for part in resolved.parts}, f"non-PC context forbidden: {resolved}")
        event = resolved.read_bytes()
        _header, raw, table = parse_table(f"direct PC {language.upper()}", event)
        source_profile = profile(event, raw)
        require(source_profile == EXPECTED_CONTEXT_PROFILES[language], f"direct PC {language.upper()} profile drift")
        tables[language] = table
        profiles[language] = source_profile
    require(tuple(sorted(tables)) == ("en", "jp", "sc", "tc"), "direct PC language scope drift")
    return tables, profiles


def load_historical_manual_compact() -> tuple[Mapping[int, Mapping[str, Any]], Mapping[str, Any]]:
    require(HISTORICAL_OVERLAY_PATH.is_file(), f"historical overlay missing: {HISTORICAL_OVERLAY_PATH}")
    document = json.loads(HISTORICAL_OVERLAY_PATH.read_text(encoding="utf-8"))
    entries = document.get("entries")
    require(isinstance(entries, list), "historical overlay entries missing")
    by_id: dict[int, Mapping[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or type(entry.get("id")) is not int:
            continue
        entry_id = entry["id"]
        if entry_id in CHANGED_IDS:
            require(entry_id not in by_id, f"historical duplicate ID: {entry_id}")
            by_id[entry_id] = entry
    require(tuple(sorted(by_id)) == CHANGED_IDS, "historical manual compact coverage drift")
    for entry_id, entry in by_id.items():
        require(entry.get("operation") == HISTORICAL_OPERATION, f"historical operation drift: {entry_id}")
        require(isinstance(entry.get("ko"), str) and entry["ko"], f"historical Korean absent: {entry_id}")
    return by_id, file_spec(HISTORICAL_OVERLAY_PATH)


def scene_name(entry_id: int) -> str:
    for name, ids in SCENE_BATCHES.items():
        if entry_id in ids:
            return name
    raise ManualCompactStatic007Error(f"entry outside review scope: {entry_id}")


def historical_evidence(entry_id: int, historical: Mapping[int, Mapping[str, Any]]) -> Mapping[str, Any] | None:
    entry = historical.get(entry_id)
    if entry is None:
        return None
    legacy = str(entry["ko"])
    return {
        "operation": str(entry["operation"]),
        "legacy_manual_compact_ko": legacy,
        "legacy_manual_compact_ko_utf16le_sha256": text_hash(legacy),
        "legacy_lines": list(line_metrics(legacy)),
        "legacy_source_is_not_korean_build_input": True,
    }


def prepare(*, require_output_profile: bool) -> Bundle:
    validate_authored_targets()
    before_event, before, _before_raw, predecessor_profile, predecessor_audit, _predecessor_manifest = load_predecessor()
    contexts, context_profiles = load_direct_contexts()
    historical, historical_profile = load_historical_manual_compact()
    require(all(len(before.texts) == len(table.texts) for table in contexts.values()), "context table topology drift")

    texts = list(before.texts)
    rows: list[Mapping[str, Any]] = []
    for entry_id in REVIEWED_IDS:
        current = before.texts[entry_id]
        source_jp = contexts["jp"].texts[entry_id]
        source_en = contexts["en"].texts[entry_id]
        source_sc = contexts["sc"].texts[entry_id]
        source_tc = contexts["tc"].texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(all((current, source_jp, source_en, source_sc, source_tc, target)), f"empty reviewed row: {entry_id}")
        current_signature = control_signature(current)
        require(current_signature == control_signature(source_jp), f"strict KO/direct JP control drift: {entry_id}")
        require(control_signature(target) == current_signature, f"target control/token drift: {entry_id}")
        assert_no_break_inside_tag(current)
        assert_no_break_inside_tag(target)
        require(not RUNTIME_RE.findall(target), f"unexpected runtime token: {entry_id}")
        current_lines = line_metrics(current)
        target_lines = line_metrics(target)
        require(1 <= len(target_lines) <= MAX_LINES, f"target line count exceeds max: {entry_id}")
        require(all(line["passes_static_patch_007"] for line in target_lines), f"target layout fails: {entry_id}")
        changed = entry_id in CHANGED_IDS
        require((target != current) == changed, f"change disposition drift: {entry_id}")
        if changed:
            texts[entry_id] = target
        row: dict[str, Any] = {
            "entry_id": entry_id,
            "scene": scene_name(entry_id),
            "changed": changed,
            "strict_predecessor_ko": current,
            "target_ko": target,
            "strict_predecessor_ko_utf16le_sha256": text_hash(current),
            "target_ko_utf16le_sha256": text_hash(target),
            "direct_pc_jp": source_jp,
            "direct_pc_en": source_en,
            "direct_pc_sc": source_sc,
            "direct_pc_tc": source_tc,
            "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
            "direct_pc_en_utf16le_sha256": text_hash(source_en),
            "direct_pc_sc_utf16le_sha256": text_hash(source_sc),
            "direct_pc_tc_utf16le_sha256": text_hash(source_tc),
            "direct_control_signatures": {
                "jp": control_signature(source_jp),
                "en": control_signature(source_en),
                "sc": control_signature(source_sc),
                "tc": control_signature(source_tc),
            },
            "target_control_signature": control_signature(target),
            "strict_ko_matches_direct_jp_protected_signature": True,
            "japanese_source_line_breaks_used": False,
            "jp_lf_policy": "ignored",
            "runtime_tokens": [],
            "runtime_reservations": [],
            "runtime_proven": False,
            "current_manual_line_count": len(current_lines),
            "target_manual_line_count": len(target_lines),
            "current_lines": list(current_lines),
            "target_lines": list(target_lines),
            "current_static_patch_007_passes": all(line["passes_static_patch_007"] for line in current_lines),
            "target_static_patch_007_passes": all(line["passes_static_patch_007"] for line in target_lines),
            "terminator_policy": "UTF-16LE NUL terminator is serialized by rebuild_message_table",
        }
        if changed:
            row["rationale"] = RATIONALES[entry_id]
            row["historical_vs_current"] = historical_evidence(entry_id, historical)
            row["current_quality_conflict_check"] = {
                "status": "PASS",
                "preserved_current_terms": list(CURRENT_QUALITY_PRESERVED[entry_id]),
                "reason": "현재 strict 품질본의 고유명사·문맥을 유지한 채, direct PC 4언어에서 확인되는 누락 의미만 복원했다.",
            }
        else:
            row["rationale"] = "장면 문맥·direct PC 4언어·Static Patch 007 폭을 확인했으나 manual_compact 대상이 아니므로 유지했다."
            row["historical_vs_current"] = None
            row["current_quality_conflict_check"] = {
                "status": "NOT_APPLICABLE",
                "reason": "manual_compact 대상 밖이므로 변경하지 않았다.",
            }
        rows.append(row)

    header, _raw_again, _table_again = parse_table("strict Static007 predecessor", before_event)
    rebuilt_raw = rebuild_message_table(before, texts)
    event = recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("manual compact Static007 output", event)
    require(after_raw == rebuilt_raw, "candidate raw reparse mismatch")
    changed_ids = [index for index, (left, right) in enumerate(zip(before.texts, after.texts)) if left != right]
    require(changed_ids == list(CHANGED_IDS), f"candidate is not exact six-row diff: {changed_ids[:12]}")
    require(all(after.texts[entry_id] == TARGETS[entry_id] for entry_id in CHANGED_IDS), "candidate target text drift")
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "candidate output packed/raw profile drift")

    changed_rows = [row for row in rows if row["changed"]]
    audit = {
        "schema": "nobu16.kr.pc-event-manual-compact-static007-batch01-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "strict_input_only": PREDECESSOR_CANDIDATE_ROOT.relative_to(REPO).as_posix(),
            "only_korean_predecessor_input": True,
            "direct_pc_context_read_only": True,
            "direct_pc_context_languages": ["jp", "en", "sc", "tc"],
            "historical_manual_compact_is_comparison_only": True,
            "switch_korean_used": False,
            "japanese_source_line_breaks_used": False,
            "korean_sentence_shortened_or_deleted": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "network_operation_performed": False,
            "release_published": False,
        },
        "layout_policy": {
            "authority": "F:/Games/NOBU16/AGENTS.md Static Patch 007 baseline",
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "raw_hard_limit_px": RAW_STATIC_PATCH_007_LIMIT_PX,
            "effective_width_hard_limit_px": EFFECTIVE_STATIC_PATCH_007_LIMIT_PX,
            "max_lines": MAX_LINES,
            "draw_font_px": DRAW_FONT_PX,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_width_is_report_only": False,
            "runtime_reservations": {},
        },
        "source_profiles": {
            "strict_predecessor_static007_5777": predecessor_profile,
            "direct_pc_contexts": context_profiles,
            "historical_manual_compact_overlay": historical_profile,
        },
        "predecessor_quality_evidence": {
            "predecessor_audit_schema": predecessor_audit.get("schema"),
            "predecessor_changed_row_ids": predecessor_audit.get("actual_changed_row_ids"),
            "predecessor_static007_profile": predecessor_profile,
        },
        "coverage": {
            "reviewed_scene_batches": {name: list(ids) for name, ids in SCENE_BATCHES.items()},
            "reviewed_row_ids": list(REVIEWED_IDS),
            "reviewed_row_count": len(REVIEWED_IDS),
            "manual_compact_changed_ids": list(CHANGED_IDS),
            "manual_compact_changed_count": len(CHANGED_IDS),
            "retained_context_ids": list(RETAINED_IDS),
            "retained_context_count": len(RETAINED_IDS),
        },
        "output_event_profile": event_profile,
        "actual_changed_row_ids": changed_ids,
        "actual_changed_row_count": len(changed_ids),
        "exact_six_row_diff": changed_rows,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-manual-compact-static007-batch01-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": PREDECESSOR_WORKSTREAM,
            "candidate_relative": (PREDECESSOR_CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
            "profile": predecessor_profile,
            "strict_on_disk": True,
            "only_korean_predecessor_input": True,
        },
        "direct_pc_context_profiles": context_profiles,
        "historical_manual_compact_overlay": historical_profile,
        "changed_row_ids": list(CHANGED_IDS),
        "exact_six_row_diff": True,
        "output": event_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }
    return Bundle(event, audit, manifest, event_profile)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"candidate staging already exists: {staging}")
    staging.mkdir(parents=True)
    try:
        event_path = staging / MSGEV
        event_path.parent.mkdir(parents=True)
        event_path.write_bytes(bundle.event)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> Mapping[str, Any]:
    bundle = bundle or prepare(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "candidate event differs from deterministic build")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": list(CHANGED_IDS),
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_manual_compact_static007_batch01_v1.py",
        WORKSTREAM / "test_pc_event_manual_compact_static007_batch01_v1.py",
    ):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("authoring-check", "profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "authoring-check":
        validate_authored_targets()
        print(json.dumps({entry_id: list(line_metrics(text)) for entry_id, text in TARGETS.items()}, ensure_ascii=False))
        return 0
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        print(write_candidate(prepare(require_output_profile=True)))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = prepare(require_output_profile=True)
    print(json.dumps({"changed_row_ids": bundle.audit["actual_changed_row_ids"], "event_profile": bundle.profile}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
