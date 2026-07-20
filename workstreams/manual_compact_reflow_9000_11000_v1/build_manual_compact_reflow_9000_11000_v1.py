#!/usr/bin/env python3
"""Review-only restoration plan for 23 manual event-dialogue compactions.

This workstream deliberately creates evidence and a proposed Korean reflow
only.  It reads the strict Static Patch 007 Batch 04 predecessor, the
pre-compaction Korean backup, and direct PC JP/EN/SC/TC witnesses.  It never
creates a message binary or writes to Steam.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))

import nobu16_lz4 as lz4  # noqa: E402
import nobu16_msg_table as message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-manual-compact-static007-reflow-review.v1"
OUTPUT_PATH = WORKSTREAM / "review.v1.json"

CURRENT_KO_PATH = (
    REPO
    / "tmp"
    / "pc_event_manual_compact_4000_5000_restore_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
LEGACY_KO_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-v0.10.0-original-font-rollback-v1"
    r"\originals\MSG_PK\JP\msgev.bin"
)
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

EXPECTED_CURRENT_PROFILE = {
    "packed_sha256": "E95A773B7B6448542CF8236868CBEEE7BA49382DD0450DB75DB6CD66CF43FF60",
    "raw_sha256": "9F15BE13C0CFE09D82A9BAE616B57FCE8B4C92187624EB3686E2F850B504F146",
}
EXPECTED_LEGACY_PROFILE = {
    "packed_sha256": "2CA183DA690D45A75702EA0F35C70966786B59E9440B8B8F49BE9652342F81AC",
    "raw_sha256": "EDCF7A9CEBD605BB2275D5A3B92A76E7E2F652B2391554F24C6A8BDD2EF91A08",
}
EXPECTED_DIRECT_JP_PROFILE = {
    "packed_sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
}

TARGET_IDS = (
    9049,
    9083,
    9140,
    9141,
    9169,
    9228,
    9326,
    9338,
    9340,
    9523,
    9540,
    9541,
    9624,
    9683,
    10136,
    10183,
    10314,
    10334,
    10343,
    10463,
    10595,
    10625,
    10744,
)

ESC = "\x1b"
CA = ESC + "CA"
CB = ESC + "CB"
CC = ESC + "CC"
CZ = ESC + "CZ"

# These strings retain every source proposition.  Most keep the full legacy
# Korean surface exactly and only move Korean line boundaries.  The three
# documented source-quality corrections below do not omit or abbreviate a
# clause.
PROPOSED_KO = {
    9049: (
        f"{CA}호소카와 마사모토{CZ}, {CA}오우치 요시오키{CZ},\n"
        f"{CA}호소카와 다카쿠니{CZ}, {CA}미요시 나가요시{CZ}…\n"
        "역대 구보님들도 실력을 갖춘 다이묘를\n"
        "교묘히 갈아타며 살아남으셨사옵니다."
    ),
    9083: (
        f"{CB}미요시{CZ} 삼인중과 {CA}마쓰나가 히사미치{CZ} 등이\n"
        f"쇼군 {CA}아시카가 요시테루{CZ}의 목숨을\n"
        f"노리고 있다는 소문은 {CB}미요시가{CZ} 안에서는\n"
        "공공연한 것이 되어 있었다…"
    ),
    9140: (
        "각지에서 잇따른 전란도 고비를 넘기고\n"
        "새로운 세상이 보이기 시작한 지금,\n"
        "성씨를 고쳐 재지 지배를 굳혀야 할 때인가…"
    ),
    9141: (
        "당가에 어울리는 성씨는, 일찍이 이 땅의\n"
        "성을 다스린 조정 무관의 고위 관직\n"
        f"‘{CC}아키타성{CZ}스케’에서 딴\n"
        f"‘{CA}아키타{CZ}’뿐일 것이다."
    ),
    9169: (
        f"{CA}다케다 노부카도{CZ}는 {CA}[bm1251]{CZ},\n"
        f"{CA}노부시게{CZ}와 같은 어머니에게서 난 아우로,\n"
        f"그 용모는 {CA}[bm1251]{CZ}와 꼭 닮았다고\n"
        "전해진다."
    ),
    9228: (
        f"이 무렵 {CA}가키자키 요시히로{CZ}는\n"
        f"성을 {CA}마쓰마에{CZ}로 삼았다.\n"
        f"{CB}가키자키 가문{CZ}은 데릴사위로 들어온 객장\n"
        f"{CA}다케다 노부히로{CZ} 이래 {CB}와카사 다케다씨{CZ}의 지류라 칭했으나…"
    ),
    9326: (
        f"한편, {CA}호조 우지쓰나{CZ}의 죽음으로\n"
        f"균형이 무너진 {CC}간토{CZ}에서는 {CA}이마가와{CZ}·{CA}다케다{CZ}·\n"
        f"{CA}양 우에스기{CZ}가 지금이야말로 호기라며\n"
        f"새 당주 {CA}우지야스{CZ}에게 도전하려 하고 있었다…"
    ),
    9338: (
        f"그 {CA}아사쿠라{CZ}와 맹약을 맺은\n"
        f"{CA}아자이 나가마사{CZ}에게, {CA}노부나가{CZ}는\n"
        f"누이 {CA}오이치{CZ}를 시집보냈다.\n"
        "사이에 낀 부부의 고뇌의 나날이 시작되려 하고 있다――"
    ),
    9340: (
        f"{CA}노부나가{CZ}는 제장에게 명해 통일 사업을 서두르게 한다\n"
        f"{CC}호쿠리쿠{CZ}의 {CA}우에스기 가게카쓰{CZ}에게는\n"
        f"{CA}시바타 가쓰이에{CZ}를 배치하고, {CC}간토{CZ}의 억제는\n"
        f"{CA}다키가와 가즈마스{CZ}·{CA}[b1871]{CZ} 등을…"
    ),
    9523: (
        f"{CA}미요시{CZ} 가신 {CA}마쓰나가 나가요리{CZ}는\n"
        f"{CA}마쓰나가 히사히데{CZ}의 동생으로,\n"
        f"{CA}나가요시{CZ}의 우필을 거쳐 출세한 형과 달리,\n"
        "무용이 뛰어나 전공을 세워 출세했다고 한다."
    ),
    9540: (
        f"이리하여 {CA}니카이도{CZ}에서 이름을 고친\n"
        f"{CA}아시나 모리타카{CZ}가 탄생했다.\n"
        f"{CA}히코히메{CZ}는 {CA}아난히메{CZ}의 여동생으로,\n"
        f"{CA}모리타카{CZ}에게는 이모뻘 되는 여성이다."
    ),
    9541: (
        f"{CB}니카이도가{CZ}와 {CB}다테가{CZ}의 영향력이 강해지는 것을 두려워한\n"
        f"{CB}아시나{CZ} 가신들은 맹렬히 반대했으나, {CA}모리우지{CZ}는\n"
        f"{CA}모리타카{CZ}에게 {CB}아시나{CZ} 가명을 잇게 하는 일을\n"
        "강행했다."
    ),
    9624: (
        f"거듭된 {CA}가게카쓰{CZ}의 고사에도 불구하고,\n"
        f"{CA}가게토라{CZ}는 {CA}우에스기 성{CZ}을 허락했고,\n"
        f"{CA}가게카쓰{CZ}는 {CA}우에스기{CZ}인 채로\n"
        "가신으로서 섬기게 되었다."
    ),
    9683: (
        "지금의 쇼군가는 검술에만 힘쓰고, 정무의\n"
        f"주도권은 {CB}미요시가{CZ}에게 넘어가 허울뿐.\n"
        "주군께서 상락하시어 천하에 호령을\n"
        "내리시는 것이 어떻겠습니까?"
    ),
    10136: (
        f"{CB}서군{CZ}은 {CA}모리 히데모토{CZ}와 {CA}깃카와 히로이에{CZ} 등이\n"
        "이끄는 삼만여 명,\n"
        f"이에 맞선 {CB}도미타군{CZ}은 이천에도 못 미치는\n"
        "소수였다."
    ),
    10183: (
        f"{CA}미쓰나리{CZ}의 거병 소식에 {CA}도쿠가와 이에야스{CZ}는\n"
        f"{CC}아이즈{CZ} 정벌을 중단했다.\n"
        f"차남 {CA}유키 히데야스{CZ}에게는 {CC}우쓰노미야{CZ}에 머물러\n"
        f"{CB}우에스기군{CZ}의 진출을 막으라고 명했고……"
    ),
    10314: (
        f"그들은 먼저 {CB}도요토미{CZ}의 은혜를 입고도\n"
        f"{CB}동군{CZ}에 가담한 다이묘들을 처벌하고\n"
        f"힘을 합쳐 {CB}도쿠가와 가문{CZ}에 맞서기로\n"
        "결정했다."
    ),
    10334: (
        f"{CA}미쓰나리{CZ}는 {CA}이에야스{CZ}에게 가담한\n"
        f"{CB}도요토미{CZ}의 은혜를 입은 다이묘들을\n"
        f"처벌했다. {CB}동군{CZ} 장수들의 당주를\n"
        "교체하고 영지를 줄였다."
    ),
    10343: (
        f"{CC}모가미{CZ}의 소수 병력은\n"
        f"본거지 {CC}야마가타{CZ}와 {CB}하세도성{CZ}까지 다가온 {CB}우에스기군{CZ}을\n"
        "잘 버텨 냈지만\n"
        f"{CC}세키가하라{CZ}의 패전 소식을 듣고 항복을 결심했다."
    ),
    10463: (
        f"그들은 먼저 {CB}도요토미{CZ}의 은혜를 입고도\n"
        f"{CB}동군{CZ}에 가담한 다이묘들을 처벌하고\n"
        f"힘을 합쳐 {CB}도쿠가와 가문{CZ}에 맞서기로\n"
        "결정했다."
    ),
    10595: (
        f"{CA}도쿠가와 이에야스{CZ}를 받쳐 온 후다이의 대표로\n"
        f"{CA}사카이 다다쓰구{CZ}·{CA}혼다 다다카쓰{CZ}·\n"
        f"{CA}사카키바라 야스마사{CZ}·{CA}이이 나오마사{CZ}의\n"
        f"{CB}도쿠가와{CZ} 사천왕이 있다."
    ),
    10625: (
        f"{CC}도쿠가와 이에야스{CZ}는 {CA}세키가하라{CZ}에서\n"
        f"{CA}이시다 미쓰나리{CZ} 등을 물리치고\n"
        f"{CC}후시미성{CZ}에서 정이대장군으로 임명되어\n"
        "명실공히 무가의 정점에 올랐다."
    ),
    10744: (
        f"{CA}요시모토{CZ}의 조략에 의해\n"
        f"{CB}야마노우치 우에스기가{CZ}, {CB}오기가야쓰 우에스기가{CZ},\n"
        f"{CB}고가 아시카가가{CZ}가 일제히 봉기해\n"
        f"{CC}가와고에성{CZ}을 포위한 것이다."
    ),
}

SEMANTIC_RESTORATIONS = {
    9049: ["역대 구보가 실력 있는 다이묘를 갈아타며 살아남았다는 존대 서술을 복원했다."],
    9083: ["요시테루의 목숨을 노린다는 소문과 미요시가 안에서 공공연했다는 결말을 복원했다."],
    9140: ["각지 전란의 고비, 새 시대의 조짐, 성씨 변경, 재지 지배 강화의 네 의미 단위를 모두 유지했다."],
    9141: ["顕職은 현직이 아니라 고위 관직이므로 그 관계를 바로잡고, 아키타성스케에서 따온 성씨라는 뜻을 복원했다."],
    9169: ["노부카도의 동복 관계와 [bm1251]를 닮았다는 전승을 모두 복원했다."],
    9228: ["마쓰마에로의 성 변경, 데릴사위 객장, 와카사 다케다씨 지류 자칭의 세 사실을 복원했다."],
    9326: ["우지쓰나 사후의 간토 균형 붕괴와 세 세력의 호기 판단·우지야스 도전을 복원했다."],
    9338: ["아사쿠라와의 맹약, 오이치의 혼인, 사이에 낀 부부의 고뇌가 시작되는 흐름을 복원했다."],
    9340: ["제장에게 통일 사업을 재촉한 명령, 호쿠리쿠 배치, 간토 견제의 세 병렬 조치를 복원했다."],
    9523: ["나가요리의 형제 관계, 형의 우필 경력, 본인의 무용·전공에 의한 출세를 복원했다."],
    9540: ["니카이도에서 아시나 모리타카로 바뀐 사실과 히코히메·아난히메·모리타카의 친족 관계를 복원했다."],
    9541: ["니카이도·다테의 영향력 확대 우려, 아시나 가신의 맹렬한 반대, 가명 계승 강행을 복원했다."],
    9624: ["가게카쓰의 반복된 고사, 가게토라의 우에스기 성 허락, 가신으로 섬김의 결과를 복원했다."],
    9683: ["쇼군가의 명목화와 미요시가의 정무 장악, 상락하여 천하에 호령하라는 제안을 복원했다."],
    10136: ["서군의 지휘자·삼만여 병력과 도미타군의 이천 미만 병력이라는 대비를 복원했다."],
    10183: ["거병 소식, 아이즈 정벌 중단, 차남에게 우쓰노미야 잔류와 우에스기군 저지를 명한 흐름을 복원했다."],
    10314: ["도요토미의 은혜를 입고 동군에 가담한 다이묘의 처벌과 도쿠가와 가문 대항 결정을 복원했다."],
    10334: ["이에야스에게 가담한 도요토미 은고 다이묘의 처벌 및 동군 장수의 당주 교체·영지 삭감을 복원했다."],
    10343: ["모가미 소수 병력의 방어, 하세도성까지 다가온 우에스기군, 세키가하라 패전보 뒤 항복 결심을 복원했다."],
    10463: ["10314와 같은 반복 사건으로, 처벌과 도쿠가와 가문 대항 결정을 완전한 문장으로 복원했다."],
    10595: ["후다이의 대표인 도쿠가와 사천왕과 네 명의 구성원을 모두 복원했다."],
    10625: ["세키가하라 승리, 후시미성에서의 정이대장군 임명, 무가 정점 도달을 복원했다."],
    10744: ["요시모토의 조략, 세 가문의 동시 봉기, 가와고에성 포위를 복원했다."],
}

# Every other proposed row preserves the legacy visible surface after only
# changing line breaks.  These three rows contain a necessary source-quality
# correction or a semantic-equivalent reflow needed to stay within four lines.
LEGACY_SURFACE_EXCEPTIONS = {
    9141: "顕職을 '현직'으로 둔 뜻을 '고위 관직'으로 바로잡았다.",
    9228: "네 줄 안에서 지류 자칭의 의미를 보존하도록 '지류라 칭했으나'로 한국어 표현만 재배치했다.",
    10334: "직접 JP의 인물·가문 색상 태그 순서를 유지하면서, 도요토미 은고 다이묘가 이에야스에 가담했다는 관계를 완전한 한국어로 다시 배열했다.",
}

RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
MAX_EFFECTIVE_WIDTH_PX = 912
MAX_RAW_WIDTH_PX = 1440
MAX_LINES = 4

ESC_RE = re.compile(r"\x1b(?:CA|CB|CC|CZ)")
RUNTIME_RE = re.compile(r"\[([a-z]+)(\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*(?:\d+)?(?:\.\d+)?[A-Za-z]")
OTHER_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1a\x1c-\x1f]")


class ReviewError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_digest(value: str) -> str:
    return digest(value.encode("utf-16-le"))


def profile(path: Path) -> tuple[dict[str, Any], tuple[str, ...]]:
    require(path.is_file(), f"read-only source missing: {path}")
    packed = path.read_bytes()
    _header, raw = lz4.decompress_wrapper(packed)
    table = message_table.parse_message_table(raw)
    require(
        message_table.rebuild_message_table(table, table.texts) == raw,
        f"message-table round trip differs: {path}",
    )
    return (
        {
            "path": str(path),
            "packed_size": len(packed),
            "packed_sha256": digest(packed),
            "raw_size": len(raw),
            "raw_sha256": digest(raw),
            "string_count": len(table.texts),
        },
        table.texts,
    )


def normalize_linebreaks(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def normalized_visible_surface(value: str) -> str:
    # A semantic reflow can move an existing inter-word space to either side
    # of a newline.  This comparison intentionally ignores whitespace only;
    # punctuation and every visible Korean/CJK character remain significant.
    return re.sub(r"\s+", "", ESC_RE.sub("", normalize_linebreaks(value)))


def is_full_width_visible(character: str) -> bool:
    """Static Patch 007 class: Korean/CJK scripts full; punctuation half."""
    return (
        "가" <= character <= "힣"
        or "一" <= character <= "鿿"
        or "ぁ" <= character <= "ゟ"
        or "ァ" <= character <= "ヿ"
        or "Ａ" <= character <= "ｚ"
    )


def control_signature(value: str) -> dict[str, Any]:
    return {
        "esc_tokens": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "unknown_percent_count": len(re.findall(r"%(?!\d+\$?[-+#0 ]*(?:\d+)?(?:\.\d+)?[A-Za-z])", value)),
        "nul_count": value.count("\x00"),
        "other_controls": OTHER_CONTROL_RE.findall(value),
    }


def assert_colour_tags(value: str, entry_id: int) -> None:
    active = False
    position = 0
    while position < len(value):
        if value[position] == ESC:
            token = value[position : position + 3]
            require(ESC_RE.fullmatch(token) is not None, f"{entry_id}: malformed ESC tag {token!r}")
            if token == CZ:
                require(active, f"{entry_id}: unpaired colour close")
                active = False
            else:
                require(not active, f"{entry_id}: nested colour tag")
                active = True
            position += 3
            continue
        require(not (active and value[position] in "\r\n"), f"{entry_id}: line break inside colour tag")
        position += 1
    require(not active, f"{entry_id}: unterminated colour tag")


def layout(
    entry_id: int,
    value: str,
    current_names: tuple[str, ...],
    reservations: dict[str, Any],
) -> dict[str, Any]:
    lines: list[dict[str, Any]] = []
    for line_number, encoded_line in enumerate(normalize_linebreaks(value).split("\n"), 1):
        visible_template = ESC_RE.sub("", encoded_line)
        dynamic: list[dict[str, Any]] = []

        def render(match: re.Match[str]) -> str:
            token = match.group(0)
            name_id = int(match.group(2))
            require(0 <= name_id < len(current_names), f"{entry_id}: runtime token outside table: {token}")
            reservation = reservations.get(token)
            require(reservation is not None, f"{entry_id}: token reservation absent: {token}")
            display = ESC_RE.sub("", normalize_linebreaks(current_names[name_id])).replace("\n", " ")
            display_full = sum(is_full_width_visible(character) for character in display)
            dynamic.append(
                {
                    "token": token,
                    "source_name_id": name_id,
                    "display_string": display,
                    "display_full_width_character_count": display_full,
                    "display_half_width_character_count": len(display) - display_full,
                    "reserved_raw_g1n_width_px": reservation["reserved_full_name_width_px"],
                    "reserved_effective_width_px": math.ceil(
                        reservation["reserved_full_name_width_px"] * DRAW_FONT_PX / RAW_FULL_WIDTH_PX
                    ),
                    "runtime_proven": False,
                }
            )
            return display

        display = RUNTIME_RE.sub(render, visible_template)
        literal = RUNTIME_RE.sub("", visible_template)
        literal_full = sum(is_full_width_visible(character) for character in literal)
        literal_half = len(literal) - literal_full
        reserved_raw = sum(item["reserved_raw_g1n_width_px"] for item in dynamic)
        raw = literal_full * RAW_FULL_WIDTH_PX + literal_half * RAW_HALF_WIDTH_PX + reserved_raw
        effective = math.ceil(raw * DRAW_FONT_PX / RAW_FULL_WIDTH_PX)
        display_full = sum(is_full_width_visible(character) for character in display)
        lines.append(
            {
                "line_number": line_number,
                "display_string": display,
                "raw_g1n_width_px": raw,
                "effective_width_px": effective,
                "full_width_character_count": display_full,
                "half_width_character_count": len(display) - display_full,
                "literal_raw_g1n_width_px": literal_full * RAW_FULL_WIDTH_PX + literal_half * RAW_HALF_WIDTH_PX,
                "reserved_raw_g1n_width_px": reserved_raw,
                "runtime_reservations": dynamic,
                "over_effective_912px": effective > MAX_EFFECTIVE_WIDTH_PX,
            }
        )
    return {
        "line_count": len(lines),
        "all_lines_pass_static_patch_007": all(not line["over_effective_912px"] for line in lines),
        "lines": lines,
    }


def aggregate_runtime_reservations(proposed_layout: dict[str, Any]) -> dict[str, Any]:
    all_items = [
        reservation
        for line in proposed_layout["lines"]
        for reservation in line["runtime_reservations"]
    ]
    if not all_items:
        return {
            "actual_runtime_tokens": [],
            "raw_g1n_px": 0,
            "effective_width_px": 0,
            "runtime_proven": False,
            "reason": "No runtime name token occurs in this row.",
        }
    distinct: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in all_items:
        if item["token"] not in seen:
            distinct.append(item)
            seen.add(item["token"])
    return {
        "actual_runtime_tokens": distinct,
        "raw_g1n_px": sum(item["reserved_raw_g1n_width_px"] for item in distinct),
        "effective_width_px": sum(item["reserved_effective_width_px"] for item in distinct),
        "runtime_proven": False,
        "reason": "Conservative token reservation comes from the reviewed manifest and is scaled by 30/48; no unrelated runtime route is inferred.",
    }


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def main() -> int:
    current_profile, current = profile(CURRENT_KO_PATH)
    require(
        {key: current_profile[key] for key in EXPECTED_CURRENT_PROFILE} == EXPECTED_CURRENT_PROFILE,
        "strict 4000–5000 restoration source profile drift",
    )
    legacy_profile, legacy = profile(LEGACY_KO_PATH)
    require(
        {key: legacy_profile[key] for key in EXPECTED_LEGACY_PROFILE} == EXPECTED_LEGACY_PROFILE,
        "legacy full Korean source profile drift",
    )
    source_profiles: dict[str, dict[str, Any]] = {}
    direct: dict[str, tuple[str, ...]] = {}
    for language, path in DIRECT_PATHS.items():
        source_profiles[language], direct[language] = profile(path)
    require(
        {key: source_profiles["jp"][key] for key in EXPECTED_DIRECT_JP_PROFILE} == EXPECTED_DIRECT_JP_PROFILE,
        "direct JP source profile drift",
    )
    for label, texts in (("legacy", legacy), *direct.items()):
        require(len(texts) == len(current), f"{label}/current string-count drift")

    historical = read_json(HISTORICAL_MANIFEST)
    historical_entries = historical.get("entries")
    require(isinstance(historical_entries, list), "historical entry list absent")
    historical_by_id = {
        row.get("id"): row
        for row in historical_entries
        if isinstance(row, dict)
        and (
            row.get("operation") == "manual_compact_korean_layout"
            or "manual_compact_korean_layout" in row.get("newline_operations", [])
        )
    }
    require(tuple(sorted(TARGET_IDS)) == TARGET_IDS, "target IDs must be sorted")
    require(set(TARGET_IDS) == set(PROPOSED_KO), "proposal scope mismatch")
    require(all(entry_id in historical_by_id for entry_id in TARGET_IDS), "target outside manual compact inventory")

    reservations_document = read_json(RESERVATION_MANIFEST)
    reservations = reservations_document.get("reservations")
    require(isinstance(reservations, dict), "runtime reservation map absent")

    rows: list[dict[str, Any]] = []
    for entry_id in TARGET_IDS:
        current_ko = current[entry_id]
        legacy_ko = legacy[entry_id]
        proposed_ko = PROPOSED_KO[entry_id]
        for label, value in (("current", current_ko), ("legacy", legacy_ko), ("proposed", proposed_ko)):
            assert_colour_tags(value, entry_id)
        current_signature = control_signature(current_ko)
        legacy_signature = control_signature(legacy_ko)
        proposed_signature = control_signature(proposed_ko)
        jp_signature = control_signature(direct["jp"][entry_id])
        require(current_signature == legacy_signature == proposed_signature == jp_signature, f"{entry_id}: control signature drift")

        layouts = {
            "legacy": layout(entry_id, legacy_ko, current, reservations),
            "current": layout(entry_id, current_ko, current, reservations),
            "proposed": layout(entry_id, proposed_ko, current, reservations),
        }
        require(1 <= layouts["proposed"]["line_count"] <= MAX_LINES, f"{entry_id}: proposed line count")
        require(layouts["proposed"]["all_lines_pass_static_patch_007"], f"{entry_id}: proposed width")

        unchanged_legacy_surface = entry_id not in LEGACY_SURFACE_EXCEPTIONS
        if unchanged_legacy_surface:
            require(
                normalized_visible_surface(legacy_ko) == normalized_visible_surface(proposed_ko),
                f"{entry_id}: unintended legacy visible-content drift",
            )
        historical_row = historical_by_id[entry_id]
        rows.append(
            {
                "entry_id": entry_id,
                "historical_operation": historical_row.get("operation"),
                "historical_newline_operations": historical_row.get("newline_operations", []),
                "review_status": "PASS — source-complete restoration and Korean semantic reflow",
                "semantic_restoration": SEMANTIC_RESTORATIONS[entry_id],
                "legacy_surface_change": LEGACY_SURFACE_EXCEPTIONS.get(entry_id),
                "current_ko": current_ko,
                "current_ko_utf16le_sha256": text_digest(current_ko),
                "legacy_full_ko": legacy_ko,
                "legacy_full_ko_utf16le_sha256": text_digest(legacy_ko),
                "proposed_ko": proposed_ko,
                "proposed_ko_utf16le_sha256": text_digest(proposed_ko),
                "visible_content_preserved_from_legacy_after_linebreak_normalization": unchanged_legacy_surface,
                "source_evidence": {language: direct[language][entry_id] for language in ("jp", "en", "sc", "tc")},
                "control_signature": {
                    "current_legacy_proposed_direct_jp_match": True,
                    **proposed_signature,
                    "line_break_inside_tag": False,
                },
                "runtime_token_reservation": aggregate_runtime_reservations(layouts["proposed"]),
                "layouts": layouts,
            }
        )

    payload = {
        "schema": SCHEMA,
        "review_kind": "proposal_only",
        "resource": "MSG_PK/JP/msgev.bin",
        "scope": {
            "entry_ids": list(TARGET_IDS),
            "entry_count": len(rows),
            "selection_reason": "All assigned rows are marked manual_compact_korean_layout in the historical manifest. The compact text is not trusted as a semantic baseline; each row is compared with direct PC JP/EN/SC/TC and the pre-compaction Korean source before a four-line Static Patch 007 reflow is proposed.",
        },
        "provenance_refresh": {
            "authoritative_current_candidate": "pc_event_manual_compact_4000_5000_restore_v1",
            "packed_sha256": current_profile["packed_sha256"],
            "raw_sha256": current_profile["raw_sha256"],
            "batch04_scoped_texts_unchanged_in_current_predecessor": True,
            "all_23_current_texts_re_read_from_current_predecessor": True,
        },
        "layout_policy": {
            "baseline": "Static Patch 007 verified PK event-dialogue layout",
            "maximum_lines": MAX_LINES,
            "raw_g1n_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_g1n_half_width_px": RAW_HALF_WIDTH_PX,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "maximum_effective_width_px": MAX_EFFECTIVE_WIDTH_PX,
            "maximum_raw_g1n_width_px": MAX_RAW_WIDTH_PX,
            "japanese_source_line_breaks_used": False,
            "japanese_line_break_policy": "Direct Japanese line breaks are semantic witnesses only. Korean line breaks are authored independently at Korean sentence or clause boundaries.",
            "dynamic_token_policy": "Each dynamic token line reserves the manifest raw full-name width and reports ceil(raw * 30 / 48); runtime_proven stays false.",
        },
        "inputs": {
            "strict_current_korean": current_profile,
            "legacy_full_korean": legacy_profile,
            "direct_pc_context": source_profiles,
            "historical_manual_compact_manifest": {
                "path": str(HISTORICAL_MANIFEST),
                "sha256": digest(HISTORICAL_MANIFEST.read_bytes()),
            },
            "runtime_token_reservation_manifest": {
                "path": str(RESERVATION_MANIFEST),
                "sha256": digest(RESERVATION_MANIFEST.read_bytes()),
            },
        },
        "rows": rows,
        "safety": {
            "candidate_bin_written": False,
            "git_operation_performed": False,
            "steam_game_resource_written": False,
            "release_published": False,
            "network_operation_performed": False,
        },
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT_PATH), "entry_count": len(rows), "candidate_bin_written": False, "steam_game_resource_written": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
