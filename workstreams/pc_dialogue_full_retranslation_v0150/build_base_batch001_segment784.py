#!/usr/bin/env python3
"""Build Base authoring segment 784 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S784.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s784", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:81:0": "[합전: 부대 명령]",
    "14:81:1": (
        "\n"
        "합전에서는 협격 저지나 퇴각로 공격처럼 전장 전체를 보고\n"
        "판단해야 하는 상황이 생깁니다.\n"
        "이런 상황에서는 무장이 어떻게 행동해야 할지 지시를 요청합니다.\n"
        "무엇을 우선하고 어떻게 명령할지 침착하게 상황을 판단합시다.\n"
        "\n"
        "특성에 따라 선호하는 행동이 있는 무장은 지시를 요청하지 않고\n"
        "독단으로 행동하기도 합니다."
    ),
    "14:82:0": "◇명령 방법",
    "14:82:1": (
        "\n"
        "무장의 제안을 받아들이려면\n"
        "부대에 이동 명령을 내려야 합니다.\n"
        "부대를 선택한 뒤 이동할 지점을 선택합니다.\n"
        "\n"
        "부대는 지정된 지점으로 이동해 그곳에서 대기합니다.\n"
        "대기를 해제하거나 명령을 중단하려면\n"
        "부대를 선택한 뒤 부대 위에 나타나는 버튼을 누릅니다."
    ),
    "14:83:0": "◇명령 방법",
    "14:83:1": (
        "\n"
        "무장의 제안을 받아들이려면\n"
        "부대에 이동 명령을 내려야 합니다.\n"
        "부대를 선택한 뒤 이동할 지점을 선택합니다.\n"
        "\n"
        "부대는 지정된 지점으로 이동해 그곳에서 대기합니다.\n"
        "대기를 해제하거나 명령을 중단하려면\n"
        "부대를 선택한 뒤 ㌘+㍗을 누릅니다."
    ),
    "14:84:0": "[합전: 부대 상태]",
    "14:84:1": (
        "\n"
        "부대는 전투를 계속하면 병력과 체력이 줄어\n"
        "결국 전투할 수 없는 상태가 됩니다.\n"
        "부대가 최상의 상태로 싸우도록 상태를 주의 깊게 살핍시다.\n"
        "\n"
    ),
    "14:84:2": "◇주의해야 할 아군 상태",
    "14:84:3": (
        "\n\u3000"
        "·부대의 병력\n"
        "·부대의 체력\n"
        "·상태 이상"
    ),
    "14:85:0": "◇병력",
    "14:85:1": (
        "\n"
        '병력이 0이 된 부대는 "괴멸"하고\n'
        "지휘하던 무장은 전장을 떠납니다.\n"
        "운이 나쁘면 적에게 붙잡히거나 전사할 수도 있습니다.\n"
        "\n"
        '병력이 줄어든 부대는 괴멸을 피하기 위해 "퇴각"합니다.\n'
        "퇴각 중인 부대는 어떤 지시도 받지 않고 아군의 퇴각로만을 향합니다.\n"
        "포박이나 전사를 막으려면 호위할 필요도 있습니다."
    ),
    "14:86:0": "◇체력",
    "14:86:1": (
        "\n"
        '부대에는 병력 외에 "체력"도 있습니다.\n'
        "체력이 줄면 부대 능력이 낮아집니다.\n"
        "\n"
        "·체력은 전투하면 줄고 전투하지 않고 대기하면 회복된다\n"
        "·방어력이 높을수록 체력이 잘 줄지 않는다\n"
        "·체력이 줄어든 부대는 공격과 방어가 크게 저하된다"
    ),
    "14:87:0": "[상태 이상]",
    "14:87:1": (
        "\n"
        "상태 이상에 걸린 부대는 행동이 제한됩니다.\n"
        "\n"
    ),
    "14:87:2": "◇혼란",
    "14:87:3": (
        "\n\u3000"
        "·전법, 특수 요충지 발동, 퇴각로 파괴로 발생\n"
        "·이동, 전투, 명령이 불가능해진다. 일정 시간이 지나면 해제\n"
        "\n"
    ),
    "14:87:4": "◇퇴각",
    "14:87:5": (
        "\n\u3000"
        "·병력이 줄어들면 발생\n"
        "·전투나 명령이 불가능해지고 가장 가까운 아군 퇴각로로 이동한다\n"
        "·퇴각로에 도착하면 전장에서 이탈한다\n"
        "※충성이 낮은 무장이나 국인중 부대는 평소보다 일찍 퇴각한다"
    ),
}

EXPECTED_ARITIES = {81: 2, 82: 2, 83: 2, 84: 4, 85: 2, 86: 2, 87: 6}
BASE_PK_DIVERGENCES = {
    "JP": {81, 84},
    "SC": {81, 84},
    "TC": {81, 84},
}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
CONTROLLER_GLYPHS = set("㌘㍗")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {81: 113, 82: 114, 83: 115, 84: 116, 85: 117, 86: 118, 87: 119}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 784 record has no configured PK mapping: {base_record_id}") from exc


def expected_gaps(arity: int) -> tuple[bytes, ...]:
    return tuple(
        part
        for _ in range(arity // 2)
        for part in (b"\x1b\x43\x49", b"\x1b\x43\x5a")
    ) + (b"\x05\x05\x05",)


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in CONTROLLER_GLYPHS]


def layout_signature(text: str) -> tuple[object, ...]:
    protected = ENGINE.protected_signature(text)
    return (
        text.count("\n"),
        tuple(line.count("\u3000") for line in text.split("\n")),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(protected["non_layout_controls"]),
        protected["leading_whitespace"],
        protected["trailing_whitespace"],
    )


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
            for record_id in range(81, 88)
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
        if divergences != BASE_PK_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 784 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    for record_id, expected_arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 784 literal arity drifted: 14:{record_id}")
        if record_gaps(source_records[(14, record_id)]) != expected_gaps(expected_arity):
            raise RuntimeError(f"segment 784 pristine literal/opcode boundary drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected_gaps(expected_arity):
            raise RuntimeError(f"segment 784 current literal/opcode boundary drifted: 14:{record_id}")
        if any(not literal.text.strip() for literal in source_literals + current_literals):
            raise RuntimeError(f"segment 784 unexpectedly contains a blank literal: 14:{record_id}")

    source_82 = ENGINE.parse_record_literals(source_records[(14, 82)])[0].text
    source_83 = ENGINE.parse_record_literals(source_records[(14, 83)])[0].text
    current_82 = ENGINE.parse_record_literals(current_records[(14, 82)])[0].text
    current_83 = ENGINE.parse_record_literals(current_records[(14, 83)])[0].text
    if source_82 != source_83 or current_82 != current_83:
        raise RuntimeError("14:82:0 and 14:83:0 exact source/current title reuse drifted")
    if TRANSLATIONS["14:82:0"] != TRANSLATIONS["14:83:0"]:
        raise RuntimeError("14:82:0 and 14:83:0 must translate exactly alike")

    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[
            literal_id
        ].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"{coordinate} LF/U+3000/token layout signature drifted")
        if "\r" in translation:
            raise RuntimeError(f"{coordinate} must not add CR")
        if ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"{coordinate} retains kana or CJK Han text")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")
        if glyph_skeleton(translation) != glyph_skeleton(current_text):
            raise RuntimeError(f"{coordinate} controller-glyph skeleton drifted")

    expected_u3000 = {"14:84:3", "14:87:3", "14:87:5"}
    actual_u3000 = {
        coordinate for coordinate, translation in TRANSLATIONS.items() if "\u3000" in translation
    }
    if actual_u3000 != expected_u3000:
        raise RuntimeError("segment 784 protected U+3000 coordinates drifted")
    if any(TRANSLATIONS[coordinate].count("\u3000") != 1 for coordinate in expected_u3000):
        raise RuntimeError("segment 784 protected U+3000 count drifted")

    for coordinate in ("14:81:0", "14:84:0"):
        if not TRANSLATIONS[coordinate].startswith("[합전:"):
            raise RuntimeError(f"{coordinate} must preserve the Base 合戦 heading")
        if "전장:" in TRANSLATIONS[coordinate]:
            raise RuntimeError(f"{coordinate} imported the PK 戦場 heading")
    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "합전",
        "상태 이상",
        "혼란",
        "퇴각",
        "특수 요충지",
        "퇴각로",
        "국인중",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 784 required terminology drifted")
    if any(term in joined for term in ("철수", "퇴로", "퇴각 지점", "호족")):
        raise RuntimeError("segment 784 retains a forbidden legacy term")
    if len(TRANSLATIONS) != 20:
        raise RuntimeError("segment 784 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S784",
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
