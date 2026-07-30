#!/usr/bin/env python3
"""Build Base authoring segment 792 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S792.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s792",
        ENGINE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
COMMON_RELATION_CONDITIONS = (
    "\n·동맹, 종속, 정전 관계가 아니며 동맹 상대의 종속 세력도 아님\n"
    "·자세력과 인접한 성임\n"
)
COMMON_SUCCESS_FACTORS = (
    "\n·실행 무장의 지략이 성공률에 영향을 준다\n"
    '·대상 무장의 소속 성에 특성 "이닌도"가 발현되어 있으면 실패한다'
)
TRANSLATIONS: dict[str, str] = {
    "14:123:0": "[유언비어]",
    "14:123:1": "\n대상 무장의 충성을 낮춥니다.\n\n",
    "14:123:2": "◇조건",
    "14:123:3": COMMON_RELATION_CONDITIONS + "·충성이 노란색인 무장이 있음\n\n",
    "14:123:4": "◇효과에 영향을 주는 요소",
    "14:123:5": COMMON_SUCCESS_FACTORS,
    "14:124:0": "[빼내기]",
    "14:124:1": "\n충성이 낮은 무장을 자세력으로 빼냅니다.\n\n",
    "14:124:2": "◇조건",
    "14:124:3": COMMON_RELATION_CONDITIONS + "·충성이 빨간색인 무장이 있음\n\n",
    "14:124:4": "◇효과에 영향을 주는 요소",
    "14:124:5": COMMON_SUCCESS_FACTORS,
    "14:125:0": "[선동]",
    "14:125:1": "\n대상 성의 군에서 잇키를 일으킵니다.\n\n",
    "14:125:2": "◇조건",
    "14:125:3": COMMON_RELATION_CONDITIONS + "·잇키를 일으킬 수 있는 군이 있음\n\n",
    "14:125:4": "◇효과에 영향을 주는 요소",
    "14:125:5": (
        "\n·실행 무장과 대상 성의 지략이 성공률에 영향을 준다\n"
        '·대상 무장의 소속 성에 특성 "이닌도"가 발현되어 있으면 실패한다'
    ),
    "14:126:0": "[파괴]",
    "14:126:1": "\n적 성의 내구와 병력을 줄입니다.\n\n",
    "14:126:2": "◇조건",
    "14:126:3": COMMON_RELATION_CONDITIONS + "\n",
    "14:126:4": "◇효과에 영향을 주는 요소",
    "14:126:5": COMMON_SUCCESS_FACTORS,
}

EXPECTED_ARITIES = {123: 6, 124: 6, 125: 6, 126: 6}
EXPECTED_DIVERGENCES = {"JP": {123, 124, 125, 126}, "SC": set(), "TC": set()}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
PROTECTED_GLYPHS = set("◇")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {123: 173, 124: 174, 125: 175, 126: 176}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 792 record has no configured PK mapping: {base_record_id}"
        ) from exc


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def expected_gaps(arity: int) -> tuple[bytes, ...]:
    return tuple([b"\x1b\x43\x49", b"\x1b\x43\x5a"] * (arity // 2) + [b"\x05\x05\x05"])


def line_layout_signature(text: str) -> tuple[object, ...]:
    lines = text.split("\n")
    protected = ENGINE.protected_signature(text)
    return (
        text.count("\n"),
        tuple(line[: len(line) - len(line.lstrip(" \t\u3000"))] for line in lines),
        tuple(line[len(line.rstrip(" \t\u3000")) :] for line in lines),
        tuple(line.count("\u3000") for line in lines),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(protected["non_layout_controls"]),
        protected["leading_whitespace"],
        protected["trailing_whitespace"],
    )


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in PROTECTED_GLYPHS]


def assert_available_duplicate_decision(coordinate: str, translation: str) -> None:
    if not OUTPUT.parent.is_dir():
        return
    for decision_path in OUTPUT.parent.glob("base_msggame_B001_S*.private.v1.jsonl"):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate and row.get("translation") != translation:
                raise RuntimeError(f"duplicate translation differs from {coordinate}")


def assert_scope(prepared: Any) -> None:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    source_records = ENGINE.archive_records(base.pristine_archive)
    current_records = ENGINE.archive_records(base.current_archive)
    pk_source_records = ENGINE.archive_records(pk.pristine_archive)
    base_context_records = {
        language: ENGINE.archive_records(archive)
        for language, archive in base.context_archives.items()
    }
    pk_context_records = {
        language: ENGINE.archive_records(archive)
        for language, archive in pk.context_archives.items()
    }

    if {mapped_pk_record_id(record_id) for record_id in EXPECTED_ARITIES} != set(
        range(173, 177)
    ):
        raise RuntimeError("segment 792 PK insertion mapping drifted")
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in EXPECTED_ARITIES
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(14, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(14, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences != EXPECTED_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 792 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 792 arity drifted: 14:{record_id}")
        expected = expected_gaps(arity)
        if record_gaps(source_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 792 pristine opcode gaps drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 792 current opcode gaps drifted: 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                raise RuntimeError(f"segment 792 contains a blank target: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 792 decision is missing: {coordinate}")
            if line_layout_signature(translation) != line_layout_signature(literal.text):
                raise RuntimeError(f"segment 792 layout signature drifted: {coordinate}")
            if glyph_skeleton(translation) != glyph_skeleton(literal.text):
                raise RuntimeError(f"segment 792 protected-glyph skeleton drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 792 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 792 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(
                    f"segment 792 retains banned fullwidth punctuation: {coordinate}"
                )
    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 24:
        raise RuntimeError("segment 792 decision universe drifted")

    condition_source = {
        ENGINE.parse_record_literals(source_records[(14, record_id)])[2].text
        for record_id in EXPECTED_ARITIES
    }
    influence_source = {
        ENGINE.parse_record_literals(source_records[(14, record_id)])[4].text
        for record_id in EXPECTED_ARITIES
    }
    if condition_source != {"◇条件"} or influence_source != {"◇効果に影響する要素"}:
        raise RuntimeError("segment 792 repeated source headings drifted")
    if {TRANSLATIONS[f"14:{record_id}:2"] for record_id in EXPECTED_ARITIES} != {"◇조건"}:
        raise RuntimeError("segment 792 repeated condition heading translation drifted")
    if {TRANSLATIONS[f"14:{record_id}:4"] for record_id in EXPECTED_ARITIES} != {
        "◇효과에 영향을 주는 요소"
    }:
        raise RuntimeError("segment 792 repeated influence heading translation drifted")
    assert_available_duplicate_decision("14:42:2", "◇조건")
    assert_available_duplicate_decision("14:42:4", "◇효과에 영향을 주는 요소")

    repeated_factor_records = (123, 124, 126)
    repeated_factor_sources = {
        ENGINE.parse_record_literals(source_records[(14, record_id)])[5].text
        for record_id in repeated_factor_records
    }
    repeated_factor_translations = {
        TRANSLATIONS[f"14:{record_id}:5"] for record_id in repeated_factor_records
    }
    if len(repeated_factor_sources) != 1 or repeated_factor_translations != {
        COMMON_SUCCESS_FACTORS
    }:
        raise RuntimeError("14:123/124/126 exact success-factor repetition drifted")
    if TRANSLATIONS["14:123:3"].splitlines()[:3] != TRANSLATIONS[
        "14:124:3"
    ].splitlines()[:3]:
        raise RuntimeError("14:123/124 shared relation conditions drifted")
    if TRANSLATIONS["14:125:5"].splitlines()[-1] != COMMON_SUCCESS_FACTORS.splitlines()[-1]:
        raise RuntimeError("14:125 shared 伊忍道 failure condition drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "유언비어",
        "빼내기",
        "선동",
        "파괴",
        "동맹",
        "종속",
        "정전",
        "자세력",
        "노란색",
        "빨간색",
        "지략",
        "이닌도",
        "잇키",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 792 required terminology drifted")
    if any(term in joined for term in ("유언]", "인발", "화공", "황색", "적색")):
        raise RuntimeError("segment 792 retains a forbidden legacy terminology variant")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_scope(prepared)
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(
                f"decision target is absent from the current Base universe: {coordinate}"
            )
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S792",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
                "confirmed_non_display": 0,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
