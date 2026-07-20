#!/usr/bin/env python3
"""Human semantic restoration review for 6xxx manual event-text compactions.

This workstream is evidence only.  It deliberately writes a review JSON and a
validation JSON under its own directory, but never writes a candidate binary,
the Steam installation, Git state, a release, or the network.

The legacy Korean file is recovery material, not a blind authority: every
selected row is compared with pristine direct-PC JP plus installed PC EN/SC/TC.
The proposal keeps all protected controls and restores the non-abbreviated
meaning at Korean clause boundaries under the static-patch-007, four-line
event-dialogue baseline.
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
OUTPUT = PUBLIC / "manual_compact_6000_review.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"

TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.manual-compact-6000-review.v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
MIN_ID = 6000
MAX_ID = 6999
EXPECTED_ROW_COUNT = 192

RUNTIME_FONT_PX = 30
MAX_EFFECTIVE_WIDTH_PX = 912
MAX_RAW_WIDTH_PX = 1440
MAX_LINES = 4
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24

CURRENT_PATH = (
    REPO
    / "tmp"
    / "pc_event_manual_compact_static007_batch05_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
CURRENT_EXPECTED = {
    "packed_sha256": "8B7B9BF8F104C56F3EED0B3B5E1871E416466CD443020D6306135CCA56E7FE42",
    "raw_sha256": "D49A221732551E6DA673657A577828640E438D02B23AF3B529130A2B9689CC7F",
}

# The parent baseline was replaced by batch05 while this review was underway.
# The selected 6xxx rows must remain byte-for-text identical across that
# provenance transition, so the review verifies that rather than assuming it.
PRIOR_CURRENT_PATH = (
    REPO
    / "tmp"
    / "pc_event_manual_compact_4000_5000_restore_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
PRIOR_CURRENT_EXPECTED = {
    "packed_sha256": "E95A773B7B6448542CF8236868CBEEE7BA49382DD0450DB75DB6CD66CF43FF60",
    "raw_sha256": "9F15BE13C0CFE09D82A9BAE616B57FCE8B4C92187624EB3686E2F850B504F146",
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
KNOWN_REFLOW_PATH = REPO / "workstreams" / "manual_compact_reflow_6000_8000" / "review.v1.json"

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
VISIBLE_UNIT_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]|[가-힣A-Za-z0-9]+|[^\s]")


# Only rows listed here differ from a normalized recovery of the legacy Korean
# text.  They are individually source-reviewed, not a global rewrap rule.
#
# Eight rows reconcile a later current quality change with restored source
# content.  6379 is the one later-current revision that is already source
# complete and is deliberately preserved below.  6654 reuses the previously
# reviewed semantic four-line proposal after revalidating the same sources.
OVERRIDES: dict[int, dict[str, str]] = {
    6072: {
        "strategy": "restore_legacy_text_with_source_quality_semantic_reflow",
        "judgement": "Restore the missing arbitrary-control and excess-conduct clauses; phrase 目に余る as conduct that has gone too far.",
        "text": (
            "하지만 쇼군 \x1bCA요시아키\x1bCZ 공을 꼭두각시처럼\n"
            "제멋대로 부리고 \x1bCC히에이산\x1bCZ에 불을 지르는 등\n"
            "\x1bCA노부나가\x1bCZ의 행태가 도를 넘은 것도 사실이오."
        ),
    },
    6143: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "judgement": "Keep the current dynamic clan token, while restoring the heavy losses, several stand-in retainers, and unaccompanied flight to Hamamatsu.",
        "text": (
            "참패한 \x1bCB[bs1871]\x1bCZ군은 수많은 장병을 잃었고,\n"
            "\x1bCA[bm1871]\x1bCZ도 여러 측근을 대신 희생시킨 끝에,\n"
            "맨몸으로 \x1bCC하마마쓰성\x1bCZ으로 달아났다."
        ),
    },
    6235: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "judgement": "Restore the elder-brother-in-law relation, Nagamasa's own justice, and his resolute rising; the compact current phrase wrongly reduced the relation to 처남.",
        "text": (
            "천하를 제 것으로 삼으려 전횡을 거듭하는\n"
            "손위처남 \x1bCA오다 노부나가\x1bCZ에 맞서,\n"
            "자신의 의를 관철하고자 결연히 일어선\n"
            "\x1bCA아자이 나가마사\x1bCZ…"
        ),
    },
    6275: {
        "strategy": "restore_legacy_text_with_source_quality_grammar_fix",
        "judgement": "Restore the full complaint while correcting the ungrammatical 나를 쇼군으로 construction to the source-faithful accusation against one who disregards the shogun.",
        "text": (
            "\x1bCA노부나가\x1bCZ 놈… 감히 쇼군을 무엇이라 여기는가!\n"
            "내가 \x1bCA노부나가\x1bCZ의 도움으로 쇼군이 된 것은 사실이나,\n"
            "나 없이는 \x1bCA노부나가\x1bCZ도 있을 수 없었을 텐데!"
        ),
    },
    6314: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "judgement": "Retain the current dynamic Fujitaka token and restore continued hesitation, the assent to become 호코슈, and the formal thanks to Yoshiaki.",
        "text": (
            "\x1bCA미쓰히데\x1bCZ는 여전히 망설였으나, \x1bCA[b1773]\x1bCZ의\n"
            "열성적인 설득으로 호코슈가 되기를 승낙하고,\n"
            "\x1bCA요시아키\x1bCZ에게 감사 인사를 올렸다."
        ),
    },
    6326: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "judgement": "Restore the direct address to the Three, their post-Nagayoshi conduct, and the speaker's criticism of Yoshitsugu's weakness.",
        "text": (
            "삼인방 놈들… \x1bCA나가요시\x1bCZ 님이 돌아가신 뒤의\n"
            "방약무인한 행동거지, 눈 뜨고 볼 수 없다!\n"
            "\x1bCA요시쓰구\x1bCZ 님도 \x1bCA요시쓰구\x1bCZ 님이지. 너무나 마음이 약하시니…"
        ),
    },
    6343: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "judgement": "Restore Yoshitsugu's custody, Hisahide's independent force at Shigisan, and the subsequent vassal-daimyo relation to Nobunaga.",
        "text": (
            "\x1bCA히사히데\x1bCZ는 \x1bCA미요시 요시쓰구\x1bCZ의 신병을 \x1bCA노부나가\x1bCZ에게 맡기고,\n"
            "자신은 \x1bCC시기산성\x1bCZ에서 독립 세력이 되어\n"
            "\x1bCA노부나가\x1bCZ에게 종속한 다이묘가 되었다."
        ),
    },
    6379: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "Preserve the current source-complete revision: it keeps the brothers' grandfather, the clan's destruction, the orphaned Kunichika, and Fusaie's protection without abbreviation.",
        "text": (
            "일찍이 형제의 조부 \x1bCA조소카베 가네쓰구\x1bCZ가\n"
            "\x1bCB모토야마 가문\x1bCZ에 멸망하자, 고아가 된\n"
            "\x1bCA쿠니치카\x1bCZ를 \x1bCA이치조 후사이에\x1bCZ가 보호했다."
        ),
    },
    6408: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "judgement": "Replace the over-specific 유폐 with the source's being kept unused, while restoring the continued subordination and loss of daimyo-house standing.",
        "text": (
            "한편 \x1bCC도사\x1bCZ에 남아 \x1bCA모토치카\x1bCZ에게 계속 종속된\n"
            "\x1bCA가네사다\x1bCZ의 아들 \x1bCA다다마사\x1bCZ는 제대로 쓰이지 못한 채,\n"
            "다이묘 가문으로서의 체면도 잃었다."
        ),
    },
    6511: {
        "strategy": "restore_legacy_text_with_source_quality_grammar_fix",
        "judgement": "Restore the youth, elder-retainer duty, and responsibility clauses; make the final collective responsibility grammatically natural in Korean.",
        "text": (
            "주군께서 무모한 싸움을 하시는 것은 젊음 탓.\n"
            "무리한 싸움에서 이기게 하는 것이 우리 노신의 소임.\n"
            "주군께는 허물이 없사옵니다. 저희 책임이라 사료하옵니다."
        ),
    },
    6588: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "judgement": "Retain the current formal 전봉 terminology, and restore Nobukatsu's intended grant, refusal, dispossession, later grant to the dynamic recipient, and the later-time framing.",
        "text": (
            "\x1bCB호조\x1bCZ의 옛 영지는 \x1bCA오다 노부카쓰\x1bCZ에게\n"
            "주어질 터였으나, 전봉을 거부한 탓에 개역되고,\n"
            "\x1bCA[b1871]\x1bCZ에게 주어진 것은\n"
            "훗날의 일이다…"
        ),
    },
    6584: {
        "strategy": "restore_legacy_text_with_semantic_reflow_runtime_reservation",
        "judgement": "Restore the son-in-law relation, survival, four named recipients, and seppuku order; split the first legacy line because the conservative dynamic-name reservation makes it 960 effective px.",
        "text": (
            "\x1bCA[b1871]\x1bCZ의 사위이기도 했던\n"
            "\x1bCA우지나오\x1bCZ는 목숨을 부지했고, 주전파인\n"
            "\x1bCA우지마사\x1bCZ·\x1bCA우지테루\x1bCZ, 중신 \x1bCA마쓰다 노리히데\x1bCZ와\n"
            "\x1bCA다이도지 마사시게\x1bCZ 네 사람에게 할복이 명해졌다…"
        ),
    },
    6654: {
        "strategy": "restore_legacy_text_with_previously_reviewed_semantic_reflow",
        "judgement": "Reuse the prior reviewed four-line reflow after direct-source revalidation: retain 게다가, both absent commanders, the father-son relation, and the concluding contrast.",
        "text": (
            "게다가 \x1bCB모리\x1bCZ 수군의 주장인 \x1bCA무라카미 다케요시\x1bCZ나\n"
            "\x1bCA고바야카와 다카카게\x1bCZ의 모습조차 없이,\n"
            "\x1bCA다케요시\x1bCZ의 아들 \x1bCA모토요시\x1bCZ가\n"
            "이끌고 있었음에도 불구하고, 말이다…"
        ),
    },
    6724: {
        "strategy": "reconcile_current_revision_with_source_complete_text",
        "judgement": "Keep the current 고즈키성 spelling, and restore the callous-decision framing, Katsuhisa's suicide, barely achieved restoration, and second tragic destruction.",
        "text": (
            "비정한 \x1bCA노부나가\x1bCZ의 결단으로 \x1bCC고즈키성\x1bCZ은 함락되었다.\n"
            "\x1bCA가쓰히사\x1bCZ는 자결하고, 겨우 재흥을 이룬 \x1bCB아마고\x1bCZ도\n"
            "다시 멸망의 비극을 맞이하게 되었다…"
        ),
    },
    6980: {
        "strategy": "restore_legacy_text_with_semantic_reflow_runtime_reservation",
        "judgement": "Restore the equal-strategist objective and the requirement to settle the matter personally; split the long dynamic-token line at a Korean clause boundary for the conservative reservation.",
        "text": (
            "이걸로 된 것입니다.\n"
            "\x1bCA[bm826]\x1bCZ 님이 저와 어깨를 나란히 할\n"
            "군사가 되기 위해서라도 이 일은\n"
            "스스로의 손으로 매듭지어야 합니다."
        ),
    },
}


class ReviewError(RuntimeError):
    """Raised when a pinned input or review invariant is violated."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_sha256(value: str) -> str:
    return sha256(value.encode("utf-16-le"))


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing JSON source: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def profile(path: Path) -> tuple[dict[str, Any], tuple[str, ...]]:
    require(path.is_file(), f"missing read-only message source: {path}")
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(
        rebuild_message_table(table, table.texts) == raw,
        f"message-table round trip differs: {path}",
    )
    return (
        {
            "path": str(path),
            "packed_size": len(packed),
            "packed_sha256": sha256(packed),
            "raw_size": len(raw),
            "raw_sha256": sha256(raw),
            "string_count": len(table.texts),
        },
        table.texts,
    )


def normalize_linebreaks(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def normalize_legacy_layout(value: str) -> str:
    """Remove only inherited leading source indentation, never Korean content."""
    return "\n".join(
        line.lstrip(" \u3000") for line in normalize_linebreaks(value).split("\n")
    )


def is_full_width_visible(character: str) -> bool:
    """Static-patch-007 reporting class for Korean/CJK visible glyphs."""
    codepoint = ord(character)
    return (
        0x1100 <= codepoint <= 0x11FF  # Hangul Jamo
        or 0x3130 <= codepoint <= 0x318F  # Compatibility Jamo
        or 0x3040 <= codepoint <= 0x30FF  # Kana
        or 0x3400 <= codepoint <= 0x4DBF  # CJK extension A
        or 0x4E00 <= codepoint <= 0x9FFF  # CJK unified ideographs
        or 0xAC00 <= codepoint <= 0xD7A3  # Hangul syllables
        or 0xA960 <= codepoint <= 0xA97F  # Hangul Jamo extended-A
        or 0xD7B0 <= codepoint <= 0xD7FF  # Hangul Jamo extended-B
    )


def assert_colour_tags(value: str, entry_id: int) -> None:
    in_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"{entry_id}: malformed ESC {token!r}")
            if token == "\x1bCZ":
                require(in_span, f"{entry_id}: unmatched ESC close")
                in_span = False
            else:
                require(not in_span, f"{entry_id}: nested ESC colour tag")
                in_span = True
            cursor += 3
            continue
        require(
            not (in_span and value[cursor] in "\r\n"),
            f"{entry_id}: line break inserted inside a colour span",
        )
        cursor += 1
    require(not in_span, f"{entry_id}: unterminated ESC colour tag")


def control_signature(value: str) -> dict[str, Any]:
    other_controls = [
        f"U+{ord(character):04X}"
        for character in value
        if ord(character) < 0x20 and character not in {"\x00", "\n", "\r", "\x1b"}
    ]
    assert_colour_tags(value, -1)
    return {
        "esc_tokens": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "terminator_nul_count": value.count("\x00"),
        "other_control_codepoints": other_controls,
        "line_break_inside_tag": False,
    }


def visible_units(value: str) -> list[str]:
    return VISIBLE_UNIT_RE.findall(ESC_RE.sub("", value))


def reintroduced_surface_units(before: str, after: str) -> list[str]:
    """Expose target-side Korean surface units absent from a compact version."""
    left = visible_units(before)
    right = visible_units(after)
    result: list[str] = []
    for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(a=left, b=right).get_opcodes():
        if tag in {"insert", "replace"}:
            for unit in right[j1:j2]:
                if unit not in result:
                    result.append(unit)
    return result[:64]


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
            require(0 <= number < len(names), f"{entry_id}: runtime token outside table: {token}")
            reservation = reservations.get(token)
            require(reservation is not None, f"{entry_id}: missing runtime reservation: {token}")
            displayed = ESC_RE.sub("", normalize_linebreaks(names[number])).replace("\n", " ")
            display_full = sum(is_full_width_visible(character) for character in displayed)
            display_half = len(displayed) - display_full
            reserved_raw = reservation["reserved_full_name_width_px"]
            runtime_items.append(
                {
                    "token": token,
                    "source_name_id": number,
                    "display_string": displayed,
                    "display_full_width_character_count": display_full,
                    "display_half_width_character_count": display_half,
                    "reserved_raw_g1n_width_px": reserved_raw,
                    "reserved_effective_width_px": math.ceil(reserved_raw * RUNTIME_FONT_PX / RAW_FULL_WIDTH_PX),
                    "runtime_proven": False,
                    "reservation_reason": "Scene-limited conservative reservation scaled by 30/48; not runtime-proven.",
                }
            )
            return displayed

        display = RUNTIME_RE.sub(render_runtime, visible_template)
        literal = RUNTIME_RE.sub("", visible_template)
        literal_full = sum(is_full_width_visible(character) for character in literal)
        literal_half = len(literal) - literal_full
        reserved_raw = sum(item["reserved_raw_g1n_width_px"] for item in runtime_items)
        raw_width = literal_full * RAW_FULL_WIDTH_PX + literal_half * RAW_HALF_WIDTH_PX + reserved_raw
        effective_width = math.ceil(raw_width * RUNTIME_FONT_PX / RAW_FULL_WIDTH_PX)
        display_full = sum(is_full_width_visible(character) for character in display)
        display_half = len(display) - display_full
        result.append(
            {
                "line_number": line_number,
                "encoded_string": encoded_line,
                "display_string": display,
                "raw_g1n_width_px": raw_width,
                "literal_raw_g1n_width_px": literal_full * RAW_FULL_WIDTH_PX + literal_half * RAW_HALF_WIDTH_PX,
                "reserved_raw_g1n_width_px": reserved_raw,
                "effective_width_px": effective_width,
                "full_width_character_count": display_full,
                "half_width_character_count": display_half,
                "runtime_reservations": runtime_items,
                "exceeds_912px": effective_width > MAX_EFFECTIVE_WIDTH_PX,
            }
        )
    return result


def source_profile_summary(profile_value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: profile_value[key]
        for key in ("path", "packed_sha256", "raw_sha256", "packed_size", "raw_size", "string_count")
    }


def main() -> int:
    current_profile, current = profile(CURRENT_PATH)
    require(
        current_profile["packed_sha256"] == CURRENT_EXPECTED["packed_sha256"],
        "batch05 strict current packed profile drift",
    )
    require(
        current_profile["raw_sha256"] == CURRENT_EXPECTED["raw_sha256"],
        "batch05 strict current raw profile drift",
    )
    prior_profile, prior = profile(PRIOR_CURRENT_PATH)
    require(
        prior_profile["packed_sha256"] == PRIOR_CURRENT_EXPECTED["packed_sha256"],
        "prior strict current packed profile drift",
    )
    require(
        prior_profile["raw_sha256"] == PRIOR_CURRENT_EXPECTED["raw_sha256"],
        "prior strict current raw profile drift",
    )
    jp_profile, jp = profile(DIRECT_JP_PATH)
    en_profile, en = profile(DIRECT_EN_PATH)
    sc_profile, sc = profile(DIRECT_SC_PATH)
    tc_profile, tc = profile(DIRECT_TC_PATH)
    legacy_profile, legacy = profile(LEGACY_KO_PATH)
    for label, texts in (("prior", prior), ("jp", jp), ("en", en), ("sc", sc), ("tc", tc), ("legacy", legacy)):
        require(len(texts) == len(current), f"{label} string count differs from batch05 current")

    historical = read_json(HISTORICAL_MANIFEST)
    reservations_doc = read_json(RESERVATION_MANIFEST)
    inventory = read_json(INVENTORY_MANIFEST)
    known_reflow = read_json(KNOWN_REFLOW_PATH)
    reservations = reservations_doc.get("reservations")
    require(isinstance(reservations, dict), "runtime reservation map missing")
    historical_entries = historical.get("entries")
    require(isinstance(historical_entries, list), "historical entry list missing")
    inventory_rows = inventory.get("rows")
    require(isinstance(inventory_rows, list), "inventory row list missing")
    inventory_by_id = {row["entry_id"]: row for row in inventory_rows if isinstance(row, dict)}

    selected = [
        row
        for row in historical_entries
        if isinstance(row, dict)
        and MIN_ID <= row.get("id", -1) <= MAX_ID
        and (
            row.get("operation") == "manual_compact_korean_layout"
            or "manual_compact_korean_layout" in row.get("newline_operations", [])
        )
    ]
    selected.sort(key=lambda row: row["id"])
    require(len(selected) == EXPECTED_ROW_COUNT, f"manual compact 6xxx count drift: {len(selected)}")
    selected_ids = [row["id"] for row in selected]
    require(
        all(current[entry_id] == prior[entry_id] for entry_id in selected_ids),
        "batch05 changed a scoped 6xxx current string unexpectedly",
    )

    known_6654_rows = [row for row in known_reflow.get("rows", []) if row.get("entry_id") == 6654]
    require(len(known_6654_rows) == 1, "known 6654 reflow record missing")
    require(
        OVERRIDES[6654]["text"] == known_6654_rows[0]["proposed_ko"],
        "6654 proposal differs from the previously reviewed reflow",
    )

    reviewed_rows: list[dict[str, Any]] = []
    strategy_counts: Counter[str] = Counter()
    runtime_rows: list[int] = []
    current_preserved_ids: list[int] = []
    current_reconciled_ids: list[int] = []
    semantic_reflow_ids: list[int] = []
    source_quality_fix_ids: list[int] = []
    legacy_restore_ids: list[int] = []

    for historical_row in selected:
        entry_id = historical_row["id"]
        compact = historical_row.get("ko")
        require(isinstance(compact, str), f"{entry_id}: historical compact Korean missing")
        current_ko = current[entry_id]
        legacy_ko = normalize_legacy_layout(legacy[entry_id])
        override = OVERRIDES.get(entry_id)
        if override is None:
            proposed = legacy_ko
            strategy = "restore_legacy_precompaction_full_korean_text"
            judgement = (
                "Direct PC JP/EN/SC/TC retains semantic material compacted out of the current row; "
                "restore the source-complete legacy Korean without shortening and retain its Korean clause boundaries."
            )
            legacy_restore_ids.append(entry_id)
        else:
            proposed = override["text"]
            strategy = override["strategy"]
            judgement = override["judgement"]

        assert_colour_tags(current_ko, entry_id)
        assert_colour_tags(legacy_ko, entry_id)
        assert_colour_tags(proposed, entry_id)
        current_signature = control_signature(current_ko)
        proposed_signature = control_signature(proposed)
        direct_signature = control_signature(jp[entry_id])
        require(
            proposed_signature == current_signature == direct_signature,
            f"{entry_id}: proposed/current/direct-JP protected-control signature differs",
        )
        metrics = layout_lines(entry_id, proposed, current, reservations)
        require(1 <= len(metrics) <= MAX_LINES, f"{entry_id}: line count {len(metrics)} exceeds {MAX_LINES}")
        require(
            not any(line["exceeds_912px"] for line in metrics),
            f"{entry_id}: proposal exceeds {MAX_EFFECTIVE_WIDTH_PX}px",
        )
        runtime_tokens = proposed_signature["runtime_tokens"]
        if runtime_tokens:
            runtime_rows.append(entry_id)
        if strategy == "preserve_current_post_compaction_quality_revision":
            current_preserved_ids.append(entry_id)
        elif strategy.startswith("reconcile_current_revision"):
            current_reconciled_ids.append(entry_id)
        if "semantic_reflow" in strategy or "previously_reviewed_semantic_reflow" in strategy:
            semantic_reflow_ids.append(entry_id)
        if "grammar_fix" in strategy:
            source_quality_fix_ids.append(entry_id)
        strategy_counts[strategy] += 1

        inventory_row = inventory_by_id.get(entry_id)
        require(inventory_row is not None, f"{entry_id}: inventory row missing")
        proposed_units = reintroduced_surface_units(compact, proposed)
        current_to_proposed = reintroduced_surface_units(current_ko, proposed)
        reviewed_rows.append(
            {
                "entry_id": entry_id,
                "scene_batch_id": inventory_row.get("scene_batch_id"),
                "review_status": "ready_for_semantic_restoration_candidate",
                "review_judgement": judgement,
                "restoration_strategy": strategy,
                "current_quality_preserved": strategy == "preserve_current_post_compaction_quality_revision",
                "current_quality_reconciled": strategy.startswith("reconcile_current_revision"),
                "historical_manual_compact_ko": compact,
                "current_ko_at_batch05_strict_baseline": current_ko,
                "legacy_precompaction_ko": legacy_ko,
                "proposed_ko": proposed,
                "legacy_matches_proposed_after_normalization": legacy_ko == proposed,
                "historical_compact_to_proposed_surface_units": proposed_units,
                "current_to_proposed_surface_units": current_to_proposed,
                "direct_pc_sources": {
                    "jp": jp[entry_id],
                    "en": en[entry_id],
                    "sc": sc[entry_id],
                    "tc": tc[entry_id],
                },
                "current_ko_utf16le_sha256": text_sha256(current_ko),
                "legacy_precompaction_ko_utf16le_sha256": text_sha256(legacy_ko),
                "proposed_ko_utf16le_sha256": text_sha256(proposed),
                "control_signature": {
                    "current": current_signature,
                    "legacy": control_signature(legacy_ko),
                    "proposed": proposed_signature,
                    "direct_pc_jp": direct_signature,
                    "proposed_current_direct_jp_match": True,
                },
                "runtime_token_reservation": {
                    "actual_runtime_tokens": runtime_tokens,
                    "runtime_proven": False,
                    "policy": "Known scene-limited conservative reservation only; every reserved raw width is scaled by 30/48 for the static-patch-007 effective width.",
                },
                "layout": {
                    "line_count": len(metrics),
                    "max_lines": MAX_LINES,
                    "all_lines_pass_static_patch_007": True,
                    "lines": metrics,
                },
                "any_line_exceeds_912px": False,
            }
        )

    require(len(reviewed_rows) == EXPECTED_ROW_COUNT, "review count accounting drift")
    require(current_preserved_ids == [6379], f"unexpected current-preserved IDs: {current_preserved_ids}")
    require(
        current_reconciled_ids == [6143, 6235, 6314, 6326, 6343, 6408, 6588, 6724],
        f"unexpected current-reconciled IDs: {current_reconciled_ids}",
    )
    require(semantic_reflow_ids == [6072, 6584, 6654, 6980], f"unexpected semantic reflow IDs: {semantic_reflow_ids}")
    require(source_quality_fix_ids == [6275, 6511], f"unexpected grammar fix IDs: {source_quality_fix_ids}")
    require(len(legacy_restore_ids) == 177, f"legacy restore count drift: {len(legacy_restore_ids)}")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "resource": RESOURCE,
            "event_id_range": [MIN_ID, MAX_ID],
            "manual_compact_target_count": len(reviewed_rows),
            "candidate_binary_created": False,
            "steam_files_written": False,
            "git_or_release_actions_performed": False,
            "network_operation_performed": False,
        },
        "layout_baseline": {
            "runtime_font_px": RUNTIME_FONT_PX,
            "runtime_usable_line_width_px": MAX_EFFECTIVE_WIDTH_PX,
            "max_lines": MAX_LINES,
            "raw_g1n_full_width_advance_px": RAW_FULL_WIDTH_PX,
            "raw_g1n_half_width_advance_px": RAW_HALF_WIDTH_PX,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "raw_g1n_pass_limit_px": MAX_RAW_WIDTH_PX,
            "effective_width_pass_limit_px": MAX_EFFECTIVE_WIDTH_PX,
            "dynamic_name_reservations": "Reserve the known token raw width, then scale by 30/48. runtime_proven remains false.",
        },
        "sources": {
            "current_ko_batch05_strict_baseline": source_profile_summary(current_profile),
            "prior_current_ko_before_batch05": source_profile_summary(prior_profile),
            "direct_pc_jp_pristine": source_profile_summary(jp_profile),
            "direct_pc_en": source_profile_summary(en_profile),
            "direct_pc_sc": source_profile_summary(sc_profile),
            "direct_pc_tc": source_profile_summary(tc_profile),
            "legacy_precompaction_ko_backup": source_profile_summary(legacy_profile),
            "historical_manual_compact_manifest": {
                "path": str(HISTORICAL_MANIFEST),
                "sha256": sha256(HISTORICAL_MANIFEST.read_bytes()),
            },
            "runtime_reservation_manifest": {
                "path": str(RESERVATION_MANIFEST),
                "sha256": sha256(RESERVATION_MANIFEST.read_bytes()),
            },
            "inventory_manifest": {
                "path": str(INVENTORY_MANIFEST),
                "sha256": sha256(INVENTORY_MANIFEST.read_bytes()),
            },
            "previously_reviewed_6654_reflow": {
                "path": str(KNOWN_REFLOW_PATH),
                "sha256": sha256(KNOWN_REFLOW_PATH.read_bytes()),
                "entry_id": 6654,
            },
        },
        "baseline_transition": {
            "batch05_replaced_prior_current_for_global_chain": True,
            "selected_6xxx_rows_unchanged_count": len(selected_ids),
            "selected_6xxx_rows_changed_count": 0,
            "comparison": "Every selected current Korean string is equal in the prior and batch05 strict candidates.",
        },
        "judgement_groups": [
            {
                "group": "legacy_source_complete_restoration",
                "ids": legacy_restore_ids,
                "reason": "Direct PC JP/EN/SC/TC supports the unabridged legacy Korean; restore semantic content and existing Korean clause boundaries without shortening.",
            },
            {
                "group": "later_current_revision_reconciled_with_source_complete_text",
                "ids": current_reconciled_ids,
                "reason": "A later current revision changed terms/tokens but remained abbreviated or incomplete; retain the valid current detail and restore all direct-source content.",
            },
            {
                "group": "later_current_revision_preserved",
                "ids": current_preserved_ids,
                "reason": "The later current text is already source-complete and non-abbreviated, so it is preserved rather than replaced by an older backup.",
            },
            {
                "group": "semantic_reflow_required",
                "ids": semantic_reflow_ids,
                "reason": "The restoration is retained in full but placed at Korean semantic clause boundaries; 6654 reuses the previously reviewed four-line plan.",
            },
            {
                "group": "source_quality_grammar_fix",
                "ids": source_quality_fix_ids,
                "reason": "The full semantic recovery is retained while correcting a clear Korean grammar/meaning issue found during direct-source comparison.",
            },
            {
                "group": "runtime_name_tokens",
                "ids": runtime_rows,
                "reason": "Token widths are conservatively reserved and scaled, but runtime_proven is false; scene-specific in-game evidence remains required before claiming runtime proof.",
            },
        ],
        "counts": {
            "restoration_strategy_counts": dict(sorted(strategy_counts.items())),
            "legacy_full_text_restoration_count": len(legacy_restore_ids),
            "current_quality_preserved_count": len(current_preserved_ids),
            "current_quality_reconciled_count": len(current_reconciled_ids),
            "semantic_reflow_count": len(semantic_reflow_ids),
            "source_quality_grammar_fix_count": len(source_quality_fix_ids),
            "runtime_token_row_count": len(runtime_rows),
            "all_rows_four_or_fewer_lines": True,
            "all_rows_within_912px": True,
        },
        "entries": reviewed_rows,
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
        "schema": "nobu16.kr.manual-compact-6000-review-validation.v1",
        "review_output": str(OUTPUT),
        "review_output_sha256": sha256(OUTPUT.read_bytes()),
        "target_count": len(reviewed_rows),
        "baseline_transition_selected_6xxx_rows_unchanged_count": len(selected_ids),
        "max_line_count": max(row["layout"]["line_count"] for row in reviewed_rows),
        "over_912px_line_count": sum(
            line["exceeds_912px"]
            for row in reviewed_rows
            for line in row["layout"]["lines"]
        ),
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
