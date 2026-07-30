#!/usr/bin/env python3
"""Build Base authoring segment 695 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S695.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s695", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3022:0": "퇴각로에 적이라고!?\n말머리를 돌려라!　쳐부순다!",
    "9:3023:0": "퇴각로의 적군을\n무찔러야 합니다!",
    "9:3024:0": "퇴각로에 적군이!?\n되돌아간다!　서둘러라!",
    "9:3025:0": "거슬리는 사격이군…\n고지의 적을 제압하러 간다!",
    "9:3026:0": "궁지에 몰리기 전에\n고지의 적을 제거하라!",
    "9:3027:0": "적에게 사격할 틈을 주지 마라\n고지의 적을 치리라!",
    "9:3028:0": "공격이 격렬합니다…\n고지를 빼앗으러 가겠습니다",
    "9:3029:0": "고지를 장악하지 않으면\n제대로 싸울 수 없겠군",
    "9:3030:0": "일방적으로 사격당해서야\n고지를 빼앗을 수밖에 없겠군",
    "9:3031:0": "고지를 탈취하라\n피해를 막아 내는 것이다",
    "9:3032:0": "제멋대로 쏴 대다니!\n고지의 적에게 되갚아 주마!",
    "9:3033:0": "이대로는 피해가 커집니다…\n고지를 차지하러 가겠습니다",
    "9:3034:0": "죽음만 기다리지 마라\n고지의 적을 친다!",
    "9:3035:0": "피해를 막기 위해\n고지를 빼앗으러 가겠습니다",
    "9:3036:0": "위에서 사격당해서는 싸울 수 없다\n고지의 적을 공격한다!",
    "9:3037:0": "사격을 받아서는 나아갈 수 없다!\n어쩔 수 없군, 물러나라!",
    "9:3038:0": "이렇게 사격당해서는 나아갈 수 없다\n일단 물러날까…",
    "9:3039:0": "잠시 후퇴하라!\n화살과 탄환이 닿지 않는 곳으로",
    "9:3040:0": "사격이 닿지 않는 곳으로\n후퇴하도록 하지요",
    "9:3041:0": "계속 맞고만 있을 수는 없으니\n물러날 수밖에 없겠군…",
    "9:3042:0": "여기서는 표적이 될 뿐이다\n후방으로 물러나자",
    "9:3043:0": "이렇게 사격당해서야…\n후퇴해야 하겠군",
}

DYNAMIC_RUNTIME_COORDINATES: set[str] = set()
STATIC_COORDINATES = set(TRANSLATIONS)


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required" if static else "pending",
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available"
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
                "segment": "base_msggame_B001_S695",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
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
