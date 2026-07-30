#!/usr/bin/env python3
"""Build Base authoring segment 749 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S749.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s749", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:114:0": '게다가 이 "',
    "13:114:1": '"은(는) 지략에도 자신이\n',
    "13:114:2": "조략이나 외교 등\n능한 분야에서 재능을 발휘하고 싶습니다…",
    "13:115:0": '또한 영토의 발전을 생각하신다면\n정무에 능한 이 "',
    "13:115:1": '"의 재능이\n반드시 도움이 될 날이 오',
    "13:116:0": "다만… 각 분야의 능력에는 딱히\n내세울 만한 것이 없으나\n특성의 힘으로 활약해 보이겠습니다",
    "13:117:0": "통솔력이 뛰어난 인물이라면 우선\n",
    "13:117:1": "의 이름이 떠오르",
    "13:117:2": "\n군의 발전이나 전투 때에는 든든한 힘이 될 터…",
    "13:118:0": "무용이 뛰어난 가신이라면 우선\n",
    "13:118:1": "\n우리 가문에서 가장 뛰어난 전투의 달인이라 생각하",
    "13:119:0": '우리 가문 최고의 지략가라면 "',
    "13:119:1": '"님 말고는\n달리 없',
    "13:119:2": "\n조략과 외교에서 재능을 발휘해 줄 터…",
    "13:120:0": '영토의 발전을 생각하신다면\n정무에 능한 "',
    "13:120:1": '"님을\n내정의 기둥으로 삼는 것이 중요합니다',
    "13:121:0": "유용한 특성도 갖춘 인물이니\n적극적으로 활용하는 것이 좋겠습니다",
    "13:122:0": "특별한 특성은 없으나\n능력을 살릴 수 있는 곳에 배치한다면\n반드시 활약할 수 있을 것입니다",
    "13:123:0": "외람되오나 이",
    "13:123:1": "\n통솔력만큼은 누구에게도 뒤지지 않",
    "13:123:2": "\n군을 발전시키거나 전투를 치를 때에도 믿고 맡겨",
    "13:124:0": "무용이라면 누구에게도 뒤지지 않",
    "13:124:1": '\n전투에서는 이 "',
    "13:124:2": '"에게 선봉의 소임을',
    "13:124:3": "\n적을 무찔러 보이",
}

RUNTIME_RECORD_IDS = {114, 115, 117, 118, 119, 120, 123, 124}
DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in RUNTIME_RECORD_IDS
}
EXPECTED_RUNTIME_GAPS = {
    114: (b"", b"\x02\x46\x35", b"\x01\x43\x5e\x00\x00\x00", b"\x05\x05\x05"),
    115: (b"", b"\x02\x46\x35", b"\x01\x43\x1e\x04\x00\x00\x05\x05\x05"),
    117: (b"", b"\x02\x48\x33", b"\x01\x43\x5a\x04\x00\x00", b"\x05\x05\x05"),
    118: (b"", b"\x02\x48\x33\x01\x43\x56\x02\x00\x00", b"\x05\x05\x05"),
    119: (b"", b"\x02\x48\x33", b"\x01\x43\x2a\x04\x00\x00", b"\x05\x05\x05"),
    120: (b"", b"\x02\x48\x33", b"\x05\x05\x05"),
    123: (
        b"",
        b"\x02\x46\x35",
        b"\x01\x43\x2a\x04\x00\x00",
        b"\x01\x43\x42\x01\x00\x00\x05\x05\x05",
    ),
    124: (
        b"",
        b"\x01\x43\x2a\x04\x00\x00",
        b"\x02\x46\x35",
        b"\x01\x43\x7c\x03\x00\x00",
        b"\x01\x43\x1e\x04\x00\x00\x05\x05\x05",
    ),
}
EXPECTED_MERGED_LITERAL_COUNTS = {
    116: (2, 1),
    122: (2, 1),
}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」")


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def assert_scope(prepared: Any) -> None:
    source_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    for record_id, expected in EXPECTED_RUNTIME_GAPS.items():
        if record_gaps(source_records[(13, record_id)]) != expected:
            raise RuntimeError(f"pristine runtime skeleton drifted: 13:{record_id}")
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current runtime skeleton drifted: 13:{record_id}")
    for record_id, expected in EXPECTED_MERGED_LITERAL_COUNTS.items():
        actual = (
            len(ENGINE.parse_record_literals(source_records[(13, record_id)])),
            len(ENGINE.parse_record_literals(current_records[(13, record_id)])),
        )
        if actual != expected:
            raise RuntimeError(f"merged-literal authority drifted at 13:{record_id}: {actual}")
        if record_gaps(current_records[(13, record_id)]) != (b"", b"\x05\x05\x05"):
            raise RuntimeError(f"merged current record retains an unexpected opcode: 13:{record_id}")
    if len(TRANSLATIONS) != 25 or len(DYNAMIC_RUNTIME_COORDINATES) != 22:
        raise RuntimeError("segment 749 visible/static-runtime counts drifted")
    for translation in TRANSLATIONS.values():
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError("segment 749 must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 749 retains banned fullwidth punctuation")


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
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_same_coordinate_pk_jp_en_sc_tc_context_where_available"
                ),
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
                "segment": "base_msggame_B001_S749",
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
