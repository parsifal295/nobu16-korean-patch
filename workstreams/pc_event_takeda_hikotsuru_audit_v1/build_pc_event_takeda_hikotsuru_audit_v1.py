#!/usr/bin/env python3
"""Build a read-only PC event audit for the 3527–3564 Takeda/Hikotsuru range.

The audit consumes the pinned Wave 101 private Korean candidate and direct PC
JP/EN/SC/TC resources as read-only evidence. It writes a deterministic report
under this workstream only; it never writes a candidate binary, Steam, Git,
release, or network state.
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
OUTPUT = PUBLIC / "pc_event_takeda_hikotsuru_audit.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-takeda-hikotsuru-audit.v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
ROW_COUNT = 17_916
TARGET_IDS = tuple(range(3_527, 3_565))

RUNTIME_FONT_PX = 30
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
MAX_RAW_WIDTH_PX = 1_440
MAX_EFFECTIVE_WIDTH_PX = 912
MAX_LINES = 4

# The task began from Wave 100. Wave 101 was created while this audit was
# starting, and its exact 3489–3526 diff is non-overlapping with this scope.
CURRENT_PATH = (
    REPO
    / "tmp"
    / "pc_event_kanto_quality_wave101_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
CURRENT_EXPECTED: Mapping[str, Any] = {
    "packed_sha256": "96DBB584AE96157E3B7013CAF86A4876CDB0B87EFF66433CB9236206996C2D91",
    "packed_size": 1_048_079,
    "raw_sha256": "507F8FB7CF75D327F8CC88725E17BE3DA1084C4BD96237B9F1A1E8CE5F9D3B41",
    "raw_size": 1_043_960,
    "string_count": ROW_COUNT,
}
W100_PREDECESSOR_PATH = (
    REPO
    / "tmp"
    / "pc_event_ending_regions_quality_wave100_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
W100_PREDECESSOR_EXPECTED: Mapping[str, Any] = {
    "packed_sha256": "245043679E4A7A75628519829C1B16372A8FD085A1CC7F0F4EE97F52BB66BA60",
    "packed_size": 1_048_043,
    "raw_sha256": "F7DB831E850F191CC6320E54BF878DCC8B7F3DC4F5D51AD66379D64617F553ED",
    "raw_size": 1_043_924,
    "string_count": ROW_COUNT,
}
W101_REBASE_CHANGED_IDS = (
    3489,
    3490,
    3491,
    3493,
    3497,
    3500,
    3502,
    3505,
    3506,
    3508,
    3510,
    3514,
    3516,
    3522,
    3526,
)

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


# These are audit proposals only. No candidate binary is created here. Every
# authored manual LF is a Korean semantic boundary, never a copied JP LF.
PROPOSALS: Mapping[int, Mapping[str, str]] = {
    3529: {
        "change_type": "semantic_and_contextual_reflow",
        "text": "아, 주군이시군요.\n태어날 아이들을 위해\n가훈을 만들고 있었습니다.",
        "rationale": "これは御館様의 자연스러운 발견형 호칭과 生まれてくる子의 복수 대상을 복원한다.",
        "source_basis": "JP これは御館様・生まれてくる子のため, EN children that are to born, SC/TC 将要出生的孩子·即將出生的孩子.",
    },
    3530: {
        "change_type": "semantic_and_contextual_reflow",
        "text": (
            "……주군이라 부르지 말거라.\n"
            "우리는 형제가 아니냐.\n"
            "그래, 어떤 가훈을 만들고 있느냐?\n"
            "내게도 보여 주겠느냐?"
        ),
        "rationale": "御館様はやめよ의 대상은 ‘주군’이라는 호칭 자체이므로, 현재의 생략된 목적어를 복원한다.",
        "source_basis": "JP 御館様はやめよ、我らは兄弟ではないか, EN stop calling me lord; we are brothers.",
    },
    3532: {
        "change_type": "typographic_and_contextual_reflow",
        "text": "음……\n“제1조, 영원히 주군을\n배반해서는 안 된다.”",
        "rationale": "조문 번호와 본문을 문장부호로 구분하고, ‘주군을 배반’이라는 서술 단위를 한 줄에 보존한다.",
        "source_basis": "JP 其の一 未来永劫、御館様に背くようなことがあってはならない.",
    },
    3533: {
        "change_type": "typographic_and_contextual_reflow",
        "text": "“제2조, 주군에게 받은 녹봉에\n절대로 불만을 품어서는 안 된다.”",
        "rationale": "둘째 줄 첫머리의 수동 삽입 공백을 제거하고, 조문 번호와 본문을 한국어 문장으로 정리한다.",
        "source_basis": "JP 其の二 御館様からいただく扶持に決して不満を持ってはならない.",
    },
    3536: {
        "change_type": "contextual_reflow",
        "text": (
            f"그, 그러냐…… 조금만 더,\n"
            f"{cb('다케다 가문')} 밖에서도 쓸 만한 내용으로\n"
            "만들 수 없겠느냐?"
        ),
        "rationale": "‘쓸 만한 내용’이라는 명사구를 같은 줄에 두어 기존의 단어 경계 분절을 해소한다.",
        "source_basis": "JP 武田の外でも役立つものにはできぬのか.",
    },
    3539: {
        "change_type": "semantic_and_contextual_reflow",
        "text": (
            f"생각해 보면 아버지는 너에게야말로\n"
            f"{cb('다케다 가문')}의 당주 자리를 물려주려 하셨다.\n"
            "그래서 남몰래 가보를 네게 주셨던 게 아니냐?"
        ),
        "rationale": "お前にこそ의 강조와 武田の当主の座라는 가문 당주 지위를 복원한다.",
        "source_basis": "JP お前にこそ武田の当主の座を譲ろうとしていた, EN intended you to take the position as leader of the clan.",
    },
    3540: {
        "change_type": "semantic_grammar_correction",
        "text": "예, 모두 형님께 바쳤습니다만.",
        "rationale": "문맥 없이 이어지는 ‘하지만’을 일본어 のですが의 여운을 남기는 ‘습니다만’으로 바로잡는다.",
        "source_basis": "JP はい、すべて兄上に献上いたしましたが, EN I have offered it all to you, Brother.",
    },
    3541: {
        "change_type": "semantic_correction",
        "text": "(아버지의 뜻도 헛되었겠군……)",
        "rationale": "父上も報われぬ는 아버지가 의도한 후계 구상이 이루어지지 않았다는 뜻이므로 ‘보람’의 주체를 아버지의 뜻으로 바로잡는다.",
        "source_basis": "JP 父上も報われぬな, SC 父亲的愿望一点都没得到回报, TC 父親大人的願望並沒有實現.",
    },
    3542: {
        "change_type": "semantic_and_contextual_reflow",
        "text": (
            f"형님께는 {cb('다케다')}를 천하로 이끌 힘이 있습니다.\n"
            "저는 작은 재주밖에 없으니,\n"
            "그저 형님을 믿고 따를 뿐입니다."
        ),
        "rationale": "武田を天下に導く力가 ‘형님께 있는 힘’이라는 구조와 小才しか持たぬ의 겸양을 복원한다.",
        "source_basis": "JP 兄上には武田を天下に導く力がございます。小才しか持たぬ私は…, EN power to bring these lands under Takeda control.",
    },
    3546: {
        "change_type": "contextual_reflow",
        "text": f"({ca('덴큐 노부시게')}, 가신으로서는\n이보다 나은 장수가 없겠지……)",
        "rationale": "둘째 줄 첫머리의 수동 삽입 공백을 제거하고, 고유명사와 가신으로서의 평가는 그대로 보존한다.",
        "source_basis": "JP 典厩信繁、家臣としては、これほどの将はあるまい.",
    },
    3547: {
        "change_type": "contextual_reflow",
        "text": (
            "(하지만 우리는 피를 나눈 형제다.\n"
            "육친의 정 같은 것이 있어도 좋을 텐데.\n"
            "그렇게 생각하는 건 내 어리광일까……)"
        ),
        "rationale": "둘째·셋째 줄 첫머리의 수동 삽입 공백만 제거해 각 문장 단위를 그대로 유지한다.",
        "source_basis": "JP 我らは血の繋がった兄弟。肉親の情らしきものがあってもよい。",
    },
    3548: {
        "change_type": "semantic_and_contextual_reflow_with_runtime_reservation",
        "text": (
            "99개 조항에 이르는 다케다 노부시게의 가훈에는,\n"
            f"{ca('[bm1251]')} 공에게 충성을 맹세하게 하는 항목뿐 아니라,\n"
            "무사의 생활 규범을 보인 항목도 많았으며……"
        ),
        "rationale": "忠義を誓わせる를 ‘충성을 맹세하게 하는’으로, 示す를 ‘보인’으로 바로잡는다. 런타임 이름의 접두사 의미는 추측하지 않는다.",
        "source_basis": "JP [bm1251]への忠義を誓わせる項目以外にも武士の生活規範を示す項目も多くあり.",
    },
    3550: {
        "change_type": "semantic_restoration_and_contextual_reflow",
        "text": (
            f"{cb('류조지')} 가문의 전략을 맡은 참모 {ca('나베시마 나오시게')}.\n"
            "그 바쁜 나날을 내조의 공으로 뒷받침한 이는\n"
            f"사랑하는 아내 {ca('히코쓰루히메')}였다."
        ),
        "rationale": "‘내조로 받친’ 오기를 고치고, 龍造寺家의 전략·内助の功·恋女房의 정보를 모두 복원한다.",
        "source_basis": "JP 龍造寺家の戦略を担う参謀・鍋島直茂。その多忙な日々を内助の功で支えたのが恋女房の彦鶴姫.",
    },
    3551: {
        "change_type": "semantic_restoration_and_contextual_reflow",
        "text": (
            "두 사람의 인연의 시작은 전설로 전해진다.\n"
            "어느 날 전투에서 개선해 돌아오던 길에,\n"
            f"{ca('나오시게')}는 {cc('이이모리성')}에서 {ca('히코쓰루')}에게\n"
            "첫눈에 반했다고 한다……"
        ),
        "rationale": "馴れ初め·ある時·見初めた의 인연 시작, 어느 날, 첫눈에 반함을 복원한다. ‘처음 보았다’만으로는 見初めた의 뜻이 빠진다.",
        "source_basis": "JP 二人の馴れ初めは伝説に彩られている。ある時、合戦から凱旋帰国する途中、直茂は飯盛城で彦鶴を見初めた.",
    },
    3554: {
        "change_type": "semantic_grammar_correction",
        "text": "예상치 못하게 많은 장병이 찾아오자,\n점심 준비에 쫓긴 시녀들은\n큰 혼란에 빠졌다.",
        "rationale": "예상치 못한 대상은 ‘많은 장병의 방문’이므로 어순을 바로잡고, 準備に追われた의 다급함을 보존한다.",
        "source_basis": "JP 予期せぬ大人数の将兵が訪れたため、昼食の準備に追われた侍女たちは大混乱に陥っていた.",
    },
    3555: {
        "change_type": "contextual_reflow",
        "text": "여러분, 조금 진정하세요!\n손님 수만큼 정어리를 준비해 두었습니다.\n일을 나눠 차례대로 구우면 됩니다!",
        "rationale": "‘손님 수만큼’을 한 의미 단위로 붙여 기존의 수동 줄 분절을 해소한다.",
        "source_basis": "JP お客様の人数分の鰯は用意してあります。作業を分担して順に焼いていけばよろしい.",
    },
    3559: {
        "change_type": "contextual_reflow",
        "text": "(훌륭한 지시로 시녀들을 이끌며\n수많은 정어리를 굽고 있다……\n저토록 현명한 여인이 있다니.)",
        "rationale": "둘째·셋째 줄 첫머리의 수동 삽입 공백만 제거해 독백의 세 의미 단위를 유지한다.",
        "source_basis": "JP 見事な指図で、侍女たちをまとめ大量の鰯を焼いている…賢い女性もいたものだな.",
    },
    3561: {
        "change_type": "semantic_honorific_restoration_and_contextual_reflow",
        "text": (
            f"저분은 {ca('이시이 쓰네노부')}의 따님,\n"
            f"{ca('히코쓰루')} 님입니다. 예전에는\n"
            f"{ca('노토미 노부즈미')} 님께 시집가셨으나,\n"
            f"{ca('노토미')} 님이 전사하시어 과부가 되셨습니다……"
        ),
        "rationale": "ご息女・様・殿의 대화체 경어를 복원하고, 후가가 된 사정을 존대 서술로 유지한다.",
        "source_basis": "JP 石井常延のご息女彦鶴様。以前は納富信澄殿に嫁いでおられましたが、納富殿が戦死されたため、後家となられ.",
    },
    3563: {
        "change_type": "semantic_restoration_and_contextual_reflow",
        "text": (
            "재치를 발휘해 시녀들을 지휘할 뿐 아니라\n"
            f"앞장서 정어리를 굽는 {ca('히코쓰루')}의 솜씨에\n"
            f"매료된 {ca('나오시게')}는 훗날 정식으로 청혼했다."
        ),
        "rationale": "機転を利かせて·だけでなく·率先して의 재치, 병행, 솔선을 복원한다.",
        "source_basis": "JP 機転を利かせて、侍女を差配するだけでなく率先して鰯を焼く彦鶴の手際の良さに魅了された直茂.",
    },
    3564: {
        "change_type": "semantic_restoration_and_contextual_reflow",
        "text": (
            "전국시대에는 드문 연애결혼으로\n"
            f"아내가 된 {ca('히코쓰루')}는 총명함과 포용력으로\n"
            f"냉철한 군사 {ca('나베시마 나오시게')}를\n"
            "뒷받침했다고 한다……"
        ),
        "rationale": "戦国時代としては, 軍師, 支えたという의 시대 맥락·책사 직위·전승형 서술을 복원한다.",
        "source_basis": "JP 戦国時代としては珍しい恋愛結婚で妻に迎えられた彦鶴は、聡明さと包容力で冷徹なる軍師・鍋島直茂を支えたという.",
    },
}

REFLOW_ONLY_IDS = (3536, 3546, 3547, 3555, 3559)
TYPOGRAPHIC_REFLOW_IDS = (3532, 3533)
SEMANTIC_PROPOSAL_IDS = (
    3529,
    3530,
    3539,
    3540,
    3541,
    3542,
    3548,
    3550,
    3551,
    3554,
    3561,
    3563,
    3564,
)
RUNTIME_PROPOSAL_IDS = (3548,)
PRESERVE_NOTES: Mapping[int, str] = {
    3527: "장면 표제는 현재 고유명사 표기와 보호 태그를 유지한다.",
    3549: "고슈 법도지차제는 이 범위의 직접 대조만으로 대체 독음을 확정할 근거가 없어 기존 표기를 유지한다.",
}


class AuditError(RuntimeError):
    """Raised when an input, protected structure, or deterministic report drifts."""


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


def layout_record(
    entry_id: int,
    value: str,
    names: Sequence[str],
    reservations: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
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
    require(TARGET_IDS == tuple(range(3527, 3565)), "target range drift")
    proposal_ids = tuple(PROPOSALS)
    require(proposal_ids == tuple(sorted(proposal_ids)), "proposal ordering drift")
    require(set(proposal_ids).issubset(TARGET_IDS), "proposal escapes target range")
    groups = (set(REFLOW_ONLY_IDS), set(TYPOGRAPHIC_REFLOW_IDS), set(SEMANTIC_PROPOSAL_IDS))
    require(not groups[0] & groups[1] and not groups[0] & groups[2] and not groups[1] & groups[2], "classification overlap")
    require(set(proposal_ids) == set().union(*groups), "proposal classification coverage drift")
    require(set(RUNTIME_PROPOSAL_IDS).issubset(SEMANTIC_PROPOSAL_IDS), "runtime proposal scope drift")
    require(set(W101_REBASE_CHANGED_IDS).isdisjoint(TARGET_IDS), "Wave 101 overlaps this audit")
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
    current_profile, current = load_table(CURRENT_PATH, CURRENT_EXPECTED, "Wave 101 strict Korean input")
    w100_profile, w100 = load_table(W100_PREDECESSOR_PATH, W100_PREDECESSOR_EXPECTED, "Wave 100 predecessor")
    rebase_changed_ids = [entry_id for entry_id, (before, after) in enumerate(zip(w100, current)) if before != after]
    require(rebase_changed_ids == list(W101_REBASE_CHANGED_IDS), "Wave 101 rebase diff scope drift")
    require(
        all(current[entry_id] == w100[entry_id] for entry_id in TARGET_IDS),
        "Wave 101 rebase changed a 3527–3564 audit row",
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
            judgement = proposal["rationale"]
            basis = proposal["source_basis"]
        else:
            status = "reviewed_preserve"
            judgement = PRESERVE_NOTES.get(
                entry_id,
                "순정 PC JP와 PC EN/SC/TC의 의미·보호 구조를 대조한 뒤 현재 한국어 문안과 문맥 개행을 유지했다.",
            )
            basis = "Direct PC JP/EN/SC/TC meaning corroboration; JP line breaks are not copied."
        status_counts[status] += 1
        source_texts = {language: texts[entry_id] for language, (_profile, texts) in sources.items()}
        source_hashes = {language: text_digest(text) for language, text in source_texts.items()}
        entries.append(
            {
                "entry_id": entry_id,
                "review_status": status,
                "changed_in_this_audit": changed,
                "change_type": proposal.get("change_type") if proposal else "reviewed_preserve",
                "review_judgement": judgement,
                "source_basis": basis,
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
            "event_name": "다케다 노부시게 가훈 및 나베시마 나오시게·히코쓰루 장면",
            "strict_input_rebased_from_wave100_to_wave101": True,
            "wave101_changed_ids": list(rebase_changed_ids),
            "wave101_changed_range_nonoverlapping_with_target": True,
            "target_range_identical_between_wave100_and_wave101": True,
            "candidate_binary_created": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "release_published": False,
            "network_operation_performed": False,
        },
        "sources": {
            "strict_korean_input": source_summary(current_profile),
            "wave100_predecessor_for_nonoverlap_check": source_summary(w100_profile),
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
            "typographic_contextual_reflow_ids": list(TYPOGRAPHIC_REFLOW_IDS),
            "semantic_change_ids": list(SEMANTIC_PROPOSAL_IDS),
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
        "strict_input_rebased_from_wave100_to_wave101": True,
        "wave101_changed_range_nonoverlapping_with_target": True,
        "static_high_confidence_count": len(changed_ids),
        "runtime_or_ui_hold_count": 0,
        "all_current_lines_within_static_patch_007": True,
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
    for path in (SCRIPT, WORKSTREAM / "README_KO.md", WORKSTREAM / "test_pc_event_takeda_hikotsuru_audit_v1.py"):
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
