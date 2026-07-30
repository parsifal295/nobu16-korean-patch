#!/usr/bin/env python3
"""Build Base authoring segment 777 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S777.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s777",
        ENGINE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:42:0": "[무장 탐색]",
    "14:42:1": "\n주변의 낭인을 찾아 등용합니다.\n\n",
    "14:42:2": "◇조건",
    "14:42:3": "\n특별한 조건 없음\n\n",
    "14:42:4": "◇효과에 영향을 주는 요소",
    "14:42:5": '\n·능력 "정무"가 성공률에 영향',
    "14:43:0": "[석고 증강]",
    "14:43:1": (
        '\n"농촌"을 장악하여 석고를 높입니다.\n'
        "본거지의 농촌은 군 개발로 장악할 수 있으므로\n"
        '본거지 이외의 농촌은 "석고 증강"으로 장악합시다.\n'
        "\n"
    ),
    "14:43:2": "◇조건",
    "14:43:3": (
        "\n·본거지가 아님\n"
        "·성이 교전 중이지 않음\n"
        "·아직 장악하지 않은 농촌이 있음\n"
        "\n"
    ),
    "14:43:4": "◇효과에 영향을 주는 요소",
    "14:43:5": '\n·능력 "정무"가 석고 증가량에 영향',
    "14:44:0": "[상업 발전]",
    "14:44:1": (
        '\n"시장"을 장악하여 상업을 높입니다.\n'
        "본거지의 시장은 군 개발로 장악할 수 있으므로\n"
        '본거지 이외의 시장은 "상업 발전"으로 장악합시다.\n'
        "\n"
    ),
    "14:44:2": "◇조건",
    "14:44:3": (
        "\n·본거지가 아님\n"
        "·성이 교전 중이지 않음\n"
        "·아직 장악하지 않은 시장이 있음\n"
        "\n"
    ),
    "14:44:4": "◇효과에 영향을 주는 요소",
    "14:44:5": '\n·능력 "정무"가 상업 증가량에 영향',
    "14:45:0": "[수복]",
    "14:45:1": "\n성을 수복하여 내구를 회복합니다.\n\n",
    "14:45:2": "◇조건",
    "14:45:3": "\n·성이 교전 중이지 않음\n·내구가 최대치에 미달함\n\n",
    "14:45:4": "◇효과에 영향을 주는 요소",
    "14:45:5": '\n·능력 "정무"가 내구 회복량에 영향',
}

EXPECTED_ARITIES = {42: 6, 43: 6, 44: 6, 45: 6}
EXPECTED_DIVERGENCES = {"JP": set(), "SC": set(), "TC": set()}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_exact_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {42: 64, 43: 65, 44: 66, 45: 67}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 777 record has no configured PK mapping: {base_record_id}"
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
    leading = tuple(line[: len(line) - len(line.lstrip(" \t\u3000"))] for line in lines)
    trailing = tuple(line[len(line.rstrip(" \t\u3000")) :] for line in lines)
    return (
        text.count("\n"),
        leading,
        trailing,
        tuple(line.count("\u3000") for line in lines),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
    )


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

    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(42, 46)
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
                f"segment 777 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 777 arity drifted: 14:{record_id}")
        expected = expected_gaps(arity)
        if record_gaps(source_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 777 pristine opcode gaps drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 777 current opcode gaps drifted: 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                raise RuntimeError(f"segment 777 contains a blank target: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 777 decision is missing: {coordinate}")
            if line_layout_signature(translation) != line_layout_signature(literal.text):
                raise RuntimeError(f"segment 777 layout signature drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 777 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 777 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(f"segment 777 retains banned fullwidth punctuation: {coordinate}")

    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 24:
        raise RuntimeError("segment 777 decision universe drifted")

    condition_source = {
        ENGINE.parse_record_literals(source_records[(14, record_id)])[2].text
        for record_id in range(42, 48)
    }
    condition_current = {
        ENGINE.parse_record_literals(current_records[(14, record_id)])[2].text
        for record_id in range(42, 48)
    }
    if condition_source != {"◇条件"} or condition_current != {"◇조건"}:
        raise RuntimeError("14:42:2~14:47:2 exact condition heading contract drifted")
    for record_id in range(42, 46):
        if TRANSLATIONS[f"14:{record_id}:2"] != "◇조건":
            raise RuntimeError(f"14:{record_id}:2 exact condition translation drifted")
    for record_id in (46, 47):
        assert_available_duplicate_decision(f"14:{record_id}:2", "◇조건")

    influence_source = {
        ENGINE.parse_record_literals(source_records[(14, record_id)])[4].text
        for record_id in range(42, 47)
    }
    influence_current = {
        ENGINE.parse_record_literals(current_records[(14, record_id)])[4].text
        for record_id in range(42, 47)
    }
    if influence_source != {"◇効果に影響する要素"} or influence_current != {
        "◇효과에 영향을 주는 요소"
    }:
        raise RuntimeError("14:42:4~14:46:4 exact influence heading contract drifted")
    for record_id in range(42, 46):
        if TRANSLATIONS[f"14:{record_id}:4"] != "◇효과에 영향을 주는 요소":
            raise RuntimeError(f"14:{record_id}:4 exact influence translation drifted")
    assert_available_duplicate_decision("14:46:4", "◇효과에 영향을 주는 요소")

    source_42_5 = ENGINE.parse_record_literals(source_records[(14, 42)])[5].text
    source_46_5 = ENGINE.parse_record_literals(source_records[(14, 46)])[5].text
    current_42_5 = ENGINE.parse_record_literals(current_records[(14, 42)])[5].text
    current_46_5 = ENGINE.parse_record_literals(current_records[(14, 46)])[5].text
    if source_42_5 != source_46_5 or current_42_5 != current_46_5:
        raise RuntimeError("14:42:5/14:46:5 exact success-factor literal drifted")
    if TRANSLATIONS["14:42:5"] != '\n·능력 "정무"가 성공률에 영향':
        raise RuntimeError("14:42:5 exact success-factor translation drifted")
    assert_available_duplicate_decision("14:46:5", TRANSLATIONS["14:42:5"])

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "무장 탐색",
        "석고 증강",
        "상업 발전",
        "수복",
        "장악",
        "본거지",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 777 required terminology drifted")
    if any(
        term in joined
        for term in (
            "본거 이외",
            "수리",
            "호족",
            "노력",
            "교전 중이 아님",
            "내구가 최대가 아님",
        )
    ):
        raise RuntimeError("segment 777 retains a forbidden legacy term")


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
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
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
                "segment": "base_msggame_B001_S777",
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
