#!/usr/bin/env python3
"""Build Base authoring segment 24 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S24.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s24", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "3:3:0": "저장 데이터를 덮어씁니다\n계속하시겠습니까?",
    "3:4:0": "저장하지 못했습니다",
    "3:5:0": "저장을 완료했습니다",
    "3:6:0": "이 저장 데이터를 불러올 수 없습니다\n데이터와 게임의 버전이 일치하지 않습니다\n게임을 최신 버전으로 업데이트해 주십시오",
    "3:7:0": "플레이 중인 시나리오를 중단하고\n이 데이터를 불러오시겠습니까?",
    "3:8:0": "이 저장 데이터를 불러옵니다\n계속하시겠습니까?",
    "3:9:0": "데이터를 불러오지 못했습니다(",
    "3:9:1": ")",
    "3:10:0": "파일을 만들지 못했습니다",
    "3:11:0": "보유하지 않은 DLC가 포함되어 있습니다",
    "3:12:0": "게임을 최신 버전으로\n업데이트해 주십시오",
    "3:13:0": "변경한 설정을 적용하지 않고 돌아갑니다\n계속하시겠습니까?",
    "3:14:0": "데이터가 손상되었습니다",
    "3:15:0": "명의 등록 무장을 불러왔습니다",
    "3:16:0": "친부·혈연으로 등록 무장이 설정된 경우\n해당 친부·혈연을 삭제했습니다",
    "3:17:0": "생년을 변경하면 친부 설정이 무효가 됩니다\n계속하시겠습니까?",
    "3:18:0": "수명을 변경하면",
    "3:18:1": "의\n친부 설정이 무효가 됩니다\n계속하시겠습니까?",
    "3:19:0": "수명을 변경하면",
    "3:19:1": "을 비롯한 이들의\n친부 설정이 무효가 됩니다\n계속하시겠습니까?",
    "3:20:0": "성별을 변경하면 친부 설정이 무효가 됩니다\n계속하시겠습니까?",
    "3:21:0": "시나리오 「군웅요란」이 개방되었습니다",
    "3:22:0": "추가 콘텐츠 데이터가 없어\n일부 무장이 등장하지 않습니다\n※다시 다운로드한 뒤\n 게임을 시작하면 등장합니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {9, 15, 18, 19}
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
                "segment": "base_msggame_B001_S24",
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
