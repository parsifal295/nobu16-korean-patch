#!/usr/bin/env python3
"""Build Base authoring segment 667 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S667.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s667", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2436:0": "다음은―",
    "9:2436:1": "이(가) 나선다\n승부하자!",
    "9:2437:0": "이곳은―",
    "9:2437:1": "이(가)\n막아야겠군",
    "9:2438:0": "마저 이길 수 있다고\n생각한다면 큰 오산이다",
    "9:2439:0": "이(가) 상대다!\n앞서처럼 되지는 않을 것이다",
    "9:2440:0": "이번에는―",
    "9:2440:1": "이(가) 나선다!\n자, 승부다!",
    "9:2441:0": "이(가) 상대다\n",
    "9:2441:1": "에게는 지지 않는다",
    "9:2442:0": "전장에 선―",
    "9:2442:1": "은(는)\n그리 만만하지 않습니다",
    "9:2443:0": "이번에는―",
    "9:2443:1": "(이)다!\n자, 덤벼 보아라",
    "9:2444:0": "새로 온 적들도 모조리\n박살 내 주마!",
    "9:2445:0": "새 상대인가, 바라던 바다!",
    "9:2446:0": "예비대라니 가소롭구나\n누가 오든 매한가지다",
    "9:2447:0": "새 적이군요\n진형을 다시 짜십시오!",
    "9:2448:0": "새 상대인가!\n팔이 근질거리는구나!",
    "9:2449:0": "이때 예비대인가\n흠, 예상대로군",
    "9:2450:0": "새 상대께서 납셨는가\n그래야 재미있지!",
    "9:2451:0": "오오, 적의 예비대인가\n싸울 맛이 나는구나!",
    "9:2452:0": "새 병력이 오더라도\n그저 싸울 뿐이다!",
    "9:2453:0": "예비대가 있었더냐\n차라리 한꺼번에 올 것이지",
    "9:2454:0": "새 상대입니까\n제법 즐겁게 해 주시는군요",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2436:0",
    "9:2436:1",
    "9:2437:0",
    "9:2437:1",
    "9:2438:0",
    "9:2439:0",
    "9:2440:0",
    "9:2440:1",
    "9:2441:0",
    "9:2441:1",
    "9:2442:0",
    "9:2442:1",
    "9:2443:0",
    "9:2443:1",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
                "segment": "base_msggame_B001_S667",
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
