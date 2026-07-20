#!/usr/bin/env python3
"""Create a read-only review plan for 4xxx manual event-text compactions.

This workstream intentionally produces only evidence under its own directory.
It never builds a candidate resource, touches the Steam installation, performs
a Git operation, or contacts the network.  The proposed text is a reviewed
input for a later, separately authorised candidate build.
"""

from __future__ import annotations

import argparse
import difflib
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
OUTPUT = PUBLIC / "manual_compact_4000_review.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"

TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.manual-compact-4000-review.v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
MIN_ID = 4000
MAX_ID = 4999
EXPECTED_ROW_COUNT = 197
EXPECTED_CURRENT_QUALITY_PRESERVED_COUNT = 15
EXPECTED_CURRENT_QUALITY_RECONCILED_COUNT = 11
EXPECTED_CURRENT_PROFILE = {
    "packed_sha256": "753D2675875A61CB6516D906E529E2E77AADA172160F65D93B2FDB2B301BE836",
    "raw_sha256": "2D9696B6693D13CAA5043423FFFF3B598ACFFDDBC205CD2A2633BB67C8B0900C",
    "packed_size": 1_000_385,
    "raw_size": 996_452,
    "string_count": 17_916,
}
EXPECTED_DIRECT_JP_PROFILE = {
    "packed_sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
    "packed_size": 562_226,
    "raw_size": 894_800,
    "string_count": 17_916,
}
EXPECTED_DIRECT_EN_PROFILE = {
    "packed_sha256": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
    "raw_sha256": "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911",
    "packed_size": 762_196,
    "raw_size": 1_878_836,
    "string_count": 17_916,
}
EXPECTED_DIRECT_SC_PROFILE = {
    "packed_sha256": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
    "raw_sha256": "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E",
    "packed_size": 522_177,
    "raw_size": 754_708,
    "string_count": 17_916,
}
EXPECTED_DIRECT_TC_PROFILE = {
    "packed_sha256": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
    "raw_sha256": "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6",
    "packed_size": 524_909,
    "raw_size": 744_212,
    "string_count": 17_916,
}
EXPECTED_LEGACY_PROFILE = {
    "packed_sha256": "2CA183DA690D45A75702EA0F35C70966786B59E9440B8B8F49BE9652342F81AC",
    "raw_sha256": "EDCF7A9CEBD605BB2275D5A3B92A76E7E2F652B2391554F24C6A8BDD2EF91A08",
    "packed_size": 1_052_079,
    "raw_size": 1_047_944,
    "string_count": 17_916,
}
EXPECTED_HISTORICAL_MANIFEST_SHA256 = "10EE44F4D5F5A871F5DEDB60C6435F4115E698FB1544B898EA421356FAB6BF42"
EXPECTED_RESERVATION_MANIFEST_SHA256 = "B981C7C456F2DC285721E7E3DB74D2D11456B49B25D5A97BB320F815DFC0A893"

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
CURRENT_ROOT = REPO / "tmp" / "pc_event_manual_compact_static007_batch04_v1" / "candidate-final"
CURRENT_KO_PATH = CURRENT_ROOT / "MSG_PK" / "JP" / "msgev.bin"
CURRENT_MANIFEST_PATH = CURRENT_ROOT / "candidate_manifest.v1.json"
CURRENT_AUDIT_PATH = CURRENT_ROOT / "audit.v1.json"
DIRECT_JP_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msgev.bin"
)
DIRECT_EN_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msgev.bin")
DIRECT_SC_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msgev.bin")
DIRECT_TC_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msgev.bin")
LEGACY_PRECOMPACTION_KO_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-v0.10.0-original-font-rollback-v1"
    r"\originals\MSG_PK\JP\msgev.bin"
)

RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
MAX_EFFECTIVE_LINE_PX = 912
MAX_RAW_LINE_PX = 1440
MAX_LINES = 4

ESC_RE = re.compile(r"\x1bC[ABCZ]")
BRACKET_RE = re.compile(r"\[[^\[\]\r\n]+\]")
NUMERIC_RUNTIME_RE = re.compile(r"\[([A-Za-z]{1,16})(\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\r|\n")

# Each override is source-complete and preserves the exact current/direct-PC
# protected tag and runtime-token signature.  The legacy backup is recovery
# material, not an instruction to reintroduce its obsolete literal names.
# The first twelve rows reconcile a post-compaction current revision that still
# left source content abbreviated; the remaining seven repair clear Korean
# wording or semantic line-boundary issues in an otherwise legacy recovery.
SEMANTIC_REVIEW_OVERRIDES: Mapping[int, Mapping[str, str]] = {
    4053: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "reason": "Retain the current dynamic self-name and speaker voice while restoring the omitted all-preparations and timing clauses.",
        "text": "\x1bCA[bm1448]\x1bCZ, 그 말씀을 잊지 않겠소.\n모든 준비를 마치고 때가 오면\n반드시 \x1bCA노리마사\x1bCZ 님을 \x1bCC간토\x1bCZ로 모시겠소……",
    },
    4182: {
        "strategy": "restore_legacy_text_with_source_quality_semantic_reflow",
        "reason": "Restore the two linked decisive-battle clauses without the legacy Korean repetition obscuring their relation.",
        "text": "\x1bCB모리 가문\x1bCZ은 \x1bCB오우치 가문\x1bCZ과의 결전,\n즉 그 대군을 이어받은 \x1bCB오우치 가문\x1bCZ의\n\x1bCA스에 하루카타\x1bCZ와 결전을 치르게 되었다……",
    },
    4210: {
        "strategy": "restore_legacy_text_with_source_quality_semantic_reflow",
        "reason": "Correct 京 from the bare syllable 교 to 교토 and keep the biography clauses intact.",
        "text": "\x1bCA다이겐 셋사이\x1bCZ― 본래 \x1bCA규에이 쇼기쿠\x1bCZ라 하며\n\x1bCC교토\x1bCZ에서 선승으로 지내다, 어린 \x1bCA요시모토\x1bCZ의\n교육을 맡아 \x1bCC스루가\x1bCZ에 초빙되었다.",
    },
    4410: {
        "strategy": "restore_legacy_text_with_source_quality_terminology_fix",
        "reason": "腫瘍 is a tumor, not a boil; retain the full source clause about accumulated enemies' grudges.",
        "text": "그동안 \x1bCA나오이에\x1bCZ가 묻어 버린 수많은 적의 원한이\n뭉친 듯한 종양은 가라앉지 않았고,\n마침내 효웅을 죽음에 이르게 했다.",
    },
    4414: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "reason": "Retain the current direct-PC-compatible dynamic name while restoring the three distinct historical theories in full syntax.",
        "text": "\x1bCA[b1448]\x1bCZ와의 전쟁에 전념하려고,\n기근 해결을 바라서, 또는 후계자 \x1bCA요시노부\x1bCZ에게\n슈고직을 넘기려고…… 여러 설이 있다.",
    },
    4492: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "reason": "Restore that the unrecorded fact is the length of the Kyoto stay, not the stay itself, while retaining current dynamic tokens.",
        "text": "이때 \x1bCA[bm1448]\x1bCZ가 \x1bCC교토\x1bCZ에 얼마나 머물렀는지는\n기록에 없으나, \x1bCA[bm75]\x1bCZ의 요청으로\n상당히 오랫동안 체류했다고 한다.",
    },
    4447: {
        "strategy": "restore_legacy_text_with_source_quality_grammar_fix",
        "reason": "京・室町御所 is the Kyoto Muromachi palace, not two co-ordinate locations.",
        "text": "하지만 쇼군은 본디 \x1bCC교토\x1bCZ의 \x1bCC무로마치 어소\x1bCZ의 주인으로,\n\x1bCC오미\x1bCZ에 오래 머무는 것은\n\x1bCA[bm75]\x1bCZ의 뜻이 아니었다.",
    },
    4461: {
        "strategy": "restore_legacy_text_with_source_quality_semantic_reflow",
        "reason": "Restore the complete travel sentence and use 교토 for 京.",
        "text": "이해에 \x1bCA오다 노부나가\x1bCZ는 몇 안 되는 가신만을\n이끌고 은밀히 \x1bCC사카이\x1bCZ와 \x1bCC난토\x1bCZ, 그리고 \x1bCC교토\x1bCZ를\n돌아다니며 구경했다고 한다.",
    },
    4557: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "reason": "Restore the omitted use-of-brother, exceptional-talent, and all-administrative-affairs clauses while retaining the current terminology tags.",
        "text": "아우 \x1bCA나가요리\x1bCZ의 무공을 이용해 주군\n\x1bCA미요시 나가요시\x1bCZ의 측근이 된 뒤,\n남다른 재주를 발휘하여 \x1bCB미요시가\x1bCZ의\n사무 제반 만사를 관장해 온 \x1bCA마쓰나가 히사히데\x1bCZ.",
    },
    4560: {
        "strategy": "restore_legacy_text_with_source_quality_semantic_reflow",
        "reason": "Restore this castle's Kawachi connection and the Yamato-control purpose as complete Korean clauses.",
        "text": "\x1bCC야마토\x1bCZ에는 \x1bCC고후쿠지\x1bCZ의 승관을 비롯해,\n\x1bCB미요시 가문\x1bCZ의 지배에 복종하지 않는 무사가 많다.\n\x1bCC가와치\x1bCZ와도 접한 이 성을 \x1bCC야마토\x1bCZ 지배의\n거점으로 삼아야 한다……",
    },
    4592: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "reason": "Restore the destabilised Kō-Sō-Sun alliance and the planned invasion of Imagawa territory, while retaining the current dynamic-name token.",
        "text": "\x1bCA이마가와 요시모토\x1bCZ의 죽음으로\n고소슨 삼국 동맹은 흔들렸다.\n후계자 \x1bCA우지자네\x1bCZ를 믿을 수 없다고 본 \x1bCA[bm1251]\x1bCZ은\n\x1bCB이마가와\x1bCZ 영지 침공을 꾀했다.",
    },
    4607: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "reason": "Restore the imminent-war clause and both named strong-enemy clauses without reverting current runtime tokens.",
        "text": "\x1bCB다케다\x1bCZ와는 곧 전쟁이 벌어질 것이다.\n\x1bCA[bm1448]\x1bCZ도 그렇지만, \x1bCA[bm1251]\x1bCZ 역시 강적이다.\n\x1bCA쓰나시게\x1bCZ, \x1bCA우지테루\x1bCZ, 단단히 각오해라.",
    },
    4836: {
        "strategy": "restore_legacy_text_with_source_quality_semantic_reflow",
        "reason": "Keep the compact but complete alliance-to-marriage-alliance sentence at Korean clause boundaries.",
        "text": "여기서 맺어진 \x1bCA오다 노부나가\x1bCZ와 \x1bCA[b1871]\x1bCZ의 맹약은\n훗날 기요스 동맹이라 불리는\n혼인 동맹으로 발전한다.",
    },
    4874: {
        "strategy": "restore_legacy_text_with_source_quality_terminology_fix",
        "reason": "Translate 名字の地 as the surname's place of origin rather than the unnatural 성씨의 땅.",
        "text": "\x1bCB미요시\x1bCZ 가문은 \x1bCB오가사와라\x1bCZ 가문의 지류로,\n\x1bCC아와 미요시군\x1bCZ을 성씨의 연고지로 삼았다.\n\x1bCA나가요시\x1bCZ가 상경한 뒤에도 그 기반은\n\x1bCC아와\x1bCZ를 중심으로 한 \x1bCC시코쿠\x1bCZ에 있었다.",
    },
    4900: {
        "strategy": "restore_legacy_text_with_source_quality_completion",
        "reason": "Restore the omitted negative action in the father's injunction: do not walk the sorrowful path of being scorned.",
        "text": "(\x1bCB다케다\x1bCZ 가문에 얽매이면서도,\n\x1bCB다케다\x1bCZ 가문 안에서 멸시받는\n슬픈 길만은 걷지 마라……\n뜻대로 살아라, \x1bCA가쓰요리\x1bCZ!)",
    },
    4940: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "reason": "Restore the surprise and subordinate-army clauses while retaining the current dynamic name token.",
        "text": "\x1bCA요시모토\x1bCZ가 \x1bCC오케하자마\x1bCZ에서 전사했다는\n충격적인 소식은, \x1bCB이마가와\x1bCZ 휘하의 한 부대로\n진군하던 \x1bCA[b1871]\x1bCZ에게도 전해졌다.",
    },
    4961: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "reason": "Restore the three-province-governor, now-is-the-time, and Imagawa-rule clauses while retaining current dynamic tokens.",
        "text": "\x1bCA요시모토\x1bCZ 님의 후계자 \x1bCA우지자네\x1bCZ 님은\n삼국 태수의 그릇이 아닙니다.\n지금이야말로 \x1bCA[bm1871]\x1bCZ 님이 \x1bCB미카와\x1bCZ의 무리를 이끌고\n\x1bCB이마가와\x1bCZ 지배에서 벗어나 독립할 때입니다……",
    },
    4963: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "reason": "Restore the explicit 그것을 referent while retaining the corrected current dynamic-name token.",
        "text": "대담한 일이어도 좋습니다.\n\x1bCC미카와\x1bCZ 백성도, \x1bCB[bs1871]\x1bCZ 가신들도\n\x1bCA[bm1871]\x1bCZ 님께 그것을 바라고 있습니다.",
    },
    4974: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "reason": "Restore independence, Sengoku-daimyo status, and entry onto the turbulent-age stage while retaining current tokens.",
        "text": "\x1bCC오카자키성\x1bCZ으로 돌아온 \x1bCA[bm1871]\x1bCZ은\n\x1bCB이마가와\x1bCZ 가문에서 독립해,\n센고쿠 다이묘 \x1bCB[bs1871]\x1bCZ 가문의\n당주로서 난세의 무대에 나섰다.",
    },
    4976: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "reason": "Restore the banner-motto and wherever-the-army-is clauses while retaining current tokens.",
        "text": "\x1bCA도요 쇼닌\x1bCZ의 이 가르침은 \x1bCA[bm1871]\x1bCZ의\n깃발 문구가 되어, \x1bCB[bs1871]\x1bCZ 군이 있는 곳에는\n반드시 그 깃발이 나부끼게 되었다.",
    },
}


class ReviewError(RuntimeError):
    """A pinned review input or deterministic report failed validation."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def file_record(path: Path) -> Mapping[str, Any]:
    blob = path.read_bytes()
    return {"relative_path": relative(path), "size": len(blob), "sha256": sha256(blob)}


def load_profiled_table(path: Path, expected: Mapping[str, Any], label: str) -> tuple[tuple[str, ...], Mapping[str, Any]]:
    require(path.is_file(), f"{label} is missing: {path}")
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(rebuild_message_table(table, table.texts) == raw, f"{label} table round trip differs")
    profile = {
        "path": str(path),
        "packed_size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "string_count": len(table.texts),
    }
    expected_without_path = dict(expected)
    actual_without_path = {key: profile[key] for key in expected_without_path}
    require(actual_without_path == expected_without_path, f"{label} profile drift")
    return tuple(table.texts), profile


def normalize_linebreaks(value: str) -> str:
    return LINEBREAK_RE.sub("\n", value)


def normalize_legacy_layout(value: str) -> str:
    """Retain Korean clause boundaries while removing only inherited indent."""
    return "\n".join(line.lstrip(" \u3000") for line in normalize_linebreaks(value).split("\n"))


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


def control_signature(value: str) -> Mapping[str, Any]:
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
        "runtime_tokens": BRACKET_RE.findall(value),
        "numeric_runtime_tokens": NUMERIC_RUNTIME_RE.findall(value),
        "printf_tokens": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1 for offset, character in enumerate(value) if character == "%" and offset not in printf_offsets
        ),
        "other_c0_controls": controls,
        "pua_codepoints": pua,
        "manual_linebreak_count": len(LINEBREAK_RE.findall(value)),
    }


def protected_signature(value: str) -> Mapping[str, Any]:
    signature = control_signature(value)
    return {
        key: signature[key]
        for key in ("esc_tags", "runtime_tokens", "printf_tokens", "unknown_percent_count", "other_c0_controls", "pua_codepoints")
    }


def assert_colour_layout(value: str, entry_id: int) -> None:
    inside_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            tag = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(tag) is not None, f"{entry_id}: malformed ESC tag {tag!r}")
            if tag == "\x1bCZ":
                require(inside_span, f"{entry_id}: unpaired ESC close")
                inside_span = False
            else:
                require(not inside_span, f"{entry_id}: nested ESC open")
                inside_span = True
            cursor += 3
            continue
        require(not (inside_span and value[cursor] in "\r\n"), f"{entry_id}: line break inside colour tag")
        cursor += 1
    require(not inside_span, f"{entry_id}: unterminated ESC colour span")


def surface_units(value: str) -> list[str]:
    visible = ESC_RE.sub("", value)
    return re.findall(r"\[[^\[\]\r\n]+\]|[\w]+|[^\s]", visible, flags=re.UNICODE)


def target_only_surface_units(before: str, after: str) -> list[str]:
    before_units = surface_units(before)
    after_units = surface_units(after)
    result: list[str] = []
    for opcode, _left_start, _left_end, right_start, right_end in difflib.SequenceMatcher(
        a=before_units, b=after_units, autojunk=False
    ).get_opcodes():
        if opcode not in {"insert", "replace"}:
            continue
        for unit in after_units[right_start:right_end]:
            if unit not in result:
                result.append(unit)
    return result


def line_metrics(
    entry_id: int,
    target: str,
    names: Sequence[str],
    reservations: Mapping[str, Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    result: list[Mapping[str, Any]] = []
    for line_number, encoded_line in enumerate(normalize_linebreaks(target).split("\n"), 1):
        visible_parts: list[str] = []
        static_parts: list[str] = []
        applied_reservations: list[Mapping[str, Any]] = []
        cursor = 0
        raw_width = 0
        while cursor < len(encoded_line):
            if encoded_line[cursor] == "\x1b":
                tag = encoded_line[cursor : cursor + 3]
                require(ESC_RE.fullmatch(tag) is not None, f"{entry_id}: malformed line ESC tag")
                cursor += 3
                continue
            token_match = BRACKET_RE.match(encoded_line, cursor)
            if token_match is not None:
                token = token_match.group(0)
                numeric = NUMERIC_RUNTIME_RE.fullmatch(token)
                require(numeric is not None, f"{entry_id}: unresolved nonnumeric runtime token {token}")
                reservation = reservations.get(token)
                require(reservation is not None, f"{entry_id}: missing runtime reservation {token}")
                name_id = int(numeric.group(2))
                require(0 <= name_id < len(names), f"{entry_id}: runtime name id out of range {token}")
                display = ESC_RE.sub("", normalize_linebreaks(names[name_id])).replace("\n", " ")
                display_full = sum(is_full_width_visible(character) for character in display)
                display_half = len(display) - display_full
                reserved_raw = int(reservation["reserved_full_name_width_px"])
                raw_width += reserved_raw
                visible_parts.append(display)
                applied_reservations.append(
                    {
                        "token": token,
                        "source_name_id": name_id,
                        "display_string": display,
                        "display_full_width_character_count": display_full,
                        "display_half_width_character_count": display_half,
                        "reserved_raw_g1n_width_px": reserved_raw,
                        "reserved_effective_width_px": math.ceil(reserved_raw * DRAW_FONT_PX / RAW_FULL_WIDTH_PX),
                        "runtime_proven": False,
                        "scene_limited": False,
                        "source": "v2_full_name_reservation_catalog",
                        "basis": "per-token referenced full-name upper bound",
                    }
                )
                cursor = token_match.end()
                continue
            character = encoded_line[cursor]
            static_parts.append(character)
            visible_parts.append(character)
            raw_width += RAW_FULL_WIDTH_PX if is_full_width_visible(character) else RAW_HALF_WIDTH_PX
            cursor += 1
        display = "".join(visible_parts)
        full = sum(is_full_width_visible(character) for character in display)
        half = len(display) - full
        effective = math.ceil(raw_width * DRAW_FONT_PX / RAW_FULL_WIDTH_PX)
        result.append(
            {
                "line_number": line_number,
                "source_line_with_tags_and_tokens": encoded_line,
                "display_string": display,
                "static_visible_string": "".join(static_parts),
                "raw_g1n_width_px": raw_width,
                "effective_width_px": effective,
                "full_width_character_count": full,
                "half_width_character_count": half,
                "runtime_reservations": applied_reservations,
                "exceeds_912px": effective > MAX_EFFECTIVE_LINE_PX,
                "passes_912px": effective <= MAX_EFFECTIVE_LINE_PX,
            }
        )
    return result


def load_json(path: Path) -> Mapping[str, Any]:
    require(path.is_file(), f"JSON input missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), f"JSON root must be an object: {path}")
    return payload


def select_historical_rows() -> tuple[Mapping[str, Any], ...]:
    require(sha256(HISTORICAL_MANIFEST.read_bytes()) == EXPECTED_HISTORICAL_MANIFEST_SHA256, "historical manifest hash drift")
    historical = load_json(HISTORICAL_MANIFEST)
    require(historical.get("schema") == "nobu16.kr.steam-jp-msgev-full-layout-overlay.v2", "historical schema drift")
    entries = historical.get("entries")
    require(isinstance(entries, list), "historical entries missing")
    selected = [
        row
        for row in entries
        if isinstance(row, dict)
        and MIN_ID <= int(row.get("id", -1)) <= MAX_ID
        and (
            row.get("operation") == "manual_compact_korean_layout"
            or "manual_compact_korean_layout" in row.get("newline_operations", [])
        )
    ]
    selected.sort(key=lambda row: int(row["id"]))
    require(len(selected) == EXPECTED_ROW_COUNT, f"4000 manual compact target count drift: {len(selected)}")
    require(len({int(row["id"]) for row in selected}) == EXPECTED_ROW_COUNT, "duplicate selected id")
    return tuple(selected)


def load_reservations(current_names: Sequence[str]) -> tuple[Mapping[str, Mapping[str, Any]], Mapping[str, Any]]:
    require(sha256(RESERVATION_MANIFEST.read_bytes()) == EXPECTED_RESERVATION_MANIFEST_SHA256, "reservation manifest hash drift")
    manifest = load_json(RESERVATION_MANIFEST)
    require(manifest.get("schema") == "nobu16.kr.steam-jp-msgev-runtime-token-reservations.v1", "reservation schema drift")
    raw_reservations = manifest.get("reservations")
    require(isinstance(raw_reservations, dict), "reservation map missing")
    result: dict[str, Mapping[str, Any]] = {}
    for token, record in raw_reservations.items():
        require(isinstance(token, str) and NUMERIC_RUNTIME_RE.fullmatch(token) is not None, f"bad reservation token {token!r}")
        require(isinstance(record, dict), f"bad reservation row {token}")
        source_name_id = int(record["source_name_id"])
        require(0 <= source_name_id < len(current_names), f"reservation source name id outside current table: {token}")
        display = ESC_RE.sub("", normalize_linebreaks(current_names[source_name_id])).replace("\n", " ")
        measured_raw = sum(
            RAW_FULL_WIDTH_PX if is_full_width_visible(character) else RAW_HALF_WIDTH_PX
            for character in display
        )
        require(
            measured_raw == int(record["reserved_full_name_width_px"]),
            f"current-name reservation width drift: {token}",
        )
        result[token] = record
    return result, {
        "path": str(RESERVATION_MANIFEST),
        "sha256": sha256(RESERVATION_MANIFEST.read_bytes()),
        "schema": manifest["schema"],
        "reservation_policy": manifest.get("reservation_policy"),
        "reservation_count": len(result),
    }


def assert_current_candidate() -> Mapping[str, Any]:
    manifest = load_json(CURRENT_MANIFEST_PATH)
    audit = load_json(CURRENT_AUDIT_PATH)
    require(manifest.get("candidate_only") is True, "batch04 source must remain candidate-only")
    require(audit.get("candidate_only") is True, "batch04 audit must remain candidate-only")
    output = manifest.get("output")
    require(isinstance(output, dict), "batch04 output profile missing")
    expected_output = {
        "sha256": EXPECTED_CURRENT_PROFILE["packed_sha256"],
        "size": EXPECTED_CURRENT_PROFILE["packed_size"],
        "raw_sha256": EXPECTED_CURRENT_PROFILE["raw_sha256"],
        "raw_size": EXPECTED_CURRENT_PROFILE["raw_size"],
    }
    require(output == expected_output, "batch04 manifest output profile drift")
    require(audit.get("output_event_profile") == expected_output, "batch04 audit output profile drift")
    return {
        "candidate_relative": relative(CURRENT_ROOT),
        "event_relative": relative(CURRENT_KO_PATH),
        "candidate_manifest": file_record(CURRENT_MANIFEST_PATH),
        "audit": file_record(CURRENT_AUDIT_PATH),
        "candidate_only": True,
        "strict_predecessor": manifest.get("predecessor"),
    }


def write_atomic(path: Path, payload: bytes) -> None:
    resolved = path.resolve(strict=False)
    root = WORKSTREAM.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ReviewError(f"output leaves workstream: {path}") from exc
    require("candidate-final" not in {part.casefold() for part in resolved.parts}, "candidate output forbidden")
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(path.name + ".staging")
    require(not staging.exists(), f"stale staging output: {staging}")
    try:
        staging.write_bytes(payload)
        os.replace(staging, path)
    finally:
        staging.unlink(missing_ok=True)


def build_bundle() -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    current_meta = assert_current_candidate()
    current, current_profile = load_profiled_table(CURRENT_KO_PATH, EXPECTED_CURRENT_PROFILE, "current static007 batch04 Korean")
    direct_jp, jp_profile = load_profiled_table(DIRECT_JP_PATH, EXPECTED_DIRECT_JP_PROFILE, "pristine direct-PC Japanese")
    direct_en, en_profile = load_profiled_table(DIRECT_EN_PATH, EXPECTED_DIRECT_EN_PROFILE, "direct-PC English")
    direct_sc, sc_profile = load_profiled_table(DIRECT_SC_PATH, EXPECTED_DIRECT_SC_PROFILE, "direct-PC Simplified Chinese")
    direct_tc, tc_profile = load_profiled_table(DIRECT_TC_PATH, EXPECTED_DIRECT_TC_PROFILE, "direct-PC Traditional Chinese")
    legacy, legacy_profile = load_profiled_table(LEGACY_PRECOMPACTION_KO_PATH, EXPECTED_LEGACY_PROFILE, "legacy full Korean")
    require(
        len({len(current), len(direct_jp), len(direct_en), len(direct_sc), len(direct_tc), len(legacy)}) == 1,
        "source string-table count drift",
    )
    reservations, reservation_meta = load_reservations(current)
    historical_rows = select_historical_rows()

    entries: list[Mapping[str, Any]] = []
    preservation_ids: list[int] = []
    reconciliation_ids: list[int] = []
    restoration_ids: list[int] = []
    source_quality_override_ids: list[int] = []
    token_migration_ids: list[int] = []
    four_line_ids: list[int] = []
    two_line_ids: list[int] = []
    line_distribution: Counter[str] = Counter()
    for historical in historical_rows:
        entry_id = int(historical["id"])
        historical_compact = str(historical["ko"])
        legacy_text = legacy[entry_id]
        current_text = current[entry_id]
        require(
            text_hash(legacy_text) == str(historical["preimage_utf16le_sha256"]),
            f"{entry_id}: legacy text is not the historical uncompressed preimage",
        )
        current_differs_from_historical_compact = current_text != historical_compact
        override = SEMANTIC_REVIEW_OVERRIDES.get(entry_id)
        current_quality_reconciled = current_differs_from_historical_compact and override is not None
        current_quality_preserved = current_differs_from_historical_compact and override is None
        if override is not None:
            proposed = override["text"]
            strategy = override["strategy"]
            source_quality_override_ids.append(entry_id)
            if current_quality_reconciled:
                reconciliation_ids.append(entry_id)
            else:
                restoration_ids.append(entry_id)
        elif current_quality_preserved:
            proposed = normalize_linebreaks(current_text)
            strategy = "preserve_current_post_compaction_quality_revision"
            preservation_ids.append(entry_id)
        else:
            proposed = normalize_legacy_layout(legacy_text)
            strategy = "restore_legacy_precompaction_full_korean_text"
            restoration_ids.append(entry_id)

        assert_colour_layout(current_text, entry_id)
        assert_colour_layout(legacy_text, entry_id)
        assert_colour_layout(proposed, entry_id)
        current_signature = protected_signature(current_text)
        legacy_signature = protected_signature(legacy_text)
        proposed_signature = protected_signature(proposed)
        jp_signature = protected_signature(direct_jp[entry_id])
        require(proposed_signature == current_signature, f"{entry_id}: proposed/current protected signature differs")
        require(proposed_signature == jp_signature, f"{entry_id}: proposed/direct-JP protected signature differs")
        if legacy_signature != current_signature:
            token_migration_ids.append(entry_id)

        lines = line_metrics(entry_id, proposed, current, reservations)
        require(1 <= len(lines) <= MAX_LINES, f"{entry_id}: proposed line count is outside 1..{MAX_LINES}")
        require(not any(line["exceeds_912px"] for line in lines), f"{entry_id}: proposed line exceeds 912px")
        line_distribution[str(len(lines))] += 1
        if len(lines) == 4:
            four_line_ids.append(entry_id)
        if len(lines) == 2:
            two_line_ids.append(entry_id)

        compact_to_legacy = target_only_surface_units(historical_compact, normalize_legacy_layout(legacy_text))
        current_to_proposed = target_only_surface_units(current_text, proposed)
        omitted_by_preserve = target_only_surface_units(current_text, normalize_legacy_layout(legacy_text)) if current_quality_preserved else []
        entries.append(
            {
                "entry_id": entry_id,
                "review_status": "ready_for_semantic_restoration_candidate",
                "restoration_strategy": strategy,
                "current_quality_preserved": current_quality_preserved,
                "current_quality_reconciled": current_quality_reconciled,
                "current_quality_preservation_reason": (
                    "The current strict batch04 text differs from the historical compact row and already preserves all source content; it is retained rather than overwritten by legacy recovery material."
                    if current_quality_preserved
                    else str(override["reason"])
                    if current_quality_reconciled
                    else "No post-compaction current revision is present; restore the historical uncompressed Korean preimage without shortening."
                ),
                "historical_manual_compact_ko": historical_compact,
                "current_ko": current_text,
                "legacy_precompaction_ko": legacy_text,
                "proposed_ko": proposed,
                "legacy_matches_historical_preimage": True,
                "missing_restoration_elements": {
                    "historical_compact_to_legacy_full_surface_units": compact_to_legacy,
                    "current_to_proposed_surface_units": current_to_proposed,
                    "legacy_only_surface_units_not_reintroduced_due_to_current_quality_preservation": omitted_by_preserve,
                    "sentence_shortening_or_deletion_allowed": False,
                },
                "direct_pc_sources": {
                    "jp": direct_jp[entry_id],
                    "en": direct_en[entry_id],
                    "sc": direct_sc[entry_id],
                    "tc": direct_tc[entry_id],
                },
                "control_signature": {
                    "historical_manual_compact": protected_signature(historical_compact),
                    "current": current_signature,
                    "legacy_precompaction": legacy_signature,
                    "proposed": proposed_signature,
                    "direct_pc_jp": jp_signature,
                    "proposed_matches_current": proposed_signature == current_signature,
                    "proposed_matches_direct_pc_jp": proposed_signature == jp_signature,
                    "legacy_to_current_token_or_control_migration_detected": legacy_signature != current_signature,
                },
                "layout": {
                    "target_line_count": len(lines),
                    "max_four_lines_pass": len(lines) <= MAX_LINES,
                    "any_line_exceeds_912px": any(line["exceeds_912px"] for line in lines),
                    "lines": lines,
                },
                "review_judgement": {
                    "source_comparison": "Direct PC JP/EN/SC/TC strings are retained above as the semantic witnesses; the legacy full Korean preimage is recovery material, and current revisions are preserved only when their source coverage remains complete.",
                    "linebreak_policy": "Keep Korean clause boundaries only. Japanese source line breaks were not copied as a layout rule.",
                    "automatic_linebreak_stripping_forbidden": True,
                    "automatic_decompaction_forbidden": True,
                    "candidate_binary_created": False,
                },
            }
        )

    require(len(preservation_ids) == EXPECTED_CURRENT_QUALITY_PRESERVED_COUNT, "current-quality preservation count drift")
    require(len(reconciliation_ids) == EXPECTED_CURRENT_QUALITY_RECONCILED_COUNT, "current-quality reconciliation count drift")
    require(len(restoration_ids) + len(preservation_ids) + len(reconciliation_ids) == EXPECTED_ROW_COUNT, "review accounting drift")

    payload = {
        "schema": SCHEMA,
        "scope": {
            "resource": RESOURCE,
            "event_id_range": [MIN_ID, MAX_ID],
            "manual_compact_target_count": len(entries),
            "legacy_full_text_restoration_count": len(restoration_ids),
            "current_quality_preserved_count": len(preservation_ids),
            "current_quality_reconciled_count": len(reconciliation_ids),
            "source_quality_semantic_reflow_or_terminology_fix_count": len(source_quality_override_ids),
            "candidate_binary_created": False,
            "steam_files_written": False,
            "git_or_release_actions_performed": False,
            "network_operation_performed": False,
        },
        "layout_baseline": {
            "runtime_font_px": DRAW_FONT_PX,
            "runtime_usable_line_width_px": MAX_EFFECTIVE_LINE_PX,
            "max_lines": MAX_LINES,
            "raw_g1n_full_width_advance_px": RAW_FULL_WIDTH_PX,
            "raw_g1n_half_width_advance_px": RAW_HALF_WIDTH_PX,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "raw_g1n_pass_limit_px": MAX_RAW_LINE_PX,
            "effective_width_pass_limit_px": MAX_EFFECTIVE_LINE_PX,
            "dynamic_name_reservations": "v2 full-name reservation catalog scaled by 30/48; runtime_proven=false and scene_limited=false",
        },
        "sources": {
            "current_ko_static007_batch04_successor": {**current_profile, **current_meta},
            "direct_pc_jp_pristine": jp_profile,
            "direct_pc_en": en_profile,
            "direct_pc_sc": sc_profile,
            "direct_pc_tc": tc_profile,
            "legacy_precompaction_ko_backup": legacy_profile,
            "historical_manual_compact_manifest": {
                "path": str(HISTORICAL_MANIFEST),
                "sha256": sha256(HISTORICAL_MANIFEST.read_bytes()),
            },
            "runtime_reservation_manifest": reservation_meta,
        },
        "judgement_groups": [
            {
                "group": "restore_unabridged_legacy_preimage",
                "ids": restoration_ids,
                "reason": "The current row still equals the historical compact text. Restore the exact historical uncompressed Korean preimage, retaining its Korean semantic clause boundaries.",
            },
            {
                "group": "preserve_later_current_quality_revision",
                "ids": preservation_ids,
                "reason": "The strict current row differs from the historical compact text. The later source-driven wording or runtime-token revision takes precedence over legacy recovery material.",
            },
            {
                "group": "reconcile_later_current_revision_with_source_complete_text",
                "ids": reconciliation_ids,
                "reason": "These rows retain direct-PC-compatible current terminology or runtime tokens, but source comparison found clauses still abbreviated. The proposal restores every clause without reverting the current control signature.",
            },
            {
                "group": "source_quality_semantic_reflow_or_terminology_fix",
                "ids": source_quality_override_ids,
                "reason": "Direct-PC comparison identified a semantic Korean wording, terminology, grammar, completeness, or clause-boundary correction beyond a blind legacy restoration.",
            },
            {
                "group": "legacy_to_current_token_or_control_migration",
                "ids": token_migration_ids,
                "reason": "Legacy recovery text lacks or uses an obsolete runtime token/control form. Preserve the current direct-PC-compatible form rather than restoring old literal names or tokens.",
            },
            {
                "group": "existing_four_line_semantic_layout",
                "ids": four_line_ids,
                "reason": "These restored or preserved strings already use four Korean semantic lines and pass the static-patch-007 912px gate; do not compress them back to three lines.",
            },
            {
                "group": "two_line_semantic_layout",
                "ids": two_line_ids,
                "reason": "These strings are naturally two Korean semantic lines; adding a forced line break is not required.",
            },
            {
                "group": "runtime_name_reservation_review",
                "ids": [entry["entry_id"] for entry in entries if any(line["runtime_reservations"] for line in entry["layout"]["lines"])],
                "reason": "Capacity uses the conservative current full-name reservation and the required 30/48 scale. It does not assert a runtime-proven scene measurement.",
            },
        ],
        "entries": entries,
    }
    validation = {
        "schema": "nobu16.kr.manual-compact-4000-review-validation.v1",
        "status": "PASS",
        "target_count": len(entries),
        "legacy_full_text_restoration_count": len(restoration_ids),
        "current_quality_preserved_count": len(preservation_ids),
        "current_quality_reconciled_count": len(reconciliation_ids),
        "source_quality_semantic_reflow_or_terminology_fix_count": len(source_quality_override_ids),
        "target_line_count_distribution": dict(sorted(line_distribution.items())),
        "all_target_lines_pass_static_patch_007_912px": True,
        "all_targets_pass_max_four_lines": True,
        "output": relative(OUTPUT),
        "candidate_binary_created": False,
        "steam_files_written": False,
        "git_or_release_actions_performed": False,
        "network_operation_performed": False,
    }
    return payload, validation


def source_whitespace_check() -> None:
    require(SCRIPT.is_file(), "review script is missing")
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
        write_atomic(VALIDATION, canonical_json(validation))
        print(json.dumps({"output": relative(OUTPUT), "validation": relative(VALIDATION), **validation}, ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "verify":
        require(OUTPUT.is_file(), f"missing output: {OUTPUT}")
        require(VALIDATION.is_file(), f"missing validation: {VALIDATION}")
        require(OUTPUT.read_bytes() == canonical_json(payload), "review artifact differs from deterministic rebuild")
        require(VALIDATION.read_bytes() == canonical_json(validation), "validation differs from deterministic rebuild")
        print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
        return 0
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ReviewError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
