#!/usr/bin/env python3
"""Build Base authoring segment 733 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S733.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s733", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3766:0": "적이 요충지를 제압했군요\n요충지를 장악해 우위를 얻는 것이 합전의 요체\n자세히 설명해 드리겠습니다",
    "9:3767:0": "적의 퇴각로를 파괴하시다니 참으로 훌륭하옵니다!\n퇴각로를 장악하는 자가 싸움을 지배합니다\n설명은 제게 맡겨 주십시오",
    "9:3768:0": "퇴각로를 파괴당했습니까, 적도 제법이군요\n퇴각로를 장악하는 자가 싸움을 지배합니다\n설명은 제게 맡겨 주십시오",
    "9:3769:0": "주군의 명령을 받은 전령이\n부대를 향해 출발했군요\n전령들의 역할을 설명해 드리겠사옵니다",
    "9:3770:0": "선봉 부대가 전투를 시작했군요!\n싸움에서는 아군이 무너지지 않은 채 적진을 무너뜨려야 합니다\n부대 통제에 관해 설명해 드리겠습니다",
    "9:3771:0": "슬슬 부대에 지시를 내리실 때로군요\n합전에서 어떻게 명령을 내리면 되는지\n설명은 제게 맡겨 주십시오",
    "9:3772:0": "이렇게 우세한데 강화를 맺으라니…?\n",
    "9:3772:1": "쓰노쿠마",
    "9:3772:2": " 님은 지나치게 소극적이다!",
    "9:3773:0": "이리된 이상, 우리가 선봉에 서서\n무리해서라도 싸움을 시작할 수밖에 없다",
    "9:3774:0": "다키타",
    "9:3774:1": "와 ",
    "9:3774:2": "사이키",
    "9:3774:3": "가 멋대로 출진했다고…!?\n강화도, 오토모도 망칠 셈인가…!",
    "9:3775:0": "도시히사",
    "9:3775:1": "의 말대로다\n",
    "9:3775:2": "오토모",
    "9:3775:3": "군은 일부만 나왔구나",
    "9:3776:0": "강화 사절이 효과를 냈군요\n방침을 두고 서로 반목한 모양입니다",
    "9:3777:0": "계획대로 츠리노부세를 펼친다\n",
    "9:3777:1": "오토모",
    "9:3777:2": "의 선봉을 유인해 복병으로 친다",
}

STATIC_COORDINATES = set(TRANSLATIONS)
DYNAMIC_RUNTIME_COORDINATES: set[str] = set()
COLOR_CONTROL_GAPS: dict[int, tuple[bytes, ...]] = {
    3772: (b"", b"\x1bC1", b"\x1bCZ", b"\x05\x05\x05"),
    3774: (b"\x1bC1", b"\x1bCZ", b"\x1bC1", b"\x1bCZ", b"\x05\x05\x05"),
    3775: (b"\x1bC1", b"\x1bCZ", b"\x1bC3", b"\x1bCZ", b"\x05\x05\x05"),
    3777: (b"", b"\x1bC3", b"\x1bCZ", b"\x05\x05\x05"),
}


def record_gaps(record: Any) -> tuple[bytes, ...]:
    gaps: list[bytes] = []
    cursor = 0
    for literal in ENGINE.parse_record_literals(record):
        gaps.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    pristine_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    for record_id, expected_gaps in COLOR_CONTROL_GAPS.items():
        if (
            record_gaps(pristine_records[(9, record_id)]) != expected_gaps
            or record_gaps(current_records[(9, record_id)]) != expected_gaps
        ):
            raise RuntimeError(f"color-control skeleton drift: 9:{record_id}")
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
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_exact_pk_record_context_where_available"
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
                "segment": "base_msggame_B001_S733",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": 0,
                "confirmed_non_display": 0,
                "color_control_record_count": len(COLOR_CONTROL_GAPS),
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
