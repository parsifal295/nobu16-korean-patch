#!/usr/bin/env python3
"""Build Base authoring segment 748 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S748.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s748", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:105:0": '가신 중에서는 "',
    "13:105:1": '"에게\n',
    "13:105:2": "이라는 특성이",
    "13:105:3": "\n믿음직한 인재라 할 수 있습니다",
    "13:106:0": "또한 통솔력이 뛰어나므로\n군을 발전시키거나 전투를 치를 때에도 도움이 될 것입니다",
    "13:107:0": "또한 무용이 뛰어난 무장이니\n전투에서는 선봉에 서서 적을 쓰러뜨려\n주었으면 하오",
    "13:108:0": "또한 지략가로도 이름나 있으므로\n조략과 외교 분야에서 그 재능을\n발휘할 수 있을 것입니다",
    "13:109:0": "또한 정무에 능하므로\n영지의 발전을 위해 내정의 핵심으로\n활약하게 하는 것도 좋겠습니다",
    "13:110:0": "다만 특기할 만한 능력은 없으나\n특성을 살려 활약해 주기를 바란다",
    "13:111:0": '불초 소인은 "',
    "13:111:1": '"이라는\n특성을 지니고 있으니\n믿고 맡겨 주십시오!',
    "13:112:0": "또한 외람되오나 이",
    "13:112:1": "\n통솔력만큼은 자신이",
    "13:112:2": "\n군을 발전시키거나 전투를 치를 때에도 믿고 맡겨",
    "13:113:0": "무용만큼은 자신이",
    "13:113:1": '\n전투에서는 이 "',
    "13:113:2": '"에게 선봉의 소임을',
    "13:113:3": "\n적을 무찔러 보이",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {105, 111, 112, 113}
}
EXPECTED_CURRENT_GAPS = {
    105: (
        b"",
        b"\x02\x48\x33",
        b"\x1b\x43\x49\x02\x3c\x1b\x43\x5a",
        b"\x01\x43\x5e\x00\x00\x00",
        b"\x05\x05\x05",
    ),
    111: (b"", b"\x1b\x43\x49\x02\x3c\x1b\x43\x5a", b"\x05\x05\x05"),
    112: (
        b"",
        b"\x02\x46\x35",
        b"\x01\x43\x52\x00\x00\x00",
        b"\x01\x43\x42\x01\x00\x00\x05\x05\x05",
    ),
    113: (
        b"",
        b"\x01\x43\x5e\x00\x00\x00",
        b"\x02\x46\x35",
        b"\x01\x43\x7c\x03\x00\x00",
        b"\x01\x43\x1e\x04\x00\x00\x05\x05\x05",
    ),
}


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def assert_runtime_scope(prepared: Any) -> None:
    source_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    for record_id, expected in EXPECTED_CURRENT_GAPS.items():
        if record_gaps(source_records[(13, record_id)]) != expected:
            raise RuntimeError(f"pristine literal/opcode boundary drifted: 13:{record_id}")
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current literal/opcode boundary drifted: 13:{record_id}")
    for record_id in range(106, 111):
        expected = (b"", b"\x05\x05\x05")
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"expected a merged current literal without live opcodes: 13:{record_id}")
    for record_id in (108, 110):
        source_count = len(ENGINE.parse_record_literals(source_records[(13, record_id)]))
        current_count = len(ENGINE.parse_record_literals(current_records[(13, record_id)]))
        if (source_count, current_count) != (2, 1):
            raise RuntimeError(f"merged-literal authority drifted: 13:{record_id}")
    if len(TRANSLATIONS) != 18:
        raise RuntimeError("segment 748 must contain exactly 18 visible decisions")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_runtime_scope(prepared)
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
                "segment": "base_msggame_B001_S748",
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
