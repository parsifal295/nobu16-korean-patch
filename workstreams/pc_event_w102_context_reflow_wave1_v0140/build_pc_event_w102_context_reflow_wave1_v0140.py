#!/usr/bin/env python3
"""Build a current-W102 event-dialogue context reflow candidate.

The candidate changes only authored LF positions in twenty current Steam PK
event lines.  It does not shorten prose, rewrite names, alter control tags, or
touch dynamic tokens.  Every resulting line is measured with the active
30px/912px/four-line layout contract.  ``build`` writes only to ``private``;
Steam is never modified by this script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
ORIGINAL_ROOT = (
    Path(r"F:\Games\NOBU16\KR_PATCH_BACKUP")
    / "file_only_transaction"
    / "jp-runtime-wave05-20260715-v1"
    / "originals"
)
RESOURCE = "MSG_PK/JP/msgev.bin"
CURRENT_PATH = STEAM_ROOT / RESOURCE
JP_PATH = ORIGINAL_ROOT / RESOURCE
CURRENT_SHA256 = "D20E1CC9E1014473DCFCE7C247721FFA912955B0CB6EEA71BB00BD055977FB4E"
CURRENT_RAW_SHA256 = "15CC03C20B0E12D4AF2619968CD97C451D5B6A073BB0659000D0E8C6BC645A6B"
JP_SHA256 = "03426B59D32EB628021DE43BC02FF82B56B04D97C25CE37F735630EA7C4E2002"
EXPECTED_TEXT_COUNT = 17_916
RUNTIME_LEDGER_PATH = (
    REPO
    / "workstreams"
    / "pc_event_runtime_layout_inventory_v2"
    / "public"
    / "pc_event_runtime_layout_inventory.v2.json"
)

RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
EFFECTIVE_LINE_LIMIT_PX = 912
RAW_LINE_LIMIT_PX = 1_440
MAX_LINES = 4

PUBLIC_PATH = WORKSTREAM / "public" / "pc_event_w102_context_reflow_wave1.v1.json"
VALIDATION_PATH = WORKSTREAM / "validation.v1.json"
REPORT_PATH = WORKSTREAM / "REPORT_KO.md"
PRIVATE_REVIEW_PATH = WORKSTREAM / "private" / "pc_event_w102_context_reflow_wave1.review.v1.json"
PRIVATE_CANDIDATE_PATH = WORKSTREAM / "private" / "candidate" / RESOURCE

ESC_RE = re.compile(r"\x1bC[ABCZ]")
NAME_TOKEN_RE = re.compile(r"\[(?:b|bm|bs)\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\r|\n")


# Current W102 source text -> same text with context-aware manual line feeds.
# The strings deliberately contain actual ESC color tags and dynamic name tokens.
FIXES: Mapping[int, tuple[str, str]] = {
    3442: (
        "정쟁 때마다 \x1bCB아시카가 가문\x1bCZ의 당주는 \x1bCC교토\x1bCZ를 떠났고,\n현 쇼군 \x1bCA아시카가 [bm75]\x1bCZ 또한\n\x1bCC교토\x1bCZ가 아닌\n\x1bCC오미\x1bCZ에서 원복을 치르고 쇼군직에 올랐다.",
        "정쟁 때마다 \x1bCB아시카가 가문\x1bCZ의 당주는 \x1bCC교토\x1bCZ를 떠났고,\n현 쇼군 \x1bCA아시카가 [bm75]\x1bCZ 또한\n\x1bCC교토\x1bCZ가 아닌 \x1bCC오미\x1bCZ에서 원복을 치르고 쇼군직에 올랐다.",
    ),
    3564: (
        "전국시대에는 드문 연애결혼으로\n아내가 된 \x1bCA히코쓰루\x1bCZ는 총명함과 포용력으로\n냉철한 군사 \x1bCA나베시마 나오시게\x1bCZ를\n뒷받침했다고 한다……",
        "전국시대에는 드문 연애결혼으로\n아내가 된 \x1bCA히코쓰루\x1bCZ는 총명함과 포용력으로\n냉철한 군사 \x1bCA나베시마 나오시게\x1bCZ를 뒷받침했다고 한다……",
    ),
    5780: (
        "적이 된 이상, \x1bCB아자이\x1bCZ를 신속히 멸하고\n\x1bCC오미\x1bCZ를 우리 것으로 만들어야 한다.\n이번에는 \x1bCA[bm1871]\x1bCZ에게\n후방 지원을 부탁해 두었다.",
        "적이 된 이상, \x1bCB아자이\x1bCZ를 신속히 멸하고\n\x1bCC오미\x1bCZ를 우리 것으로 만들어야 한다.\n이번에는 \x1bCA[bm1871]\x1bCZ에게 후방 지원을 부탁해 두었다.",
    ),
    5784: (
        "우리가 \x1bCB[bs1871] 가문\x1bCZ에 원군을 청한다면,\n\x1bCB아자이 가문\x1bCZ도 \x1bCB아사쿠라 가문\x1bCZ에\n구원을 청하겠지……\n큰 싸움이 되겠군.",
        "우리가 \x1bCB[bs1871] 가문\x1bCZ에 원군을 청한다면,\n\x1bCB아자이 가문\x1bCZ도 \x1bCB아사쿠라 가문\x1bCZ에 구원을 청하겠지……\n큰 싸움이 되겠군.",
    ),
    5785: (
        "\x1bCA오다 노부나가\x1bCZ가 \x1bCA[b1871]\x1bCZ의\n군과 함께 \x1bCC오미\x1bCZ로 진군한다는 소식이\n\x1bCC오다니성\x1bCZ에도 전해지자, \x1bCA아자이 나가마사\x1bCZ는\n\x1bCA아사쿠라 요시카게\x1bCZ에게 구원을 청했다.",
        "\x1bCA오다 노부나가\x1bCZ가 \x1bCA[b1871]\x1bCZ의 군과 함께\n\x1bCC오미\x1bCZ로 진군한다는 소식이\n\x1bCC오다니성\x1bCZ에도 전해지자, \x1bCA아자이 나가마사\x1bCZ는\n\x1bCA아사쿠라 요시카게\x1bCZ에게 구원을 청했다.",
    ),
    5790: (
        "어찌 이럴 수가!!\n의형을 배신하면서까지\n오랜 인연을 중히 여겨 아사쿠라 편에 선\n우리를 직접 구원하지 않다니……",
        "어찌 이럴 수가!!\n의형을 배신하면서까지 오랜 인연을 중히 여겨\n아사쿠라 편에 선 우리를\n직접 구원하지 않다니……",
    ),
    5791: (
        "……하지만, \x1bCB아사쿠라\x1bCZ에는\n고 \x1bCA소테키\x1bCZ 님이\n단련한 정예병이 있습니다.",
        "……하지만, \x1bCB아사쿠라\x1bCZ에는\n고 \x1bCA소테키\x1bCZ 님이 단련한 정예병이 있습니다.",
    ),
    5803: (
        "\x1bCC히쿠마성\x1bCZ을 함락한\n\x1bCA[b1871]\x1bCZ는\n마침내 \x1bCC도토미\x1bCZ 공략을 이루었다……",
        "\x1bCC히쿠마성\x1bCZ을 함락한 \x1bCA[b1871]\x1bCZ는\n마침내 \x1bCC도토미\x1bCZ 공략을 이루었다……",
    ),
    5885: (
        "\x1bCC아네가와\x1bCZ에서 격돌한\n\x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 연합군과\n\x1bCB아자이\x1bCZ·\x1bCB아사쿠라\x1bCZ 연합군의 전투는\n초반부터 \x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 측이 우세했다.",
        "\x1bCC아네가와\x1bCZ에서 격돌한 \x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 연합군과\n\x1bCB아자이\x1bCZ·\x1bCB아사쿠라\x1bCZ 연합군의 전투는\n초반부터 \x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 측이 우세했다.",
    ),
    5886: (
        "\x1bCB아사쿠라군\x1bCZ에서 분전한 이는\n\x1bCA마가라 나오타카\x1bCZ였다. \x1bCB[bs1871]\x1bCZ군의 맹공\n속에서 칼을 휘두르며 싸웠으나,\n마지막에는 홀로 적진에 돌격해 전사했다.",
        "\x1bCB아사쿠라군\x1bCZ에서 분전한 이는 \x1bCA마가라 나오타카\x1bCZ였다.\n\x1bCB[bs1871]\x1bCZ군의 맹공 속에서\n칼을 휘두르며 싸웠으나,\n마지막에는 홀로 적진에 돌격해 전사했다.",
    ),
    5887: (
        "\x1bCB아사쿠라군\x1bCZ이 \x1bCB[bs1871]\x1bCZ의 공격에\n패퇴할 무렵, \x1bCB아자이 가문\x1bCZ의 본대도\n\x1bCB오다 가문\x1bCZ의 정면 공격을 받아,\n패색이 짙어지고 있었다.",
        "\x1bCB아사쿠라군\x1bCZ이 \x1bCB[bs1871]\x1bCZ의 공격에 패퇴할 무렵,\n\x1bCB아자이 가문\x1bCZ의 본대도 \x1bCB오다 가문\x1bCZ의 정면 공격을\n받아, 패색이 짙어지고 있었다.",
    ),
    5891: (
        "\x1bCB아자이 가문\x1bCZ에는\n이런 때에\n목숨만 건지려는 비겁자가 필요 없다!\n\x1bCB아자이 가문\x1bCZ을 위해 그 목을 내놓아라!",
        "\x1bCB아자이 가문\x1bCZ에는 이런 때에\n목숨만 건지려는 비겁자가 필요 없다!\n\x1bCB아자이 가문\x1bCZ을 위해 그 목을 내놓아라!",
    ),
    5897: (
        "여기 든 것은 \x1bCB아자이군\x1bCZ 대장\n\x1bCA미타무라 사에몬노조\x1bCZ의 목이다!\n부디 \x1bCA노부나가\x1bCZ 님께서\n확인해 주시길!",
        "여기 든 것은\n\x1bCB아자이군\x1bCZ 대장 \x1bCA미타무라 사에몬노조\x1bCZ의 목이다!\n부디 \x1bCA노부나가\x1bCZ 님께서 확인해 주시길!",
    ),
    5912: (
        "\x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 진영은 대승에 들떴지만,\n\x1bCA나가마사\x1bCZ와 \x1bCA요시카게\x1bCZ의 목을\n벤 것은 아니어서\n두 가문에는 아직 여력이 남아 있었다.",
        "\x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 진영은 대승에 들떴지만,\n\x1bCA나가마사\x1bCZ와 \x1bCA요시카게\x1bCZ의 목을 벤 것은 아니어서\n두 가문에는 아직 여력이 남아 있었다.",
    ),
    5913: (
        "오히려 이 승리로 \x1bCA노부나가\x1bCZ의 세력이\n커지는 것을 경계한\n\x1bCB미요시\x1bCZ·\x1bCC엔랴쿠지\x1bCZ·\x1bCB혼간지\x1bCZ 등이\n반 \x1bCA노부나가\x1bCZ 노선을 취하기 시작했다.",
        "오히려 이 승리로 \x1bCA노부나가\x1bCZ의 세력이 커지는 것을 경계한\n\x1bCB미요시\x1bCZ·\x1bCC엔랴쿠지\x1bCZ·\x1bCB혼간지\x1bCZ 등이\n반 \x1bCA노부나가\x1bCZ 노선을 취하기 시작했다.",
    ),
    5914: (
        "\x1bCC아네가와\x1bCZ에서의 승리가\n오히려 \x1bCA노부나가\x1bCZ를 궁지로 몰아넣는,\n얄궂은 결과로 이어졌다……",
        "\x1bCC아네가와\x1bCZ에서의 승리가 오히려 \x1bCA노부나가\x1bCZ를 궁지로 몰아넣는,\n얄궂은 결과로 이어졌다……",
    ),
    5974: (
        "오늘날에도 \x1bCA노부나가\x1bCZ를 묘사할 때 쓰이는\n‘제육천마왕’은 \x1bCA[bm1251]\x1bCZ에게 보낸\n답서에서 풍자로 자칭한 말이라고\n전해진다.",
        "오늘날에도 \x1bCA노부나가\x1bCZ를 묘사할 때 쓰이는\n‘제육천마왕’은 \x1bCA[bm1251]\x1bCZ에게 보낸 답서에서\n풍자로 자칭한 말이라고 전해진다.",
    ),
    5979: (
        "연회에는 당주 \x1bCA모토나리\x1bCZ를 비롯해,\n‘모리의 두 강’이라 불린 \x1bCA깃카와 모토하루\x1bCZ,\n\x1bCA고바야카와 다카카게\x1bCZ도\n자리했다.",
        "연회에는 당주 \x1bCA모토나리\x1bCZ를 비롯해,\n‘모리의 두 강’이라 불린 \x1bCA깃카와 모토하루\x1bCZ,\n\x1bCA고바야카와 다카카게\x1bCZ도 자리했다.",
    ),
    7310: (
        "포위군에 소속되어 있던 \x1bCA구리야마 젠스케\x1bCZ는\n곧장 성 안으로 들어가,\n유폐된 주군 \x1bCA[b826]\x1bCZ의 감옥으로\n향했다.",
        "포위군에 소속되어 있던 \x1bCA구리야마 젠스케\x1bCZ는\n곧장 성 안으로 들어가,\n유폐된 주군 \x1bCA[b826]\x1bCZ의 감옥으로 향했다.",
    ),
    8284: (
        "대치가 길어지며\n전쟁을 꺼리는 분위기가 짙어지는 가운데,\n\x1bCA[b1871]\x1bCZ의 진영에\n충격적인 소식이 전해졌다…",
        "대치가 길어지며 전쟁을 꺼리는 분위기가 짙어지는 가운데,\n\x1bCA[b1871]\x1bCZ의 진영에 충격적인 소식이 전해졌다…",
    ),
}


class ReflowError(RuntimeError):
    """Raised when source text, tags, or layout contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReflowError(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_sha256(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any, *, source_free: bool = False) -> bytes:
    return (json.dumps(value, ensure_ascii=source_free, indent=2, sort_keys=True) + "\n").encode("ascii" if source_free else "utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def full_width(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xAC00 <= codepoint <= 0xD7AF
        or 0xF900 <= codepoint <= 0xFAFF
    )


def load_token_reservations() -> Mapping[str, Mapping[str, Any]]:
    """Load W102's same-ID Korean runtime-name width reservations.

    The layout inventory is not reused for its line breaks.  It is used only
    for the user's required 30/48-scaled dynamic-name reservation data, which
    was derived from the current W102 token/name relation.
    """

    ledger = json.loads(RUNTIME_LEDGER_PATH.read_text(encoding="utf-8"))
    require(ledger.get("schema") == "nobu16.kr.pc-event-runtime-layout-inventory.v2", "runtime ledger schema differs")
    profile = ledger.get("strict_korean_input", {}).get("event_profile", {})
    require(profile.get("sha256") == CURRENT_SHA256, "runtime ledger is not W102")
    result: dict[str, Mapping[str, Any]] = {}
    for row in ledger.get("rows", []):
        for line in row.get("lines", []):
            for reservation in line.get("runtime_name_reservations", []):
                token = reservation.get("token")
                display = reservation.get("display_string")
                raw = reservation.get("reserved_raw_g1n_width_px")
                effective = reservation.get("reserved_effective_width_px")
                require(isinstance(token, str) and NAME_TOKEN_RE.fullmatch(token) is not None, "invalid runtime token reservation")
                require(isinstance(display, str) and display, f"missing runtime display: {token}")
                require(isinstance(raw, int) and isinstance(effective, int), f"missing runtime width: {token}")
                require(math.ceil(raw * DRAW_FONT_PX / RAW_FULL_WIDTH_PX) == effective, f"runtime scale differs: {token}")
                previous = result.get(token)
                current = {
                    "token": token,
                    "display_string": display,
                    "reserved_raw_g1n_width_px": raw,
                    "reserved_effective_width_px": effective,
                }
                require(previous is None or previous == current, f"ambiguous runtime reservation: {token}")
                result[token] = current
    require(result, "runtime reservation ledger is empty")
    return result


def strip_layout_tokens(value: str, reservations: Mapping[str, Mapping[str, Any]]) -> tuple[str, list[Mapping[str, Any]]]:
    visible = ESC_RE.sub("", value)
    used: list[Mapping[str, Any]] = []

    def replace_name(match: re.Match[str]) -> str:
        token = match.group(0)
        reservation = reservations.get(token)
        require(reservation is not None, f"unreserved runtime name token: {token}")
        used.append(reservation)
        return str(reservation["display_string"])

    visible = NAME_TOKEN_RE.sub(replace_name, visible)
    require(PRINTF_RE.search(visible) is None, f"printf token is out of scope: {value!r}")
    require(all(unicodedata.category(character) != "Cc" for character in visible if character not in "\r\n"), "unexpected control after token expansion")
    return visible, used


def structure_signature(value: str) -> Mapping[str, Any]:
    return {
        "esc_tags": ESC_RE.findall(value),
        "name_tokens": NAME_TOKEN_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        # A removed LF becomes a normal inter-word space when two Korean words
        # are put on one line.  Compare semantic text after normalizing only
        # horizontal/line-break whitespace, never after deleting it.
        "text_with_layout_whitespace_normalized": re.sub(r"[ \t\r\n]+", " ", value),
    }


def validate_colour_structure(value: str) -> None:
    active = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            tag = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(tag) is not None, f"malformed ESC tag: {tag!r}")
            if tag == "\x1bCZ":
                require(active, "unmatched color reset")
                active = False
            else:
                require(not active, "nested color span")
                active = True
            cursor += 3
            continue
        require(not (active and value[cursor] in "\r\n"), "line break inside color span")
        cursor += 1
    require(not active, "unclosed color span")


def line_metrics(value: str, reservations: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    validate_colour_structure(value)
    result: list[dict[str, Any]] = []
    for line in LINEBREAK_RE.split(value):
        display, used = strip_layout_tokens(line, reservations)
        full = sum(1 for character in display if full_width(character))
        half = len(display) - full
        raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
        effective = math.ceil(raw * DRAW_FONT_PX / RAW_FULL_WIDTH_PX)
        result.append(
            {
                "display_string": display,
                "raw_g1n_width_px": raw,
                "effective_width_px": effective,
                "full_width_character_count": full,
                "half_width_character_count": half,
                "is_over_912px": effective > EFFECTIVE_LINE_LIMIT_PX,
                "runtime_name_reservations": used,
            }
        )
    require(len(result) <= MAX_LINES, f"manual lines exceed {MAX_LINES}: {value!r}")
    require(all(not row["is_over_912px"] for row in result), f"line exceeds 912px: {value!r}")
    return result


def load_tables() -> tuple[bytes, Any, Sequence[str], Sequence[str]]:
    packed = CURRENT_PATH.read_bytes()
    require(sha256(packed) == CURRENT_SHA256, "current Steam W102 MSGEV SHA differs")
    _header, raw = decompress_wrapper(packed)
    require(sha256(raw) == CURRENT_RAW_SHA256, "current Steam W102 MSGEV raw SHA differs")
    table = parse_message_table(raw)
    require(rebuild_message_table(table, table.texts) == raw, "current table parse/rebuild differs")
    jp_packed = JP_PATH.read_bytes()
    require(sha256(jp_packed) == JP_SHA256, "direct PC JP MSGEV SHA differs")
    _jp_header, jp_raw = decompress_wrapper(jp_packed)
    jp_table = parse_message_table(jp_raw)
    require(len(table.texts) == EXPECTED_TEXT_COUNT, "current event text count differs")
    # W102 Korean MSGEV has six later-added rows; the direct JP table remains
    # prefix-aligned for every selected coordinate.
    require(len(jp_table.texts) == EXPECTED_TEXT_COUNT - 6, "direct JP event text count differs")
    require(len(table.texts) >= len(jp_table.texts), "current event table shrank")
    return packed, table, table.texts, jp_table.texts


def build_model() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], bytes]:
    packed, table, current, japanese = load_tables()
    reservations = load_token_reservations()
    texts = list(current)
    private_rows: list[dict[str, Any]] = []
    for entry_id, (before, after) in FIXES.items():
        require(current[entry_id] == before, f"current source text differs: {entry_id}")
        require(before != after, f"no-op replacement: {entry_id}")
        require(structure_signature(before) == structure_signature(after), f"tag/token/text structure differs: {entry_id}")
        metrics = line_metrics(after, reservations)
        texts[entry_id] = after
        private_rows.append(
            {
                "entry_id": entry_id,
                "before": before,
                "after": after,
                "direct_jp_utf16le_sha256": text_sha256(japanese[entry_id]),
                "line_count": len(metrics),
                "lines": metrics,
            }
        )
    raw = rebuild_message_table(table, texts)
    candidate = recompress_wrapper(raw, packed)
    _candidate_header, candidate_raw = decompress_wrapper(candidate)
    require(candidate_raw == raw, "candidate wrapper round-trip differs")
    candidate_table = parse_message_table(candidate_raw)
    require(candidate_table.texts == tuple(texts), "candidate parse differs")
    for entry_id, (before, after) in enumerate(zip(current, candidate_table.texts, strict=True)):
        if entry_id in FIXES:
            require(after == FIXES[entry_id][1], f"selected row differs: {entry_id}")
        else:
            require(before == after, f"unselected row changed: {entry_id}")
    public = {
        "schema": "nobu16.kr.pc-event-w102-context-reflow-wave1.v1",
        "source_free": True,
        "scope": {
            "resource": RESOURCE,
            "entry_count": len(FIXES),
            "text_shortened": False,
            "tags_tokens_preserved": True,
            "max_lines": MAX_LINES,
            "effective_line_limit_px": EFFECTIVE_LINE_LIMIT_PX,
            "steam_game_resource_written": False,
        },
        "resource": {
            "source": {"sha256": CURRENT_SHA256, "size": len(packed)},
            "target": {"sha256": sha256(candidate), "size": len(candidate)},
            "operations": [
                {
                    "entry_id": entry_id,
                    "before_utf16le_sha256": text_sha256(before),
                    "after_utf16le_sha256": text_sha256(after),
                    "line_count": len(line_metrics(after, reservations)),
                    "max_effective_width_px": max(row["effective_width_px"] for row in line_metrics(after, reservations)),
                }
                for entry_id, (before, after) in sorted(FIXES.items())
            ],
        },
    }
    require(canonical_json(public, source_free=True).isascii(), "public artifact contains source text")
    private = {"schema": "nobu16.kr.pc-event-w102-context-reflow-wave1-private.v1", "rows": private_rows}
    validation = {
        "schema": "nobu16.kr.pc-event-w102-context-reflow-wave1-validation.v1",
        "status": "PASS",
        "entry_count": len(FIXES),
        "proofs": {
            "current_w102_source_hash_pinned": True,
            "direct_pc_jp_hash_pinned": True,
            "tags_tokens_and_visible_text_preserved": True,
            "four_line_912px_layout_passed": True,
            "unselected_rows_preserved": True,
            "steam_game_resource_written": False,
        },
    }
    return public, private, validation, candidate


def report(validation: Mapping[str, Any]) -> bytes:
    return (
        "# W102 이벤트 문맥 개행 보정 1차\n\n"
        "현 Steam W102 이벤트 본문에서 조사·관형절·피수식어가 줄 사이에서 갈라지는 20개 항목을 "
        "문장 축약 없이 재개행했다. 모든 줄은 Static Patch 007과 009/010의 30px·912px·4줄 "
        "계약으로 다시 측정했다.\n\n"
        f"- 수정 이벤트: {validation['entry_count']}개\n"
        "- 색상 태그, 런타임 토큰, 표시 문구는 보존한다.\n"
        "- 후보는 작업 디렉터리에만 생성하며 Steam 설치 파일은 쓰지 않는다.\n"
    ).encode("utf-8")


def payloads(public: Mapping[str, Any], private: Mapping[str, Any], validation: Mapping[str, Any]) -> Mapping[Path, bytes]:
    return {
        PUBLIC_PATH: canonical_json(public, source_free=True),
        PRIVATE_REVIEW_PATH: canonical_json(private),
        VALIDATION_PATH: canonical_json(validation, source_free=True),
        REPORT_PATH: report(validation),
    }


def write_outputs(public: Mapping[str, Any], private: Mapping[str, Any], validation: Mapping[str, Any], candidate: bytes) -> None:
    for path, payload in payloads(public, private, validation).items():
        atomic_write(path, payload)
    atomic_write(PRIVATE_CANDIDATE_PATH, candidate)


def verify_outputs(public: Mapping[str, Any], private: Mapping[str, Any], validation: Mapping[str, Any], candidate: bytes) -> None:
    for path, payload in payloads(public, private, validation).items():
        require(path.is_file() and path.read_bytes() == payload, f"generated output differs: {path}")
    require(PRIVATE_CANDIDATE_PATH.is_file() and PRIVATE_CANDIDATE_PATH.read_bytes() == candidate, "candidate differs")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify"))
    args = parser.parse_args()
    try:
        public, private, validation, candidate = build_model()
        if args.command == "build":
            write_outputs(public, private, validation, candidate)
        elif args.command == "verify":
            verify_outputs(public, private, validation, candidate)
    except (OSError, ValueError, ReflowError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": "PASS", "entry_count": validation["entry_count"], "steam_game_resource_written": False}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
