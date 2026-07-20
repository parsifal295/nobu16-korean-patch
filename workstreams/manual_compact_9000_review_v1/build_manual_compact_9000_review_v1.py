#!/usr/bin/env python3
"""Read-only semantic restoration review for 9xxx manual event compactions.

The historical ``manual_compact_korean_layout`` overlay is not treated as a
semantic source.  Every selected entry is compared against the full Korean
backup and direct PC JP/EN/SC/TC witnesses.  This program produces only a
review manifest: it neither creates a message binary nor writes to Steam,
Git, a release, or the network.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PUBLIC = WORKSTREAM / "public"
OUTPUT = PUBLIC / "manual_compact_9000_review.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.manual-compact-9000-review.v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
MIN_ID = 9000
MAX_ID = 9999
EXPECTED_ROW_COUNT = 283

# Static Patch 007 is authoritative for PK event dialogue.  ``1440`` is the
# raw-G1N equivalent of 912 effective pixels at the verified 30px runtime
# layout; the obsolete raw-960 / effective-600 gate is never used here.
RUNTIME_FONT_PX = 30
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
MAX_RAW_WIDTH_PX = 1440
MAX_EFFECTIVE_WIDTH_PX = 912
MAX_LINES = 4

CURRENT_PATH = (
    REPO
    / "tmp"
    / "pc_event_manual_compact_static007_6000_7999_restore_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
CURRENT_EXPECTED = {
    "packed_sha256": "D99390D4F2D7D469C105439A11476B01830F5E96287B278C164045CBC7BA3547",
    "raw_sha256": "567C8C3C2F371E27CBE6FFEAB9F8F3EE7F6D6F13A2C179682A5A7F7D3F35780F",
}
DIRECT_JP_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals"
    r"\MSG_PK\JP\msgev.bin"
)
DIRECT_EN_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msgev.bin")
DIRECT_SC_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msgev.bin")
DIRECT_TC_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msgev.bin")
LEGACY_KO_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-v0.10.0-original-font-rollback-v1"
    r"\originals\MSG_PK\JP\msgev.bin"
)
HISTORICAL_MANIFEST = (
    REPO
    / "workstreams"
    / "steam_jp_msgev_full_layout_v2"
    / "public"
    / "msgev_ko_steam_jp_full_layout.v2.json"
)
RESERVATION_MANIFEST = (
    REPO
    / "workstreams"
    / "steam_jp_msgev_full_layout_v2"
    / "public"
    / "runtime_token_reservations.v1.json"
)
INVENTORY_MANIFEST = (
    REPO
    / "workstreams"
    / "pc_event_manual_compact_korean_layout_inventory_v1"
    / "public"
    / "msgev_manual_compact_korean_layout_inventory.v1.json"
)
SPECIAL_REFLOW_REVIEW = (
    REPO / "workstreams" / "manual_compact_reflow_9000_11000_v1" / "review.v1.json"
)

ESC = "\x1b"
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
VISIBLE_UNIT_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]|[가-힣A-Za-z0-9]+|[^\s]")

# Only these rows have text changed after the historical manual compaction.
# They are judged independently below; reverting all nine to the old backup
# would regress corrected names or more complete later wording.
CURRENT_DIFF_IDS = (9075, 9081, 9148, 9337, 9470, 9491, 9540, 9753, 9998)

# The prior review authoritatively supplied source-complete Korean semantic
# reflows for legacy lines that exceeded Static Patch 007.  Re-read and
# re-measure them against the final strict predecessor rather than recreating
# or blindly replacing their wording.
SPECIAL_REFLOW_IDS = (
    9049, 9083, 9140, 9141, 9169, 9228, 9326, 9338, 9340, 9523, 9540,
    9541, 9624, 9683,
)

# Later revisions that are not safely restored as a wholesale old-backup
# string.  Each keeps every proposition in direct JP and is split only at
# Korean sentence / clause boundaries.  No shortening or deleted clause is
# introduced here.
QUALITY_OVERRIDES: dict[int, dict[str, str]] = {
    9075: {
        "strategy": "preserve_current_source_complete_quality_revision",
        "judgement": (
            "Keep the later complete account: repeated Nagashima uprisings, "
            "the surrendered Ikko force being deceived and killed, the remaining "
            "people being burned, and the cruelty of the method all remain explicit."
        ),
    },
    9081: {
        "strategy": "reconcile_current_with_source_complete_metaphor_restoration",
        "judgement": (
            "Restore the source's mikoshi (가마) metaphor and the fact that the "
            "speaker has built power in Kinai through the shogun's authority; retain "
            "the complete threat to pull down an uncooperative mikoshi."
        ),
        "text": (
            f"우리는 쇼군의 권위를 가마 삼아 {ESC}CC기나이{ESC}CZ에\n"
            "세력을 쌓아 왔다. 우리의 뜻에 따르지 않는\n"
            "가마라면… 차라리 끌어내려 버리자."
        ),
    },
    9148: {
        "strategy": "reconcile_current_with_corrected_name_and_full_kanji_clause",
        "judgement": (
            "Retain the later corrected reading 야스히데, while restoring that the "
            "Gamō clan had used the Hide character for generations before the rename "
            "to Ujisato and the ensuing warrior's birth."
        ),
        "text": (
            f"이리하여 {ESC}CA야스히데{ESC}CZ는 {ESC}CB가모가{ESC}CZ 대대로 써 온\n"
            f"'히데' 자를 버리고 {ESC}CA우지사토{ESC}CZ로 개명했다.\n"
            f"전국 무장 '{ESC}CA가모 우지사토{ESC}CZ'의 탄생이다."
        ),
    },
    9337: {
        "strategy": "restore_legacy_source_complete_korean_with_semantic_boundaries",
        "judgement": (
            "Restore the full origin, Echizen daimyō role, the Yoshiaaki-as-palanquin "
            "metaphor, jealousy at losing it, and especially hostile conclusion; the "
            "later shortened '곁자리' wording is not retained."
        ),
        "text": (
            f"그리고 {ESC}CA오다{ESC}CZ와 같은 {ESC}CA시바{ESC}CZ 가신이라는 출신을 지닌\n"
            f"{ESC}CC에치젠{ESC}CZ의 다이묘 {ESC}CA아사쿠라 요시카게{ESC}CZ는, {ESC}CA요시아키{ESC}CZ라는 가마를\n"
            "빼앗긴 질시도 있어, 유달리 적대하게 된다…"
        ),
    },
    9470: {
        "strategy": "reconcile_current_with_corrected_name_and_full_causality",
        "judgement": (
            "Retain the later corrected Toki Yorinori name while restoring the timing "
            "after Miyoshino's birth, the first-son relationship, and the causal rumor "
            "that Yorinori was Takamasa's biological father."
        ),
        "text": (
            f"{ESC}CA미요시노{ESC}CZ가 그 뒤 얼마 안 되어 {ESC}CA도시마사{ESC}CZ의 장남 {ESC}CA다카마사{ESC}CZ를\n"
            f"낳았기에, {ESC}CA다카마사{ESC}CZ의 친아버지가\n"
            f"{ESC}CA도키 요리노리{ESC}CZ라는 소문이 나돌았다."
        ),
    },
    9491: {
        "strategy": "reconcile_current_with_corrected_name_and_full_status_clause",
        "judgement": (
            "Retain the later corrected Jisshinsai reading while restoring the Shimazu "
            "house-elder service, Ijuin household's current head, priesthood during the "
            "surrender talks, and the Kōkan religious name."
        ),
        "text": (
            f"하지만 {ESC}CA짓신사이{ESC}CZ 이래 {ESC}CB시마즈{ESC}CZ의 가로를 지낸\n"
            f"{ESC}CB이주인가{ESC}CZ의 당대 당주 {ESC}CA다다무네{ESC}CZ는 이미\n"
            f"항복 교섭 때 출가하여 {ESC}CA고칸{ESC}CZ이라 칭하고 있었다."
        ),
    },
    9753: {
        "strategy": "restore_legacy_source_complete_korean_with_explicit_object",
        "judgement": (
            "Restore the many prior battles, the fated arch-enemy, and the explicit "
            "object '그 힘' that is steadily being worn down; the later compact line "
            "was needlessly less specific."
        ),
        "text": (
            f"{ESC}CA[bm1251]{ESC}CZ와 수많은 싸움을 벌여 온\n"
            f"숙명의 대적 {ESC}CA[b1448]{ESC}CZ―\n"
            f"{ESC}CA[bm1251]{ESC}CZ는 착실히 그 힘을 깎아 나갔다."
        ),
    },
    9998: {
        "strategy": "restore_legacy_source_complete_korean_with_next_battlefield",
        "judgement": (
            "Restore the possessive strategy and exertion clauses, the clear Western "
            "Army advantage in Hokuriku, and the next-battlefield framing before Mino "
            "and Ōgaki Castle."
        ),
        "text": (
            f"{ESC}CA오타니 요시쓰구{ESC}CZ의 계략과 {ESC}CA니와 나가시게{ESC}CZ의 분전으로\n"
            f"{ESC}CC서군{ESC}CZ은 {ESC}CB호쿠리쿠{ESC}CZ에서 확실한 우세를 점했다.\n"
            f"{ESC}CA요시쓰구{ESC}CZ는 다음 전장인 {ESC}CC미노{ESC}CZ·{ESC}CC오가키성{ESC}CZ으로 향했다."
        ),
    },
}

# The tokens below resolve to one named officer in this scene's pinned table.
# The old Korean surface had an objectively wrong postposition for that
# known display.  Correct only these exact rows; do not infer postpositions
# globally for runtime tokens.
STATIC_TOKEN_PARTICLE_FIXES: dict[int, dict[str, str]] = {
    9327: {
        "strategy": "restore_full_legacy_korean_with_scene_limited_token_particle_fix",
        "judgement": "Restore the full chronology and audience clause, correcting the observed scene display '사이토 도산' to the consonant-final topic particle '은'.",
        "text": (
            "덴분 22년(1553년)―\n"
            f"{ESC}CC미노{ESC}CZ의 다이묘 {ESC}CA[b924]{ESC}CZ은, 멍청이라 소문난 사위\n"
            f"{ESC}CA오다 노부나가{ESC}CZ에게 흥미를 품고 회견을 고대하고 있었다."
        ),
    },
    9559: {
        "strategy": "restore_full_legacy_korean_with_scene_limited_token_particle_fix",
        "judgement": "Restore the alliance-and-kinship setup and Suruga attack, correcting the observed vowel-final display '다케다 하루노부' to subject particle '가'.",
        "text": (
            "일찍이 맹약을 맺고, 인척이기도 했을\n"
            f"{ESC}CA[b1251]{ESC}CZ가 손바닥 뒤집듯 배신하여,\n"
            f"{ESC}CC스루가{ESC}CZ로 쳐들어왔기 때문이리라…"
        ),
    },
    9567: {
        "strategy": "restore_full_legacy_korean_with_scene_limited_token_particle_fix",
        "judgement": "Keep the warning and marital relation, correcting the observed vowel-final display '다케다 하루노부' from topic particle '은' to '는'.",
        "text": (
            f"당황하지 마라. {ESC}CA[bm1251]{ESC}CZ는 호락호락한 사내가 아니다.\n"
            f"게다가 그대의 아내도 {ESC}CA[bm1251]{ESC}CZ의 딸이 아닌가."
        ),
    },
    9571: {
        "strategy": "restore_full_legacy_korean_with_scene_limited_token_particle_fix",
        "judgement": "Keep the Takeda preparation and two-front warning, correcting observed vowel-final '나가오 가게토라' from connective '과' to '와'.",
        "text": (
            f"{ESC}CB다케다{ESC}CZ를 적으로 돌리려면,\n"
            "그에 상응하는 준비가 필요하다.\n"
            f"{ESC}CB[bs1448]{ESC}CZ와 {ESC}CB다케다{ESC}CZ…양쪽을 상대하기는 어려운 일이니."
        ),
    },
    9589: {
        "strategy": "restore_full_legacy_korean_with_scene_limited_token_particle_fix",
        "judgement": "Keep the Kawagoe victory, Kantō unification, and two rivals, correcting observed vowel-final '다케다 하루노부' from connective '과' to '와'.",
        "text": (
            f"가와고에 합전에서 고가 구보와 {ESC}CB양 우에스기{ESC}CZ에 쾌승하고\n"
            f"{ESC}CC간토{ESC}CZ를 아우르며 {ESC}CA[b1448]{ESC}CZ와 {ESC}CA[b1251]{ESC}CZ와\n"
            f"대치한 사가미의 웅걸 {ESC}CA호조 우지야스{ESC}CZ."
        ),
    },
    9754: {
        "strategy": "restore_full_legacy_korean_with_scene_limited_token_particle_fix",
        "judgement": "Keep the final-castle capture narrative, correcting observed vowel-final '나가오 가게토라' from subject particle '이' to '가'.",
        "text": (
            f"그리고, 마지막 성까지 몰린 {ESC}CA[bm1448]{ESC}CZ가\n"
            f"지금, {ESC}CA[bm1251]{ESC}CZ 앞에 사로잡힌 모습으로\n"
            "나타난 것이다…"
        ),
    },
}

# These three legacy strings are source-complete, but become too wide only
# after the required conservative runtime-name reservation is applied.  Their
# wording is unchanged; only Korean semantic boundaries are moved to four
# lines.  They are deliberately separate from later-current quality changes.
RUNTIME_RESERVATION_REFLOWS: dict[int, dict[str, str]] = {
    9297: {
        "strategy": "reflow_full_legacy_korean_for_runtime_reservation",
        "judgement": (
            "Keep the expulsion from Shinano, escape to Echigo, reliance on the named "
            "ally, and Katsurao Castle recapture attempt.  Split before the reserved "
            "ally name so the conservative token width remains below raw 1440."
        ),
        "text": (
            f"일찍이 {ESC}CA[b1251]{ESC}CZ에게 {ESC}CC시나노{ESC}CZ에서 쫓겨나\n"
            f"{ESC}CC에치고{ESC}CZ로 달아난 {ESC}CA무라카미 요시키요{ESC}CZ는\n"
            f"{ESC}CA[b1448]{ESC}CZ에게 의지하여,\n"
            f"{ESC}CC가쓰라오성{ESC}CZ 탈환을 시도했다."
        ),
    },
    9298: {
        "strategy": "reflow_full_legacy_korean_for_runtime_reservation",
        "judgement": (
            "Keep the campaign to repel the Murakami force in North Shinano, "
            "Yoshikiyo's second flight to Echigo, and the warning that the episode "
            "did not end there.  Split the token-bearing opening at its clause boundary."
        ),
        "text": (
            f"{ESC}CA[bm1251]{ESC}CZ는 {ESC}CB무라카미 세력{ESC}CZ을 물리치고자\n"
            f"{ESC}CC기타시나노{ESC}CZ로 출진.\n"
            f"패한 {ESC}CA요시키요{ESC}CZ는 다시 {ESC}CC에치고{ESC}CZ로 달아났으나,\n"
            "이번에는 그것으로 끝나지 않았다."
        ),
    },
    9333: {
        "strategy": "reflow_full_legacy_korean_for_runtime_reservation",
        "judgement": (
            "Keep the turn to the eastern provinces, the planned mountain crossing to "
            "inherit the Kantō Kanrei post, and the determined Hōjō–Takeda resistance. "
            "The reserved token is isolated at a Korean clause boundary."
        ),
        "text": (
            f"눈을 {ESC}CC동국{ESC}CZ으로 돌리면, 간토 간레이직을 잇고자\n"
            f"산을 넘을 것을 기약하는 {ESC}CA[b1448]{ESC}CZ에 맞서,\n"
            f"단호히 막아 내려는 {ESC}CB호조{ESC}CZ·{ESC}CB다케다{ESC}CZ 두 영웅이\n"
            "이를 갈고 있었다."
        ),
    },
}


class ReviewError(RuntimeError):
    """Raised when a pinned source or review invariant drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_sha256(value: str) -> str:
    return sha256(value.encode("utf-16-le"))


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def profile(path: Path) -> tuple[dict[str, Any], tuple[str, ...]]:
    require(path.is_file(), f"missing message source: {path}")
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(rebuild_message_table(table, table.texts) == raw, f"message-table round trip differs: {path}")
    return ({
        "path": str(path),
        "packed_size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "string_count": len(table.texts),
    }, table.texts)


def normalize_linebreaks(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def normalize_legacy_layout(value: str) -> str:
    return "\n".join(line.lstrip(" \u3000") for line in normalize_linebreaks(value).split("\n"))


def is_full_width_visible(character: str) -> bool:
    point = ord(character)
    return (
        0x1100 <= point <= 0x11FF or 0x3130 <= point <= 0x318F
        or 0x3040 <= point <= 0x30FF or 0x3400 <= point <= 0x4DBF
        or 0x4E00 <= point <= 0x9FFF or 0xAC00 <= point <= 0xD7A3
        or 0xA960 <= point <= 0xA97F or 0xD7B0 <= point <= 0xD7FF
    )


def assert_colour_tags(value: str, entry_id: int) -> None:
    in_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == ESC:
            token = value[cursor:cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"{entry_id}: malformed ESC tag {token!r}")
            if token == f"{ESC}CZ":
                require(in_span, f"{entry_id}: unmatched color close")
                in_span = False
            else:
                require(not in_span, f"{entry_id}: nested color span")
                in_span = True
            cursor += 3
        else:
            require(not (in_span and value[cursor] in "\r\n"), f"{entry_id}: line break inside color tag")
            cursor += 1
    require(not in_span, f"{entry_id}: unterminated color span")


def control_signature(value: str) -> dict[str, Any]:
    assert_colour_tags(value, -1)
    return {
        "esc_tokens": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "terminator_nul_count": value.count("\x00"),
        "other_control_codepoints": [
            f"U+{ord(character):04X}" for character in value
            if ord(character) < 0x20 and character not in {"\x00", "\n", "\r", ESC}
        ],
        "line_break_inside_tag": False,
    }


def visible_units(value: str) -> list[str]:
    return VISIBLE_UNIT_RE.findall(ESC_RE.sub("", value))


def reintroduced_surface_units(before: str, after: str) -> list[str]:
    result: list[str] = []
    for operation, _a1, _a2, b1, b2 in difflib.SequenceMatcher(
        a=visible_units(before), b=visible_units(after)
    ).get_opcodes():
        if operation in {"insert", "replace"}:
            for unit in visible_units(after)[b1:b2]:
                if unit not in result:
                    result.append(unit)
    return result[:96]


def layout_lines(
    entry_id: int,
    target: str,
    names: tuple[str, ...],
    reservations: dict[str, Any],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line_number, encoded_line in enumerate(normalize_linebreaks(target).split("\n"), 1):
        visible_template = ESC_RE.sub("", encoded_line)
        runtime_items: list[dict[str, Any]] = []

        def render_runtime(match: re.Match[str]) -> str:
            token = match.group(0)
            number = int(re.search(r"(\d+)\]$", token).group(1))
            require(0 <= number < len(names), f"{entry_id}: runtime token out of range {token}")
            reservation = reservations.get(token)
            require(isinstance(reservation, dict), f"{entry_id}: runtime reservation missing for {token}")
            display = ESC_RE.sub("", normalize_linebreaks(names[number])).replace("\n", " ")
            display_full = sum(is_full_width_visible(character) for character in display)
            runtime_items.append({
                "token": token,
                "source_name_id": number,
                "display_string": display,
                "display_full_width_character_count": display_full,
                "display_half_width_character_count": len(display) - display_full,
                "reserved_raw_g1n_width_px": reservation["reserved_full_name_width_px"],
                "reserved_effective_width_px": math.ceil(
                    reservation["reserved_full_name_width_px"] * RUNTIME_FONT_PX / RAW_FULL_WIDTH_PX
                ),
                "runtime_proven": False,
                "reservation_reason": "Scene-limited conservative reservation, scaled 30/48; not runtime-proven.",
            })
            return display

        display = RUNTIME_RE.sub(render_runtime, visible_template)
        literal = RUNTIME_RE.sub("", visible_template)
        literal_full = sum(is_full_width_visible(character) for character in literal)
        literal_half = len(literal) - literal_full
        reserved_raw = sum(item["reserved_raw_g1n_width_px"] for item in runtime_items)
        raw_width = literal_full * RAW_FULL_WIDTH_PX + literal_half * RAW_HALF_WIDTH_PX + reserved_raw
        effective_width = math.ceil(raw_width * RUNTIME_FONT_PX / RAW_FULL_WIDTH_PX)
        display_full = sum(is_full_width_visible(character) for character in display)
        result.append({
            "line_number": line_number,
            "encoded_string": encoded_line,
            "display_string": display,
            "raw_g1n_width_px": raw_width,
            "literal_raw_g1n_width_px": literal_full * RAW_FULL_WIDTH_PX + literal_half * RAW_HALF_WIDTH_PX,
            "reserved_raw_g1n_width_px": reserved_raw,
            "effective_width_px": effective_width,
            "full_width_character_count": display_full,
            "half_width_character_count": len(display) - display_full,
            "runtime_reservations": runtime_items,
            "exceeds_912px": effective_width > MAX_EFFECTIVE_WIDTH_PX,
        })
    return result


def source_summary(value: dict[str, Any]) -> dict[str, Any]:
    keys = ("path", "packed_sha256", "raw_sha256", "packed_size", "raw_size", "string_count")
    return {key: value[key] for key in keys}


def main() -> int:
    current_profile, current = profile(CURRENT_PATH)
    require(current_profile["packed_sha256"] == CURRENT_EXPECTED["packed_sha256"], "final strict predecessor packed baseline drift")
    require(current_profile["raw_sha256"] == CURRENT_EXPECTED["raw_sha256"], "final strict predecessor raw baseline drift")
    jp_profile, jp = profile(DIRECT_JP_PATH)
    en_profile, en = profile(DIRECT_EN_PATH)
    sc_profile, sc = profile(DIRECT_SC_PATH)
    tc_profile, tc = profile(DIRECT_TC_PATH)
    legacy_profile, legacy = profile(LEGACY_KO_PATH)
    for label, values in (("jp", jp), ("en", en), ("sc", sc), ("tc", tc), ("legacy", legacy)):
        require(len(values) == len(current), f"{label} message count differs from strict baseline")

    historical = read_json(HISTORICAL_MANIFEST)
    reservation_doc = read_json(RESERVATION_MANIFEST)
    inventory = read_json(INVENTORY_MANIFEST)
    special_review = read_json(SPECIAL_REFLOW_REVIEW)
    historical_entries = historical.get("entries")
    reservations = reservation_doc.get("reservations")
    inventory_rows = inventory.get("rows")
    special_rows = special_review.get("rows")
    require(isinstance(historical_entries, list), "historical entries missing")
    require(isinstance(reservations, dict), "runtime reservations missing")
    require(isinstance(inventory_rows, list), "inventory rows missing")
    require(isinstance(special_rows, list), "special reflow rows missing")
    inventory_by_id = {row["entry_id"]: row for row in inventory_rows if isinstance(row, dict)}
    special_by_id = {row["entry_id"]: row for row in special_rows if isinstance(row, dict)}
    require(set(SPECIAL_REFLOW_IDS).issubset(set(special_by_id)), "special reflow ID source drift")

    selected = [
        row for row in historical_entries
        if isinstance(row, dict)
        and MIN_ID <= row.get("id", -1) <= MAX_ID
        and (
            row.get("operation") == "manual_compact_korean_layout"
            or "manual_compact_korean_layout" in row.get("newline_operations", [])
        )
    ]
    selected.sort(key=lambda row: row["id"])
    require(len(selected) == EXPECTED_ROW_COUNT, f"manual compact target count drift: {len(selected)}")
    selected_ids = tuple(row["id"] for row in selected)
    require(set(CURRENT_DIFF_IDS).issubset(set(selected_ids)), "current diff ID outside selected scope")
    require(set(SPECIAL_REFLOW_IDS).issubset(set(selected_ids)), "special reflow ID outside selected scope")
    actual_current_diffs = tuple(row["id"] for row in selected if current[row["id"]] != row.get("ko"))
    require(actual_current_diffs == CURRENT_DIFF_IDS, f"current diff scope drift: {actual_current_diffs}")

    reviewed: list[dict[str, Any]] = []
    strategy_counts: Counter[str] = Counter()
    normal_restore_ids: list[int] = []
    current_preserved_ids: list[int] = []
    current_reconciled_ids: list[int] = []
    special_reflow_ids: list[int] = []
    runtime_reservation_reflow_ids: list[int] = []
    token_particle_fix_ids: list[int] = []
    runtime_rows: list[int] = []

    for historical_row in selected:
        entry_id = historical_row["id"]
        compact = historical_row.get("ko")
        require(isinstance(compact, str), f"{entry_id}: historical compact Korean missing")
        current_ko = current[entry_id]
        legacy_ko = normalize_legacy_layout(legacy[entry_id])
        override = QUALITY_OVERRIDES.get(entry_id)
        runtime_reflow = RUNTIME_RESERVATION_REFLOWS.get(entry_id)
        particle_fix = STATIC_TOKEN_PARTICLE_FIXES.get(entry_id)
        prior_special = special_by_id.get(entry_id)

        if entry_id in SPECIAL_REFLOW_IDS:
            require(isinstance(prior_special, dict), f"{entry_id}: special reflow source missing")
            proposed = prior_special.get("proposed_ko")
            require(isinstance(proposed, str), f"{entry_id}: special proposed Korean missing")
            strategy = "revalidate_prior_source_complete_static007_semantic_reflow"
            judgement = (
                "Revalidated the previously reviewed source-complete Korean reflow against "
                "the final strict predecessor and direct PC witnesses; its Korean clause "
                "boundaries are retained and re-measured under raw<=1440/effective<=912."
            )
            special_reflow_ids.append(entry_id)
        elif override is not None and "text" in override:
            proposed = override["text"]
            strategy = override["strategy"]
            judgement = override["judgement"]
            current_reconciled_ids.append(entry_id)
        elif override is not None:
            proposed = current_ko
            strategy = override["strategy"]
            judgement = override["judgement"]
            current_preserved_ids.append(entry_id)
        elif runtime_reflow is not None:
            proposed = runtime_reflow["text"]
            strategy = runtime_reflow["strategy"]
            judgement = runtime_reflow["judgement"]
            runtime_reservation_reflow_ids.append(entry_id)
        elif particle_fix is not None:
            proposed = particle_fix["text"]
            strategy = particle_fix["strategy"]
            judgement = particle_fix["judgement"]
            token_particle_fix_ids.append(entry_id)
        else:
            proposed = legacy_ko
            strategy = "restore_precompaction_source_complete_korean"
            judgement = (
                "The historical manual compact row is not used as a semantic baseline. "
                "Direct PC JP/EN/SC/TC and the full Korean backup were individually checked; "
                "restore the unabridged Korean at its Korean clause boundaries without shortening."
            )
            normal_restore_ids.append(entry_id)

        assert_colour_tags(compact, entry_id)
        assert_colour_tags(current_ko, entry_id)
        assert_colour_tags(legacy_ko, entry_id)
        assert_colour_tags(proposed, entry_id)
        compact_signature = control_signature(compact)
        current_signature = control_signature(current_ko)
        legacy_signature = control_signature(legacy_ko)
        proposed_signature = control_signature(proposed)
        direct_signature = control_signature(jp[entry_id])
        require(
            proposed_signature == current_signature == compact_signature == direct_signature,
            f"{entry_id}: protected control signature drift",
        )

        metrics = layout_lines(entry_id, proposed, current, reservations)
        require(1 <= len(metrics) <= MAX_LINES, f"{entry_id}: line count exceeds {MAX_LINES}")
        require(all(line["raw_g1n_width_px"] <= MAX_RAW_WIDTH_PX for line in metrics), f"{entry_id}: raw width exceeds 1440")
        require(not any(line["exceeds_912px"] for line in metrics), f"{entry_id}: effective width exceeds 912")
        if proposed_signature["runtime_tokens"]:
            runtime_rows.append(entry_id)
        strategy_counts[strategy] += 1
        inventory_row = inventory_by_id.get(entry_id)
        require(isinstance(inventory_row, dict), f"{entry_id}: inventory row missing")

        reviewed.append({
            "entry_id": entry_id,
            "scene_batch_id": inventory_row.get("scene_batch_id"),
            "review_status": "ready_for_semantic_restoration_candidate",
            "reviewed_individually": True,
            "review_judgement": judgement,
            "restoration_strategy": strategy,
            "current_quality_preserved": entry_id in current_preserved_ids,
            "current_quality_reconciled": entry_id in current_reconciled_ids,
            "prior_special_static007_reflow_revalidated": entry_id in special_reflow_ids,
            "runtime_reservation_semantic_reflow": entry_id in runtime_reservation_reflow_ids,
            "scene_limited_token_particle_corrected": entry_id in token_particle_fix_ids,
            "historical_manual_compact_ko": compact,
            "current_ko_at_final_strict_baseline": current_ko,
            "legacy_precompaction_ko": legacy_ko,
            "proposed_ko": proposed,
            "legacy_matches_proposed_after_normalization": legacy_ko == proposed,
            "historical_compact_to_proposed_surface_units": reintroduced_surface_units(compact, proposed),
            "current_to_proposed_surface_units": reintroduced_surface_units(current_ko, proposed),
            "direct_pc_sources": {"jp": jp[entry_id], "en": en[entry_id], "sc": sc[entry_id], "tc": tc[entry_id]},
            "source_review": {
                "historical_compact_used_as_semantic_source": False,
                "direct_witnesses_checked": ["jp", "en", "sc", "tc"],
                "japanese_source_line_breaks_used_for_korean_layout": False,
                "no_sentence_shortening_or_clause_deletion": True,
            },
            "text_sha256_utf16le": {
                "historical_compact_ko": text_sha256(compact),
                "current_ko": text_sha256(current_ko),
                "legacy_precompaction_ko": text_sha256(legacy_ko),
                "proposed_ko": text_sha256(proposed),
            },
            "control_signature": {
                "historical_compact": compact_signature,
                "current": current_signature,
                "legacy": legacy_signature,
                "proposed": proposed_signature,
                "direct_pc_jp": direct_signature,
                "proposed_current_compact_direct_jp_match": True,
            },
            "runtime_token_reservation": {
                "actual_runtime_tokens": proposed_signature["runtime_tokens"],
                "runtime_proven": False,
                "policy": "Use a known scene-limited conservative raw reservation then scale 30/48; no runtime inference.",
            },
            "layout": {
                "line_count": len(metrics),
                "max_lines": MAX_LINES,
                "raw_g1n_pass_limit_px": MAX_RAW_WIDTH_PX,
                "effective_width_pass_limit_px": MAX_EFFECTIVE_WIDTH_PX,
                "all_lines_pass_static_patch_007": True,
                "lines": metrics,
            },
            "any_line_exceeds_912px": False,
        })

    require(len(reviewed) == EXPECTED_ROW_COUNT, "review count accounting drift")
    require(set(current_preserved_ids + current_reconciled_ids) == set(CURRENT_DIFF_IDS) - {9540}, "later revision accounting drift")
    require(len(special_reflow_ids) == len(SPECIAL_REFLOW_IDS), "special reflow accounting drift")
    require(set(runtime_reservation_reflow_ids) == set(RUNTIME_RESERVATION_REFLOWS), "runtime reservation reflow accounting drift")
    require(set(token_particle_fix_ids) == set(STATIC_TOKEN_PARTICLE_FIXES), "token particle fix accounting drift")

    payload = {
        "schema": SCHEMA,
        "scope": {
            "resource": RESOURCE,
            "event_id_range": [MIN_ID, MAX_ID],
            "manual_compact_target_count": len(reviewed),
            "completion": "283 of 283 rows individually reviewed",
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
            "obsolete_960px_raw_gate_used": False,
            "dynamic_name_reservations": "Reserve known token raw width then scale by 30/48; runtime_proven remains false.",
        },
        "sources": {
            "current_ko_final_strict_baseline": source_summary(current_profile),
            "direct_pc_jp_pristine": source_summary(jp_profile),
            "direct_pc_en": source_summary(en_profile),
            "direct_pc_sc": source_summary(sc_profile),
            "direct_pc_tc": source_summary(tc_profile),
            "legacy_precompaction_ko_backup": source_summary(legacy_profile),
            "historical_manual_compact_manifest": {"path": str(HISTORICAL_MANIFEST), "sha256": sha256(HISTORICAL_MANIFEST.read_bytes())},
            "runtime_reservation_manifest": {"path": str(RESERVATION_MANIFEST), "sha256": sha256(RESERVATION_MANIFEST.read_bytes())},
            "inventory_manifest": {"path": str(INVENTORY_MANIFEST), "sha256": sha256(INVENTORY_MANIFEST.read_bytes())},
            "special_reflow_review_revalidated": {"path": str(SPECIAL_REFLOW_REVIEW), "sha256": sha256(SPECIAL_REFLOW_REVIEW.read_bytes()), "ids": list(SPECIAL_REFLOW_IDS)},
        },
        "judgement_groups": [
            {"group": "full_precompaction_korean_restoration", "ids": normal_restore_ids, "reason": "Source-complete legacy Korean is restored with its Korean clause boundaries; no historical compact wording is trusted."},
            {"group": "later_quality_revision_preserved", "ids": current_preserved_ids, "reason": "The later Korean revision is source-complete and must not regress."},
            {"group": "later_quality_revision_reconciled", "ids": current_reconciled_ids, "reason": "A corrected current name or quality improvement is kept while omitted source material is restored."},
            {"group": "prior_static007_semantic_reflow_revalidated", "ids": special_reflow_ids, "reason": "Existing source-complete reflows were reused verbatim only after direct-source and raw1440/effective912 revalidation."},
            {"group": "runtime_reservation_semantic_reflow", "ids": runtime_reservation_reflow_ids, "reason": "Full legacy Korean is retained; only Korean clause breaks are moved because conservative token reservation would otherwise exceed raw1440/effective912."},
            {"group": "scene_limited_token_particle_corrections", "ids": token_particle_fix_ids, "reason": "Only observed name-table renderings in these exact scenes are corrected; no global runtime-token particle inference is used."},
            {"group": "runtime_name_tokens", "ids": runtime_rows, "reason": "Known scene-limited conservative reservation, scaled 30/48; runtime_proven is false."},
        ],
        "counts": {
            "restoration_strategy_counts": dict(sorted(strategy_counts.items())),
            "full_precompaction_restoration_count": len(normal_restore_ids),
            "current_quality_preserved_count": len(current_preserved_ids),
            "current_quality_reconciled_count": len(current_reconciled_ids),
            "prior_special_static007_reflow_revalidated_count": len(special_reflow_ids),
            "runtime_reservation_semantic_reflow_count": len(runtime_reservation_reflow_ids),
            "scene_limited_token_particle_correction_count": len(token_particle_fix_ids),
            "runtime_token_row_count": len(runtime_rows),
            "all_rows_four_or_fewer_lines": True,
            "all_rows_within_raw_1440_and_effective_912": True,
        },
        "entries": reviewed,
        "safety": {
            "candidate_binary_written": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "release_published": False,
            "network_operation_performed": False,
        },
    }
    PUBLIC.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validation = {
        "schema": "nobu16.kr.manual-compact-9000-review-validation.v1",
        "review_output": str(OUTPUT),
        "review_output_sha256": sha256(OUTPUT.read_bytes()),
        "target_count": len(reviewed),
        "current_diff_row_count": len(CURRENT_DIFF_IDS),
        "prior_special_static007_reflow_revalidated_count": len(special_reflow_ids),
        "max_line_count": max(row["layout"]["line_count"] for row in reviewed),
        "max_raw_g1n_width_px": max(line["raw_g1n_width_px"] for row in reviewed for line in row["layout"]["lines"]),
        "max_effective_width_px": max(line["effective_width_px"] for row in reviewed for line in row["layout"]["lines"]),
        "over_raw_1440_line_count": sum(line["raw_g1n_width_px"] > MAX_RAW_WIDTH_PX for row in reviewed for line in row["layout"]["lines"]),
        "over_912px_line_count": sum(line["exceeds_912px"] for row in reviewed for line in row["layout"]["lines"]),
        "candidate_binary_created": False,
        "steam_files_written": False,
        "git_or_release_actions_performed": False,
        "network_operation_performed": False,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
