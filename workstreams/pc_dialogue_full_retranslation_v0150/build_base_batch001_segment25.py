#!/usr/bin/env python3
"""Build Base authoring segment 25 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S25.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s25", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "4:3:0": "α 버전 튜토리얼을 표시하시겠습니까?",
    "4:4:0": "게임을 종료합니다\n계속하시겠습니까?",
    "4:5:0": "의 데이터를 불러옵니다\n계속하시겠습니까?",
    "4:6:0": "오카자키성이 함락되었습니다\n축하합니다!\nα 버전은 여기서 종료됩니다",
    "4:7:0": "이나바야마성이 함락되었지만\nα 버전의 목표는 오카자키성 공략입니다",
    "4:8:0": "다음에는 꼭 오카자키성 공략에 도전해 보십시오\nα 버전은 여기서 종료됩니다",
    "4:9:0": "기요스성이 함락되었습니다\nα 버전은 여기서 종료됩니다",
    "4:10:0": "마우스 오른쪽 버튼을 클릭하면 세력 메뉴가 열립니다",
    "4:11:0": "【표시 모드】\n게임 화면의 표시 방식을 설정합니다\n\n[창 모드]\n창으로 표시\n\n[전체 화면]\n전체 화면으로 표시\n\n[테두리 없음]\n테두리 없는 창으로 표시",
    "4:12:0": "【화면 크기(해상도)】\n화면 해상도를 변경합니다\n\n[권장 설정]\n1920×1080 픽셀\n1600×900 픽셀\n",
    "4:13:0": "【CG 화질】\nCG 화질을 설정합니다\n※합전 중에는 변경할 수 없습니다\n\n[속도 우선]\n속도를 우선하여 CG를 간략히 표시\n\n[표준]\nCG를 표준 화질로 표시\n\n[화질 우선]\n화질을 우선하여 CG를 상세히 표시",
}

DYNAMIC_RUNTIME_COORDINATES = {"4:5:0"}


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
                "segment": "base_msggame_B001_S25",
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
