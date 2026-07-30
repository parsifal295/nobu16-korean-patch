#!/usr/bin/env python3
"""Build Base authoring segment 27 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S27.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s27", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "4:26:0": "【AI 호전도】\n타 세력의 호전도를 설정합니다\n높을수록 적국을 침공하기 쉬워집\n니다",
    "4:27:0": "【수명】\n무장의 수명을 설정합니다\n",
    "4:27:1": "※시나리오 시작 후에는 변경할 수 없습니다",
    "4:27:2": "\n\n[사실]\n사실에 따른 수명\n\n[장수]\n사실보다 긴 수명\n\n[없음]\n수명이 없어져 전사나 이벤트\n이외의 경우에는 사망하지 않음",
    "4:28:0": "【전사】\n무장이 전투에서 사망하는 빈도를\n설정합니다\n\n[적음] / [보통] / \n[많음] / [없음]",
    "4:29:0": "【무장명】\n무장명 표시 방식을 전환합니다\n\n[관용]\n관용적인 이름을 우선하여 표시\n\n[역사]\n역사상의 성명을 우선하여 표시\n\n예: (관용) 사나다 유키무라\n    (역사) 사나다 노부시게",
    "4:30:0": "【역사 이벤트】\n역사적 사건을 무장의 대화\n이벤트 등으로 발생시키는\n방식을 설정합니다\n\n[있음] / [없음]\n\n※이벤트에는 사실에 따른 것과\n 『노부나가의 야망·신생』\n 오리지널 이벤트가 있습니다\n※게임 내 이벤트 목록에서\n 개별적으로 설정할 수도 있습니다",
    "4:31:0": "【공주 무장】\n공주를 무장으로 등장시키도록 설정\n합니다\n 공주  …결연과 혼인 동맹 가능\n 공주 무장…공주의 역할에 더해\n     무장으로도 행동 가능\n",
    "4:31:1": "※시나리오 선택 전에만 변경 가능",
    "4:31:2": "\n\n[있음]\n모든 공주가 공주 무장으로 등장\n\n[없음]\n모든 공주가 공주로 등장",
    "4:32:0": "【가상 공주 출생】\n가상의 공주가 태어나도록 설정합니다\n※공주는 결연과 혼인 동맹에 필요합니다\n\n[있음] / [없음]",
    "4:33:0": "【조언】\n가신의 제안을 통해 지금 해야 할\n일을 안내받습니다\n※처음 플레이하는 분께 추천\n\n[있음] / [없음]",
    "4:34:0": "【자율 행동】\n부대가 출진할 때 모든 자율 행동을\n기본적으로 허가할지를\n설정합니다\n※부대별로 따로 설정 가능\n\n[허가]\n다음과 같은 행동을 무장이 판단해\n수행\n·목표 달성 후 가까운 성으로 귀환\n·둘로 나뉜 적의 한쪽을 공격\n·이길 수 없는 상대로부터 퇴각\n\n[금지]\n지시한 행동만 수행",
    "4:35:0": "【키 가이드】\n키 가이드 표시를 설정합니다\n\n[표시] / [숨김]",
    "4:36:0": "【카메라 조작】\n카메라 조작 방식을 설정합니다\n\n[정방향] / [반전]",
    "4:37:0": "【외교 초기 상태】\n동맹이나 종속 등 사실에 따른 외\n교 관계를 맺고 시작할지를\n선택합니다\n",
    "4:37:1": "※시나리오 시작 후에는 변경할 수 없습니다",
    "4:37:2": "\n\n[사실]\n사실에 따른 외교 관계로 시작합니다\n\n[없음]\n모든 세력이 외교 관계가 없는 상\n태로 시작합니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {27, 31, 37}
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
                "segment": "base_msggame_B001_S27",
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
