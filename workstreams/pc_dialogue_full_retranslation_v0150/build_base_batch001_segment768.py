#!/usr/bin/env python3
"""Build Base authoring segment 768 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S768.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s768", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:493:0": '"천하 평정"',
    "13:494:0": (
        "기나이를 포함한 전국 과반수의 성을 지배하에 두어 천하 평정을 달성하면\n"
        "삼직 추임 엔딩을 맞이할 수 있습니다.\n"
        "\n"
        "[삼직 추임 엔딩 조건]\n"
        "·전국 과반수의 성을 지배하에 둔다\n"
        "·기나이(야마시로, 야마토, 가와치, 이즈미, 셋쓰)의 모든 성을\n"
        "  지배하에 둔다"
    ),
    "13:495:0": '"완전 제패"',
    "13:496:0": (
        "완전 제패에는 두 가지 방법이 있습니다.\n"
        "달성 방법에 따라 각각의 엔딩을 맞이합니다.\n"
        "\n"
        "◆전국 통일\n"
        " 모든 성을 자세력만으로 지배하면 달성한다\n"
        "◆종속 통일\n"
        " 전국 과반수의 성을 지배하고\n"
        " 남은 모든 적 세력을 종속시키면 달성한다"
    ),
    "13:497:0": (
        "[전국 통일 엔딩 조건]\n"
        "·일본 전국의 모든 성을 지배하에 둔다\n"
        "\n"
        "[종속 통일 엔딩 조건]\n"
        "·전국 과반수의 성을 지배하에 둔다\n"
        "·자세력 이외의 모든 다이묘 가문을 종속시킨다"
    ),
    "13:498:0": '"군 제압"',
    "13:499:0": (
        "출진 중인 부대가 군 제압을 시작했습니다.\n"
        "\n"
        "[군 제압 규칙]\n"
        "·적의 영지에 도달하면 그 군을 제압하기 시작한다\n"
        "·부대는 제압이 끝날 때까지 군에 머문다\n"
        "·제압한 군은 자세력의 영지가 된다\n"
        "·제압 완료까지 일정한 시간이 걸린다\n"
    ),
    "13:500:0": '"부대와 교전"',
    "13:501:0": (
        "출진 중인 부대가 적 부대와 접촉했습니다.\n"
        "\n"
        "[교전 규칙]\n"
        "·적 부대와 접촉하면 교전이 시작된다\n"
        "·교전 중에는 부대 능력에 따라 병력이 감소한다\n"
        "·병력이 0이 되면 부대가 괴멸한다\n"
        "·교전이 끝날 때까지 부대는 그 자리에 머문다"
    ),
    "13:502:0": '"시나리오와 세력"',
    "13:503:0": (
        "게임을 시작하려면 먼저 시나리오와 세력을 선택합니다.\n"
        "원하는 시나리오와 세력을 선택해 주십시오.\n"
        "\n"
        "무엇을 선택할지 고민된다면\n"
        '시나리오 "'
    ),
    "13:503:1": "오케하자마 전투",
    "13:503:2": '"의 "',
    "13:503:3": "오다 가문",
    "13:503:4": '"\n조합을 추천합니다.',
    "13:504:0": '"제도 개신 LV1"',
    "13:505:0": (
        '정책 "제도 개신"을 발령하여 "성하 방침"을 설정할 수 있게 되었습니다.\n'
        "성하 방침을 정하면 성주가 자율적으로 성하 시설을 건설합니다.\n"
        '성하 방침은 "성하 시설" 명령에서 설정할 수 있습니다.\n'
        "\n"
        "[해금된 내용]\n"
        "·성하 방침"
    ),
    "13:506:0": '"금전 수입 증가"',
    "13:507:0": (
        "금전 수입을 늘리는 방법은 익히셨습니까?\n"
        "금전은 여러 명령에 필요합니다.\n"
        "금전이 부족하여 명령을 실행하기 어렵다면\n"
        "수입 증가를 목표로 삼는 것이 좋습니다.\n"
        "\n"
        "[금전 수입을 늘리는 법]\n"
        "·각 성의 상업을 높인다\n"
        "·정무가 높은 무장을 영주나 대관으로 임명한다"
    ),
    "13:508:0": (
        "금전 수입을 효율적으로 늘리려면 여러 명령을 동시에\n"
        "실행하는 것이 중요하므로 많은"
    ),
    "13:508:1": "㈹노동력",
    "13:508:2": "이 필요합니다.\n",
    "13:508:3": "㈹노동력",
    "13:508:4": (
        "은 석고에 따라 늘릴 수 있습니다.\n"
        "\n"
        "[석고를 높이려면]\n"
        '·"군 개발"로 농촌을 장악한다\n'
        '·"성하 시설"로 관개 수로를 건설한다 등'
    ),
}

EXPECTED_GAPS = {
    503: (
        b"",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
    508: (
        b"",
        b"\x1b\x43\x52",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x52",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
}
BASE_PK_DIVERGENCES = {
    "JP": {496, 501},
    "SC": {496, 501, 503},
    "TC": {494, 496, 497, 501, 503},
}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）【】")
CONTROLLER_GLYPHS = set("㍑㌍㌦㍗㍍㎝㌣㌘㊤㊥㈲㈹")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def mapped_pk_record_id(base_record_id: int) -> int:
    if 493 <= base_record_id <= 508:
        return base_record_id + 44
    raise RuntimeError(f"segment 768 record has no configured PK mapping: {base_record_id}")


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in CONTROLLER_GLYPHS]


def prior_translation(coordinate: str) -> str:
    for decision_path in sorted(OUTPUT.parent.glob("base_msggame_B001_S*.private.v1.jsonl")):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate:
                return str(row["translation"])
    raise RuntimeError(f"prior exact translation is absent: {coordinate}")


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
            for record_id in range(493, 509)
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(13, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(13, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences != BASE_PK_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 768 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    for record_id, expected in EXPECTED_GAPS.items():
        if record_gaps(source_records[(13, record_id)]) != expected:
            raise RuntimeError(f"pristine literal/opcode boundary drifted: 13:{record_id}")
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current literal/opcode boundary drifted: 13:{record_id}")

    for record_id in range(493, 509):
        expected_arity = 5 if record_id in EXPECTED_GAPS else 1
        source_literals = ENGINE.parse_record_literals(source_records[(13, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(13, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 768 literal arity drifted: 13:{record_id}")

    for coordinate, translation in TRANSLATIONS.items():
        _, record_text, literal_text = coordinate.split(":")
        record_id = int(record_text)
        literal_id = int(literal_text)
        current_text = ENGINE.parse_record_literals(current_records[(13, record_id)])[literal_id].text
        if translation.count("\n") != current_text.count("\n"):
            raise RuntimeError(f"{coordinate} line-count contract drifted")
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError(f"{coordinate} must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")
        if glyph_skeleton(translation) != glyph_skeleton(current_text):
            raise RuntimeError(f"{coordinate} controller-glyph skeleton drifted")

    source_508 = ENGINE.parse_record_literals(source_records[(13, 508)])
    current_508 = ENGINE.parse_record_literals(current_records[(13, 508)])
    for prior_record_id, prior_literal_id in ((298, 3), (302, 2)):
        source_prior = ENGINE.parse_record_literals(source_records[(13, prior_record_id)])
        current_prior = ENGINE.parse_record_literals(current_records[(13, prior_record_id)])
        if source_508[1].text != source_prior[prior_literal_id].text:
            raise RuntimeError(
                f"pristine exact labour literal drifted: 13:508:1 != 13:{prior_record_id}:{prior_literal_id}"
            )
        if current_508[1].text != current_prior[prior_literal_id].text:
            raise RuntimeError(
                f"current exact labour literal drifted: 13:508:1 != 13:{prior_record_id}:{prior_literal_id}"
            )
    if source_508[1].text != source_508[3].text or current_508[1].text != current_508[3].text:
        raise RuntimeError("13:508 duplicated labour literals drifted")
    approved_labour = prior_translation("13:298:3")
    if approved_labour != prior_translation("13:302:2"):
        raise RuntimeError("prior approved labour literal translations differ")
    if [TRANSLATIONS[f"13:508:{literal_id}"] for literal_id in (1, 3)] != [
        approved_labour,
        approved_labour,
    ]:
        raise RuntimeError("13:508 must exactly reuse the approved labour glyph literal")
    assembled_508 = "".join(TRANSLATIONS[f"13:508:{literal_id}"] for literal_id in range(5))
    expected_assembled_508 = (
        "금전 수입을 효율적으로 늘리려면 여러 명령을 동시에\n"
        "실행하는 것이 중요하므로 많은㈹노동력이 필요합니다.\n"
        "㈹노동력은 석고에 따라 늘릴 수 있습니다.\n"
        "\n"
        "[석고를 높이려면]\n"
        '·"군 개발"로 농촌을 장악한다\n'
        '·"성하 시설"로 관개 수로를 건설한다 등'
    )
    if assembled_508 != expected_assembled_508:
        raise RuntimeError("13:508 assembled visible sentence drifted")
    if "사형" in TRANSLATIONS["13:501:0"] or "처형" in TRANSLATIONS["13:501:0"]:
        raise RuntimeError("13:501 imported the PK-only death sentence")
    if "◆전국 통일" not in TRANSLATIONS["13:496:0"] or "◆종속 통일" not in TRANSLATIONS["13:496:0"]:
        raise RuntimeError("13:496 must retain the Base JP branch markers")
    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "천하 평정",
        "삼직 추임",
        "전국 통일",
        "종속 통일",
        "군",
        "영지",
        "제도 개신",
        "성하 방침",
        "노동력",
        "석고",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 768 required terminology drifted")
    if "노력" in joined:
        raise RuntimeError("segment 768 retains a forbidden legacy term")
    if len(TRANSLATIONS) != 24:
        raise RuntimeError("segment 768 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S768",
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
