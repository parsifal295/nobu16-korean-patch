#!/usr/bin/env python3
"""Read-only quality/layout audit for PC PK ending-region event rows 3309–3484.

The current Korean candidate is inspected directly against pristine PC Japanese
and the installed PC EN/SC/TC references.  The script deliberately creates a
ledger/report only: it does not construct an ``msgev.bin`` candidate and it
does not write Steam, Git, release, or network state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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
OUTPUT = PUBLIC / "pc_event_ending_regions_audit.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-ending-regions-audit.v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
START_ID = 3309
END_ID = 3484
TARGET_IDS = tuple(range(START_ID, END_ID + 1))

RUNTIME_FONT_PX = 30
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
MAX_EFFECTIVE_WIDTH_PX = 912
MAX_RAW_WIDTH_PX = 1440
MAX_LINES = 4

PRE_W98_KO_PATH = (
    REPO
    / "tmp"
    / "pc_event_manual_compact_static007_3xxx_runtime_restore_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
CURRENT_KO_PATH = (
    REPO
    / "tmp"
    / "pc_event_gifu_quality_wave98_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
W98_ALLOWED_CHANGE_START_ID = 3287
W98_ALLOWED_CHANGE_END_ID = 3307
DIRECT_PATHS = {
    "jp": Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
        r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals"
        r"\MSG_PK\JP\msgev.bin"
    ),
    "en": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msgev.bin"),
    "sc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msgev.bin"),
    "tc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msgev.bin"),
}

EXPECTED = {
    "current_ko": {
        "packed_sha256": "62C7F55506DB59A43761DDCE07FB5DA4175AD0AC4B68C03507B37AD52E2AEBD3",
        "raw_sha256": "D0FAB9C303F8F456184DCDD89AC929C675D6528080F8C29E419E1249BD9B7408",
        "string_count": 17916,
    },
    "pre_w98_ko": {
        "packed_sha256": "CFF60029741A596F40EA19DF9F05A8FEC53E240EF09C750B732D052195A04D35",
        "raw_sha256": "920373F9AFA47959C291025A3D3230B4064261997090AFC01A1EE57F61153FFB",
        "string_count": 17916,
    },
    "jp": {
        "packed_sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
        "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
        "string_count": 17916,
    },
    "en": {
        "packed_sha256": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
        "raw_sha256": "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911",
        "string_count": 17916,
    },
    "sc": {
        "packed_sha256": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
        "raw_sha256": "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E",
        "string_count": 17916,
    },
    "tc": {
        "packed_sha256": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
        "raw_sha256": "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6",
        "string_count": 17916,
    },
}

ESC = "\x1b"
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z][A-Za-z0-9_]*\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\r|\n")
INTERNAL_KEY_RE = re.compile(r"^event_ending_region_[a-z0-9_]+$")

# These are deliberately limited to wording/semantic corrections that remain
# fully static.  Dynamic-token rows stay in the runtime/UI hold class until
# the token display and its reservation are independently proven.
CORRECTIONS: Mapping[int, Mapping[str, Any]] = {
    3331: {
        "proposed_ko": (
            f"{ESC}CC가미가타{ESC}CZ와 {ESC}CC간토{ESC}CZ를 잇는 "
            f"{ESC}CC도카이도{ESC}CZ 연선에는\n"
            "진취적인 다이묘가 자주 등장해,\n"
            "세력 다툼도 치열했지만……"
        ),
        "reason": (
            "先進的な大名が現れることも多く의 뜻을 보존하면서, "
            "직역투인 ‘나타나는 일도 많아’를 자연스러운 서술로 바로잡는다."
        ),
        "semantic_obligations": [
            "가미가타·간토를 잇는 도카이도 지역",
            "진취적인 다이묘의 빈번한 등장",
            "치열한 세력 다툼",
        ],
    },
    3413: {
        "proposed_ko": (
            "전란에서 벗어난 사람들은 해방감에\n"
            "힘입어, 여러 외국과의 교역에 힘썼고,\n"
            "일본은 큰 경제 발전의 시대를 맞았다."
        ),
        "reason": (
            "諸外国との交易은 국내 여러 나라가 아니라 ‘여러 외국과의 교역’이다. "
            "대상 범위를 분명히 하되 문장 내용은 줄이지 않는다."
        ),
        "semantic_obligations": [
            "전란 종결 뒤의 해방감",
            "여러 외국과의 교역",
            "일본의 큰 경제 발전",
        ],
    },
    3446: {
        "proposed_ko": (
            f"이대로는 끝이 없겠군. {ESC}CC교토{ESC}CZ로 돌아가기\n"
            f"위해…… 여기서 {ESC}CA하루모토{ESC}CZ와 결별하자.\n"
            f"{ESC}CA나가요시{ESC}CZ와 교섭을 진행하라!"
        ),
        "reason": (
            "晴元は切ろう는 하루모토와 관계를 끊자는 정치적 결단이다. "
            "기존 ‘하루모토를 끊는다’의 살해로도 읽힐 수 있는 표현을 ‘결별하자’로 바로잡는다."
        ),
        "semantic_obligations": [
            "교토 귀환 목적",
            "하루모토와의 결별",
            "나가요시와의 교섭 추진",
        ],
    },
    3475: {
        "proposed_ko": (
            "뻔한 꾀병에 걸려들다니.\n"
            "순진하다고 말할 수는 있어도, 전국시대에는\n"
            "말 그대로 목숨을 잃게 만드는 약점이다……"
        ),
        "reason": (
            "素直とは言えるが의 양보·대조를 한국어 문장으로 완결한다. "
            "순진함과 전국시대의 치명적 약점이라는 두 의미를 모두 보존한다."
        ),
        "semantic_obligations": [
            "뻔한 꾀병에 속음",
            "순진함으로는 말할 수 있음",
            "전국시대에서는 목숨을 잃게 할 약점",
        ],
    },
    3477: {
        "proposed_ko": (
            f"없다. 전에도 말했을 텐데.\n"
            f"내가 노리는 것은 {ESC}CB오다 가문{ESC}CZ이 아니다.\n"
            "천하다!"
        ),
        "reason": (
            "俺が見ているのは…天下だ의 ‘보는’은 단순 시각이 아니라 지향/야망이다. "
            "‘노리는 것’으로 화자의 천하 쟁취 의지를 자연스럽고 정확하게 살린다."
        ),
        "semantic_obligations": [
            "후회가 없다는 단언",
            "오다 가문만이 목표가 아님",
            "천하가 목표임",
        ],
    },
    3479: {
        "proposed_ko": (
            f"({ESC}CA노부카쓰{ESC}CZ 님을 죽음으로 몰아넣은 것은\n"
            f"다른 누구도 아닌 이 {ESC}CA가쓰이에{ESC}CZ다……\n"
            "언젠가 반드시 그 대가를 치러야겠지.)"
        ),
        "reason": (
            "일본어 원문의 행두 들여쓰기가 한국어 대사에 그대로 남아 있다. "
            "괄호 속 독백의 세 문장·색상 태그·의미를 그대로 두고 불필요한 행두 공백만 제거한다."
        ),
        "semantic_obligations": [
            "노부카쓰를 죽음으로 몰아넣은 주체가 가쓰이에임",
            "훗날 대가를 치러야 함",
            "괄호 독백 형식 유지",
        ],
    },
}


class AuditError(RuntimeError):
    """Raised for source, control-code, or deterministic-report drift."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_digest(value: str) -> str:
    return digest(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def path_label(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return str(path)


def load_table(path: Path, expected: Mapping[str, Any], label: str) -> tuple[dict[str, Any], tuple[str, ...]]:
    require(path.is_file(), f"missing {label}: {path}")
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(rebuild_message_table(table, table.texts) == raw, f"{label}: message-table round trip differs")
    profile = {
        "path": path_label(path),
        "packed_size": len(packed),
        "packed_sha256": digest(packed),
        "raw_size": len(raw),
        "raw_sha256": digest(raw),
        "string_count": len(table.texts),
    }
    for key, expected_value in expected.items():
        require(profile[key] == expected_value, f"{label}: {key} drift")
    return profile, tuple(table.texts)


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


def control_signature(value: str) -> dict[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(value))
    printf_offsets = {match.start() for match in printf_matches}
    other_controls: list[str] = []
    pua: list[str] = []
    for offset, character in enumerate(value):
        if character in "\r\n" or character == ESC:
            continue
        if unicodedata.category(character) == "Cc":
            other_controls.append(f"U+{ord(character):04X}")
        if 0xE000 <= ord(character) <= 0xF8FF:
            pua.append(f"U+{ord(character):04X}")
    return {
        "esc_tags": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1 for offset, character in enumerate(value) if character == "%" and offset not in printf_offsets
        ),
        "other_c0_controls": other_controls,
        "pua_codepoints": pua,
        "terminator_nul_count": value.count("\x00"),
    }


def assert_colour_layout(value: str, entry_id: int) -> None:
    inside = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == ESC:
            tag = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(tag) is not None, f"{entry_id}: malformed ESC tag {tag!r}")
            if tag == f"{ESC}CZ":
                require(inside, f"{entry_id}: unpaired colour close")
                inside = False
            else:
                require(not inside, f"{entry_id}: nested colour span")
                inside = True
            cursor += 3
            continue
        require(not (inside and value[cursor] in "\r\n"), f"{entry_id}: LF inside colour span")
        cursor += 1
    require(not inside, f"{entry_id}: unterminated colour span")


def line_metrics(value: str, entry_id: int, runtime_tokens: Sequence[str]) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    for line_number, encoded_line in enumerate(normalize_linebreaks(value).split("\n"), 1):
        assert_colour_layout(encoded_line, entry_id)
        display_string = ESC_RE.sub("", encoded_line)
        literal_string = RUNTIME_RE.sub("", display_string)
        full_count = sum(is_full_width_visible(character) for character in literal_string)
        half_count = len(literal_string) - full_count
        raw_width = full_count * RAW_FULL_WIDTH_PX + half_count * RAW_HALF_WIDTH_PX
        effective_width = math.ceil(raw_width * RUNTIME_FONT_PX / RAW_FULL_WIDTH_PX)
        lines.append(
            {
                "line_number": line_number,
                "encoded_string": encoded_line,
                "display_string": display_string,
                "measurement_visible_string": literal_string,
                "runtime_tokens_removed_for_literal_measurement": bool(runtime_tokens),
                "raw_g1n_width_px": raw_width,
                "effective_width_px": effective_width,
                "full_width_character_count": full_count,
                "half_width_character_count": half_count,
                "exceeds_912px": effective_width > MAX_EFFECTIVE_WIDTH_PX,
            }
        )
    return lines


def static_layout(value: str, entry_id: int) -> dict[str, Any]:
    signature = control_signature(value)
    tokens = signature["runtime_tokens"]
    lines = line_metrics(value, entry_id, tokens)
    layout = {
        "line_count": len(lines),
        "max_lines": MAX_LINES,
        "runtime_tokens": tokens,
        "runtime_token_reservation_applied": False,
        "lines": lines,
    }
    if tokens:
        require(1 <= len(lines) <= MAX_LINES, f"{entry_id}: source has more than four manual lines")
        layout.update(
            {
                "measurement_status": "runtime_or_ui_hold_literal_only",
                "runtime_display_proven": False,
                "runtime_width_reservation_proven": False,
                "all_lines_pass_static_patch_007": None,
                "reason": (
                    "Runtime token spelling is preserved but this audit has no token-display route or "
                    "full-name reservation proof; literal-only widths are informational, not a pass claim."
                ),
            }
        )
        return layout
    require(1 <= len(lines) <= MAX_LINES, f"{entry_id}: static text has invalid line count")
    require(not any(line["exceeds_912px"] for line in lines), f"{entry_id}: static line exceeds 912px")
    layout.update(
        {
            "measurement_status": "static_patch_007_pass",
            "runtime_display_proven": True,
            "runtime_width_reservation_proven": True,
            "all_lines_pass_static_patch_007": True,
        }
    )
    return layout


def source_summary(profile: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: profile[key]
        for key in ("path", "packed_size", "packed_sha256", "raw_size", "raw_sha256", "string_count")
    }


def direct_source_hashes(sources: Mapping[str, Sequence[str]], entry_id: int) -> dict[str, str]:
    return {language: text_digest(strings[entry_id]) for language, strings in sources.items()}


def build_bundle() -> tuple[dict[str, Any], dict[str, Any]]:
    current_profile, current = load_table(CURRENT_KO_PATH, EXPECTED["current_ko"], "current Korean strict input")
    pre_w98_profile, pre_w98 = load_table(PRE_W98_KO_PATH, EXPECTED["pre_w98_ko"], "pre-W98 Korean strict input")
    profiles: dict[str, Mapping[str, Any]] = {
        "current_ko_w98": current_profile,
        "pre_w98_ko_for_nonoverlap_check": pre_w98_profile,
    }
    sources: dict[str, Sequence[str]] = {}
    for language, path in DIRECT_PATHS.items():
        profile, strings = load_table(path, EXPECTED[language], f"direct PC {language.upper()}")
        profiles[language] = profile
        sources[language] = strings
    require(
        len(pre_w98) == len(current) and all(len(strings) == len(current) for strings in sources.values()),
        "source message-table count mismatch",
    )
    require(set(CORRECTIONS).issubset(TARGET_IDS), "correction target outside audit range")
    w98_changed_ids = [
        entry_id
        for entry_id, (before, after) in enumerate(zip(pre_w98, current))
        if before != after
    ]
    require(w98_changed_ids, "W98 rebased input has no changed rows")
    require(
        all(W98_ALLOWED_CHANGE_START_ID <= entry_id <= W98_ALLOWED_CHANGE_END_ID for entry_id in w98_changed_ids),
        f"W98 change escaped allowed range {W98_ALLOWED_CHANGE_START_ID}–{W98_ALLOWED_CHANGE_END_ID}: {w98_changed_ids}",
    )
    require(
        all(current[entry_id] == pre_w98[entry_id] for entry_id in TARGET_IDS),
        "W98 changed a 3309–3484 ending-region audit row",
    )

    entries: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    static_line_metrics: list[Mapping[str, Any]] = []
    runtime_hold_ids: list[int] = []
    internal_key_hold_ids: list[int] = []
    correction_ids: list[int] = []

    for entry_id in TARGET_IDS:
        current_ko = current[entry_id]
        assert_colour_layout(current_ko, entry_id)
        signature = control_signature(current_ko)
        is_internal_key = INTERNAL_KEY_RE.fullmatch(current_ko) is not None
        if entry_id in CORRECTIONS:
            classification = "static_high_confidence_correction"
        elif is_internal_key or signature["runtime_tokens"]:
            classification = "runtime_or_ui_hold"
        else:
            classification = "reviewed_preserve"
        counts[classification] += 1

        entry: dict[str, Any] = {
            "entry_id": entry_id,
            "classification": classification,
            "current_ko": current_ko,
            "current_ko_utf16le_sha256": text_digest(current_ko),
            "direct_pc_source_utf16le_sha256": direct_source_hashes(sources, entry_id),
            "control_signature": signature,
            "review_policy": {
                "manual_compact_history_used_as_quality_authority": False,
                "direct_pc_jp_en_sc_tc_compared": True,
                "japanese_source_linebreaks_used_as_layout_authority": False,
                "korean_linebreaks_are_manual_semantic_boundaries": True,
                "sentence_shortening_or_deletion_allowed": False,
                "automatic_linebreak_stripping_forbidden": True,
                "max_lines": MAX_LINES,
            },
        }
        if is_internal_key:
            internal_key_hold_ids.append(entry_id)
            entry.update(
                {
                    "review_judgement": "이벤트 식별 키이며 다이얼로그 표시 문자열이 아니다.",
                    "layout": {
                        "measurement_status": "not_applicable_internal_event_key",
                        "line_count": 0,
                        "runtime_display_proven": False,
                        "all_lines_pass_static_patch_007": None,
                    },
                }
            )
        else:
            layout = static_layout(current_ko, entry_id)
            entry["layout"] = layout
            if signature["runtime_tokens"]:
                runtime_hold_ids.append(entry_id)
                entry["review_judgement"] = (
                    "동적 토큰의 실제 표시 문자열과 예약 폭이 이 범위에서 검증되지 않아, "
                    "문구·개행의 수정 판단을 보류한다."
                )
            elif entry_id in CORRECTIONS:
                proposal = CORRECTIONS[entry_id]
                proposed = str(proposal["proposed_ko"])
                assert_colour_layout(proposed, entry_id)
                proposed_signature = control_signature(proposed)
                require(
                    proposed_signature == signature,
                    f"{entry_id}: proposed control/token signature drift",
                )
                proposed_layout = static_layout(proposed, entry_id)
                require(
                    proposed_layout["all_lines_pass_static_patch_007"] is True,
                    f"{entry_id}: proposed layout not Static Patch 007-safe",
                )
                correction_ids.append(entry_id)
                static_line_metrics.extend(proposed_layout["lines"])
                entry.update(
                    {
                        "review_judgement": str(proposal["reason"]),
                        "correction": {
                            "proposed_ko": proposed,
                            "proposed_ko_utf16le_sha256": text_digest(proposed),
                            "semantic_obligations_preserved": list(proposal["semantic_obligations"]),
                            "direct_pc_sources_for_meaning_review": {
                                language: strings[entry_id] for language, strings in sources.items()
                            },
                            "current_layout": layout,
                            "proposed_layout": proposed_layout,
                            "control_signature_preserved": True,
                            "sentence_shortened_or_deleted": False,
                            "japanese_linebreaks_copied": False,
                            "tag_internal_linebreak_inserted": False,
                        },
                    }
                )
            else:
                static_line_metrics.extend(layout["lines"])
                entry["review_judgement"] = (
                    "원문 의미, 제어 코드, 한국어 문장 흐름 및 Static Patch 007 정적 폭을 재검토했으며 "
                    "현 문구를 보존한다."
                )
        entries.append(entry)

    require(len(entries) == len(TARGET_IDS), "entry accounting drift")
    require(correction_ids == sorted(CORRECTIONS), "correction accounting drift")
    require(not set(correction_ids) & set(runtime_hold_ids), "dynamic row placed in static correction scope")
    require(all(entry["classification"] in counts for entry in entries), "classification accounting drift")
    require(
        all(
            entry["layout"]["all_lines_pass_static_patch_007"] is not False
            for entry in entries
        ),
        "unexpected static layout failure",
    )

    max_raw = max(line["raw_g1n_width_px"] for line in static_line_metrics)
    max_effective = max(line["effective_width_px"] for line in static_line_metrics)
    max_line_count = max(
        entry["layout"]["line_count"]
        for entry in entries
        if entry["layout"]["measurement_status"] != "not_applicable_internal_event_key"
    )
    payload = {
        "schema": SCHEMA,
        "scope": {
            "resource": RESOURCE,
            "start_id": START_ID,
            "end_id": END_ID,
            "target_ids": list(TARGET_IDS),
            "target_row_count": len(TARGET_IDS),
            "strict_input_rebased_to": "pc_event_gifu_quality_wave98_v1/candidate-final",
            "w98_allowed_change_start_id": W98_ALLOWED_CHANGE_START_ID,
            "w98_allowed_change_end_id": W98_ALLOWED_CHANGE_END_ID,
            "w98_changed_ids": w98_changed_ids,
            "w98_target_rows_identical_to_pre_w98": True,
            "candidate_binary_created": False,
            "steam_files_written": False,
            "git_or_release_actions_performed": False,
            "network_operation_performed": False,
        },
        "layout_baseline": {
            "authority": "Static Patch 007 verified PK event-dialogue layout",
            "runtime_font_px": RUNTIME_FONT_PX,
            "runtime_usable_line_width_px": MAX_EFFECTIVE_WIDTH_PX,
            "max_lines": MAX_LINES,
            "raw_g1n_full_width_advance_px": RAW_FULL_WIDTH_PX,
            "raw_g1n_half_width_advance_px": RAW_HALF_WIDTH_PX,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "raw_g1n_pass_limit_px": MAX_RAW_WIDTH_PX,
            "effective_width_pass_limit_px": MAX_EFFECTIVE_WIDTH_PX,
            "base_ev_strdata_rule_inherited": False,
            "runtime_token_policy": (
                "A row with a runtime token is not passed merely from its literal width. "
                "Its token route and scaled reservation must be proven in a later dedicated audit."
            ),
        },
        "classification_policy": {
            "reviewed_preserve": "정적 표시 행으로서 직접 원문 대조와 현재 30px/4줄 폭 검토를 통과했다.",
            "static_high_confidence_correction": "동적 토큰이 없는 행에서 원문 의미 또는 한국어 품질 문제를 확인했고, 완전한 보존형 수정안을 제시했다.",
            "runtime_or_ui_hold": "이벤트 키이거나 런타임 토큰의 실제 표시 폭·형태가 미검증이라 현재 단계에서 문구 수정 후보로 승격하지 않는다.",
        },
        "sources": {name: source_summary(profile) for name, profile in profiles.items()},
        "counts": {
            "classification": dict(sorted(counts.items())),
            "static_high_confidence_correction_ids": correction_ids,
            "runtime_token_hold_ids": runtime_hold_ids,
            "internal_event_key_hold_ids": internal_key_hold_ids,
            "static_or_proposed_max_raw_g1n_width_px": max_raw,
            "static_or_proposed_max_effective_width_px": max_effective,
            "max_manual_line_count": max_line_count,
            "static_or_proposed_lines_over_912px": 0,
            "static_or_proposed_rows_over_four_lines": 0,
            "sentence_shortened_or_deleted": False,
        },
        "entries": entries,
        "safety": {
            "candidate_binary_written": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "release_published": False,
            "network_operation_performed": False,
        },
    }
    validation = {
        "schema": "nobu16.kr.pc-event-ending-regions-audit-validation.v1",
        "status": "PASS",
        "review_output": path_label(OUTPUT),
        "target_row_count": len(TARGET_IDS),
        "classification": dict(sorted(counts.items())),
        "correction_ids": correction_ids,
        "w98_changed_ids": w98_changed_ids,
        "w98_target_rows_identical_to_pre_w98": True,
        "runtime_token_hold_count": len(runtime_hold_ids),
        "internal_event_key_hold_count": len(internal_key_hold_ids),
        "max_raw_g1n_width_px": max_raw,
        "max_effective_width_px": max_effective,
        "max_manual_line_count": max_line_count,
        "candidate_binary_created": False,
        "steam_files_written": False,
        "git_or_release_actions_performed": False,
        "network_operation_performed": False,
    }
    return payload, validation


def write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def source_whitespace_check() -> None:
    for number, line in enumerate(SCRIPT.read_text(encoding="utf-8").splitlines(), 1):
        require(line == line.rstrip(), f"trailing whitespace at {SCRIPT.name}:{number}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "summary"))
    args = parser.parse_args(argv)
    source_whitespace_check()
    payload, validation = build_bundle()
    if args.command == "build":
        write_atomic(OUTPUT, canonical_json(payload))
        expected_validation = {**validation, "review_output_sha256": digest(OUTPUT.read_bytes())}
        write_atomic(VALIDATION, canonical_json(expected_validation))
        print(json.dumps(expected_validation, ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "verify":
        require(OUTPUT.is_file(), f"missing review output: {OUTPUT}")
        require(VALIDATION.is_file(), f"missing validation output: {VALIDATION}")
        require(OUTPUT.read_bytes() == canonical_json(payload), "review JSON differs from deterministic rebuild")
        expected_validation = {**validation, "review_output_sha256": digest(OUTPUT.read_bytes())}
        require(VALIDATION.read_bytes() == canonical_json(expected_validation), "validation JSON differs from deterministic rebuild")
        print(json.dumps(expected_validation, ensure_ascii=False, sort_keys=True))
        return 0
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
