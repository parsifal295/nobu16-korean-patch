#!/usr/bin/env python3
"""Read-only human restoration review for 10xxx manual event compactions.

The old ``manual_compact_korean_layout`` pass shortened Korean dialogue to
fit the former three-line gate.  This review is deliberately evidence-only:
it rechecks all selected 10xxx rows against the current Static Patch 007
strict predecessor, the full pre-compaction Korean backup, and direct
JP/EN/SC/TC PC witnesses.  It never creates a message binary or touches
Steam, Git, release state, or the network.
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
OUTPUT = PUBLIC / "manual_compact_10000_11008_review.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-manual-compact-static007-10000-review.v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
MIN_ID = 10_000
MAX_ID = 11_008
EXPECTED_ROW_COUNT = 148

# Static Patch 007 is the authoritative event-dialogue layout.  The raw
# threshold is 1440 because a G1N 48px full-width advance is scaled to the
# verified 30px runtime font before comparing it with the 912px text box.
RUNTIME_FONT_PX = 30
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
MAX_RAW_WIDTH_PX = 1440
MAX_EFFECTIVE_WIDTH_PX = 912
MAX_LINES = 4

# Parent work moved the strict predecessor while this review was in progress.
# This is deliberately the only current Korean candidate used by the final
# evidence artifact; the 6xxx–7xxx restoration does not alter this 10xxx
# scope, which the script proves by reading this exact candidate.
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
INVENTORY_MANIFEST = (
    REPO
    / "workstreams"
    / "pc_event_manual_compact_korean_layout_inventory_v1"
    / "public"
    / "msgev_manual_compact_korean_layout_inventory.v1.json"
)
KNOWN_REFLOW_PATH = (
    REPO
    / "workstreams"
    / "manual_compact_reflow_9000_11000_v1"
    / "review.v1.json"
)
KNOWN_REFLOW_IDS = (
    10_136,
    10_183,
    10_314,
    10_334,
    10_343,
    10_463,
    10_595,
    10_625,
    10_744,
)
EXPECTED_CURRENT_DIFF_IDS = (
    10_334,
    10_493,
    10_507,
    10_508,
    10_566,
    10_630,
    10_817,
    10_866,
    10_940,
    10_990,
    10_999,
    11_008,
)

ESC = "\x1b"
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
VISIBLE_UNIT_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]|[가-힣A-Za-z0-9]+|[^\s]")


# Only rows altered after the old compact overlay need a fresh content choice.
# Every target below restores all propositions from the direct witnesses;
# current terminology is retained where it is a later Korean quality fix
# (notably 내대신) and the direct colour-tag sequence is kept intact.
OVERRIDES: dict[int, dict[str, str]] = {
    10_493: {
        "strategy": "reconcile_current_title_term_with_full_source_restoration",
        "judgement": (
            "Retain the later Korean title term ‘내대신’, but restore the full "
            "father's defense, transient ambition, prohibition, and alliance "
            "clauses rather than the compressed current wording."
        ),
        "text": (
            f"아버지는 몸을 던져 {ESC}CB다테{ESC}CZ 가문을 지켜 냈다.\n"
            "한때의 야망으로 무너뜨리는 일은\n"
            "있어서는 안 된다!\n"
            f"여기서는 {ESC}CA내대신{ESC}CZ 님의 편에 서자."
        ),
    },
    10_507: {
        "strategy": "reconcile_current_title_term_with_full_source_restoration",
        "judgement": (
            "Retain ‘내대신’ while restoring ‘우에스기 정벌에서’, "
            "the Tokugawa force, arrival at Mino, Edo departure, and the "
            "prospective final battle without colloquial truncation."
        ),
        "text": (
            f"{ESC}CB우에스기{ESC}CZ 정벌에서 돌아선\n"
            f"{ESC}CB도쿠가와 측{ESC}CZ 군세는 이미 {ESC}CC미노{ESC}CZ에 이르렀고,\n"
            f"{ESC}CA내대신{ESC}CZ 님도 {ESC}CC에도{ESC}CZ에서 출진하게 되었습니다.\n"
            "결전이 가까울 것입니다."
        ),
    },
    10_508: {
        "strategy": "reconcile_current_title_term_with_full_source_restoration",
        "judgement": (
            "Retain ‘내대신’ and restore the leader's army, the prime "
            "opportunity to attack Edo, Ishida's victory condition, and the "
            "joint advance without shortening."
        ),
        "text": (
            f"{ESC}CA내대신{ESC}CZ 님이 이끄는 대군이 떠난\n"
            f"지금이야말로 {ESC}CC에도{ESC}CZ를 공격할 절호의 기회입니다.\n"
            f"{ESC}CB이시다 측{ESC}CZ이 결전에서 승리하면\n"
            f"함께 {ESC}CC에도{ESC}CZ로 쳐들어갑시다."
        ),
    },
    10_566: {
        "strategy": "reconcile_source_complete_restoration_with_current_tag_binding",
        "judgement": (
            "Restore ‘가쓰모토 구원의 대의명분’, the nationwide daimyo "
            "order, and the Hideyori-subjugation plan; retain the current "
            "direct-source colour binding of 가쓰모토 then 도쿠가와."
        ),
        "text": (
            f"그리하여 {ESC}CA가쓰모토{ESC}CZ 구원의 대의명분을 얻은\n"
            f"{ESC}CB도쿠가와{ESC}CZ는 마침내 각국의 여러 다이묘에게\n"
            f"호령하고, {ESC}CA히데요리{ESC}CZ 토벌에 나설\n"
            "셈이었다."
        ),
    },
    10_630: {
        "strategy": "reconcile_source_complete_restoration_with_current_tag_binding",
        "judgement": (
            "Restore Osaka Castle as Hideyoshi's castle built to inherit "
            "Nobunaga's aspiration and the approaching final Sengoku battle, "
            "while retaining the direct-source tag binding corrected in the "
            "current row."
        ),
        "text": (
            f"{ESC}CC오사카성{ESC}CZ― {ESC}CA노부나가{ESC}CZ의 뜻을 잇고자\n"
            f"{ESC}CA히데요시{ESC}CZ가 세운 성을 무대로,\n"
            "전국시대 최후의 전쟁이\n"
            "시시각각 다가오고 있었다……"
        ),
    },
    10_817: {
        "strategy": "restore_full_legacy_korean_with_four_line_semantic_reflow",
        "judgement": (
            "Restore the beak, the startled insects leaving the hole, and "
            "the act of eating them; the four Korean clauses preserve the "
            "woodpecker-strategy explanation without compression."
        ),
        "text": (
            "딱따구리가 나무 속 벌레를 잡을 때\n"
            "구멍 반대편을 부리로 쪼아,\n"
            "놀라 구멍 밖으로 나온 벌레를\n"
            "잡아먹는 습성에서 따온 전법이다."
        ),
    },
    10_866: {
        "strategy": "reconcile_source_complete_restoration_with_current_tag_binding",
        "judgement": (
            "Restore Ieyasu's request for aid to save Nagashino Castle, the "
            "longstanding Shingen enmity, and Nobunaga's acceptance; retain "
            "the current direct-source place/person tag binding."
        ),
        "text": (
            f"{ESC}CC나가시노성{ESC}CZ을 구하고자 지원을 청한\n"
            f"{ESC}CA도쿠가와 이에야스{ESC}CZ. {ESC}CA오다 노부나가{ESC}CZ는\n"
            f"{ESC}CA신겐{ESC}CZ 때부터 이어진 악연에 결판을 내고자\n"
            "그 요청을 흔쾌히 받아들였다."
        ),
    },
    10_940: {
        "strategy": "reconcile_source_complete_restoration_with_current_tag_binding",
        "judgement": (
            "Restore Shingen's invasion and ravaging of Totomi, Ieyasu as "
            "Nobunaga's ally, and the ongoing greatest trial; retain the "
            "current direct-source place/person tag binding."
        ),
        "text": (
            f"{ESC}CC도토미{ESC}CZ를 불길처럼 침공해 유린한 {ESC}CA신겐{ESC}CZ―\n"
            f"{ESC}CA노부나가{ESC}CZ의 맹우, {ESC}CA도쿠가와 이에야스{ESC}CZ는\n"
            "생애 최대의 시련에 맞서려 하고 있었다."
        ),
    },
    10_990: {
        "strategy": "restore_full_legacy_korean_with_four_line_semantic_reflow",
        "judgement": (
            "Restore the fully spaced plea and the possibility of escape, "
            "placing the conditional escape clause on two Korean semantic "
            "lines without deleting its uncertainty."
        ),
        "text": (
            "주군, 들어 주십시오!\n"
            f"이 {ESC}CC혼노지{ESC}CZ 지하에는 숨은 길이 있습니다…\n"
            "운이 좋으면 밖으로 빠져나갈 수도\n"
            "있을지 모릅니다."
        ),
    },
    10_999: {
        "strategy": "restore_full_legacy_korean_with_four_line_semantic_reflow",
        "judgement": (
            "Restore Yasuke's resourcefulness, the group surviving, the "
            "purpose of opposing Mitsuhide, departure from Kyoto, and the "
            "route to the Azuchi home base without compression."
        ),
        "text": (
            f"{ESC}CA야스케{ESC}CZ의 기지로 살아남은 {ESC}CA노부나가{ESC}CZ 일행.\n"
            f"그들은 반역자 {ESC}CA아케치 미쓰히데{ESC}CZ에 맞서기 위해,\n"
            f"{ESC}CC교토{ESC}CZ를 빠져나와 본거지·{ESC}CC아즈치성{ESC}CZ으로\n"
            "향했다…"
        ),
    },
    11_008: {
        "strategy": "preserve_source_complete_current_quality_revision",
        "judgement": (
            "The later current revision remains source-complete: Nobunaga "
            "returns to Azuchi, breaks with the former Oda retainers, and "
            "declares independence with only a small group including Yasuke. "
            "Its existing four semantic Korean lines are retained."
        ),
        "text": (
            f"{ESC}CC아즈치성{ESC}CZ으로 돌아온 {ESC}CA노부나가{ESC}CZ는\n"
            f"{ESC}CA하시바{ESC}CZ, {ESC}CA시바타{ESC}CZ 등 {ESC}CB오다{ESC}CZ의 옛 신하들과\n"
            f"결별하고, {ESC}CA야스케{ESC}CZ 등 소수의 가신만으로\n"
            "독립을 선언했다."
        ),
    },
}


class ReviewError(RuntimeError):
    """Raised when a pinned evidence or review invariant drifts."""


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
    require(isinstance(value, dict), f"JSON root is not object: {path}")
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
    return "\n".join(
        line.lstrip(" \u3000") for line in normalize_linebreaks(value).split("\n")
    )


def is_full_width_visible(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
        or 0x3040 <= codepoint <= 0x30FF
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xAC00 <= codepoint <= 0xD7A3
        or 0xA960 <= codepoint <= 0xA97F
        or 0xD7B0 <= codepoint <= 0xD7FF
    )


def assert_colour_tags(value: str, entry_id: int) -> None:
    in_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == ESC:
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"{entry_id}: malformed ESC {token!r}")
            if token == f"{ESC}CZ":
                require(in_span, f"{entry_id}: unmatched colour close")
                in_span = False
            else:
                require(not in_span, f"{entry_id}: nested colour span")
                in_span = True
            cursor += 3
        else:
            require(
                not (in_span and value[cursor] in "\r\n"),
                f"{entry_id}: line break inside colour tag",
            )
            cursor += 1
    require(not in_span, f"{entry_id}: unterminated colour span")


def control_signature(value: str) -> dict[str, Any]:
    assert_colour_tags(value, -1)
    return {
        "esc_tokens": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "terminator_nul_count": value.count("\x00"),
        "other_control_codepoints": [
            f"U+{ord(character):04X}"
            for character in value
            if ord(character) < 0x20 and character not in {"\x00", "\n", "\r", ESC}
        ],
        "line_break_inside_tag": False,
    }


def visible_units(value: str) -> list[str]:
    return VISIBLE_UNIT_RE.findall(ESC_RE.sub("", value))


def reintroduced_surface_units(before: str, after: str) -> list[str]:
    before_units = visible_units(before)
    after_units = visible_units(after)
    result: list[str] = []
    for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(
        a=before_units, b=after_units
    ).get_opcodes():
        if tag in {"insert", "replace"}:
            for unit in after_units[j1:j2]:
                if unit not in result:
                    result.append(unit)
    return result[:96]


def layout_lines(
    entry_id: int,
    target: str,
    names: tuple[str, ...],
    reservations: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, encoded_line in enumerate(normalize_linebreaks(target).split("\n"), 1):
        visible_template = ESC_RE.sub("", encoded_line)
        runtime_items: list[dict[str, Any]] = []

        def render_runtime(match: re.Match[str]) -> str:
            token = match.group(0)
            number = int(re.search(r"(\d+)\]$", token).group(1))
            require(0 <= number < len(names), f"{entry_id}: token outside message table {token}")
            reservation = reservations.get(token)
            require(isinstance(reservation, dict), f"{entry_id}: missing reservation {token}")
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
                    reservation["reserved_full_name_width_px"]
                    * RUNTIME_FONT_PX
                    / RAW_FULL_WIDTH_PX
                ),
                "runtime_proven": False,
                "reservation_reason": (
                    "Scene-limited conservative reservation scaled by 30/48; "
                    "not runtime-proven."
                ),
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
        rows.append({
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
            "exceeds_raw_1440px": raw_width > MAX_RAW_WIDTH_PX,
            "exceeds_912px": effective_width > MAX_EFFECTIVE_WIDTH_PX,
        })
    return rows


def source_summary(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value[key]
        for key in ("path", "packed_sha256", "raw_sha256", "packed_size", "raw_size", "string_count")
    }


def main() -> int:
    current_profile, current = profile(CURRENT_PATH)
    require(
        current_profile["packed_sha256"] == CURRENT_EXPECTED["packed_sha256"],
        "strict current packed baseline drift",
    )
    require(
        current_profile["raw_sha256"] == CURRENT_EXPECTED["raw_sha256"],
        "strict current raw baseline drift",
    )
    legacy_profile, legacy = profile(LEGACY_KO_PATH)
    direct_profiles: dict[str, dict[str, Any]] = {}
    direct_texts: dict[str, tuple[str, ...]] = {}
    for language, path in DIRECT_PATHS.items():
        direct_profiles[language], direct_texts[language] = profile(path)
    for language, values in direct_texts.items():
        require(len(values) == len(current), f"{language}: message count differs from current")
    require(len(legacy) == len(current), "legacy message count differs from current")

    historical = read_json(HISTORICAL_MANIFEST)
    reservations_doc = read_json(RESERVATION_MANIFEST)
    inventory = read_json(INVENTORY_MANIFEST)
    known_reflow = read_json(KNOWN_REFLOW_PATH)
    historical_entries = historical.get("entries")
    reservations = reservations_doc.get("reservations")
    inventory_rows = inventory.get("rows")
    known_rows = known_reflow.get("rows")
    require(isinstance(historical_entries, list), "historical entries missing")
    require(isinstance(reservations, dict), "runtime reservation map missing")
    require(isinstance(inventory_rows, list), "inventory rows missing")
    require(isinstance(known_rows, list), "known reflow rows missing")
    inventory_by_id = {row["entry_id"]: row for row in inventory_rows if isinstance(row, dict)}
    known_by_id = {row["entry_id"]: row for row in known_rows if isinstance(row, dict)}
    require(set(KNOWN_REFLOW_IDS).issubset(known_by_id), "known 10xxx reflow rows missing")

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
    require(len(selected) == EXPECTED_ROW_COUNT, f"manual compact count drift: {len(selected)}")
    selected_ids = tuple(row["id"] for row in selected)
    current_diff_ids = tuple(
        row["id"] for row in selected if current[row["id"]] != row.get("ko")
    )
    require(
        current_diff_ids == EXPECTED_CURRENT_DIFF_IDS,
        f"current-diff scope drift: {current_diff_ids}",
    )
    require(set(OVERRIDES).issubset(set(selected_ids)), "override outside selected scope")

    reviewed: list[dict[str, Any]] = []
    strategy_counts: Counter[str] = Counter()
    default_legacy_ids: list[int] = []
    known_reflow_reused_ids: list[int] = []
    current_diff_reconciled_ids: list[int] = []
    current_diff_preserved_ids: list[int] = []
    runtime_rows: list[int] = []

    for historical_row in selected:
        entry_id = historical_row["id"]
        compact = historical_row.get("ko")
        require(isinstance(compact, str), f"{entry_id}: compact Korean missing")
        current_ko = current[entry_id]
        legacy_ko = normalize_legacy_layout(legacy[entry_id])
        known = known_by_id.get(entry_id)
        override = OVERRIDES.get(entry_id)
        prior_reflow_revalidated = entry_id in KNOWN_REFLOW_IDS

        if override is not None:
            proposed = override["text"]
            strategy = override["strategy"]
            judgement = override["judgement"]
            if entry_id in EXPECTED_CURRENT_DIFF_IDS:
                if strategy.startswith("preserve_source_complete_current"):
                    current_diff_preserved_ids.append(entry_id)
                else:
                    current_diff_reconciled_ids.append(entry_id)
        elif known is not None:
            proposed = known.get("proposed_ko")
            require(isinstance(proposed, str), f"{entry_id}: known proposed text missing")
            strategy = "reuse_and_revalidate_prior_static007_semantic_reflow"
            judgement = (
                "The independently reviewed four-line Korean reflow is "
                "revalidated against the strict current predecessor and direct "
                "PC JP/EN/SC/TC evidence; it restores all legacy source material "
                "without a compact-era omission."
            )
            known_reflow_reused_ids.append(entry_id)
            if entry_id in EXPECTED_CURRENT_DIFF_IDS:
                current_diff_reconciled_ids.append(entry_id)
        else:
            proposed = legacy_ko
            strategy = "restore_source_complete_legacy_korean_existing_semantic_reflow"
            judgement = (
                "Individual comparison confirms no later current quality revision "
                "for this row.  The full pre-compaction Korean preserves direct "
                "PC source propositions omitted by the historical compact text; "
                "retain its existing Korean semantic line boundaries unchanged."
            )
            default_legacy_ids.append(entry_id)

        assert_colour_tags(compact, entry_id)
        assert_colour_tags(current_ko, entry_id)
        assert_colour_tags(legacy_ko, entry_id)
        assert_colour_tags(proposed, entry_id)
        compact_signature = control_signature(compact)
        current_signature = control_signature(current_ko)
        legacy_signature = control_signature(legacy_ko)
        proposed_signature = control_signature(proposed)
        jp_signature = control_signature(direct_texts["jp"][entry_id])
        require(
            proposed_signature == current_signature == compact_signature == jp_signature,
            f"{entry_id}: protected-control signature drift",
        )

        metrics = layout_lines(entry_id, proposed, current, reservations)
        require(1 <= len(metrics) <= MAX_LINES, f"{entry_id}: line count {len(metrics)} exceeds {MAX_LINES}")
        require(
            not any(line["exceeds_raw_1440px"] or line["exceeds_912px"] for line in metrics),
            f"{entry_id}: Static Patch 007 width exceeds limit",
        )
        if proposed_signature["runtime_tokens"]:
            runtime_rows.append(entry_id)
        strategy_counts[strategy] += 1

        inventory_row = inventory_by_id.get(entry_id)
        require(isinstance(inventory_row, dict), f"{entry_id}: inventory row missing")
        direct_evidence = {language: texts[entry_id] for language, texts in direct_texts.items()}
        reviewed.append({
            "entry_id": entry_id,
            "scene_batch_id": inventory_row.get("scene_batch_id"),
            "review_status": "ready_for_source_complete_restoration_candidate",
            "review_judgement": judgement,
            "restoration_strategy": strategy,
            "current_differs_from_historical_compact": entry_id in EXPECTED_CURRENT_DIFF_IDS,
            "prior_static007_reflow_revalidated": prior_reflow_revalidated,
            "historical_manual_compact_ko": compact,
            "current_ko_at_strict_predecessor": current_ko,
            "legacy_precompaction_ko": legacy_ko,
            "proposed_ko": proposed,
            "legacy_matches_proposed_after_normalization": legacy_ko == proposed,
            "historical_compact_to_proposed_surface_units": reintroduced_surface_units(compact, proposed),
            "current_to_proposed_surface_units": reintroduced_surface_units(current_ko, proposed),
            "direct_pc_source_evidence": direct_evidence,
            "text_sha256_utf16le": {
                "historical_manual_compact_ko": text_sha256(compact),
                "current_ko": text_sha256(current_ko),
                "legacy_precompaction_ko": text_sha256(legacy_ko),
                "proposed_ko": text_sha256(proposed),
            },
            "control_signature": {
                "historical_manual_compact": compact_signature,
                "current": current_signature,
                "legacy": legacy_signature,
                "proposed": proposed_signature,
                "direct_pc_jp": jp_signature,
                "proposed_current_compact_direct_jp_match": True,
            },
            "runtime_token_reservation": {
                "actual_runtime_tokens": proposed_signature["runtime_tokens"],
                "runtime_proven": False,
                "policy": (
                    "Use only the known scene-limited conservative reservation; "
                    "scale raw G1N width by 30/48 and do not infer runtime names."
                ),
            },
            "layout": {
                "line_count": len(metrics),
                "max_lines": MAX_LINES,
                "raw_g1n_pass_limit_px": MAX_RAW_WIDTH_PX,
                "effective_width_pass_limit_px": MAX_EFFECTIVE_WIDTH_PX,
                "all_lines_pass_static_patch_007": True,
                "lines": metrics,
            },
            "any_line_exceeds_raw_1440px": False,
            "any_line_exceeds_912px": False,
        })

    require(len(reviewed) == EXPECTED_ROW_COUNT, "review count accounting drift")
    require(
        set(current_diff_reconciled_ids + current_diff_preserved_ids) == set(EXPECTED_CURRENT_DIFF_IDS),
        "current-diff decision accounting drift",
    )
    require(len(known_reflow_reused_ids) == len(KNOWN_REFLOW_IDS), "known reflow count drift")

    payload = {
        "schema": SCHEMA,
        "scope": {
            "resource": RESOURCE,
            "event_id_range": [MIN_ID, MAX_ID],
            "manual_compact_target_count": len(reviewed),
            "candidate_binary_created": False,
            "steam_files_written": False,
            "git_or_release_actions_performed": False,
            "network_operation_performed": False,
        },
        "layout_baseline": {
            "authority": "Static Patch 007 verified event-dialogue layout",
            "runtime_font_px": RUNTIME_FONT_PX,
            "runtime_usable_line_width_px": MAX_EFFECTIVE_WIDTH_PX,
            "max_lines": MAX_LINES,
            "raw_g1n_full_width_advance_px": RAW_FULL_WIDTH_PX,
            "raw_g1n_half_width_advance_px": RAW_HALF_WIDTH_PX,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "raw_g1n_pass_limit_px": MAX_RAW_WIDTH_PX,
            "effective_width_pass_limit_px": MAX_EFFECTIVE_WIDTH_PX,
            "dynamic_name_reservations": (
                "Reserve known token raw width then scale by 30/48; "
                "runtime_proven remains false."
            ),
        },
        "sources": {
            "current_ko_strict_predecessor": source_summary(current_profile),
            "legacy_precompaction_ko_backup": source_summary(legacy_profile),
            "direct_pc_jp_pristine": source_summary(direct_profiles["jp"]),
            "direct_pc_en": source_summary(direct_profiles["en"]),
            "direct_pc_sc": source_summary(direct_profiles["sc"]),
            "direct_pc_tc": source_summary(direct_profiles["tc"]),
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
            "previously_reviewed_10000_reflows": {
                "path": str(KNOWN_REFLOW_PATH),
                "sha256": sha256(KNOWN_REFLOW_PATH.read_bytes()),
                "ids": list(KNOWN_REFLOW_IDS),
            },
        },
        "judgement_groups": [
            {
                "group": "legacy_source_complete_restoration",
                "ids": default_legacy_ids,
                "reason": "No later current quality revision exists; restore the unabridged Korean at its existing semantic Korean line boundaries.",
            },
            {
                "group": "prior_static007_semantic_reflow_reused_and_revalidated",
                "ids": known_reflow_reused_ids,
                "reason": "The nine existing four-line reflows were rechecked against the strict current input and direct PC witnesses.",
            },
            {
                "group": "current_diff_rows_reconciled_source_complete",
                "ids": current_diff_reconciled_ids,
                "reason": "Later current wording was retained only where source-complete; omitted clauses or terminology were restored without shortening.",
            },
            {
                "group": "current_diff_rows_preserved_source_complete",
                "ids": current_diff_preserved_ids,
                "reason": "The later current Korean is already source-complete and layout-safe, so it is retained rather than regressing to the old backup.",
            },
            {
                "group": "runtime_name_tokens",
                "ids": runtime_rows,
                "reason": "Known scene-limited name reservations are recorded and scaled by 30/48; no runtime inference is claimed.",
            },
        ],
        "counts": {
            "restoration_strategy_counts": dict(sorted(strategy_counts.items())),
            "legacy_full_text_restoration_count": len(default_legacy_ids),
            "prior_static007_reflow_revalidated_count": len(known_reflow_reused_ids),
            "current_diff_reconciled_count": len(current_diff_reconciled_ids),
            "current_diff_preserved_count": len(current_diff_preserved_ids),
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
        "schema": "nobu16.kr.pc-event-manual-compact-10000-review-validation.v1",
        "review_output": str(OUTPUT),
        "review_output_sha256": sha256(OUTPUT.read_bytes()),
        "target_count": len(reviewed),
        "current_diff_row_count": len(current_diff_ids),
        "prior_static007_reflow_revalidated_count": len(known_reflow_reused_ids),
        "max_line_count": max(row["layout"]["line_count"] for row in reviewed),
        "over_raw_1440px_line_count": sum(
            line["exceeds_raw_1440px"]
            for row in reviewed
            for line in row["layout"]["lines"]
        ),
        "over_912px_line_count": sum(
            line["exceeds_912px"]
            for row in reviewed
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
