#!/usr/bin/env python3
"""Build Base authoring segment 674 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S674.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s674", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2563:0": "송충이 모양의 투구 앞장식에 떨어라!\n",
    "9:2563:1": "이(가) 나선다, 첫 공은 내 것이다!",
    "9:2564:0": "이 메기 꼬리 모양 투구를 따르라!\n선봉은―",
    "9:2564:1": "(이)로다!",
    "9:2565:0": "기세가 대단하군!\n",
    "9:2565:1": "도 질 수는 없지!",
    "9:2566:0": "공을 먼저 세웠는가\n서둘러 만회해야 한다!",
    "9:2567:0": "훌륭히 앞장섰구나!\n우리도 뒤따르자",
    "9:2568:0": "선수를 빼앗겼군요\n이대로 질 수는 없습니다",
    "9:2569:0": "참으로 담대하도다!\n우리도 본받아야 한다",
    "9:2570:0": "호오, 우리 몫의 공도\n남겨 주시구려",
    "9:2571:0": "대단하십니다!\n나도 저리되고 싶군요!",
    "9:2572:0": "싸움은 이제부터다\n지금은 공을 양보하겠소",
    "9:2573:0": "훌륭합니다!\n",
    "9:2573:1": "들도 뒤따릅시다",
    "9:2574:0": "한발 늦었는가\n하지만 훌륭하구나!",
    "9:2575:0": "그 공의 덕을 우리도\n입고 싶습니다",
    "9:2576:0": "전투가 시작됐는가\n어서 합류해야 한다!",
    "9:2577:0": "이(가) 출진",
    "9:2578:0": "드디어 내 차례인가!\n가자, 녀석들아!",
    "9:2579:0": "나설 차례로군\n진군하도록 하자!",
    "9:2580:0": "드디어 나설 차례인가\n진군하도록 하자",
    "9:2581:0": "출진할 때가 되었군요\n나아갑시다",
    "9:2582:0": "우리가 나설 차례다\n마음껏 싸우자!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2563:0",
    "9:2563:1",
    "9:2564:0",
    "9:2564:1",
    "9:2565:0",
    "9:2565:1",
    "9:2573:0",
    "9:2573:1",
    "9:2577:0",
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
                "segment": "base_msggame_B001_S674",
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
