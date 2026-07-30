#!/usr/bin/env python3
"""Build Base authoring segment 26 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S26.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s26", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "4:14:0": "【사운드 설정】\n게임 내 음량을 조절합니다\n\n[마스터 볼륨]\n게임 전체 음량 설정\n\n[BGM 음량] / [효과음 음량] /\n[음성·영상 음량]\n각 항목의 음량 설정",
    "4:15:0": "【사운드 출력】\n음질을 설정합니다\n\n[스테레오] / [서라운드]",
    "4:16:0": "【자동 저장】\n일정 기간마다 자동으로 저장하는\n방식을 설정합니다\n\n[매월]\n달이 바뀔 때\n\n[계절마다]\n1월·4월·7월·10월이 될 때\n\n[매년]\n매년 1월이 될 때\n\n[사용 안 함]\n자동으로 저장하지 않음",
    "4:17:0": "【자동 메시지 넘김】\n메시지 자동 표시 방식을 설정합니\n다\n\n[저속] / [중속] / [고속] / [최고속]\n메시지가 자동으로 넘어갈 때까지\n걸리는 시간을 설정\n\n[사용 안 함]\n입력할 때까지 메시지를 넘기지 않\n음",
    "4:18:0": "【요약 정보 표시 속도】\n성이나 부대 등에 커서를 맞췄을\n때 정보가 표시되기까지 걸리는\n시간을 조정합니다\n\n[저속] / [중속]\n일정 시간이 지난 뒤 표시\n\n[고속]\n즉시 표시",
    "4:19:0": "【화면 가장자리 스크롤】\n커서를 화면 가장자리로 옮겼을 때\n지도를 스크롤하는 방식을\n설정합니다\n\n[저속] / [중속] / [고속]\n스크롤 속도를 설정\n\n[사용 안 함]\n화면 가장자리 스크롤을 사용하지 않음",
    "4:20:0": "【명령 시 카메라 이동】\n성이나 부대 메뉴를 열 때 또는 명\n령을 실행할 때 카메라가 자동으로\n움직이도록 설정합니다\n\n[사용] / [사용 안 함]",
    "4:21:0": "【사건 보고 시 카메라 이동】\n지도에서 일어난 사건에 따른 카메라\n동작을 설정합니다\n\n[사용]\n사건 보고 시 카메라 이동\n\n[사용 안 함]\n일부 예외를 제외하고 사건 보고 시\n카메라를 이동하지 않음",
    "4:22:0": "【난이도】\n게임 난이도를 설정합니다\n\n[초초급]\n느긋하게 즐기고 싶은 플레이어용\n\n[초급]\n적당한 난이도를 즐기고 싶은 플레이어용\n\n[중급]\n게임에 익숙한 플레이어용\n\n[상급]\n도전할 만한 난이도를 원하는 플레이어용",
    "4:23:0": "【병량 수입(타 세력)】\n타 세력의 병량 수입량을 설정합니다\n플레이어 세력과 내정치가 같더라도\n수입량이 달라집니다",
    "4:24:0": "【금전 수입(타 세력)】\n타 세력의 금전 수입량을 설정합니다\n플레이어 세력과 내정치가 같더라도\n수입량이 달라집니다",
    "4:25:0": "【AI 레벨】\n타 세력의 판단 능력을 설정합니다\n높을수록 다양한 전략을\n더 효율적으로 수행합니다",
}

DYNAMIC_RUNTIME_COORDINATES: set[str] = set()


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
                "segment": "base_msggame_B001_S26",
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
