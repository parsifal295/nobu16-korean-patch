#!/usr/bin/env python3
"""Re-review 5xxx manual Korean event compactions without creating a binary.

This workstream is deliberately an evidence-and-restoration plan only.  It
reads the current static007 3-line 5777 event successor, pristine direct-PC JP text, installed
direct-PC EN/SC/TC comparison text, and the pre-compaction Korean backup.  Its
only output is the JSON review artifact under this workstream's ``public``
directory; it never writes a game resource, Steam file, candidate binary, or
Git state.
"""

from __future__ import annotations

import difflib
import hashlib
import json
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


SCHEMA = "nobu16.kr.manual-compact-5000-review.v1"
OUTPUT_PATH = WORKSTREAM / "public" / "manual_compact_5000_review.v1.json"
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

# This is the current semantic baseline, not a historical Steam installation.
CURRENT_KO_PATH = (
    REPO
    / "tmp"
    / "pc_event_5777_kanegasaki_static007_3line_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
DIRECT_JP_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals"
    r"\MSG_PK\JP\msgev.bin"
)
DIRECT_EN_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msgev.bin")
DIRECT_SC_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msgev.bin")
DIRECT_TC_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msgev.bin")

# This backup predates the three-line manual-compaction pass and contains the
# unabridged Korean sentence as it existed before that pass.  It is never used
# blindly: direct PC JP/EN/SC/TC evidence is embedded for every reviewed row,
# while post-compaction quality edits from CURRENT_KO_PATH win over this backup.
LEGACY_PRECOMPACTION_KO_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-v0.10.0-original-font-rollback-v1"
    r"\originals\MSG_PK\JP\msgev.bin"
)

EXPECTED_CURRENT_PROFILE = {
    "packed_sha256": "1F7E42E10C0034CD70565993BE3DB311DF3A5356525B6BA14B31987752967745",
    "raw_sha256": "92B11470E00C7A5004739847D2548286D296B76D4C6016FD1B5E0DDD542EB611",
}
EXPECTED_DIRECT_JP_PROFILE = {
    "packed_sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
}

MIN_ID = 5000
MAX_ID = 5999
EXPECTED_TARGET_COUNT = 164
EXPECTED_CURRENT_QUALITY_PRESERVED_COUNT = 31
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
MAX_EFFECTIVE_LINE_PX = 912
MAX_RAW_LINE_PX = 1440
MAX_LINES = 4

ESC_RE = re.compile(r"\x1b(?:CA|CB|CC|CZ)")
RUNTIME_RE = re.compile(r"\[([a-z]+)(\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*(?:\d+)?(?:\.\d+)?[A-Za-z]")

# These labels do not block restoration.  They call out the groups most worth
# doing a second stylistic pass on after the no-abbreviation restoration lands.
HISTORICAL_TERMINOLOGY_IDS = {
    5137, 5218, 5281, 5284, 5294, 5356, 5453, 5465, 5487, 5509,
    5651, 5811, 5818, 5855,
}
SPEAKER_VOICE_OR_CONTEXT_IDS = {
    5005, 5058, 5085, 5088, 5089, 5099, 5102, 5273, 5315, 5673,
    5748, 5790, 5792, 5795, 5940, 5944, 5946, 5952,
}

# The pre-compaction backup has one 5xxx row whose second Korean line would
# exceed the current static-patch-007 effective-width limit.  This changes
# only the clause boundary; it does not delete, abbreviate, or retranslate any
# source content.
SEMANTIC_REFLOW_OVERRIDES = {
    5164: (
        "\x1bCB모가미가\x1bCZ도 그런 다이묘가의 하나로,\n"
        "덴분의 난에서는 승리한 \x1bCA하루무네\x1bCZ 편에 섰으나,\n"
        "\x1bCB다테가\x1bCZ와의 관계는 단순한 것이 아니었다."
    ),
}


class ReviewError(RuntimeError):
    """Raised when a frozen read-only review input is not what it claims to be."""


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
        f"message table round-trip differs: {path}",
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


def normalize_legacy_layout(value: str) -> str:
    """Remove only inherited source indentation, never Korean words or clauses."""
    return "\n".join(
        line.lstrip(" \u3000") for line in normalize_linebreaks(value).split("\n")
    )


def is_full_width_visible(character: str) -> bool:
    """Static-patch-007 reporting class: Korean/CJK scripts are full width.

    Punctuation, spaces, digits, and Latin letters intentionally stay
    half-width even if Unicode's East-Asian-width property calls a glyph wide.
    """
    return (
        "가" <= character <= "힣"
        or "ㄱ" <= character <= "ㆎ"
        or "一" <= character <= "鿿"
        or "㐀" <= character <= "䶿"
        or "ぁ" <= character <= "ヿ"
    )


def control_signature(value: str) -> dict[str, Any]:
    return {
        "esc": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "nul_count": value.count("\x00"),
    }


def assert_colour_tags(value: str, entry_id: int) -> None:
    in_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"{entry_id}: malformed ESC {token!r}")
            if token == "\x1bCZ":
                require(in_span, f"{entry_id}: unpaired ESC close")
                in_span = False
            else:
                require(not in_span, f"{entry_id}: nested ESC colour span")
                in_span = True
            cursor += 3
            continue
        require(
            not (in_span and value[cursor] in "\r\n"),
            f"{entry_id}: line break inserted inside colour tag",
        )
        cursor += 1
    require(not in_span, f"{entry_id}: unterminated ESC colour span")


def plain_units(value: str) -> list[str]:
    visible = ESC_RE.sub("", value)
    return re.findall(r"\[[a-z]+\d+\]|[가-힣A-Za-z0-9]+|[^\s]", visible)


def reintroduced_surface_units(compact: str, target: str) -> list[str]:
    """Return target-side surface chunks absent from the compact historical row.

    This is deliberately evidence, not an assertion that every Korean surface
    change maps one-to-one to a Japanese morpheme.  The four direct-PC source
    strings alongside it are the semantic authority.
    """
    before = plain_units(compact)
    after = plain_units(target)
    result: list[str] = []
    for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(a=before, b=after).get_opcodes():
        if tag in {"insert", "replace"}:
            for unit in after[j1:j2]:
                if unit not in result:
                    result.append(unit)
    return result[:48]


def source_delta_units(current: str, target: str) -> list[str]:
    if current == target:
        return []
    return reintroduced_surface_units(current, target)


def layout_lines(
    entry_id: int,
    target: str,
    current_names: tuple[str, ...],
    reservations: dict[str, Any],
) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    for number, encoded_line in enumerate(normalize_linebreaks(target).split("\n"), 1):
        visible_template = ESC_RE.sub("", encoded_line)
        dynamic: list[dict[str, Any]] = []

        def render_token(match: re.Match[str]) -> str:
            token = match.group(0)
            name_id = int(match.group(2))
            require(0 <= name_id < len(current_names), f"{entry_id}: runtime name outside table: {token}")
            reservation = reservations.get(token)
            require(reservation is not None, f"{entry_id}: no reservation for {token}")
            display = ESC_RE.sub("", normalize_linebreaks(current_names[name_id])).replace("\n", " ")
            full = sum(1 for character in display if is_full_width_visible(character))
            half = len(display) - full
            dynamic.append(
                {
                    "token": token,
                    "source_name_id": name_id,
                    "display_string": display,
                    "reserved_raw_g1n_width_px": reservation["reserved_full_name_width_px"],
                    "reserved_effective_width_px": (
                        reservation["reserved_full_name_width_px"] * DRAW_FONT_PX
                        + RAW_FULL_WIDTH_PX
                        - 1
                    )
                    // RAW_FULL_WIDTH_PX,
                    "display_full_width_character_count": full,
                    "display_half_width_character_count": half,
                }
            )
            return display

        display = RUNTIME_RE.sub(render_token, visible_template)
        literal_without_runtime = RUNTIME_RE.sub("", visible_template)
        literal_full = sum(1 for character in literal_without_runtime if is_full_width_visible(character))
        literal_half = len(literal_without_runtime) - literal_full
        reserved_raw = sum(item["reserved_raw_g1n_width_px"] for item in dynamic)
        raw = literal_full * RAW_FULL_WIDTH_PX + literal_half * RAW_HALF_WIDTH_PX + reserved_raw
        effective = (raw * DRAW_FONT_PX + RAW_FULL_WIDTH_PX - 1) // RAW_FULL_WIDTH_PX
        display_full = sum(1 for character in display if is_full_width_visible(character))
        display_half = len(display) - display_full
        lines.append(
            {
                "line_number": number,
                "display_string": display,
                "raw_g1n_width_px": raw,
                "effective_width_px": effective,
                "full_width_character_count": display_full,
                "half_width_character_count": display_half,
                "runtime_reservations": dynamic,
                "exceeds_912px": effective > MAX_EFFECTIVE_LINE_PX,
            }
        )
    return lines


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def main() -> int:
    current_profile, current = profile(CURRENT_KO_PATH)
    require(
        current_profile["packed_sha256"] == EXPECTED_CURRENT_PROFILE["packed_sha256"],
        "current static007 3-line successor packed profile drift",
    )
    require(
        current_profile["raw_sha256"] == EXPECTED_CURRENT_PROFILE["raw_sha256"],
        "current static007 3-line successor raw profile drift",
    )
    jp_profile, jp = profile(DIRECT_JP_PATH)
    require(
        jp_profile["packed_sha256"] == EXPECTED_DIRECT_JP_PROFILE["packed_sha256"],
        "pristine direct-PC JP packed profile drift",
    )
    require(
        jp_profile["raw_sha256"] == EXPECTED_DIRECT_JP_PROFILE["raw_sha256"],
        "pristine direct-PC JP raw profile drift",
    )
    en_profile, en = profile(DIRECT_EN_PATH)
    sc_profile, sc = profile(DIRECT_SC_PATH)
    tc_profile, tc = profile(DIRECT_TC_PATH)
    legacy_profile, legacy = profile(LEGACY_PRECOMPACTION_KO_PATH)
    for label, texts in (("jp", jp), ("en", en), ("sc", sc), ("tc", tc), ("legacy", legacy)):
        require(len(texts) == len(current), f"{label}/current string-count drift")

    historical = read_json(HISTORICAL_MANIFEST)
    reservation_manifest = read_json(RESERVATION_MANIFEST)
    reservations = reservation_manifest.get("reservations")
    require(isinstance(reservations, dict), "runtime reservation map missing")
    all_entries = historical.get("entries")
    require(isinstance(all_entries, list), "historical entry list missing")
    selected = [
        entry
        for entry in all_entries
        if isinstance(entry, dict)
        and MIN_ID <= entry.get("id", -1) <= MAX_ID
        and (
            entry.get("operation") == "manual_compact_korean_layout"
            or "manual_compact_korean_layout" in entry.get("newline_operations", [])
        )
    ]
    selected.sort(key=lambda entry: entry["id"])
    require(len(selected) == EXPECTED_TARGET_COUNT, f"manual 5xxx target count: {len(selected)}")

    rows: list[dict[str, Any]] = []
    preserved_count = 0
    restoration_count = 0
    for historical_row in selected:
        entry_id = historical_row["id"]
        compact = historical_row["ko"]
        require(isinstance(compact, str), f"{entry_id}: historical compact Korean is absent")
        current_ko = current[entry_id]
        current_quality_changed = current_ko != compact
        if current_quality_changed:
            # A later source-driven quality wave already changed this row.  Do
            # not overwrite it with a historical backup simply because that
            # backup is unabridged.
            target = normalize_linebreaks(current_ko)
            strategy = "preserve_post_compaction_current_quality_revision"
            preserved_count += 1
        else:
            target = normalize_legacy_layout(legacy[entry_id])
            strategy = "restore_precompaction_full_korean_text"
            restoration_count += 1
        legacy_before_reflow: dict[str, Any] | None = None
        if entry_id in SEMANTIC_REFLOW_OVERRIDES:
            legacy_unreflowed = normalize_legacy_layout(legacy[entry_id])
            legacy_unreflowed_metrics = layout_lines(
                entry_id, legacy_unreflowed, current, reservations
            )
            legacy_before_reflow = {
                "legacy_ko": legacy_unreflowed,
                "line_count": len(legacy_unreflowed_metrics),
                "lines": legacy_unreflowed_metrics,
                "any_line_exceeds_912px": any(
                    metric["exceeds_912px"] for metric in legacy_unreflowed_metrics
                ),
                "reason": "The legacy second line is raw 2016px/effective 1260px, so it must be redistributed by Korean clause without shortening.",
            }
            target = SEMANTIC_REFLOW_OVERRIDES[entry_id]
            strategy = "restore_precompaction_full_korean_text_with_semantic_reflow"

        require(target, f"{entry_id}: empty restoration target")
        assert_colour_tags(target, entry_id)
        target_signature = control_signature(target)
        require(target_signature == control_signature(current_ko), f"{entry_id}: current control signature drift")
        require(target_signature == control_signature(jp[entry_id]), f"{entry_id}: direct JP control signature drift")
        metrics = layout_lines(entry_id, target, current, reservations)
        require(1 <= len(metrics) <= MAX_LINES, f"{entry_id}: target line count exceeds {MAX_LINES}")
        require(
            not any(metric["exceeds_912px"] for metric in metrics),
            f"{entry_id}: target exceeds static-patch-007 width",
        )

        flags: list[str] = []
        if RUNTIME_RE.search(target):
            flags.append("runtime_name_token_reservation_recheck")
        if entry_id in HISTORICAL_TERMINOLOGY_IDS:
            flags.append("historical_title_place_or_term_review_recommended")
        if entry_id in SPEAKER_VOICE_OR_CONTEXT_IDS:
            flags.append("speaker_voice_or_context_review_recommended")
        if current_quality_changed:
            flags.append("post_compaction_quality_revision_preserved")

        rows.append(
            {
                "id": entry_id,
                "review_status": "ready_for_semantic-restoration_candidate",
                "restoration_strategy": strategy,
                "review_flags": flags,
                "historical_manual_compact_ko": compact,
                "current_ko_at_static007_3line_baseline": current_ko,
                "legacy_precompaction_ko": legacy[entry_id],
                "legacy_layout_before_semantic_reflow": legacy_before_reflow,
                "proposed_ko": target,
                "historical_compact_to_proposed_surface_units": reintroduced_surface_units(compact, target),
                "current_to_proposed_surface_units": source_delta_units(current_ko, target),
                "direct_pc_sources": {
                    "jp": jp[entry_id],
                    "en": en[entry_id],
                    "sc": sc[entry_id],
                    "tc": tc[entry_id],
                },
                "current_ko_utf16le_sha256": text_digest(current_ko),
                "proposed_ko_utf16le_sha256": text_digest(target),
                "control_signature": target_signature,
                "target_line_count": len(metrics),
                "target_lines": metrics,
                "any_line_exceeds_912px": any(metric["exceeds_912px"] for metric in metrics),
                "semantic_layout_note": (
                    "The legacy second line exceeded the static-patch-007 width; the "
                    "same full sentence is redistributed at Korean clause boundaries."
                    if legacy_before_reflow is not None
                    else
                    "Existing Korean clause boundaries were retained after direct-PC "
                    "JP/EN/SC/TC comparison; only inherited leading full-width "
                    "indentation is removed."
                    if not current_quality_changed
                    else "A later current quality revision was retained after direct-PC "
                    "JP/EN/SC/TC comparison; it supersedes the historical compact record."
                ),
            }
        )

    require(
        preserved_count == EXPECTED_CURRENT_QUALITY_PRESERVED_COUNT,
        f"current quality preservation count drift: {preserved_count}",
    )
    require(restoration_count + preserved_count == EXPECTED_TARGET_COUNT, "review count accounting drift")
    payload = {
        "schema": SCHEMA,
        "scope": {
            "resource": "MSG_PK/JP/msgev.bin",
            "event_id_range": [MIN_ID, MAX_ID],
            "manual_compact_target_count": len(rows),
            "legacy_full_text_restoration_count": restoration_count,
            "post_compaction_current_quality_preserved_count": preserved_count,
            "candidate_binary_created": False,
            "steam_files_written": False,
            "git_or_release_actions_performed": False,
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
            "dynamic_name_reservations": "same 30/48 scaling; raw reservation from reviewed token manifest",
        },
        "sources": {
            "current_ko_static007_3line_successor": current_profile,
            "direct_pc_jp_pristine": jp_profile,
            "direct_pc_en": en_profile,
            "direct_pc_sc": sc_profile,
            "direct_pc_tc": tc_profile,
            "legacy_precompaction_ko_backup": legacy_profile,
            "historical_manual_compact_manifest": {
                "path": str(HISTORICAL_MANIFEST),
                "sha256": digest(HISTORICAL_MANIFEST.read_bytes()),
            },
            "runtime_reservation_manifest": {
                "path": str(RESERVATION_MANIFEST),
                "sha256": digest(RESERVATION_MANIFEST.read_bytes()),
            },
        },
        "additional_translation_judgement_groups": [
            {
                "group": "historical_titles_places_and_period_terms",
                "ids": sorted(HISTORICAL_TERMINOLOGY_IDS & {row["id"] for row in rows}),
                "reason": "Historical titles, era names, temple/castle names, and inherited terminology merit a consistency pass even though the proposed restoration is source-complete.",
            },
            {
                "group": "speaker_voice_or_contextual_tone",
                "ids": sorted(SPEAKER_VOICE_OR_CONTEXT_IDS & {row["id"] for row in rows}),
                "reason": "These rows use judgmental, honorific, or character-voice phrasing where literal source coverage alone does not settle the best Korean wording.",
            },
            {
                "group": "runtime_name_tokens",
                "ids": [row["id"] for row in rows if "runtime_name_token_reservation_recheck" in row["review_flags"]],
                "reason": "The line plan reserves the known runtime name width, but final in-game QA should exercise the named scene/token rather than infer an unrelated runtime route.",
            },
            {
                "group": "post_compaction_current_quality_revisions",
                "ids": [row["id"] for row in rows if "post_compaction_quality_revision_preserved" in row["review_flags"]],
                "reason": "These are not overwritten by the legacy recovery because the current static007 3-line baseline already contains later source-driven quality work.",
            },
        ],
        "entries": rows,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUTPUT_PATH),
                "target_count": len(rows),
                "legacy_full_text_restoration_count": restoration_count,
                "current_quality_preserved_count": preserved_count,
                "steam_files_written": False,
                "candidate_binary_created": False,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
