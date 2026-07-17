#!/usr/bin/env python3
"""Build a PC-only Korean review for the unpatched PK ending credits table.

``MSG_PK/JP/msgstf_ce.bin`` is still Japanese in the current PC JP route.
There is no PC Korean variant for this resource: the candidate rows therefore
use the live Japanese text as the builder baseline and add a Korean first-pass
translation.  Pristine/live PC Japanese is the authority.  PC EN/SC/TC are
read only for name spelling and semantic context; no Switch or historic Korean
resource is opened by this module.

All evidence files contain paired commercial text and remain under ``tmp``.
The tracked helper has no source-text literals.  It never rebuilds or writes a
Steam resource.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


REPO = Path(__file__).resolve().parents[2]
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
AUDIT_ROOT = REPO / "tmp" / "translation_quality_audit_v1"
DEFAULT_AUDIT_OUTPUT = AUDIT_ROOT / "semantic" / "msgstf_ce_pc_only_full_audit.v1.jsonl"
DEFAULT_CANDIDATE_OUTPUT = AUDIT_ROOT / "semantic" / "msgstf_ce_pc_only_quality_addendum.v1.jsonl"
DEFAULT_HOLD_OUTPUT = AUDIT_ROOT / "semantic" / "msgstf_ce_pc_only_ambiguous_holds.v1.jsonl"
GENERIC_BUILDER = REPO / "workstreams" / "translation_quality_corrections_v1" / "build_translation_quality_corrections_v1.py"

RESOURCE = "msgstf_ce"
RELATIVE_PATH = "MSG_PK/JP/msgstf_ce.bin"
PATHS = {
    "jp": STEAM_ROOT / "MSG_PK" / "JP" / "msgstf_ce.bin",
    "en": STEAM_ROOT / "MSG_PK" / "EN" / "msgstf_ce.bin",
    "sc": STEAM_ROOT / "MSG_PK" / "SC" / "msgstf_ce.bin",
    "tc": STEAM_ROOT / "MSG_PK" / "TC" / "msgstf_ce.bin",
}

# These pin the PC 1.1.7 inputs observed before any Korean overlay exists for
# this resource.  ``jp`` is both the pristine source and the current builder
# baseline until the first Korean candidate is applied.
EXPECTED_FILE_SHA256 = {
    "jp": "27E8F296E7EA452E6AC1D6D6884084D3AB635D11281AF01E3A1F0A3696710F36",
    "en": "4B86E9FC838B0C82C38B27EE84E30C01916E440D2675F5991EBF6E8E9D85E716",
    "sc": "1EBEDA27B5FB81BCD8D5D8BF3A4BFF98AE0D7ACD9CDD3E27C2CE8477556B8F3C",
    "tc": "4358E6AE4F1105CF3BDAF4B897FA41BF510F3493E4D239359C1EB3F5C1F8A4FF",
}

ENTRY_COUNT = 20
POPULATED_IDS = tuple(range(8))
EMPTY_IDS = tuple(range(8, ENTRY_COUNT))
# The reference variants intentionally differ only on the long page-5 credits
# layout.  Pinning their page line domains makes that comparison explicit and
# rejects a silent locale/file mismatch before any EN spelling is consumed.
EXPECTED_POPULATED_LINE_COUNTS = {
    "jp": (71, 69, 103, 26, 120, 121, 125, 28),
    "en": (71, 69, 103, 26, 120, 122, 125, 28),
    "sc": (71, 69, 103, 26, 120, 97, 125, 28),
    "tc": (71, 69, 103, 26, 120, 97, 125, 28),
}
# Credits pages use their widest source line as a practical page-width budget.
# A four-cell allowance admits a longer PC-EN romanized name without allowing
# a translated Korean heading to grow beyond a source page's established span.
PAGE_MAX_DISPLAY_CELL_EXCESS_ALLOWED = 4

RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
SOURCE_SCRIPT_RE = re.compile(
    r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")

sys.path.insert(0, str(REPO / "tools"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


# These are line-indexed rather than source-text keyed.  The whole-file hash
# plus the expected line-domain checks below prevent an accidental rebase from
# applying a heading to a different credit line.  Only Korean output is stored
# here; Japanese source text remains in the private audit artifacts.
LINE_REPLACEMENTS: dict[int, dict[int, str]] = {
    0: {
        0: "게임 기획자",
        29: "프로그래머",
        55: "AI 프로그래머",
        60: "도구 및 라이브러리 프로그래머",
    },
    1: {
        0: "오프닝 영상",
        1: "감독",
        4: "도검 연마 감수",
        6: "도검 연마 시연",
        9: "페이셜 액터",
        14: "모션 액터",
        23: "영상 제작",
        30: "캐릭터 디자인",
    },
    2: {
        0: "캐릭터 모델링",
        20: "스테이지 콘셉트 아트",
        23: "스테이지 모델링",
        48: "액션 디자인",
        57: "이벤트 제작",
        63: "인터페이스 디자인",
        84: "2D 애니메이션",
        99: "이펙트 디자인",
    },
    3: {
        0: "영상 제작",
        11: "테크니컬 아트",
        17: "CG 연출",
        20: "CG 품질 관리",
        23: "CG 제작 관리",
    },
    4: {
        0: "음악",
        8: "연주",
        9: "바이올린",
        45: "비올라",
        57: "첼로",
        66: "콘트라베이스",
        71: "플루트",
        76: "오보에",
        81: "클라리넷",
        86: "바순",
        91: "호른",
        100: "트럼펫",
        107: "트롬본",
        113: "튜바",
        116: "시노부에",
        118: "샤쿠하치",
    },
    5: {
        0: "녹음 스튜디오",
        4: "믹싱 스튜디오",
        8: "녹음 / 믹싱 엔지니어",
        11: "녹음 디렉터",
        14: "녹음 코디네이터",
        18: "사운드 디자이너",
        23: "출연",
        24: "내레이션",
        26: "오다 노부나가",
        28: "도요토미 히데요시 / 냉정한 남자",
        30: "다테 마사무네",
        32: "아케치 미쓰히데",
        34: "도쿠가와 이에야스 / 용감한 남자",
        36: "다케다 신겐 / 노인 남자",
        38: "우에스기 겐신 / 위엄 있는 남자",
        40: "모리 모토나리 / 난폭한 남자",
        42: "평범한 남자 / 책사 남자",
        44: "호걸 남자 / 품격 있는 남자",
        46: "평범한 여자",
        48: "용감한 여자 / 상냥한 여자",
        51: "일본어 음성 녹음 스튜디오",
        54: "일본어 음성 연출",
        55: "일본어 녹음 엔지니어",
        59: "일본어 음성 제작",
        63: "영어 음성 출연",
        64: "내레이션",
        66: "오다 노부나가",
        68: "도요토미 히데요시",
        70: "다테 마사무네 / 냉정한 남자",
        72: "아케치 미쓰히데",
        74: "도쿠가와 이에야스",
        76: "다케다 신겐",
        78: "우에스기 겐신",
        80: "모리 모토나리",
        82: "호걸 남자",
        84: "위엄 있는 남자",
        86: "여자",
        89: "영어 음성 녹음",
        90: "영어 사운드 프로덕션",
        93: "영어 음성 디렉터",
        96: "영어 녹음 엔지니어",
        99: "영어 캐스팅 디렉터",
        102: "영어 음성 프로덕션 매니저",
        105: "『노부나가의 야망·신생』 엔딩 테마",
        106: "뇌명",
        107: "가창",
        109: "작사",
        111: "작곡",
        113: "편곡",
        115: "협력",
    },
    6: {
        0: "패키지 일러스트",
        3: "크리에이티브 스튜디오",
        16: "현지화 프로듀싱",
        25: "매뉴얼",
        29: "튜토리얼",
        33: "글로벌 비즈니스",
        63: "홍보",
        76: "QA 디렉터",
        82: "QA 리드",
        87: "QA 코디네이터",
        94: "QA 엔지니어",
        99: "운영부",
        107: "상품",
        116: "라이선스",
        121: "법무",
    },
    7: {0: "제작 협력"},
}

# PC EN line positions diverge near the final theme-song block of page 5.
# These values retain the verified PC EN spellings while preserving the JP
# page's original line count and whitespace.  The four SIDE London entries
# are normalized to the same ASCII parenthesis style found in PC EN.
LINE_OVERRIDES: dict[tuple[int, int], str] = {
    (5, 94): "Kate Saxon (SIDE London)",
    (5, 97): "Jack Kirby (SIDE London)",
    (5, 100): "Jessica Cameron (SIDE London)",
    (5, 103): "Lucy Maddox (SIDE London)",
    (5, 108): "Kiyoshi Hikawa",
    (5, 110): "Naomi Tamura",
    (5, 112): "Yoshiki Fukuyama",
    (5, 114): "Daiju Takato",
    (5, 116): "Lifetime;co",
    (5, 117): "BAVIC CORPORATION",
    (5, 119): "NAGARA PRODUCTION CO.,LTD.",
    (5, 120): "NIPPON COLUMBIA CO., LTD.",
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-16-le")).hexdigest().upper()


def load_table(path: Path) -> tuple[str, ...]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def safe_under(path: Path, root: Path) -> Path:
    resolved = path.resolve(strict=False)
    allowed = root.resolve(strict=False)
    if resolved != allowed and allowed not in resolved.parents:
        raise ValueError(f"output must remain below {allowed}: {resolved}")
    return resolved


def atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def deterministic_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def split_line_ending(value: str) -> tuple[str, str]:
    if value.endswith("\r\n"):
        return value[:-2], "\r\n"
    if value.endswith("\r") or value.endswith("\n"):
        return value[:-1], value[-1]
    return value, ""


def split_outer_whitespace(value: str) -> tuple[str, str, str]:
    left = 0
    while left < len(value) and value[left].isspace():
        left += 1
    right = len(value)
    while right > left and value[right - 1].isspace():
        right -= 1
    return value[:left], value[left:right], value[right:]


def line_profile(value: str) -> list[dict[str, str]]:
    profile: list[dict[str, str]] = []
    for raw_line in value.splitlines(keepends=True):
        body, ending = split_line_ending(raw_line)
        leading, _core, trailing = split_outer_whitespace(body)
        profile.append({"leading": leading, "trailing": trailing, "ending": ending})
    return profile


def format_profile(value: str) -> dict[str, Any]:
    esc_offsets = {offset for match in ESC_RE.finditer(value) for offset in range(match.start(), match.end())}
    return {
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "escape_tags": ESC_RE.findall(value),
        "line_breaks": re.findall(r"\r\n|\n|\r", value),
        "line_whitespace": line_profile(value),
        "leading_whitespace": value[: len(value) - len(value.lstrip())],
        "trailing_whitespace": value[len(value.rstrip()) :],
        "private_use": [f"U+{ord(character):04X}" for character in value if 0xE000 <= ord(character) <= 0xF8FF],
        "controls": [
            f"U+{ord(character):04X}"
            for index, character in enumerate(value)
            if unicodedata.category(character) == "Cc" and character not in ("\r", "\n") and index not in esc_offsets
        ],
        "fullwidth_percent_count": value.count("％"),
    }


def display_cells(value: str) -> int:
    """Conservative East-Asian-width proxy used only for a credits sanity gate."""
    width = 0
    for character in value:
        if character in "\r\n":
            continue
        width += 2 if unicodedata.east_asian_width(character) in {"F", "W"} else 1
    return width


def render_page(identifier: int, source: str, english: str) -> tuple[str, dict[str, Any]]:
    source_lines = source.splitlines(keepends=True)
    english_lines = english.splitlines(keepends=True)
    if identifier != 5 and len(source_lines) != len(english_lines):
        raise ValueError(f"{RESOURCE}:{identifier}: PC JP/EN line domain diverges")
    if identifier == 5 and (len(source_lines), len(english_lines)) != (121, 122):
        raise ValueError(f"{RESOURCE}:5: expected audited JP/EN 121/122 line domain")

    replacements = LINE_REPLACEMENTS[identifier]
    result: list[str] = []
    automatic_en_indices: list[int] = []
    deltas: list[dict[str, int]] = []
    for line_index, raw_line in enumerate(source_lines):
        body, ending = split_line_ending(raw_line)
        leading, core, trailing = split_outer_whitespace(body)
        if not core:
            result.append(raw_line)
            continue

        override = LINE_OVERRIDES.get((identifier, line_index))
        if line_index in replacements:
            translated = replacements[line_index]
        elif override is not None:
            translated = override
        elif SOURCE_SCRIPT_RE.search(core):
            if line_index >= len(english_lines):
                raise ValueError(f"{RESOURCE}:{identifier}:{line_index}: no PC EN context line")
            _en_leading, en_core, _en_trailing = split_outer_whitespace(split_line_ending(english_lines[line_index])[0])
            if not en_core or SOURCE_SCRIPT_RE.search(en_core):
                raise ValueError(f"{RESOURCE}:{identifier}:{line_index}: PC EN name/context cannot be used safely")
            if identifier == 5 and line_index >= 97:
                raise ValueError(f"{RESOURCE}:5:{line_index}: final-page EN offset requires explicit override")
            translated = en_core
            automatic_en_indices.append(line_index)
        else:
            translated = core

        transformed = leading + translated + trailing + ending
        result.append(transformed)
        delta = display_cells(translated) - display_cells(core)
        if delta:
            deltas.append({"line": line_index, "display_cell_delta": delta})

    proposed = "".join(result)
    if format_profile(source) != format_profile(proposed):
        raise ValueError(f"{RESOURCE}:{identifier}: protected layout profile changed")
    if SOURCE_SCRIPT_RE.search(proposed):
        raise ValueError(f"{RESOURCE}:{identifier}: source-script residue remains in proposed Korean page")
    if not HANGUL_RE.search(proposed):
        raise ValueError(f"{RESOURCE}:{identifier}: Korean candidate has no Hangul")
    source_display_widths = [display_cells(split_line_ending(line)[0]) for line in source_lines]
    proposed_display_widths = [display_cells(split_line_ending(line)[0]) for line in result]
    source_page_max = max(source_display_widths, default=0)
    proposed_page_max = max(proposed_display_widths, default=0)
    proposed_heading_max = max((proposed_display_widths[index] for index in replacements), default=0)
    if proposed_heading_max > source_page_max:
        raise ValueError(f"{RESOURCE}:{identifier}: Korean heading exceeds its source-page display-width budget")
    if proposed_page_max > source_page_max + PAGE_MAX_DISPLAY_CELL_EXCESS_ALLOWED:
        raise ValueError(f"{RESOURCE}:{identifier}: proposed line exceeds the guarded credits-page width allowance")
    return proposed, {
        "source_line_count": len(source_lines),
        "pc_en_line_count": len(english_lines),
        "automatic_pc_en_name_or_company_line_count": len(automatic_en_indices),
        "automatic_pc_en_line_indices": automatic_en_indices,
        "explicit_heading_line_count": len(replacements),
        "explicit_pc_en_offset_override_line_count": sum(1 for key in LINE_OVERRIDES if key[0] == identifier),
        "maximum_display_cell_delta": max((row["display_cell_delta"] for row in deltas), default=0),
        "minimum_display_cell_delta": min((row["display_cell_delta"] for row in deltas), default=0),
        "nonzero_display_cell_delta_line_count": len(deltas),
        "source_page_max_display_cells": source_page_max,
        "proposed_page_max_display_cells": proposed_page_max,
        "proposed_korean_heading_max_display_cells": proposed_heading_max,
        "proposed_page_max_excess_display_cells": proposed_page_max - source_page_max,
        "korean_headings_within_source_page_width": True,
        "page_max_display_cell_excess_allowed": PAGE_MAX_DISPLAY_CELL_EXCESS_ALLOWED,
    }


def generic_builder_has_msgstf_ce_resource() -> bool:
    if not GENERIC_BUILDER.is_file():
        return False
    source = GENERIC_BUILDER.read_text(encoding="utf-8")
    return bool(re.search(r'ResourceSpec\(\s*"msgstf_ce"', source))


def build_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    file_hashes = {language: file_hash(path) for language, path in PATHS.items()}
    if file_hashes != EXPECTED_FILE_SHA256:
        raise ValueError("PC msgstf_ce baseline changed; rebase this PC-only audit before reuse")
    tables = {language: load_table(path) for language, path in PATHS.items()}
    if any(len(table) != ENTRY_COUNT for table in tables.values()):
        raise ValueError("PC msgstf_ce table cardinality differs from 20")
    if any(
        tuple(len(tables[language][identifier].splitlines()) for identifier in POPULATED_IDS)
        != EXPECTED_POPULATED_LINE_COUNTS[language]
        for language in PATHS
    ):
        raise ValueError("PC msgstf_ce JP/EN/SC/TC page line domains changed")
    if any(tables[language][identifier] for language in tables for identifier in EMPTY_IDS):
        raise ValueError("msgstf_ce expected-empty slots are no longer empty")
    if any(not tables["jp"][identifier] for identifier in POPULATED_IDS):
        raise ValueError("msgstf_ce populated PC JP slots changed")
    if any(HANGUL_RE.search(tables["jp"][identifier]) for identifier in POPULATED_IDS):
        raise ValueError("msgstf_ce PC JP baseline is no longer an untranslated Japanese page")
    if any(not SOURCE_SCRIPT_RE.search(tables["jp"][identifier]) for identifier in POPULATED_IDS):
        raise ValueError("msgstf_ce populated PC JP page lost its source-script proof")

    candidates: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    display_summary: dict[str, Any] = {}
    for identifier in range(ENTRY_COUNT):
        source = tables["jp"][identifier]
        references = {language.upper(): tables[language][identifier] for language in ("en", "sc", "tc")}
        if identifier in POPULATED_IDS:
            proposed, rendering = render_page(identifier, source, tables["en"][identifier])
            display_summary[str(identifier)] = rendering
            before_profile = format_profile(source)
            after_profile = format_profile(proposed)
            if before_profile != after_profile:
                raise ValueError(f"{RESOURCE}:{identifier}: candidate profile differs")
            candidate = {
                "resource": RESOURCE,
                "id": identifier,
                # ``ko`` intentionally equals the current live builder baseline
                # (Japanese) until this first Korean overlay is applied.
                "ko": source,
                "proposed_ko": proposed,
                "current_hash": text_hash(source),
                "source_text": source,
                "source_text_hash": text_hash(source),
                "live_jp_target_file_sha256": file_hashes["jp"],
                "pristine_pc_jp_file_sha256": file_hashes["jp"],
                "reference_contexts": references,
                "issue_type": "untranslated_pc_jp_credits_page",
                "rationale": (
                    "The current PC JP-route credits page remains Japanese because no "
                    "PC Korean msgstf_ce variant exists.  The candidate directly "
                    "translates the Japanese headings, keeps original per-line layout, "
                    "and uses only same-page PC EN spelling for credit names/companies."
                ),
                "current_pc_korean_status": "absent_live_jp_route_contains_untranslated_japanese",
                "pc_reference_use": "Pristine/current PC Japanese is authority; PC EN/SC/TC are context only",
                "rendering_validation": rendering,
                "format_validation": {
                    "current_to_proposed": "runtime_printf_escape_newline_per_line_outer_whitespace_private_use_controls_and_percent_match",
                    "all_required_checks_pass": True,
                },
                "switch_korean_translation_used": False,
                "historic_korean_translation_used": False,
                "game_files_written": False,
            }
            candidates.append(candidate)
            disposition = "candidate_high_confidence_untranslated_pc_jp_page"
            detail = "live PC JP target has no Korean variant; first-pass Korean credits page generated from PC-only evidence"
        else:
            disposition = "retained_intentional_empty_slot"
            detail = "empty in PC JP and all PC reference-language tables"
        audit_rows.append(
            {
                "schema": "nobu16.kr.msgstf-ce-pc-only-full-audit.v1",
                "resource": RESOURCE,
                "id": identifier,
                "disposition": disposition,
                "disposition_detail": detail,
                "source_jp": source,
                "source_jp_utf16le_sha256": text_hash(source),
                "current_pc_korean_status": "absent_live_jp_route_contains_untranslated_japanese" if identifier in POPULATED_IDS else "not_applicable_intentional_empty_slot",
                "current_live_target_text": source,
                "current_live_target_utf16le_sha256": text_hash(source),
                "reference_contexts": references,
                "source_file_sha256": file_hashes["jp"],
                "current_target_file_sha256": file_hashes["jp"],
                "reference_file_sha256": {language.upper(): file_hashes[language] for language in ("en", "sc", "tc")},
                "audit_scope": {
                    "pristine_pc_japanese": True,
                    "current_pc_korean_variant_present": False,
                    "current_pc_jp_route_checked": True,
                    "pc_en_sc_tc_references": True,
                    "switch_korean_read": False,
                    "historic_korean_read": False,
                    "steam_game_resource_written": False,
                },
            }
        )

    holds: list[dict[str, Any]] = []
    has_resource = generic_builder_has_msgstf_ce_resource()
    summary = {
        "schema": "nobu16.kr.msgstf-ce-pc-only-full-audit-summary.v1",
        "resource": RESOURCE,
        "relative_path": RELATIVE_PATH,
        "entry_count": len(audit_rows),
        "populated_page_count": len(POPULATED_IDS),
        "intentional_empty_entry_count": len(EMPTY_IDS),
        "current_pc_korean_page_count": 0,
        "untranslated_pc_jp_page_count": len(POPULATED_IDS),
        "new_high_confidence_candidate_count": len(candidates),
        "ambiguous_hold_count": len(holds),
        "disposition_counts": dict(sorted(Counter(row["disposition"] for row in audit_rows).items())),
        "display_width_summary": display_summary,
        "generic_translation_quality_builder_has_msgstf_ce_resource": has_resource,
        "integration_requirement": (
            "already configured with a common msgstf_ce ResourceSpec"
            if has_resource
            else "add a common ResourceSpec named msgstf_ce for MSG_PK/JP/msgstf_ce.bin and this private candidate JSONL"
        ),
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "game_files_written": False,
    }
    return audit_rows, candidates, holds, summary


def validate_rows(
    audit_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    hold_rows: list[dict[str, Any]],
    summary: Mapping[str, Any],
) -> None:
    if len(audit_rows) != ENTRY_COUNT or {row["id"] for row in audit_rows} != set(range(ENTRY_COUNT)):
        raise ValueError("full msgstf_ce audit does not cover every 0..19 coordinate exactly once")
    if {row["id"] for row in candidate_rows} != set(POPULATED_IDS):
        raise ValueError("msgstf_ce high-confidence candidate set differs from populated PC JP pages")
    if hold_rows:
        raise ValueError("msgstf_ce has no unresolved hold rows in this PC-only first-pass translation")
    expected = Counter(
        {
            "candidate_high_confidence_untranslated_pc_jp_page": len(POPULATED_IDS),
            "retained_intentional_empty_slot": len(EMPTY_IDS),
        }
    )
    if Counter(row["disposition"] for row in audit_rows) != expected:
        raise ValueError("msgstf_ce audit disposition counts differ from reviewed partition")
    for row in candidate_rows:
        if row["ko"] == row["proposed_ko"] or text_hash(row["ko"]) != row["current_hash"]:
            raise ValueError(f"{RESOURCE}:{row['id']}: candidate text/hash gate is invalid")
        if format_profile(row["ko"]) != format_profile(row["proposed_ko"]):
            raise ValueError(f"{RESOURCE}:{row['id']}: candidate format profile differs")
        if SOURCE_SCRIPT_RE.search(row["proposed_ko"]) or not HANGUL_RE.search(row["proposed_ko"]):
            raise ValueError(f"{RESOURCE}:{row['id']}: candidate Korean safety check fails")
        if row["switch_korean_translation_used"] or row["historic_korean_translation_used"] or row["game_files_written"]:
            raise ValueError(f"{RESOURCE}:{row['id']}: candidate audit scope is not PC-only/read-only")
    for row in audit_rows:
        scope = row["audit_scope"]
        if scope["switch_korean_read"] or scope["historic_korean_read"] or scope["steam_game_resource_written"]:
            raise ValueError("msgstf_ce audit scope must remain PC-only and read-only")
    if summary.get("entry_count") != ENTRY_COUNT or summary.get("new_high_confidence_candidate_count") != len(POPULATED_IDS):
        raise ValueError("msgstf_ce audit summary is inconsistent")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT_OUTPUT)
    parser.add_argument("--candidate-output", type=Path, default=DEFAULT_CANDIDATE_OUTPUT)
    parser.add_argument("--hold-output", type=Path, default=DEFAULT_HOLD_OUTPUT)
    parser.add_argument("--write", action="store_true", help="write private PC-only audit, candidate, and hold JSONL files")
    parser.add_argument("--validate", action="store_true", help="validate generated data and any existing deterministic outputs")
    args = parser.parse_args()

    outputs = {
        "audit": safe_under(args.audit_output, AUDIT_ROOT),
        "candidate": safe_under(args.candidate_output, AUDIT_ROOT),
        "hold": safe_under(args.hold_output, AUDIT_ROOT),
    }
    audit_rows, candidate_rows, hold_rows, summary = build_rows()
    validate_rows(audit_rows, candidate_rows, hold_rows, summary)
    payloads = {
        "audit": deterministic_jsonl(audit_rows),
        "candidate": deterministic_jsonl(candidate_rows),
        "hold": deterministic_jsonl(hold_rows),
    }
    if args.write:
        for key in ("audit", "candidate", "hold"):
            atomic_write(outputs[key], payloads[key])
    if args.validate:
        for key in ("audit", "candidate", "hold"):
            if outputs[key].exists() and outputs[key].read_text(encoding="utf-8") != payloads[key]:
                raise ValueError(f"existing {key} output differs from deterministic PC-only evidence")
    summary = dict(summary)
    summary["payload_sha256"] = {key: hashlib.sha256(payload.encode("utf-8")).hexdigest().upper() for key, payload in payloads.items()}
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
