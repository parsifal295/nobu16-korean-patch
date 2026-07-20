#!/usr/bin/env python3
"""Create a read-only semantic/layout review for held runtime-token rows.

The 17 rows were excluded from prior batch05/batch06 candidate creation because
their runtime token width needed direct evidence.  This script uses the strict
batch07 name table plus the per-token full-name reservation catalog to prepare
only a review JSON.  It cannot build a message binary or write Steam/Git/release
state.
"""

from __future__ import annotations

import argparse
import difflib
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
OUTPUT = PUBLIC / "manual_compact_runtime_3442_3611_review.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"

TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.manual-compact-runtime-3442-3611-review.v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
TARGET_IDS = (
    3442,
    3443,
    3444,
    3448,
    3455,
    3456,
    3459,
    3499,
    3519,
    3520,
    3524,
    3526,
    3548,
    3565,
    3576,
    3579,
    3611,
)
CURRENT_DIFF_IDS = (3611,)

RUNTIME_FONT_PX = 30
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
MAX_EFFECTIVE_WIDTH_PX = 912
MAX_RAW_WIDTH_PX = 1440
MAX_LINES = 4

# The strict chain advanced with batch07.  The predecessor comparison makes
# the non-overlap with batch07 explicit for the 17 reviewed event rows and the
# four referenced name-table rows.
CURRENT_PATH = (
    REPO
    / "tmp"
    / "pc_event_manual_compact_static007_batch07_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
CURRENT_EXPECTED = {
    "packed_sha256": "5B84334A51829A8D981F4BE5E161D73803894D29F7FA1D91AC40090671CB347D",
    "raw_sha256": "85C48E864CC06831EB8F31C713703E0E3715848EE049A36B4F53CEB757F186E3",
    "string_count": 17916,
}
PRIOR_PATH = (
    REPO
    / "tmp"
    / "pc_event_manual_compact_static007_6000_7999_restore_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
PRIOR_EXPECTED = {
    "packed_sha256": "D99390D4F2D7D469C105439A11476B01830F5E96287B278C164045CBC7BA3547",
    "raw_sha256": "567C8C3C2F371E27CBE6FFEAB9F8F3EE7F6D6F13A2C179682A5A7F7D3F35780F",
    "string_count": 17916,
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

DIRECT_EXPECTED = {
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
    "legacy": {
        "packed_sha256": "2CA183DA690D45A75702EA0F35C70966786B59E9440B8B8F49BE9652342F81AC",
        "raw_sha256": "EDCF7A9CEBD605BB2275D5A3B92A76E7E2F652B2391554F24C6A8BDD2EF91A08",
        "string_count": 17916,
    },
}

ESC = "\x1b"
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\r|\n")


def ca(value: str) -> str:
    return f"{ESC}CA{value}{ESC}CZ"


def cb(value: str) -> str:
    return f"{ESC}CB{value}{ESC}CZ"


def cc(value: str) -> str:
    return f"{ESC}CC{value}{ESC}CZ"


# Each row is manually source-reviewed.  Runtime token spelling and colour
# span order are preserved exactly; only Korean semantic line boundaries and
# omitted non-token content are restored.
PROPOSALS: Mapping[int, Mapping[str, str]] = {
    3442: {
        "strategy": "restore_complete_korean_with_scene_limited_reservation",
        "reason": "Restore repeated political strife, departure from Kyoto, the current shogun's genpuku in Omi, and accession to the shogunate.",
        "text": (
            f"정쟁 때마다 {cb('아시카가 가문')}의 당주는 {cc('교토')}를 떠났고,\n"
            f"현 쇼군 {ca('아시카가 [bm75]')}도 {cc('교토')}가 아닌\n"
            f"{cc('오미')}에서 원복을 치르고 쇼군직에 올랐다."
        ),
    },
    3443: {
        "strategy": "restore_complete_korean_with_semantic_reflow_runtime_reservation",
        "reason": "Restore the Muromachi base, repeated return attempts, Kyoto's Miyoshi rulers, and the failed negotiations. Replace '또한' with '도' so the conservative token reservation fits without deleting meaning.",
        "text": (
            f"하지만 무로마치 막부의 본거지는 역시 {cc('교토')}였다.\n"
            f"쇼군 {ca('[bm75]')}도 몇 번이나 {cc('교토')}로 돌아가려 꾀하며,\n"
            f"{cc('교토')}를 지배하는 {cb('미요시 가문')}과 교섭했지만……"
        ),
    },
    3444: {
        "strategy": "restore_complete_korean_with_scene_limited_reservation",
        "reason": "Restore the Hosokawa-retainer origin, the shogun's view of Miyoshi as a retainer's retainer, and the stalled talks.",
        "text": (
            f"{cb('미요시 가문')}은 본래 {cb('호소카와 가문')}의 가신이었다.\n"
            f"곧 쇼군 {ca('[bm75]')}의 눈에는 가신의 가신에 불과했다.\n"
            "자존심이 방해했는지 교섭은 진척되지 않았다."
        ),
    },
    3448: {
        "strategy": "restore_complete_korean_with_scene_limited_reservation",
        "reason": "Restore Nagayoshi's recognition as Otomoshu/direct shogunal retainer, the bilateral peace, and the imminent Kyoto return.",
        "text": (
            f"{ca('미요시 나가요시')}를 오토모슈, 즉 {cb('쇼군가')} 직신으로\n"
            "인정하면서 양측의 화의가 성립했다.\n"
            f"마침내 {ca('[bm75]')}의 {cc('교토')} 귀환이 눈앞에 들어왔다."
        ),
    },
    3455: {
        "strategy": "restore_complete_korean_with_semantic_reflow_runtime_reservation",
        "reason": "Restore the initially peace-sceptical retainers, their support for Harumoto, and the shogun's inability to evade the issue. Four lines are used at Korean phrase boundaries for two conservative token reservations.",
        "text": (
            f"이윽고 본래 {cb('미요시 가문')}과의 화친에\n"
            f"소극적이던 {ca('[bm75]')}의 측근 중에도\n"
            f"{ca('하루모토')}에 동조하는 자가 생겨, {ca('[bm75]')} 본인도\n"
            "더는 발뺌할 수 없는 처지에 몰렸다."
        ),
    },
    3456: {
        "strategy": "restore_complete_korean_with_semantic_reflow_runtime_reservation",
        "reason": "Restore the continued entry attempt, the wary Miyoshi obstruction, the siege at Ryozen Castle in Higashiyama, and the complete collapse of peace talks. Four semantic lines avoid the old 930px-effective reservation overflow.",
        "text": (
            f"그래도 {ca('[bm75]')} 본인은 교토 입성을 꾀했으나,\n"
            f"경계하던 {cb('미요시 세력')}에 막혀 {cc('히가시야마')}의\n"
            f"{cc('료젠성')}에 농성했다.\n"
            "이로써 화의는 완전히 무너졌다."
        ),
    },
    3459: {
        "strategy": "restore_complete_korean_with_scene_limited_reservation",
        "reason": "Restore the fall of Ryozen Castle, the renewed flight to Omi, and Harumoto's followers.",
        "text": (
            f"{cb('미요시군')}의 공격으로 {cc('료젠성')}은 함락.\n"
            f"쇼군 {ca('[bm75]')}는 다시 {cc('오미')}로 달아났고, {ca('하루모토')} 등도\n"
            "그 뒤를 따랐다."
        ),
    },
    3499: {
        "strategy": "restore_complete_korean_with_scene_limited_reservation",
        "reason": "Restore the joint-operation proposal, willing acceptance and participation in the attack, and the report reaching Ujiyasu.",
        "text": (
            f"{ca('요시모토')}는 {ca('[b1251]')}에게도 공동 작전을 제안했고,\n"
            f"{ca('[bm1251]')} 측도 흔쾌히 받아들여 공격에 가담했다.\n"
            f"이 움직임은 곧 {ca('우지야스')}에게 전해졌다."
        ),
    },
    3519: {
        "strategy": "restore_complete_korean_with_scene_limited_reservation",
        "reason": "Restore the speaker's rejection, the west-side weakness, and the trailing identification of the commander who joined Yoshimoto's camp.",
        "text": (
            f"아니, 이번 {ca('요시모토')}의 우리를 향한 포위망……\n"
            "틈이 있다면 서쪽이다.\n"
            f"{ca('요시모토')}의 진영에 가담한…… {ca('[b1251]')}."
        ),
    },
    3520: {
        "strategy": "restore_complete_korean_with_scene_limited_reservation",
        "reason": "Restore the unreadable nature of the man, his feigned cooperation, concealed plan for a fisherman's profit, and the proposal to exploit it in reverse.",
        "text": (
            f"{ca('[bm1251]')} 공은 속내를 알 수 없는 자다. 겉으로는\n"
            f"{ca('요시모토')}를 돕는 척하며 남몰래 어부지리를 노리고 있지.\n"
            "그 생각을 거꾸로 우리가 이용한다……!"
        ),
    },
    3524: {
        "strategy": "restore_complete_korean_with_scene_limited_reservation",
        "reason": "Restore the move to block Yoshimoto's encirclement, the party's destination at Kawagoe Castle, and Ujiyasu's sortie toward Kato.",
        "text": (
            f"이리하여 {ca('요시모토')}가 펼친 포위망을 막고자,\n"
            f"{ca('[b790]')} 일행은 {cc('가와고에성')}으로 향했다.\n"
            f"그리고 {ca('우지야스')}는 {cc('가토')}로 출진했다……"
        ),
    },
    3526: {
        "strategy": "restore_complete_korean_with_scene_limited_reservation",
        "reason": "Restore the youthful recognition of ability, the father's dislike of the token-named rival, and the intended Takeda succession.",
        "text": (
            f"어려서부터 그 재능을 아버지 {ca('노부토라')}에게 인정받아,\n"
            f"{ca('[bm1251]')} 공을 싫어한 {ca('노부토라')}가 {cb('다케다 가문')} 당주로\n"
            "세우려 했던 것으로 알려져 있다."
        ),
    },
    3548: {
        "strategy": "restore_complete_korean_with_scene_limited_reservation",
        "reason": "Restore the ninety-nine clauses, the loyalty pledges toward the token-named lord, and the many rules for samurai life.",
        "text": (
            "99개 조항에 이르는 다케다 노부시게의 가훈에는,\n"
            f"{ca('[bm1251]')} 공을 향한 충성을 맹세하는 항목뿐 아니라\n"
            "무사의 생활 규범을 적은 항목도 많았고……"
        ),
    },
    3565: {
        "strategy": "restore_complete_korean_with_scene_limited_reservation",
        "reason": "Restore the oil merchant's move from Kyoto to Mino, acceptance by the provincial shugo, rise as a powerful warrior, and his son's ousting of Toki.",
        "text": (
            f"{cc('교토')}에서 {cc('미노')}로 간 기름 장수는 지방 슈고인\n"
            f"{cb('도키 가문')}의 눈에 들어 유력 무장이 되었고, 그 아들\n"
            f"{ca('[bm924]')} 공이 {cb('도키')}를 몰아내 전국 다이묘가 됐다."
        ),
    },
    3576: {
        "strategy": "restore_complete_korean_with_scene_limited_reservation",
        "reason": "Restore the year marker, Sengoku-daimyo status, the small force, the journey to Kyoto, and the audience with the shogun.",
        "text": (
            f"이해에 {cc('미노')}의 전국 다이묘 {ca('사이토 다카마사')}는\n"
            "소수의 병력만 이끌고 상경하여,\n"
            f"쇼군 {ca('[b75]')}에게 배알했다."
        ),
    },
    3579: {
        "strategy": "source_complete_wording_correction_with_scene_limited_reservation",
        "reason": "Restore the speaker's father relation and evil conduct, while using natural Korean for the broad resentment that made the unavoidable suppression necessary.",
        "text": (
            f"황공합니다. {ca('[bm924]')} 공은…… 제 아버지이나,\n"
            "불의를 많이 저질러 백성들의 원성이 컸습니다.\n"
            "그래서 어쩔 수 없이 토벌했습니다."
        ),
    },
    3611: {
        "strategy": "reconcile_later_runtime_token_migration_with_complete_restoration",
        "reason": "The strict current row correctly migrated the legacy literal name to the direct-PC-compatible runtime token. Preserve that token while restoring attention to the reinforcements and the request for mediation immediately after the battle began.",
        "text": (
            f"{ca('우지야스')}는 {ca('요시모토')}의 원군인 {ca('[b1251]')}에 주목해,\n"
            "전투가 시작된 직후부터\n"
            "화친의 중재를 부탁해 두었다."
        ),
    },
}


class ReviewError(RuntimeError):
    """Raised when a pinned source or the deterministic review drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


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


def read_json(path: Path) -> Any:
    require(path.is_file(), f"missing JSON source: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_linebreaks(value: str) -> str:
    return LINEBREAK_RE.sub("\n", value)


def normalize_legacy_layout(value: str) -> str:
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


def visible_units(value: str) -> list[str]:
    visible = ESC_RE.sub("", value)
    return re.findall(r"\[[^\[\]\r\n]+\]|[\w]+|[^\s]", visible, flags=re.UNICODE)


def reintroduced_surface_units(before: str, after: str) -> list[str]:
    before_units = visible_units(before)
    after_units = visible_units(after)
    result: list[str] = []
    for opcode, _left_start, _left_end, right_start, right_end in difflib.SequenceMatcher(
        a=before_units, b=after_units, autojunk=False
    ).get_opcodes():
        if opcode in {"insert", "replace"}:
            for unit in after_units[right_start:right_end]:
                if unit not in result:
                    result.append(unit)
    return result


def full_name_from_strict_table(names: Sequence[str], source_name_id: int) -> str:
    require(0 <= source_name_id < len(names), f"runtime name ID outside strict table: {source_name_id}")
    return ESC_RE.sub("", normalize_linebreaks(names[source_name_id])).replace("\n", " ")


def line_metrics(
    entry_id: int,
    target: str,
    strict_names: Sequence[str],
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
            expected_name_hash = reservation.get("source_name_utf16le_sha256")
            require(isinstance(source_name_id, int), f"{entry_id}: invalid name ID for {token}")
            require(isinstance(reserved_raw, int), f"{entry_id}: invalid reservation width for {token}")
            require(isinstance(expected_name_hash, str), f"{entry_id}: missing name hash for {token}")
            full_name = full_name_from_strict_table(strict_names, source_name_id)
            require(text_digest(strict_names[source_name_id]) == expected_name_hash, f"{entry_id}: strict-name hash drift for {token}")
            full_count = sum(is_full_width_visible(character) for character in full_name)
            runtime_items.append(
                {
                    "token": token,
                    "source_name_id": source_name_id,
                    "strict_name_table_string": full_name,
                    "strict_name_utf16le_sha256": text_digest(strict_names[source_name_id]),
                    "full_name_display_full_width_character_count": full_count,
                    "full_name_display_half_width_character_count": len(full_name) - full_count,
                    "reserved_raw_g1n_width_px": reserved_raw,
                    "reserved_effective_width_px": math.ceil(reserved_raw * RUNTIME_FONT_PX / RAW_FULL_WIDTH_PX),
                    "reservation_scope": "This exact 17-row runtime review only; reserve the full strict-table name because prefix semantics are not inferred.",
                    "runtime_proven": False,
                }
            )
            return full_name

        strict_name_substitution = RUNTIME_RE.sub(replace_runtime, template)
        literal = RUNTIME_RE.sub("", template)
        literal_full = sum(is_full_width_visible(character) for character in literal)
        literal_half = len(literal) - literal_full
        raw_literal = literal_full * RAW_FULL_WIDTH_PX + literal_half * RAW_HALF_WIDTH_PX
        raw_reserved = sum(item["reserved_raw_g1n_width_px"] for item in runtime_items)
        raw_width = raw_literal + raw_reserved
        effective_width = math.ceil(raw_width * RUNTIME_FONT_PX / RAW_FULL_WIDTH_PX)
        measured_full = sum(is_full_width_visible(character) for character in strict_name_substitution)
        metrics.append(
            {
                "line_number": line_number,
                "encoded_string": encoded_line,
                "display_string_template": template,
                "display_string": strict_name_substitution,
                "display_string_with_strict_name_table_substitution": strict_name_substitution,
                "runtime_display_proven": False,
                "raw_g1n_width_px": raw_width,
                "literal_raw_g1n_width_px": raw_literal,
                "reserved_raw_g1n_width_px": raw_reserved,
                "effective_width_px": effective_width,
                "full_width_character_count": measured_full,
                "half_width_character_count": len(strict_name_substitution) - measured_full,
                "runtime_reservations": runtime_items,
                "exceeds_912px": effective_width > MAX_EFFECTIVE_WIDTH_PX,
            }
        )
    return metrics


def source_summary(profile: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: profile[key]
        for key in ("path", "packed_size", "packed_sha256", "raw_size", "raw_sha256", "string_count")
    }


def build_bundle() -> tuple[dict[str, Any], dict[str, Any]]:
    current_profile, current = load_table(CURRENT_PATH, CURRENT_EXPECTED, "batch07 strict input")
    prior_profile, prior = load_table(PRIOR_PATH, PRIOR_EXPECTED, "pre-batch07 strict input")
    jp_profile, jp = load_table(DIRECT_JP_PATH, DIRECT_EXPECTED["jp"], "direct JP")
    en_profile, en = load_table(DIRECT_EN_PATH, DIRECT_EXPECTED["en"], "direct EN")
    sc_profile, sc = load_table(DIRECT_SC_PATH, DIRECT_EXPECTED["sc"], "direct SC")
    tc_profile, tc = load_table(DIRECT_TC_PATH, DIRECT_EXPECTED["tc"], "direct TC")
    legacy_profile, legacy = load_table(LEGACY_KO_PATH, DIRECT_EXPECTED["legacy"], "pre-compaction Korean")
    require(
        all(len(values) == len(current) for values in (prior, jp, en, sc, tc, legacy)),
        "source table count mismatch",
    )

    historical_doc = read_json(HISTORICAL_MANIFEST)
    reservations_doc = read_json(RESERVATION_MANIFEST)
    inventory_doc = read_json(INVENTORY_MANIFEST)
    historical_entries = historical_doc.get("entries")
    reservations = reservations_doc.get("reservations")
    inventory_rows = inventory_doc.get("rows")
    require(isinstance(historical_entries, list), "historical entries missing")
    require(isinstance(reservations, Mapping), "reservation catalog missing")
    require(isinstance(inventory_rows, list), "manual inventory rows missing")
    historical_by_id = {row.get("id"): row for row in historical_entries if isinstance(row, Mapping)}
    inventory_by_id = {row.get("entry_id"): row for row in inventory_rows if isinstance(row, Mapping)}
    require(set(PROPOSALS) == set(TARGET_IDS), "proposal coverage drift")
    require(all(current[entry_id] == prior[entry_id] for entry_id in TARGET_IDS), "batch07 changed a runtime-review row")

    referenced_name_ids = sorted(
        {
            int(match.group(1))
            for entry_id in TARGET_IDS
            for match in re.finditer(r"\[[A-Za-z]{1,16}(\d+)\]", current[entry_id])
        }
    )
    require(referenced_name_ids == [75, 790, 924, 1251], f"referenced strict-name scope drift: {referenced_name_ids}")
    require(all(current[name_id] == prior[name_id] for name_id in referenced_name_ids), "batch07 changed a referenced strict name")

    entries: list[dict[str, Any]] = []
    strategy_counts: Counter[str] = Counter()
    exact_legacy_ids: list[int] = []
    reflow_ids: list[int] = []
    current_token_reconciliation_ids: list[int] = []
    all_token_spellings: set[str] = set()

    for entry_id in TARGET_IDS:
        historical = historical_by_id.get(entry_id)
        inventory = inventory_by_id.get(entry_id)
        require(isinstance(historical, Mapping), f"{entry_id}: historical selection missing")
        require(isinstance(inventory, Mapping), f"{entry_id}: inventory row missing")
        require(
            historical.get("operation") == "manual_compact_korean_layout"
            or "manual_compact_korean_layout" in historical.get("newline_operations", []),
            f"{entry_id}: not a historical manual-compact row",
        )
        compact = historical.get("ko")
        require(isinstance(compact, str), f"{entry_id}: historical Korean missing")
        current_ko = current[entry_id]
        legacy_ko = normalize_legacy_layout(legacy[entry_id])
        proposal = PROPOSALS[entry_id]
        proposed = proposal["text"]
        for value in (compact, current_ko, legacy_ko, proposed, jp[entry_id]):
            assert_colour_layout(value, entry_id)
        compact_signature = control_signature(compact)
        current_signature = control_signature(current_ko)
        legacy_signature = control_signature(legacy_ko)
        proposed_signature = control_signature(proposed)
        jp_signature = control_signature(jp[entry_id])
        require(proposed_signature == current_signature == jp_signature, f"{entry_id}: current/proposed/JP signature drift")
        if entry_id == 3611:
            require(current_ko != compact, "3611: expected current token migration absent")
            require(legacy_signature != current_signature, "3611: expected legacy literal-name signature difference absent")
        else:
            require(
                compact_signature == legacy_signature == current_signature,
                f"{entry_id}: unexpected token/control migration",
            )
        lines = line_metrics(entry_id, proposed, current, reservations)
        require(1 <= len(lines) <= MAX_LINES, f"{entry_id}: line count exceeds four")
        require(not any(line["exceeds_912px"] for line in lines), f"{entry_id}: effective width exceeds 912px")
        require(proposed_signature["runtime_tokens"], f"{entry_id}: expected runtime token absent")
        token_spellings = proposed_signature["runtime_tokens"]
        all_token_spellings.update(token_spellings)
        strategy = proposal["strategy"]
        strategy_counts[strategy] += 1
        if proposed == legacy_ko:
            exact_legacy_ids.append(entry_id)
        if "semantic_reflow" in strategy:
            reflow_ids.append(entry_id)
        if strategy.startswith("reconcile_later_runtime_token"):
            current_token_reconciliation_ids.append(entry_id)
        entries.append(
            {
                "entry_id": entry_id,
                "scene_batch_id": inventory.get("scene_batch_id"),
                "review_status": "ready_for_runtime_token_semantic_restoration_candidate",
                "restoration_strategy": strategy,
                "review_judgement": proposal["reason"],
                "historical_manual_compact_ko": compact,
                "current_ko_at_batch07_strict_baseline": current_ko,
                "legacy_precompaction_ko": legacy_ko,
                "proposed_ko": proposed,
                "legacy_matches_proposed_after_indent_normalization": proposed == legacy_ko,
                "historical_compact_to_proposed_surface_units": reintroduced_surface_units(compact, proposed),
                "current_to_proposed_surface_units": reintroduced_surface_units(current_ko, proposed),
                "direct_pc_sources": {
                    "jp": jp[entry_id],
                    "en": en[entry_id],
                    "sc": sc[entry_id],
                    "tc": tc[entry_id],
                },
                "text_sha256_utf16le": {
                    "historical_manual_compact_ko": text_digest(compact),
                    "current_ko": text_digest(current_ko),
                    "legacy_precompaction_ko": text_digest(legacy_ko),
                    "proposed_ko": text_digest(proposed),
                },
                "control_signature": {
                    "historical_manual_compact": compact_signature,
                    "current": current_signature,
                    "legacy_precompaction": legacy_signature,
                    "proposed": proposed_signature,
                    "direct_pc_jp": jp_signature,
                    "legacy_to_current_token_migration": entry_id == 3611,
                },
                "layout": {
                    "line_count": len(lines),
                    "max_lines": MAX_LINES,
                    "all_lines_pass_static_patch_007": True,
                    "any_line_exceeds_912px": False,
                    "lines": lines,
                },
                "review_policy": {
                    "japanese_source_linebreaks_used_as_layout_authority": False,
                    "korean_linebreaks_are_manual_semantic_boundaries": True,
                    "sentence_shortening_or_deletion_allowed": False,
                    "automatic_linebreak_stripping_forbidden": True,
                    "automatic_decompaction_forbidden": True,
                    "runtime_prefix_semantics_inferred": False,
                },
            }
        )

    require(len(entries) == len(TARGET_IDS), "entry accounting drift")
    require(current_token_reconciliation_ids == list(CURRENT_DIFF_IDS), "token migration accounting drift")
    max_raw = max(line["raw_g1n_width_px"] for entry in entries for line in entry["layout"]["lines"])
    max_effective = max(line["effective_width_px"] for entry in entries for line in entry["layout"]["lines"])
    max_line_count = max(entry["layout"]["line_count"] for entry in entries)

    payload = {
        "schema": SCHEMA,
        "scope": {
            "resource": RESOURCE,
            "target_ids": list(TARGET_IDS),
            "manual_compact_runtime_target_count": len(entries),
            "batch07_nonoverlap_text_asserted": True,
            "batch07_nonoverlap_name_table_asserted": True,
            "later_runtime_token_migration_ids": list(current_token_reconciliation_ids),
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
            "runtime_reservation_policy": "Use the exact strict name-table row for evidence, reserve the catalog full-name width within this 17-row scope, then scale by 30/48. No prefix semantics or runtime rendering behavior is inferred.",
        },
        "sources": {
            "batch07_strict_current": source_summary(current_profile),
            "prior_6000_7999_strict_input_for_nonoverlap_check": source_summary(prior_profile),
            "direct_pc_jp_pristine": source_summary(jp_profile),
            "direct_pc_en": source_summary(en_profile),
            "direct_pc_sc": source_summary(sc_profile),
            "direct_pc_tc": source_summary(tc_profile),
            "legacy_precompaction_ko_backup": source_summary(legacy_profile),
            "historical_manual_compact_manifest": {
                "path": path_label(HISTORICAL_MANIFEST),
                "sha256": digest(HISTORICAL_MANIFEST.read_bytes()),
            },
            "runtime_reservation_manifest": {
                "path": path_label(RESERVATION_MANIFEST),
                "sha256": digest(RESERVATION_MANIFEST.read_bytes()),
            },
            "manual_compact_inventory": {
                "path": path_label(INVENTORY_MANIFEST),
                "sha256": digest(INVENTORY_MANIFEST.read_bytes()),
            },
        },
        "strict_name_table_evidence": {
            "referenced_name_ids": referenced_name_ids,
            "names": {
                str(name_id): {
                    "strict_name_table_string": current[name_id],
                    "utf16le_sha256": text_digest(current[name_id]),
                }
                for name_id in referenced_name_ids
            },
            "reservation_scope": "The reservation review is scene-limited to the listed 17 event rows; it does not claim live runtime token-prefix behavior.",
        },
        "judgement_groups": [
            {
                "group": "exact_legacy_complete_restoration",
                "ids": exact_legacy_ids,
                "reason": "The legacy Korean is source-complete and already uses valid Korean semantic boundaries under the strict-name reservation.",
            },
            {
                "group": "runtime_reservation_semantic_reflow",
                "ids": reflow_ids,
                "reason": "3443, 3455, and 3456 are manually reflowed to pass the 30/48-scaled full-name reservation without removing meaning.",
            },
            {
                "group": "later_runtime_token_migration_preserved",
                "ids": current_token_reconciliation_ids,
                "reason": "3611 retains the current direct-PC-compatible runtime token rather than reverting to the legacy literal name.",
            },
            {
                "group": "all_runtime_token_rows",
                "ids": list(TARGET_IDS),
                "reason": "Each row has at least one runtime token, an exact strict-table name hash, and a catalog full-name reservation scaled by 30/48.",
            },
        ],
        "counts": {
            "strategy_counts": dict(sorted(strategy_counts.items())),
            "exact_legacy_restoration_count": len(exact_legacy_ids),
            "semantic_reflow_count": len(reflow_ids),
            "distinct_runtime_token_spellings": sorted(all_token_spellings),
            "max_raw_g1n_width_px": max_raw,
            "max_effective_width_px": max_effective,
            "max_line_count": max_line_count,
            "all_rows_within_912px": True,
            "all_rows_within_four_lines": True,
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
        "schema": "nobu16.kr.manual-compact-runtime-3442-3611-review-validation.v1",
        "status": "PASS",
        "review_output": path_label(OUTPUT),
        "target_count": len(entries),
        "target_ids": list(TARGET_IDS),
        "referenced_name_ids": referenced_name_ids,
        "semantic_reflow_ids": reflow_ids,
        "later_runtime_token_migration_ids": current_token_reconciliation_ids,
        "max_raw_g1n_width_px": max_raw,
        "max_effective_width_px": max_effective,
        "max_line_count": max_line_count,
        "over_912px_line_count": 0,
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
        validation = {**validation, "review_output_sha256": digest(OUTPUT.read_bytes())}
        write_atomic(VALIDATION, canonical_json(validation))
        print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
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
    except (ReviewError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
