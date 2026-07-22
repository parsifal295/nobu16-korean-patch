#!/usr/bin/env python3
"""Build Base authoring segment 28 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S28.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s28", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "4:38:0": "【튜토리얼 표시】\n게임 중 튜토리얼 표시 여부를\n설정합니다\n",
    "4:38:1": "※시나리오 시작 후에는 [있음]으로\n변경할 수 없습니다",
    "4:38:2": "\n\n[있음] / [없음]",
    "4:39:0": "【임시 로그 표시】\n화면 중앙에 일시적으로 표시되는\n로그를 설정합니다\n\n[모두 표시]\n모든 범주의 로그를 표시합니다\n\n[모두 숨김]\n모든 범주의 로그를 숨깁니다\n\n[사용자 지정]\n지정한 범주의 로그만 표시합니다",
    "4:40:0": "[내정]\n정무와 건설에 관한 로그\n\n[군사]\n행군에 관한 로그\n\n[외교]\n타 세력과의 신용도에 관한 로그\n\n[조략]\n타 세력을 상대로 한 공작에 관한 로그\n\n[무장]\n무장의 상태와 지위에 관한 로그",
    "4:41:0": "【3D 커서 이동 속도】\n지도 위 3D 커서의 이동 속도를\n조절합니다\n\n[저속] / [중속] / [고속]\n3D 커서 이동 속도를 설정",
    "4:42:0": "【세력 목표】\n게임 진행 중 가신이 목표를 건의\n할지 설정합니다\n\n[있음]\n상황에 맞는 목표를 건의합니다\n달성하면 훈공을 획득합니다\n\n[없음]\n세력 목표를 건의하지 않습니다",
    "4:43:0": "【합전 연출 표시】\n합전 연출을 표시할지\n설정합니다\n\n[모두 표시]\n모든 연출을 표시\n\n[일부 표시]\n퇴각이나 궤멸 등 일부 연출만\n표시",
    "4:44:0": "【군단 상황 표시】\n군단 상황 보고를 행동 목록에\n표시할지 설정합니다\n\n[표시] / [숨김]",
    "4:45:0": "다음 가보가 들어왔습니다\n·",
    "4:45:1": "\n·",
    "4:45:2": "\n·",
    "4:46:0": "정책으로 인해 금전 수지가 적자입니다",
    "4:47:0": "정책 「",
    "4:47:1": "」을 실행할 수 있게 되었습니다",
    "4:48:0": "영주를 교체할 수 있게 되었습니다",
    "4:49:0": "성주를 교체할 수 있게 되었습니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {38, 45, 47}
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
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
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
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
                "segment": "base_msggame_B001_S28",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
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
