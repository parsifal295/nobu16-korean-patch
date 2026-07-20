#!/usr/bin/env python3
"""Read-only semantic recovery review for 8xxx manual event compactions.

This workstream does not create an event binary.  It records a source-backed
four-line restoration plan against the strict batch05 Static Patch 007
candidate.  Direct PC JP/EN/SC/TC resources are evidence only, and the Steam
installation, Git state, release state, and network are deliberately outside
the script's write scope.
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
OUTPUT = PUBLIC / "manual_compact_8000_review.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.manual-compact-8000-review.v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
MIN_ID = 8000
MAX_ID = 8999
EXPECTED_ROW_COUNT = 177

# Static Patch 007, not the obsolete 48px / 912px pre-patch line gate.
RUNTIME_FONT_PX = 30
MAX_EFFECTIVE_WIDTH_PX = 912
MAX_RAW_WIDTH_PX = 1440
MAX_LINES = 4
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24

PRIOR_CURRENT_PATH = (
    REPO
    / "tmp"
    / "pc_event_manual_compact_static007_batch05_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
PRIOR_CURRENT_EXPECTED = {
    "packed_sha256": "8B7B9BF8F104C56F3EED0B3B5E1871E416466CD443020D6306135CCA56E7FE42",
    "raw_sha256": "D49A221732551E6DA673657A577828640E438D02B23AF3B529130A2B9689CC7F",
}
CURRENT_PATH = (
    REPO
    / "tmp"
    / "pc_event_manual_compact_static007_batch06_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
CURRENT_EXPECTED = {
    "packed_sha256": "600B6F1C8BE432A5987E1A05F19DCA30AF00DB9BFBFEAC702CCB60605B19B313",
    "raw_sha256": "2EEF242A9F5183061F866C854DF51139CF0FEC3E69C004F04C665B69C91AAF5B",
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
KNOWN_REFLOW_PATH = (
    REPO
    / "workstreams"
    / "manual_compact_reflow_8000_9000_review_v1"
    / "public"
    / "manual_compact_static007_review_8449_8513_8696_8818.v1.json"
)

ESC = "\x1b"
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
VISIBLE_UNIT_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]|[가-힣A-Za-z0-9]+|[^\s]")


# These are the only 8xxx manual-compact rows whose text was changed after the
# historical compact overlay.  Each is individually source judged below; it is
# not safe to replace them wholesale with the old backup.
CURRENT_DIFF_IDS = (
    8026, 8128, 8142, 8236, 8237, 8239, 8240, 8241, 8243, 8249,
    8252, 8256, 8259, 8268, 8273, 8278, 8281, 8282, 8283, 8289,
    8292, 8296, 8300, 8302, 8442, 8449, 8471, 8472, 8473, 8476,
    8479, 8490, 8491, 8512, 8513, 8520, 8739, 8838,
)

# Four rows have a previously reviewed Static Patch 007 plan.  The proposal is
# repeated here and asserted against that independently authored record.
KNOWN_REFLOW_IDS = (8449, 8513, 8696, 8818)

# A text value is supplied only where the source comparison requires a change
# beyond retaining the already source-complete current revision.  No entry is
# shortened: all restored content is explicit in JP and corroborated by EN/SC/TC.
OVERRIDES: dict[int, dict[str, str]] = {
    8026: {
        "strategy": "reconcile_current_revision_with_source_complete_restoration",
        "judgement": "Restore the loss of the successor, the Oda clan's resulting confusion, the actor taking the first step, and the fact that he avenged his lord; the later correction from ‘갚을’ to completed ‘갚은’ is retained.",
        "text": (
            f"{ESC}CA노부나가{ESC}CZ와 적자 {ESC}CA노부타다{ESC}CZ가 세상을 떠나\n"
            f"후계자를 잃은 {ESC}CB오다 가문{ESC}CZ이 혼란에 빠진 가운데,\n"
            "한 걸음을 내디딘 것은\n"
            f"주군의 원수를 갚은 {ESC}CA[b754]{ESC}CZ였다."
        ),
    },
    8059: {
        "strategy": "restore_legacy_text_with_semantic_reflow_runtime_reservation",
        "judgement": "Restore the addressee's surrender, the speaker's pleasure at being remembered, and the warning not to lose the right path; split only at Korean sentence boundaries for the conservative token reservation.",
        "text": (
            "이후로는 나를 신경 쓰지 말고\n"
            f"{ESC}CA[bs754]{ESC}CZ 님에게 항복하시오.\n"
            "나를 생각해 주는 마음은 기쁘지만,\n"
            "그 마음 때문에 길을 그르치는 일이 없도록…"
        ),
    },
    8128: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current revision already restores Terumune's sudden retirement to prevent an internal power struggle and Masamune's succession as the seventeenth Date head; retain its natural Korean rather than regress to the older backup.",
    },
    8142: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current revision keeps every source fact: Arima's abandonment of the Ryuzoji, collusion with Shimazu, the punitive purpose, and the army's advance to Shimabara Peninsula.",
    },
    8236: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current revision restores the three senior retainers, their Hideyoshi-favoring diplomatic policy, their killing, and the resulting effective declaration of war.",
    },
    8237: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The later text fully retains the speaker's correction from honorific address, the late lord's bloodline, Nobukatsu's lack of ability, and the grievance that he had nevertheless been supported.",
    },
    8239: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current text preserves Nobukatsu's disadvantage alone, his late father's ally, that ally's alarm at Hideyoshi's rise, and the request for aid.",
    },
    8240: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current wording keeps the former lord's orphan, the rebuke to the ‘monkey,’ and the clan's pledged assistance to Nobukatsu without the historical truncation.",
    },
    8241: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current four-line text retains the prediction that Hideyoshi would draw in other powers and the proposal to form a united front with powers hostile to him.",
    },
    8243: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The expanded current text keeps the intervention, nationwide scope, and decisive ‘battle for supremacy’ development; it is source-complete and layout-safe.",
    },
    8249: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current scene caption preserves both sides, their confrontation at Komakiyama, and the combined Nobukatsu–ally force; it should not be reverted to the fragmentary label form.",
    },
    8252: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current text keeps the family relation, limited battle experience, Hideyoshi's concern, and participation in this campaign.",
    },
    8256: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current dialogue retains the conditional absence of the clan, Nobukatsu's lack of threat, the famous old fox, and the speaker's doubt about success.",
    },
    8259: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current revision retains Tsuneoki's milk-brother and close-retainer relation, Kiyosu Council participation, senior-retainer status, and later position under Hideyoshi.",
    },
    8268: {
        "strategy": "reconcile_current_revision_with_source_complete_terminology_fix",
        "judgement": "Keep the restored strategic content, but replace the untranslated ‘나카이리’ with the source-supported Korean ‘우회 기습’: the home-country surprise attack, reversal near Nagakute, Tokugawa ambush, and confusion all remain explicit.",
        "text": (
            f"{ESC}CB[bs1871]{ESC}CZ의 본국을 기습하려\n"
            f"우회 기습에 나선 {ESC}CA[bs754]히데쓰구{ESC}CZ의 군은\n"
            f"{ESC}CC나가쿠테{ESC}CZ 부근에서 되레 {ESC}CB도쿠가와{ESC}CZ군의\n"
            "급습을 받아 혼란에 빠졌다."
        ),
    },
    8273: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current text restores the defeat at Nagakute, all three named dead, and their valiant deaths, including the expanded personal names.",
    },
    8278: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current wording keeps the repelled flanking force, the army's raised morale, and the leader's cold observation of the battle situation.",
    },
    8281: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The corrected current location ‘고마키야마’ and the continued confrontation after the Nagakute defeat are both source-complete.",
    },
    8282: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current text retains the victory over Hidetsugu and others at Nagakute, the resulting morale, and the renewed stalemate.",
    },
    8283: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current four-line version retains clashes away from the Komakiyama front, both armies, and the absence of a decisive result.",
    },
    8289: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current text keeps Nobukatsu as commander, the loss of reason to continue fighting, the whole army, and withdrawal to Hamamatsu Castle.",
    },
    8292: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current text restores the unexpected request in Nobukatsu's letter and his recommendation that the addressee make peace with Hideyoshi.",
    },
    8296: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current dialogue retains the alliance, the need not to disgrace Nobukatsu, and the consequence of having to fight alone if peace is refused.",
    },
    8300: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current text restores Ogimaru's later name, his presentation as the token of peace, and the Battle of Komaki-Nagakute ending as a contest for supremacy.",
    },
    8302: {
        "strategy": "reconcile_current_revision_with_source_quality_semantic_reflow",
        "judgement": "Keep the current meaning but repair the awkward final phrasing: it must state that, after suppressing Nobukatsu and the ally opposition, Hideyoshi rose still higher toward the status of unifier.",
        "text": (
            f"{ESC}CA노부카쓰{ESC}CZ와 {ESC}CA[bm1871]{ESC}CZ라는\n"
            f"반대파를 억누른 {ESC}CA[b754]{ESC}CZ는\n"
            "그 뒤 더욱 높은 천하인의 자리로\n"
            "오르게 된다."
        ),
    },
    8442: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current narration fully restores the Oda collapse, manipulation of all three powers, and the Sanada clan's rise as daimyo.",
    },
    8449: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "Retain the independently reviewed current version: it restores all three trusted generals by full name and the fourfold troop count, while avoiding the older Korean's ungrammatical list construction.",
    },
    8471: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current revision keeps Kazumasa as the ruler's trusted retainer, his service before independence from Imagawa, and his achievements in many battles.",
    },
    8472: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current revision preserves the post-Honnoji change of circumstances and the responsibility for the diplomacy judged most important to the clan.",
    },
    8473: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current dialogue retains the rebuke for favoring the other clan and the request to convey and negotiate the home clan's position properly.",
    },
    8476: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current text retains the former Nobukatsu retainer, the belief that he favored the other clan, and Nobukatsu's killing of him.",
    },
    8479: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The expanded current narration preserves Kazumasa's flight, the shocking report, clan confusion, and the reason: an elder among elders had turned traitor.",
    },
    8490: {
        "strategy": "reconcile_current_revision_with_source_complete_restoration",
        "judgement": "The current version is natural but lost the source adverb ‘always’; restore it while retaining the promise to seek favorable treatment for the former clan from within the new clan.",
        "text": (
            "(하지만 안심하시오.\n"
            f"나는 {ESC}CB[bs754] 가문{ESC}CZ 안에서 늘\n"
            f"{ESC}CB[bs1871] 가문{ESC}CZ이 유리하도록\n"
            "힘쓰겠소……)"
        ),
    },
    8491: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current narration retains the lack of conspicuous achievements after transfer and the effort devoted to harmony between the two sides.",
    },
    8512: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current version fully preserves reluctant compliance, the fact that it was only a truce, and ongoing tension between both houses.",
    },
    8513: {
        "strategy": "preserve_current_quality_with_previously_reviewed_semantic_reflow",
        "judgement": "Retain the source-complete current quality wording—goal of becoming unifier, inability to leave the great clan alone, and regardless-of-appearance recruitment—while reflowing its two sentences at a natural boundary.",
        "text": (
            f"천하인을 목표로 한 {ESC}CA히데요시{ESC}CZ는\n"
            f"거대한 존재감을 유지하는 {ESC}CB[bs1871]가{ESC}CZ를\n"
            "그대로 둘 수 없었다.\n"
            f"수단을 가리지 않고 {ESC}CB[bm1871]{ESC}CZ 포섭을 꾀했다."
        ),
    },
    8520: {
        "strategy": "preserve_current_post_compaction_quality_revision",
        "judgement": "The current narration keeps both possible motives—weariness at repeated relatives or yielding to sincerity—and the final decision to submit to Hideyoshi.",
    },
    8696: {
        "strategy": "restore_legacy_text_with_previously_reviewed_semantic_reflow",
        "judgement": "Reuse the independently reviewed source-complete reflow: it restores immediate action, the bridge crossing, the charge into the enemy position, and the coalition's ensuing confusion.",
        "text": (
            f"말이 떨어지기 무섭게, {ESC}CA오니니와 사게쓰사이{ESC}CZ는\n"
            f"{ESC}CC히토토리바시{ESC}CZ를 건너 적진으로 돌격했다.\n"
            "연합군은 한동안 혼란에 빠졌다."
        ),
    },
    8739: {
        "strategy": "reconcile_current_revision_with_source_complete_restoration",
        "judgement": "Keep the later terminology but restore unambiguous ownership of the diminished power: the fated enemy fought many battles with the speaker's lord, who steadily reduced that enemy's strength. The Korean topic particle is also corrected to match the referenced vowel-final name.",
        "text": (
            f"{ESC}CA[bm1448]{ESC}CZ와 수차례 싸워 온\n"
            f"숙명의 대적 {ESC}CA다케다 [bm1251]{ESC}CZ—\n"
            f"{ESC}CA[bm1448]{ESC}CZ는 그 세력을\n"
            "꾸준히 꺾어 갔다."
        ),
    },
    8756: {
        "strategy": "restore_legacy_text_with_semantic_reflow_runtime_reservation",
        "judgement": "Restore both renowned rivals, their concealed ulterior motives, and the start of their strange lord-retainer path; split the two dynamic names across semantic lines for the conservative reservation.",
        "text": (
            f"이리하여 이름 높은 호적수였던 {ESC}CA[bm1251]{ESC}CZ와\n"
            f"{ESC}CA[bm1448]{ESC}CZ, 두 영웅은 서로 속내를 감춘 채\n"
            "기묘한 주종으로서 걸음을\n"
            "내디뎠다…"
        ),
    },
    8818: {
        "strategy": "restore_legacy_text_with_previously_reviewed_semantic_reflow",
        "judgement": "Reuse the independently reviewed four-line restoration of the edict's target daimyos, arbitrary territorial disputes, the ‘소부지’ name, and the violator subject to punishment.",
        "text": (
            f"관백 {ESC}CA히데요시{ESC}CZ는 여러 나라의 다이묘에게,\n"
            "제멋대로의 영토 다툼을 금하고,\n"
            "그것을 '소부지'라 칭하였다.\n"
            "이를 거스르는 자는 관백의 토벌을 받는다."
        ),
    },
    8838: {
        "strategy": "reconcile_current_revision_with_source_complete_restoration",
        "judgement": "Restore the source's display of composure, both prior failed attackers, the castle itself, and the defiant refusal to hand it to an upstart ‘monkey’; the compact current line lost the latter force and subject.",
        "text": (
            "천하인의 여유를 과시하려는 것이겠지.\n"
            f"하지만 {ESC}CA[bm1251]{ESC}CZ도 {ESC}CA[bm1448]{ESC}CZ도\n"
            "함락하지 못한 이 성을,\n"
            "벼락출세한 원숭이 따위에게 내줄까 보냐!"
        ),
    },
}


class ReviewError(RuntimeError):
    """Raised if pinned evidence or a review invariant drifts."""


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
    codepoint = ord(character)
    return (
        0x1100 <= codepoint <= 0x11FF or 0x3130 <= codepoint <= 0x318F
        or 0x3040 <= codepoint <= 0x30FF or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF or 0xAC00 <= codepoint <= 0xD7A3
        or 0xA960 <= codepoint <= 0xA97F or 0xD7B0 <= codepoint <= 0xD7FF
    )


def assert_colour_tags(value: str, entry_id: int) -> None:
    in_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == ESC:
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"{entry_id}: malformed ESC {token!r}")
            if token == f"{ESC}CZ":
                require(in_span, f"{entry_id}: unmatched color close")
                in_span = False
            else:
                require(not in_span, f"{entry_id}: nested color span")
                in_span = True
            cursor += 3
        else:
            require(not (in_span and value[cursor] in "\r\n"), f"{entry_id}: break inside color tag")
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
    for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(
        a=visible_units(before), b=visible_units(after)
    ).get_opcodes():
        if tag in {"insert", "replace"}:
            for unit in visible_units(after)[j1:j2]:
                if unit not in result:
                    result.append(unit)
    return result[:64]


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
                    reservation["reserved_full_name_width_px"] * RUNTIME_FONT_PX / RAW_FULL_WIDTH_PX
                ),
                "runtime_proven": False,
                "reservation_reason": "Scene-limited conservative reservation scaled by 30/48; not runtime-proven.",
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
            "exceeds_912px": effective_width > MAX_EFFECTIVE_WIDTH_PX,
        })
    return rows


def source_summary(value: dict[str, Any]) -> dict[str, Any]:
    return {key: value[key] for key in ("path", "packed_sha256", "raw_sha256", "packed_size", "raw_size", "string_count")}


def main() -> int:
    current_profile, current = profile(CURRENT_PATH)
    require(current_profile["packed_sha256"] == CURRENT_EXPECTED["packed_sha256"], "batch06 packed baseline drift")
    require(current_profile["raw_sha256"] == CURRENT_EXPECTED["raw_sha256"], "batch06 raw baseline drift")
    prior_current_profile, prior_current = profile(PRIOR_CURRENT_PATH)
    require(
        prior_current_profile["packed_sha256"] == PRIOR_CURRENT_EXPECTED["packed_sha256"],
        "batch05 prior packed baseline drift",
    )
    require(
        prior_current_profile["raw_sha256"] == PRIOR_CURRENT_EXPECTED["raw_sha256"],
        "batch05 prior raw baseline drift",
    )
    jp_profile, jp = profile(DIRECT_JP_PATH)
    en_profile, en = profile(DIRECT_EN_PATH)
    sc_profile, sc = profile(DIRECT_SC_PATH)
    tc_profile, tc = profile(DIRECT_TC_PATH)
    legacy_profile, legacy = profile(LEGACY_KO_PATH)
    for label, values in (("jp", jp), ("en", en), ("sc", sc), ("tc", tc), ("legacy", legacy)):
        require(len(values) == len(current), f"{label} message count differs from current")

    historical = read_json(HISTORICAL_MANIFEST)
    reservations_doc = read_json(RESERVATION_MANIFEST)
    inventory = read_json(INVENTORY_MANIFEST)
    known_reflow = read_json(KNOWN_REFLOW_PATH)
    reservations = reservations_doc.get("reservations")
    historical_entries = historical.get("entries")
    inventory_rows = inventory.get("rows")
    known_entries = known_reflow.get("entries")
    require(isinstance(reservations, dict), "runtime reservation map missing")
    require(isinstance(historical_entries, list), "historical entries missing")
    require(isinstance(inventory_rows, list), "inventory rows missing")
    require(isinstance(known_entries, list), "known-reflow entries missing")
    inventory_by_id = {row["entry_id"]: row for row in inventory_rows if isinstance(row, dict)}
    known_by_id = {row["id"]: row for row in known_entries if isinstance(row, dict)}
    require(set(known_by_id) == set(KNOWN_REFLOW_IDS), "known reflow ID scope drift")

    selected = [
        row for row in historical_entries
        if isinstance(row, dict) and MIN_ID <= row.get("id", -1) <= MAX_ID
        and (row.get("operation") == "manual_compact_korean_layout"
             or "manual_compact_korean_layout" in row.get("newline_operations", []))
    ]
    selected.sort(key=lambda row: row["id"])
    require(len(selected) == EXPECTED_ROW_COUNT, f"manual compact count drift: {len(selected)}")
    selected_ids = tuple(row["id"] for row in selected)
    require(
        all(current[entry_id] == prior_current[entry_id] for entry_id in selected_ids),
        "batch06 changed a reviewed 8xxx string unexpectedly",
    )
    require(set(OVERRIDES).issubset(set(selected_ids)), "override outside 8xxx manual compact scope")
    current_diff = tuple(row["id"] for row in selected if current[row["id"]] != row.get("ko"))
    require(current_diff == CURRENT_DIFF_IDS, f"current-diff scope drift: {current_diff}")

    reviewed: list[dict[str, Any]] = []
    strategy_counts: Counter[str] = Counter()
    legacy_restore_ids: list[int] = []
    current_preserved_ids: list[int] = []
    current_reconciled_ids: list[int] = []
    semantic_reflow_ids: list[int] = []
    runtime_rows: list[int] = []

    for historical_row in selected:
        entry_id = historical_row["id"]
        compact = historical_row.get("ko")
        require(isinstance(compact, str), f"{entry_id}: compact Korean missing")
        current_ko = current[entry_id]
        legacy_ko = normalize_legacy_layout(legacy[entry_id])
        override = OVERRIDES.get(entry_id)
        if override is None:
            proposed = legacy_ko
            strategy = "restore_legacy_precompaction_full_korean_text"
            judgement = (
                "Direct PC JP/EN/SC/TC retains semantic material cut by the historical compact row; "
                "restore the unabridged legacy Korean at its existing Korean clause boundaries without shortening."
            )
            legacy_restore_ids.append(entry_id)
        else:
            proposed = override.get("text", current_ko)
            strategy = override["strategy"]
            judgement = override["judgement"]

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
            f"{entry_id}: protected-control signature drift",
        )
        if entry_id in KNOWN_REFLOW_IDS:
            known = known_by_id[entry_id]
            require(proposed == known.get("proposed_ko"), f"{entry_id}: known reflow proposal drift")

        metrics = layout_lines(entry_id, proposed, current, reservations)
        require(1 <= len(metrics) <= MAX_LINES, f"{entry_id}: line count {len(metrics)} exceeds {MAX_LINES}")
        require(not any(line["exceeds_912px"] for line in metrics), f"{entry_id}: line exceeds 912px")
        if proposed_signature["runtime_tokens"]:
            runtime_rows.append(entry_id)
        if strategy.startswith("preserve_current"):
            current_preserved_ids.append(entry_id)
        if strategy.startswith("reconcile_current"):
            current_reconciled_ids.append(entry_id)
        if "semantic_reflow" in strategy:
            semantic_reflow_ids.append(entry_id)
        strategy_counts[strategy] += 1

        inventory_row = inventory_by_id.get(entry_id)
        require(isinstance(inventory_row, dict), f"{entry_id}: inventory row missing")
        reviewed.append({
            "entry_id": entry_id,
            "scene_batch_id": inventory_row.get("scene_batch_id"),
            "review_status": "ready_for_semantic_restoration_candidate",
            "review_judgement": judgement,
            "restoration_strategy": strategy,
            "current_quality_preserved": strategy.startswith("preserve_current"),
            "current_quality_reconciled": strategy.startswith("reconcile_current"),
            "previous_static007_reflow_revalidated": entry_id in KNOWN_REFLOW_IDS,
            "historical_manual_compact_ko": compact,
            "current_ko_at_batch06_strict_baseline": current_ko,
            "legacy_precompaction_ko": legacy_ko,
            "proposed_ko": proposed,
            "legacy_matches_proposed_after_normalization": legacy_ko == proposed,
            "historical_compact_to_proposed_surface_units": reintroduced_surface_units(compact, proposed),
            "current_to_proposed_surface_units": reintroduced_surface_units(current_ko, proposed),
            "direct_pc_sources": {"jp": jp[entry_id], "en": en[entry_id], "sc": sc[entry_id], "tc": tc[entry_id]},
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
                "policy": "Known scene-limited conservative reservation only; raw G1N reservation is scaled by 30/48. No runtime inference is made.",
            },
            "layout": {
                "line_count": len(metrics),
                "max_lines": MAX_LINES,
                "all_lines_pass_static_patch_007": True,
                "lines": metrics,
            },
            "any_line_exceeds_912px": False,
        })

    require(len(reviewed) == EXPECTED_ROW_COUNT, "review count accounting drift")
    require(len(legacy_restore_ids) == EXPECTED_ROW_COUNT - len(OVERRIDES), "legacy restore count accounting drift")
    require(all(entry_id in CURRENT_DIFF_IDS for entry_id in current_preserved_ids + current_reconciled_ids), "current group outside reviewed current-diff scope")

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
            "dynamic_name_reservations": "Reserve known token raw width then scale by 30/48; runtime_proven remains false.",
        },
        "sources": {
            "current_ko_batch06_strict_baseline": source_summary(current_profile),
            "prior_current_ko_batch05": source_summary(prior_current_profile),
            "direct_pc_jp_pristine": source_summary(jp_profile),
            "direct_pc_en": source_summary(en_profile),
            "direct_pc_sc": source_summary(sc_profile),
            "direct_pc_tc": source_summary(tc_profile),
            "legacy_precompaction_ko_backup": source_summary(legacy_profile),
            "historical_manual_compact_manifest": {"path": str(HISTORICAL_MANIFEST), "sha256": sha256(HISTORICAL_MANIFEST.read_bytes())},
            "runtime_reservation_manifest": {"path": str(RESERVATION_MANIFEST), "sha256": sha256(RESERVATION_MANIFEST.read_bytes())},
            "inventory_manifest": {"path": str(INVENTORY_MANIFEST), "sha256": sha256(INVENTORY_MANIFEST.read_bytes())},
            "previously_reviewed_8449_8513_8696_8818_reflows": {"path": str(KNOWN_REFLOW_PATH), "sha256": sha256(KNOWN_REFLOW_PATH.read_bytes()), "ids": list(KNOWN_REFLOW_IDS)},
        },
        "baseline_transition": {
            "batch06_replaced_batch05_for_global_chain": True,
            "selected_8xxx_rows_unchanged_count": len(selected_ids),
            "selected_8xxx_rows_changed_count": 0,
            "comparison": "Every selected 8xxx current Korean string is identical in the pinned batch05 and batch06 candidates.",
        },
        "judgement_groups": [
            {"group": "legacy_source_complete_restoration", "ids": legacy_restore_ids, "reason": "No later current quality edit exists; direct PC JP/EN/SC/TC supports restoration of the unabridged Korean text."},
            {"group": "later_current_revision_preserved", "ids": current_preserved_ids, "reason": "Individually reviewed later quality revisions are already source-complete and should not regress to the old backup."},
            {"group": "later_current_revision_reconciled", "ids": current_reconciled_ids, "reason": "A later revision contained valid quality work but a source detail or Korean wording required a source-complete correction."},
            {"group": "semantic_reflow_required", "ids": semantic_reflow_ids, "reason": "All semantic material is retained, with manual breaks chosen at Korean sentence or clause boundaries under the four-line Static Patch 007 rule."},
            {"group": "previous_static007_reflow_revalidated", "ids": list(KNOWN_REFLOW_IDS), "reason": "8449, 8513, 8696, and 8818 reuse and revalidate the prior four-row review against the strict batch05 baseline."},
            {"group": "runtime_name_tokens", "ids": runtime_rows, "reason": "Token width is conservatively reserved and scaled by 30/48; runtime_proven remains false for every row."},
        ],
        "counts": {
            "restoration_strategy_counts": dict(sorted(strategy_counts.items())),
            "legacy_full_text_restoration_count": len(legacy_restore_ids),
            "current_quality_preserved_count": len(current_preserved_ids),
            "current_quality_reconciled_count": len(current_reconciled_ids),
            "semantic_reflow_count": len(semantic_reflow_ids),
            "previous_static007_reflow_revalidated_count": len(KNOWN_REFLOW_IDS),
            "runtime_token_row_count": len(runtime_rows),
            "all_rows_four_or_fewer_lines": True,
            "all_rows_within_912px": True,
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
        "schema": "nobu16.kr.manual-compact-8000-review-validation.v1",
        "review_output": str(OUTPUT),
        "review_output_sha256": sha256(OUTPUT.read_bytes()),
        "target_count": len(reviewed),
        "current_diff_row_count": len(CURRENT_DIFF_IDS),
        "previous_static007_reflow_revalidated_count": len(KNOWN_REFLOW_IDS),
        "max_line_count": max(row["layout"]["line_count"] for row in reviewed),
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
