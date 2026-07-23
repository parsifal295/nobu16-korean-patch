#!/usr/bin/env python3
"""Build Base authoring segment 764 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S764.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s764", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:409:0": '"튜토리얼"-고쇼의 건의-',
    "13:410:0": '고쇼의 진언은 "건의"로 화면 왼쪽 목록에 표시됩니다.\n게임 초반에는 안내되는 내용에 따라 진행해 봅시다.\n\n※고쇼의 건의에는',
    "13:410:1": " ┨ ",
    "13:410:2": '아이콘이 표시됩니다\n※튜토리얼이 필요 없다면 "설정"에서 변경할 수 있습니다',
    "13:411:0": '고쇼의 진언은 "건의"로 화면 왼쪽 목록에 표시됩니다.\n게임 초반에는 안내되는 내용에 따라 진행해 봅시다.\n\n※고쇼의 건의에는',
    "13:411:1": " ┨ ",
    "13:411:2": '아이콘이 표시됩니다\n※튜토리얼이 필요 없다면 "설정"에서 변경할 수 있습니다\n※목록은 ㍍를 누른 채 ㌣로 선택할 수 있습니다',
    "13:412:0": "건의에는 몇 가지 종류가 있습니다.\n\n·고쇼의 건의 …\u3000",
    "13:412:1": "┨",
    "13:412:2": "\u3000튜토리얼에서 다음에 할 일을 건의한다\n·조언 …\u3000",
    "13:412:3": "┯",
    "13:412:4": "\u3000상황에 따라 지금 해야 할 일을 건의한다\n·일반 건의 … 가신이 필요하다고 판단한 일을 건의한다\n금전이나 노동력이 필요하며 실패할 수도 있다\n·세력 목표 건의 … 현재 설정된 세력 목표를 표시한다",
    "13:413:0": '"게임의 흐름"',
    "13:414:0": "지행, 내정, 전투의 기초를 설명했으니 내용을 정리하겠습니다.\n앞으로 가신이 본격적으로 건의와 조언을 올리므로 활용해 주십시오.\n튜토리얼은 더 남았지만 게임을 진행할 준비는 갖추었습니다.\n배운 내용을 활용해 천하통일을 목표로 합시다!\n\n[정리: 천하통일을 목표로 하려면]\n·지행과 내정으로 세력을 강화한다\n·적의 성을 제압해 영토를 넓힌다",
    "13:415:0": '[정리: 내정]\n·"지행"과 "대관"으로 자신의 영지 내정을 가신에게 맡긴다\n·"군 개발", "성하 시설", "정책"으로 세력을 강화한다',
    "13:416:0": '[정리: 외교와 군략]\n·"친선"으로 다른 가문과의 관계를 개선한다\n·"출진"해 적의 성을 제압하고 영토를 넓힌다\n\n[무엇을 해야 할지 모르겠다면]\n·화면 오른쪽 위 메뉴의 "헌언"에서 가신에게 묻는다',
    "13:417:0": '"임전 상태 표시"',
    "13:418:0": "준비 성에는 임전 상태인 군의 수가 표시되며\n모든 군이 임전 상태가 되면 아이콘 색이 바뀝니다.\n※성대와 군다이가 맡은 군은 임전 상태가 되지 않습니다\n\n임전 상태인 군이 많을수록 부대가 강화되어 오래 출진할 수 있지만\n모든 군이 임전 상태가 되기 전에도 출진할 수 있습니다.",
    "13:419:0": '"독단 출진"',
    "13:420:0": "인접한 성 사이에서 소규모 접전이 벌어지면\n성주는 독단으로 출진하기도 합니다.\n위험한 상황이라면 원군을 보냅시다.",
    "13:421:0": "[소규모 접전이 발생하면]\n·성의 지략이 낮거나 특정 특성이 있으면 독단으로 출진한다\n·그 외에는 출진 전에 허가를 구한다\n·독단 출진한 부대는 목표 성을 함락할 때까지 명령을 듣지 않는다",
    "13:422:0": '"조정의 사자"',
}

EXPECTED_GAPS = {
    410: (b"", b"\x1b\x43\x50", b"\x1b\x43\x5a", b"\x05\x05\x05"),
    411: (b"", b"\x1b\x43\x50", b"\x1b\x43\x5a", b"\x05\x05\x05"),
    412: (
        b"",
        b"\x1b\x43\x50",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x50",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）【】")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
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
    if 409 <= base_record_id <= 415:
        return base_record_id + 35
    if 416 <= base_record_id <= 422:
        return base_record_id + 36
    raise RuntimeError(f"segment 764 record has no configured PK mapping: {base_record_id}")


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
    expected_divergences = {
        "JP": {416, 418},
        "SC": {412, 418},
        "TC": {412, 415, 418},
    }
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(409, 423)
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
        if divergences != expected_divergences[language]:
            raise RuntimeError(
                f"segment 764 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    for record_id, expected in EXPECTED_GAPS.items():
        if record_gaps(source_records[(13, record_id)]) != expected:
            raise RuntimeError(f"pristine literal/color boundary drifted: 13:{record_id}")
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current literal/color boundary drifted: 13:{record_id}")
    for record_id in (410, 411):
        literal = TRANSLATIONS[f"13:{record_id}:1"]
        if literal[:1] != " " or literal[-1:] != " " or len(literal) != 3:
            raise RuntimeError(f"13:{record_id}:1 must preserve one ASCII space at each edge")
    u3000_counts = {
        coordinate: translation.count("\u3000")
        for coordinate, translation in TRANSLATIONS.items()
        if "\u3000" in translation
    }
    if u3000_counts != {"13:412:0": 1, "13:412:2": 2, "13:412:4": 1}:
        raise RuntimeError(f"segment 764 U+3000 scope drifted: {u3000_counts}")
    for translation in TRANSLATIONS.values():
        if "\r" in translation:
            raise RuntimeError("segment 764 must not add CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 764 retains banned fullwidth punctuation")
    if "고쇼의 진언" not in TRANSLATIONS["13:410:0"] or '"건의"' not in TRANSLATIONS["13:410:0"]:
        raise RuntimeError("13:410 must distinguish 小姓/進言/具申")
    if "노동력" not in TRANSLATIONS["13:412:4"]:
        raise RuntimeError("13:412 must retain 労力=노동력")
    if '"헌언"' not in TRANSLATIONS["13:416:0"]:
        raise RuntimeError("13:416 must retain 献言=헌언")
    if "준비 성" not in TRANSLATIONS["13:418:0"] or "군비 거점" in TRANSLATIONS["13:418:0"]:
        raise RuntimeError("13:418 must follow Base 準備城 authority")
    if any(term in "\n".join(TRANSLATIONS.values()) for term in ("자동 임명", "전마제")):
        raise RuntimeError("segment 764 imported a PK-only explanation")
    if len(TRANSLATIONS) != 22:
        raise RuntimeError("segment 764 decision count drifted")


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
                "segment": "base_msggame_B001_S764",
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
