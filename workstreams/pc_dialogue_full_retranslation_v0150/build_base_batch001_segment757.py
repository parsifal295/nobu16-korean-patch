#!/usr/bin/env python3
"""Build Base authoring segment 757 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S757.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s757", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TIME_BUTTON_LITERAL_0 = "왼쪽 위의 시간 진행 버튼(또는"
TIME_BUTTON_LITERAL_1 = ")"
TRANSLATIONS: dict[str, str] = {
    "13:262:0": '"조략"',
    "13:263:0": "다른 세력에 조략을 실행하면\n전투와 외교를 유리하게 이끌 수 있습니다.\n적대 세력에 사용해 봅시다.",
    "13:264:0": " > 군사 > 조략",
    "13:265:0": "다른 세력에 조략을 실행해 봅시다\n적의 손해는 곧 우리의 이익입니다",
    "13:266:0": "기본 사항",
    "13:267:0": "게임 진행 방법과 각종 도움말 등\n기초 내용을 간단히 설명합니다\n",
    "13:268:0": "기본 사항",
    "13:269:0": "게임 진행 방법과 각종 도움말 등\n기초 내용을 간단히 설명합니다\n",
    "13:270:0": '"군 개발"-시간 진행-',
    "13:271:0": "시간 진행 버튼을 누르면 세월이 흐르고,\n임무가 시작됩니다.\n시간을 진행해 군 개발 완료를 기다립시다.",
    "13:272:0": TIME_BUTTON_LITERAL_0,
    "13:272:1": TIME_BUTTON_LITERAL_1,
    "13:273:0": '군 개발을 명하셨군요\n"시간 진행"을 눌러\n경과를 지켜봅시다',
    "13:274:0": '"지행"-시간 진행-',
    "13:275:0": "영주는 자율적으로 군을 개발합니다.\n시간을 진행해 상황을 지켜봅시다.",
    "13:276:0": TIME_BUTTON_LITERAL_0,
    "13:276:1": TIME_BUTTON_LITERAL_1,
    "13:277:0": '지행지를 내리셨군요\n왼쪽 위의 "시간 진행" 버튼을 눌러\n영주의 활약을 지켜봅시다',
    "13:278:0": "시간 진행",
    "13:279:0": "공략 목표가 정해지면 자신의 영지 개발을 멈추고\n군비와 조략을 시작합니다. 군비가 완료되면 성의\n아이콘과 로그로 알림이 표시됩니다",
    "13:280:0": TIME_BUTTON_LITERAL_0,
    "13:280:1": TIME_BUTTON_LITERAL_1,
    "13:281:0": '자, 잠시 경과를\n지켜보도록 하지요\n"시간 진행"을 눌러 주시오',
}

RUNTIME_RECORD_IDS = {264, 272, 276, 280}
DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in RUNTIME_RECORD_IDS
}
EXPECTED_GAPS = {
    264: (b"\x02\x3c", b"\x05\x05\x05"),
    272: (b"", b"\x02\x3c", b"\x05\x05\x05"),
    276: (b"", b"\x02\x3c", b"\x05\x05\x05"),
    280: (b"", b"\x02\x3c", b"\x05\x05\x05"),
}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）")
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
    if 229 <= base_record_id <= 269:
        return base_record_id + 2
    if 270 <= base_record_id <= 272:
        return base_record_id + 18
    if 273 <= base_record_id <= 276:
        return base_record_id + 19
    if 277 <= base_record_id <= 280:
        return base_record_id + 20
    if base_record_id == 281:
        return base_record_id + 21
    raise RuntimeError(f"segment 757 record has no configured PK mapping: {base_record_id}")


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
            for record_id in range(262, 282)
            if [literal.text for literal in ENGINE.parse_record_literals(base_records[(13, record_id)])]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(13, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences != {263}:
            raise RuntimeError(
                f"segment 757 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    for record_id, expected in EXPECTED_GAPS.items():
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current literal/opcode boundary drifted: 13:{record_id}")
    literal_264 = ENGINE.parse_record_literals(current_records[(13, 264)])[0]
    if ENGINE.protected_signature(literal_264.text)["leading_whitespace"] != " ":
        raise RuntimeError("13:264:0 must preserve one leading ASCII space")
    for record_id in (267, 269):
        literal = ENGINE.parse_record_literals(current_records[(13, record_id)])[0]
        if ENGINE.protected_signature(literal.text)["trailing_whitespace"] != "\n":
            raise RuntimeError(f"13:{record_id}:0 must preserve one trailing LF")
    for duplicate_ids in ((228, 272, 276, 280), (266, 268), (267, 269)):
        if len({source_records[(13, record_id)].data for record_id in duplicate_ids}) != 1:
            raise RuntimeError(f"pristine Base raw duplicate drifted: {duplicate_ids}")
        if len({current_records[(13, record_id)].data for record_id in duplicate_ids}) != 1:
            raise RuntimeError(f"current Base raw duplicate drifted: {duplicate_ids}")
    for translation in TRANSLATIONS.values():
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError("segment 757 must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 757 retains banned fullwidth punctuation")
    if "전투와 외교" not in TRANSLATIONS["13:263:0"]:
        raise RuntimeError("13:263 must follow Base JP and retain both combat and diplomacy")
    if TRANSLATIONS["13:266:0"] != TRANSLATIONS["13:268:0"]:
        raise RuntimeError("13:266=13:268 translation duplicate drifted")
    if TRANSLATIONS["13:267:0"] != TRANSLATIONS["13:269:0"]:
        raise RuntimeError("13:267=13:269 translation duplicate drifted")
    expected_time_button_pair = (
        "왼쪽 위의 시간 진행 버튼(또는",
        ")",
    )
    for record_id in (272, 276, 280):
        actual = (
            TRANSLATIONS[f"13:{record_id}:0"],
            TRANSLATIONS[f"13:{record_id}:1"],
        )
        if actual != expected_time_button_pair:
            raise RuntimeError(f"13:{record_id} time-button duplicate translation drifted")
    if "지행지" not in TRANSLATIONS["13:277:0"] or '"지행"' not in TRANSLATIONS["13:274:0"]:
        raise RuntimeError("13:274/277 must distinguish 知行=지행 and 知行地=지행지")
    if "자신의 영지" not in TRANSLATIONS["13:279:0"]:
        raise RuntimeError("13:279 must use ordinary-prose 自領=자신의 영지")
    if len(TRANSLATIONS) != 23 or len(DYNAMIC_RUNTIME_COORDINATES) != 7:
        raise RuntimeError("segment 757 decision/classification count drifted")


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
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
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
                "segment": "base_msggame_B001_S757",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
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
