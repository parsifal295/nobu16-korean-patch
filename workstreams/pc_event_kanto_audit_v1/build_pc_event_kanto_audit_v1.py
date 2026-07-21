#!/usr/bin/env python3
"""Build a read-only PC event audit for the 3485–3526 Kanto scene range.

The script consumes only the pinned Wave 100 Korean private candidate and
read-only direct PC JP/EN/SC/TC resources.  It writes an audit report and its
validation record under this workstream; it never creates a game binary or
writes Steam, Git, release, or network state.
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
OUTPUT = PUBLIC / "pc_event_kanto_audit.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-kanto-audit.v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
ROW_COUNT = 17_916
TARGET_IDS = tuple(range(3_485, 3_527))

RUNTIME_FONT_PX = 30
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
MAX_RAW_WIDTH_PX = 1_440
MAX_EFFECTIVE_WIDTH_PX = 912
MAX_LINES = 4

CURRENT_PATH = (
    REPO
    / "tmp"
    / "pc_event_ending_regions_quality_wave100_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
CURRENT_EXPECTED: Mapping[str, Any] = {
    "packed_sha256": "245043679E4A7A75628519829C1B16372A8FD085A1CC7F0F4EE97F52BB66BA60",
    "packed_size": 1_048_043,
    "raw_sha256": "F7DB831E850F191CC6320E54BF878DCC8B7F3DC4F5D51AD66379D64617F553ED",
    "raw_size": 1_043_924,
    "string_count": ROW_COUNT,
}

# W100 only changes 3331/3413/3446/3475/3477/3479.  Keep W98 as an explicit
# guard that this independent 3485–3526 audit has been rebased without any
# hidden text drift inside its own range.
W98_PREDECESSOR_PATH = (
    REPO
    / "tmp"
    / "pc_event_gifu_quality_wave98_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
W98_PREDECESSOR_EXPECTED: Mapping[str, Any] = {
    "packed_sha256": "62C7F55506DB59A43761DDCE07FB5DA4175AD0AC4B68C03507B37AD52E2AEBD3",
    "packed_size": 1_048_051,
    "raw_sha256": "D0FAB9C303F8F456184DCDD89AC929C675D6528080F8C29E419E1249BD9B7408",
    "raw_size": 1_043_932,
    "string_count": ROW_COUNT,
}

STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
SOURCES: Mapping[str, tuple[Path, Mapping[str, Any]]] = {
    "jp": (
        STEAM_ROOT
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msgev.bin",
        {
            "packed_sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
            "packed_size": 562_226,
            "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
            "raw_size": 894_800,
            "string_count": ROW_COUNT,
        },
    ),
    "en": (
        STEAM_ROOT / "MSG_PK" / "EN" / "msgev.bin",
        {
            "packed_sha256": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
            "packed_size": 762_196,
            "raw_sha256": "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911",
            "raw_size": 1_878_836,
            "string_count": ROW_COUNT,
        },
    ),
    "sc": (
        STEAM_ROOT / "MSG_PK" / "SC" / "msgev.bin",
        {
            "packed_sha256": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
            "packed_size": 522_177,
            "raw_sha256": "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E",
            "raw_size": 754_708,
            "string_count": ROW_COUNT,
        },
    ),
    "tc": (
        STEAM_ROOT / "MSG_PK" / "TC" / "msgev.bin",
        {
            "packed_sha256": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
            "packed_size": 524_909,
            "raw_sha256": "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6",
            "raw_size": 744_212,
            "string_count": ROW_COUNT,
        },
    ),
}

RESERVATION_MANIFEST = (
    REPO
    / "workstreams"
    / "steam_jp_msgev_full_layout_v2"
    / "public"
    / "runtime_token_reservations.v1.json"
)

E = "\x1b"
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\r|\n")


def ca(value: str) -> str:
    return f"{E}CA{value}{E}CZ"


def cb(value: str) -> str:
    return f"{E}CB{value}{E}CZ"


def cc(value: str) -> str:
    return f"{E}CC{value}{E}CZ"


# These are proposals only.  No candidate binary is made by this workstream.
# The proposal text has a complete protected-token signature identical to the
# pinned current row, and all manual breaks are Korean semantic boundaries.
PROPOSALS: Mapping[int, Mapping[str, Any]] = {
    3489: {
        "change_type": "semantic_and_contextual_reflow",
        "text": (
            "허허, 승려답지 않게 살벌한 말을 하는군……\n"
            "하지만 스승이여, 나는 마음 깊은 곳에서\n"
            f"{ca('우지쓰나')}와 다시 한번 싸우고 싶었소."
        ),
        "rationale": "物騒な言葉는 거친 말투가 아니라 살벌하고 위험한 발언이라는 뜻이다. 발화의 고풍스러운 호칭과 재대결 의사는 보존한다.",
        "source_basis": "JP 物騒な言葉, EN unbecoming of a priest to say such a thing, SC/TC 危险的话·危險的話.",
    },
    3490: {
        "change_type": "contextual_reflow",
        "text": "5년 전의 나는 아직 젊어,\n" f"{ca('우지쓰나')} 앞에서 아무것도 하지 못했지……",
        "rationale": "인명과 뒤의 ‘앞에서’를 같은 의미 단위로 붙여, 현재의 인명 단독 행말을 해소한다.",
        "source_basis": "JP 氏綱の前に手も足も出なかった.",
    },
    3491: {
        "change_type": "semantic_and_contextual_reflow",
        "text": (
            "형을 물리치고 가독을 이은 뒤,\n"
            "우쭐해 있던 나를 깨우쳐 준 것은\n"
            f"그 {ca('우지쓰나')}였지……"
        ),
        "rationale": "家督を継ぎ・増長していた・目を覚ましてくれた의 인과를 복원한다. ‘가독을/이어’와 ‘내/눈’의 인위적 분절도 제거한다.",
        "source_basis": "JP 兄を退けて家督を継ぎ、増長していたわしの目を覚ましてくれた.",
    },
    3493: {
        "change_type": "contextual_reflow",
        "text": (
            f"흠, 말하자면 {ca('우지쓰나')}는\n"
            f"{ca('요시모토')} 님에게 또 한 분의 스승인\n"
            "셈이옵니다."
        ),
        "rationale": "존칭 ‘요시모토 님’을 줄 사이에 갈라놓지 않고, 또 한 명의 스승이라는 판정을 한 문장으로 유지한다.",
        "source_basis": "JP 義元様にとってもう一人の師というわけにございますな.",
    },
    3497: {
        "change_type": "contextual_reflow",
        "text": "이런, 자기에게 유리할 때만\n설교를 참 잘하는군. 어디,\n전쟁이 무엇인지 가르쳐 줘 볼까……",
        "rationale": "‘전쟁이 무엇인지’ 의문 명사절을 한 줄에 두어 문장 성분이 분리되지 않게 한다.",
        "source_basis": "JP どれ、ひとつ戦を教えてやろうか.",
    },
    3500: {
        "change_type": "semantic_and_contextual_reflow",
        "text": (
            f"속히 {cc('스루가')}로 향한다!\n"
            f"그 땅은 {ca('이마가와')}와 {ca('다케다')}의 움직임을 막을 요충지다.\n"
            "잃을 수는 없으니라!"
        ),
        "rationale": "封じる要를 자연스러운 한국어 ‘움직임을 막을 요충지’로 바로잡고, 목적어·서술어를 줄 사이에 분리하지 않는다.",
        "source_basis": "JP かの地は今川と武田の動きを封じる要。失うわけにはいかぬ.",
    },
    3502: {
        "change_type": "contextual_reflow_and_title_normalization",
        "text": (
            f"간토관령 {ca('노리마사')}와 {cc('오기야쓰')} {ca('도모사다')},\n"
            f"고가 공방 {ca('하루우지')}까지 합세해\n"
            f"{cc('가와고에성')}을 치려 진군 중입니다!"
        ),
        "rationale": "古河公方은 한국어 역사 용어인 ‘고가 공방’으로 쓰고, ‘가와고에성을 치려 진군’ 전체를 한 의미 단위로 둔다.",
        "source_basis": "JP 関東管領・上杉憲政、扇谷上杉朝定、古河公方・足利晴氏…河越城を攻めんと兵を進めております.",
    },
    3505: {
        "change_type": "semantic_and_contextual_reflow_and_title_normalization",
        "text": (
            f"그럼, 설마… {ca('이마가와 요시모토')}가!?\n"
            f"{cb('다케다')}뿐 아니라 {cb('양 우에스기')}와 {cb('고가 공방')}까지\n"
            "모두 조종하는 건가!?"
        ),
        "rationale": "じゃ、まさか의 전환·경악을 복원하고, 両上杉·古河公方을 ‘양 우에스기’·‘고가 공방’으로 표기한다.",
        "source_basis": "JP じゃ、まさか…義元が！？ 武田だけじゃなく両上杉と古河公方まで全部操ってるってのか！",
    },
    3506: {
        "change_type": "semantic_and_contextual_reflow",
        "text": (
            "그래, 틀림없다.\n"
            f"그럼 {cc('가와고에성')}에 모인 적병은\n"
            "얼마나 되지?"
        ),
        "rationale": "원문의 河越城을 ‘가와고에성’으로 복원한다. 현재의 ‘가와고에’만으로는 성을 목표로 한 병력 집결이라는 뜻이 빠진다.",
        "source_basis": "JP 河越城に集った敵の兵数は？, EN enemy soldiers gathered near Kawagoe Castle.",
    },
    3508: {
        "change_type": "contextual_reflow_and_title_normalization",
        "text": (
            "8만… 쉽게 모을 수는 없지.\n"
            f"허나 {cb('양 우에스기')}와 {cb('고가 공방')}이 합세하면,\n"
            "수만을 넘길 수도 있겠군…"
        ),
        "rationale": "양 우에스기와 고가 공방이라는 두 세력을 한국어 표기로 통일하고, ‘합세하면’ 조건절을 주어와 함께 배치한다.",
        "source_basis": "JP だが、両上杉と古河公方が合力したのならば.",
    },
    3510: {
        "change_type": "contextual_reflow",
        "text": (
            f"……{ca('마고쿠로')}, {cc('가와고에성')}을 맡아 주겠느냐?\n"
            "이기라는 말은 하지 않겠다.\n"
            "지지 않고 버텨 주기만 하면 된다."
        ),
        "rationale": "‘맡아 주겠느냐’ 청유구를 분리하지 않고, 승리를 요구하지 않으며 버티기만 하면 된다는 세 문장을 보존한다.",
        "source_basis": "JP 河越城を頼めるか？ 勝て、とは言わぬ。負けずに持ちこたえてくれればいい.",
    },
    3514: {
        "change_type": "contextual_reflow_with_runtime_reservation",
        "text": (
            f"미안하다, {ca('마고쿠로')}. 아니, {ca('[bm790]')}!\n"
            "내가 저지른 실수를 네게 수습하게 하다니……"
        ),
        "rationale": "호칭 정정과 런타임 인명을 같은 발화에 두고, 尻拭い를 옮긴 ‘실수를 수습’의 의미를 한 문장으로 유지한다.",
        "source_basis": "JP 孫九郎。いや、[bm790]！ わしのしくじりの、尻拭いをさせてしまうとはな…",
    },
    3516: {
        "change_type": "contextual_reflow",
        "text": "형님, 지금은 그런 약한 소리 듣고 싶지 않아!\n내가 살아 돌아오면,\n그때 내 원망이나 실컷 들어 달라고!",
        "rationale": "‘듣고 싶지 않아’를 한 줄에 보존하고, 생환 뒤 불평을 충분히 들어 달라는 말은 별도 문장으로 둔다.",
        "source_basis": "JP 今はそんな泣き言は聞きたくねえな。むしろ生きて帰ったら、あとでたっぷり俺の恨み言を聞いてくれよ！",
    },
    3522: {
        "change_type": "contextual_reflow_with_runtime_reservation",
        "text": (
            f"부탁한다, {ca('[bm790]')}.\n"
            "서쪽을 정리하면 곧바로 구원하러 가겠다.\n"
            "그때까지 절대 죽어서는 안 된다!"
        ),
        "rationale": "런타임 인명 뒤의 문장을 닫고, ‘서쪽을 정리하면’ 조건절을 다음 줄에서 완결한다.",
        "source_basis": "JP 西を片付けたら、すぐさま救援に行く。それまで決して死んではならぬぞ！",
    },
    3526: {
        "change_type": "contextual_reflow_with_runtime_reservation",
        "text": (
            f"어려서부터 그 재능을 아버지 {ca('노부토라')}에게 인정받아,\n"
            f"{ca('[bm1251]')} 공을 싫어한 {ca('노부토라')}가\n"
            f"{cb('다케다 가문')} 당주로 세우려 했던 것으로 알려져 있다."
        ),
        "rationale": "‘다케다 가문 당주로 세우려’ 서술부를 분리하지 않고, 인명 토큰을 보존한 채 원문의 부친 평가·당주 추대 의도를 유지한다.",
        "source_basis": "JP 若くしてその器量を父・信虎に見込まれ、[bm1251]を嫌っていた信虎が武田家当主に据えようとしていた.",
    },
}

REFLOW_ONLY_IDS = (3490, 3493, 3497, 3510, 3514, 3516, 3522, 3526)
SEMANTIC_CHANGE_IDS = (3489, 3491, 3500, 3502, 3505, 3506, 3508)
RUNTIME_PROPOSAL_IDS = (3514, 3522, 3526)


class AuditError(RuntimeError):
    """Raised when a pinned input, protected structure, or audit drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_digest(value: str) -> str:
    return digest(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return str(path)


def load_table(path: Path, expected: Mapping[str, Any], label: str) -> tuple[dict[str, Any], tuple[str, ...]]:
    require(path.is_file(), f"missing {label}: {path}")
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(rebuild_message_table(table, table.texts) == raw, f"{label}: message table round-trip differs")
    profile = {
        "path": relative(path),
        "packed_sha256": digest(packed),
        "packed_size": len(packed),
        "raw_sha256": digest(raw),
        "raw_size": len(raw),
        "string_count": len(table.texts),
    }
    for key, value in expected.items():
        require(profile[key] == value, f"{label}: {key} drift")
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
        if character in "\r\n" or character == E:
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
        if value[cursor] == E:
            tag = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(tag) is not None, f"{entry_id}: malformed ESC tag {tag!r}")
            if tag == f"{E}CZ":
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


def normalized_visible(value: str) -> str:
    return "".join(character for character in ESC_RE.sub("", normalize_linebreaks(value)) if not character.isspace())


def read_reservations() -> Mapping[str, Mapping[str, Any]]:
    require(RESERVATION_MANIFEST.is_file(), f"missing reservation manifest: {RESERVATION_MANIFEST}")
    document = json.loads(RESERVATION_MANIFEST.read_text(encoding="utf-8"))
    reservations = document.get("reservations")
    require(isinstance(reservations, Mapping), "runtime reservation mapping missing")
    return reservations


def full_name_from_table(names: Sequence[str], source_name_id: int) -> str:
    require(0 <= source_name_id < len(names), f"runtime name ID outside strict table: {source_name_id}")
    return ESC_RE.sub("", normalize_linebreaks(names[source_name_id])).replace("\n", " ")


def line_metrics(
    entry_id: int,
    target: str,
    names: Sequence[str],
    reservations: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    for line_number, encoded_line in enumerate(normalize_linebreaks(target).split("\n"), 1):
        assert_colour_layout(encoded_line, entry_id)
        template = ESC_RE.sub("", encoded_line)
        runtime_items: list[dict[str, Any]] = []

        def replace_runtime(match: re.Match[str]) -> str:
            token = match.group(0)
            reservation = reservations.get(token)
            require(isinstance(reservation, Mapping), f"{entry_id}: missing reservation for {token}")
            source_name_id = reservation.get("source_name_id")
            reserved_raw = reservation.get("reserved_full_name_width_px")
            expected_hash = reservation.get("source_name_utf16le_sha256")
            require(isinstance(source_name_id, int), f"{entry_id}: invalid source name ID for {token}")
            require(isinstance(reserved_raw, int), f"{entry_id}: invalid reserved width for {token}")
            require(isinstance(expected_hash, str), f"{entry_id}: missing source name hash for {token}")
            strict_name = full_name_from_table(names, source_name_id)
            require(text_digest(names[source_name_id]) == expected_hash, f"{entry_id}: strict name hash drift for {token}")
            full_count = sum(is_full_width_visible(character) for character in strict_name)
            runtime_items.append(
                {
                    "token": token,
                    "source_name_id": source_name_id,
                    "strict_name_table_string": strict_name,
                    "strict_name_utf16le_sha256": text_digest(names[source_name_id]),
                    "full_name_display_full_width_character_count": full_count,
                    "full_name_display_half_width_character_count": len(strict_name) - full_count,
                    "reserved_raw_g1n_width_px": reserved_raw,
                    "reserved_effective_width_px": math.ceil(reserved_raw * RUNTIME_FONT_PX / RAW_FULL_WIDTH_PX),
                    "runtime_proven": False,
                    "reservation_policy": "Prefix semantics are not inferred. Reserve the catalogued full strict-table name and scale raw width by 30/48.",
                }
            )
            return strict_name

        display = RUNTIME_RE.sub(replace_runtime, template)
        literal = RUNTIME_RE.sub("", template)
        literal_full = sum(is_full_width_visible(character) for character in literal)
        literal_half = len(literal) - literal_full
        raw_literal = literal_full * RAW_FULL_WIDTH_PX + literal_half * RAW_HALF_WIDTH_PX
        raw_reserved = sum(item["reserved_raw_g1n_width_px"] for item in runtime_items)
        raw_width = raw_literal + raw_reserved
        effective_width = math.ceil(raw_width * RUNTIME_FONT_PX / RAW_FULL_WIDTH_PX)
        full_count = sum(is_full_width_visible(character) for character in display)
        metrics.append(
            {
                "line_number": line_number,
                "encoded_string": encoded_line,
                "display_string_template": template,
                "display_string": display,
                "raw_g1n_width_px": raw_width,
                "literal_raw_g1n_width_px": raw_literal,
                "reserved_raw_g1n_width_px": raw_reserved,
                "effective_width_px": effective_width,
                "full_width_character_count": full_count,
                "half_width_character_count": len(display) - full_count,
                "runtime_reservations": runtime_items,
                "runtime_display_proven": False,
                "exceeds_912px": effective_width > MAX_EFFECTIVE_WIDTH_PX,
                "exceeds_raw_1440px": raw_width > MAX_RAW_WIDTH_PX,
            }
        )
    return metrics


def layout_record(entry_id: int, value: str, names: Sequence[str], reservations: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    lines = line_metrics(entry_id, value, names, reservations)
    require(1 <= len(lines) <= MAX_LINES, f"{entry_id}: line count outside 1..{MAX_LINES}")
    require(not any(line["exceeds_912px"] for line in lines), f"{entry_id}: effective layout overflow")
    require(not any(line["exceeds_raw_1440px"] for line in lines), f"{entry_id}: raw layout overflow")
    return {
        "line_count": len(lines),
        "max_lines": MAX_LINES,
        "max_raw_g1n_width_px": max(line["raw_g1n_width_px"] for line in lines),
        "max_effective_width_px": max(line["effective_width_px"] for line in lines),
        "any_line_exceeds_912px": False,
        "all_lines_pass_static_patch_007": True,
        "lines": lines,
    }


def validate_authored_scope() -> None:
    require(TARGET_IDS == tuple(range(3_485, 3_527)), "target range drift")
    proposal_ids = tuple(PROPOSALS)
    require(proposal_ids == tuple(sorted(proposal_ids)), "proposal ordering drift")
    require(set(proposal_ids).issubset(TARGET_IDS), "proposal escapes target range")
    require(set(REFLOW_ONLY_IDS).isdisjoint(SEMANTIC_CHANGE_IDS), "change classification overlap")
    require(set(REFLOW_ONLY_IDS) | set(SEMANTIC_CHANGE_IDS) == set(proposal_ids), "change classification coverage drift")
    require(set(RUNTIME_PROPOSAL_IDS).issubset(REFLOW_ONLY_IDS), "runtime proposal scope drift")
    for entry_id, proposal in PROPOSALS.items():
        target = proposal.get("text")
        require(isinstance(target, str) and target, f"{entry_id}: proposal text missing")
        require("\x00" not in target, f"{entry_id}: embedded terminator")
        assert_colour_layout(target, entry_id)
        signature = control_signature(target)
        require(signature["printf_tokens"] == [], f"{entry_id}: unexpected printf token")
        require(signature["unknown_percent_count"] == 0, f"{entry_id}: unexpected percent")
        require(signature["other_c0_controls"] == [], f"{entry_id}: unexpected C0 control")


def source_summary(profile: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: profile[key]
        for key in ("path", "packed_sha256", "packed_size", "raw_sha256", "raw_size", "string_count")
    }


def build_bundle() -> tuple[dict[str, Any], dict[str, Any]]:
    validate_authored_scope()
    current_profile, current = load_table(CURRENT_PATH, CURRENT_EXPECTED, "Wave 100 strict Korean input")
    w98_profile, w98 = load_table(W98_PREDECESSOR_PATH, W98_PREDECESSOR_EXPECTED, "Wave 98 predecessor for rebase guard")
    require(
        all(current[entry_id] == w98[entry_id] for entry_id in TARGET_IDS),
        "Wave 100 rebase changed a 3485–3526 audit row",
    )
    sources: dict[str, tuple[dict[str, Any], tuple[str, ...]]] = {}
    for language, (path, expected) in SOURCES.items():
        sources[language] = load_table(path, expected, f"direct PC {language.upper()}")
    require(all(len(texts) == len(current) for _profile, texts in sources.values()), "source table count mismatch")
    reservations = read_reservations()

    entries: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    for entry_id in TARGET_IDS:
        baseline = current[entry_id]
        proposal = PROPOSALS.get(entry_id)
        target = str(proposal["text"]) if proposal else baseline
        assert_colour_layout(baseline, entry_id)
        assert_colour_layout(target, entry_id)
        baseline_signature = control_signature(baseline)
        target_signature = control_signature(target)
        jp_signature = control_signature(sources["jp"][1][entry_id])
        require(baseline_signature == target_signature, f"{entry_id}: proposal protected signature drift")
        require(baseline_signature == jp_signature, f"{entry_id}: Korean/JP protected signature drift")
        require(target_signature["unknown_percent_count"] == 0, f"{entry_id}: unknown percent")
        require(target_signature["other_c0_controls"] == [], f"{entry_id}: unexpected control")
        current_layout = layout_record(entry_id, baseline, current, reservations)
        target_layout = layout_record(entry_id, target, current, reservations)
        changed = target != baseline
        require(changed == (proposal is not None), f"{entry_id}: proposal/change accounting drift")
        if proposal:
            if entry_id in REFLOW_ONLY_IDS:
                require(normalized_visible(baseline) == normalized_visible(target), f"{entry_id}: reflow altered visible Korean")
            status = "static_high_confidence"
        else:
            status = "reviewed_preserve"
        status_counts[status] += 1
        source_texts = {language: texts[entry_id] for language, (_profile, texts) in sources.items()}
        source_hashes = {language: text_digest(text) for language, text in source_texts.items()}
        entries.append(
            {
                "entry_id": entry_id,
                "review_status": status,
                "changed_in_this_audit": changed,
                "change_type": proposal.get("change_type") if proposal else "reviewed_preserve",
                "review_judgement": proposal.get("rationale") if proposal else "원문·PC EN/SC/TC 대조 후 현재 한국어 문안과 문맥 개행을 유지했다.",
                "source_basis": proposal.get("source_basis") if proposal else "Direct PC JP/EN/SC/TC meaning corroboration; JP line breaks are not copied.",
                "current_ko": baseline,
                "proposed_ko": target,
                "direct_pc_sources": source_texts,
                "text_sha256_utf16le": {
                    "current_ko": text_digest(baseline),
                    "proposed_ko": text_digest(target),
                    **source_hashes,
                },
                "control_signature": {
                    "current": baseline_signature,
                    "proposed": target_signature,
                    "direct_pc_jp": jp_signature,
                    "direct_pc_en": control_signature(source_texts["en"]),
                    "direct_pc_sc": control_signature(source_texts["sc"]),
                    "direct_pc_tc": control_signature(source_texts["tc"]),
                },
                "runtime_token_policy": {
                    "runtime_tokens": target_signature["runtime_tokens"],
                    "runtime_proven": False,
                    "full_name_reservation_applied": bool(target_signature["runtime_tokens"]),
                    "prefix_semantics_inferred": False,
                },
                "current_layout": current_layout,
                "proposed_layout": target_layout,
                "review_policy": {
                    "japanese_source_linebreaks_used_as_layout_authority": False,
                    "korean_linebreaks_are_manual_semantic_boundaries": True,
                    "sentence_shortening_or_deletion_allowed": False,
                    "sentence_shortened_or_deleted": False,
                    "automatic_linebreak_stripping_forbidden": True,
                    "tag_internal_linebreak_allowed": False,
                },
            }
        )

    require(len(entries) == len(TARGET_IDS), "entry accounting drift")
    changed_ids = [entry["entry_id"] for entry in entries if entry["changed_in_this_audit"]]
    require(changed_ids == list(PROPOSALS), "changed-ID ordering drift")
    require(all(entry["proposed_layout"]["all_lines_pass_static_patch_007"] for entry in entries), "proposal layout failure")
    require(all(not entry["review_policy"]["sentence_shortened_or_deleted"] for entry in entries), "shortening policy drift")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "resource": RESOURCE,
            "target_ids": list(TARGET_IDS),
            "target_row_count": len(TARGET_IDS),
            "event_name": "호조·이마가와 / 가와고에 전개와 다케다 노부시게 도입",
            "wave100_rebase_range_identical_to_wave98": True,
            "candidate_binary_created": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "release_published": False,
            "network_operation_performed": False,
        },
        "sources": {
            "strict_korean_input": source_summary(current_profile),
            "wave98_predecessor_for_nonoverlap_check": source_summary(w98_profile),
            "direct_pc_jp_pristine": source_summary(sources["jp"][0]),
            "direct_pc_en": source_summary(sources["en"][0]),
            "direct_pc_sc": source_summary(sources["sc"][0]),
            "direct_pc_tc": source_summary(sources["tc"][0]),
            "runtime_reservation_manifest": {
                "path": relative(RESERVATION_MANIFEST),
                "sha256": digest(RESERVATION_MANIFEST.read_bytes()),
            },
        },
        "layout_baseline": {
            "authority": "Static Patch 007 verified PK event-dialogue layout",
            "runtime_font_px": RUNTIME_FONT_PX,
            "runtime_line_spacing_setting": 8,
            "runtime_usable_line_width_px": MAX_EFFECTIVE_WIDTH_PX,
            "max_lines": MAX_LINES,
            "raw_g1n_full_width_advance_px": RAW_FULL_WIDTH_PX,
            "raw_g1n_half_width_advance_px": RAW_HALF_WIDTH_PX,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "raw_g1n_pass_limit_px": MAX_RAW_WIDTH_PX,
            "effective_width_pass_limit_px": MAX_EFFECTIVE_WIDTH_PX,
            "runtime_name_reservation": "Catalogued full-name raw G1N width, scaled by 30/48; runtime prefix rendering is not inferred.",
        },
        "coverage": {
            "status_counts": dict(sorted(status_counts.items())),
            "static_high_confidence_ids": changed_ids,
            "static_high_confidence_count": len(changed_ids),
            "contextual_reflow_only_ids": list(REFLOW_ONLY_IDS),
            "semantic_change_ids": list(SEMANTIC_CHANGE_IDS),
            "runtime_reservation_proposal_ids": list(RUNTIME_PROPOSAL_IDS),
            "runtime_or_ui_hold_ids": [],
            "reviewed_preserve_ids": [entry_id for entry_id in TARGET_IDS if entry_id not in PROPOSALS],
            "all_current_lines_within_static_patch_007": True,
            "all_proposed_lines_within_static_patch_007": True,
            "all_current_and_proposed_rows_within_four_lines": True,
            "sentence_shortening_or_deletion": False,
        },
        "entries": entries,
        "policy": {
            "only_korean_binary_input": relative(CURRENT_PATH),
            "direct_pc_jp_en_sc_tc_read_only_evidence": True,
            "switch_translation_used": False,
            "japanese_source_linebreaks_not_reused": True,
            "korean_manual_breaks_are_semantic": True,
            "sentence_shortening_or_deletion_allowed": False,
            "no_candidate_binary": True,
            "no_steam_git_release_or_network_action": True,
        },
    }
    validation = {
        "schema": SCHEMA + ".validation",
        "status": "PASS",
        "target_row_count": len(TARGET_IDS),
        "wave100_rebase_range_identical_to_wave98": True,
        "static_high_confidence_count": len(changed_ids),
        "runtime_or_ui_hold_count": 0,
        "all_proposed_lines_within_static_patch_007": True,
        "all_rows_within_four_lines": True,
        "candidate_binary_created": False,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }
    return report, validation


def source_whitespace_check() -> None:
    for path in (SCRIPT, WORKSTREAM / "README_KO.md", WORKSTREAM / "test_pc_event_kanto_audit_v1.py"):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def write_report(report: Mapping[str, Any], validation: Mapping[str, Any]) -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(canonical_json(report))
    VALIDATION.write_bytes(canonical_json(validation))


def verify_report() -> dict[str, Any]:
    report, validation = build_bundle()
    require(OUTPUT.is_file(), f"report missing: {OUTPUT}")
    require(VALIDATION.is_file(), f"validation missing: {VALIDATION}")
    require(OUTPUT.read_bytes() == canonical_json(report), "public report differs from deterministic audit")
    require(VALIDATION.read_bytes() == canonical_json(validation), "validation differs from deterministic audit")
    return {
        "status": "PASS",
        "report": relative(OUTPUT),
        "target_row_count": len(TARGET_IDS),
        "static_high_confidence_count": len(PROPOSALS),
        "candidate_binary_created": False,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "profile"))
    command = parser.parse_args().command
    source_whitespace_check()
    report, validation = build_bundle()
    if command == "build":
        write_report(report, validation)
        print(relative(OUTPUT))
        return 0
    if command == "verify":
        print(json.dumps(verify_report(), ensure_ascii=False, sort_keys=True))
        return 0
    print(json.dumps(report["coverage"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
