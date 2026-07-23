#!/usr/bin/env python3
"""Build Base authoring segment 675 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S675.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s675", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2583:0": "자, 활약할 기회를\n확보해야겠군",
    "9:2584:0": "이번 기회를\n살려야 하겠군",
    "9:2585:0": "드디어 내 차례인가\n기다리다 지쳤느니라!",
    "9:2586:0": "이제 나설 때로군요\n",
    "9:2586:1": "에게 맡겨 주십시오!",
    "9:2587:0": "드디어 내 차례인가!\n팔이 근질거리는군!",
    "9:2588:0": "대기는 여기까지입니다\n진군을 시작하겠습니다!",
    "9:2589:0": "나설 차례로군\n진군하도록 하자!",
    "9:2590:0": "이(가) 출진",
    "9:2591:0": "쉴 수 있는 때는 지금뿐이다\n녀석들아, 휴식이다!",
    "9:2592:0": "병사들을 쉬게\n해 둘까",
    "9:2593:0": "이곳에서 잠시\n쉬게 하도록 하자",
    "9:2594:0": "병사들을 쉬게 하려면\n지금뿐이겠군요",
    "9:2595:0": "지친 채로는 싸울 수 없다\n지금은 부대를 쉬게 하자",
    "9:2596:0": "무리는 금물인 법\n휴식을 취하게 하자",
    "9:2597:0": "모두, 지금은 쉬어라\n기력을 회복하는 것이다",
    "9:2598:0": "쉴 수 있을 때 쉬는 것\n싸움의 기본이로다",
    "9:2599:0": "병사들이 지쳐 있습니다\n잠시 쉬게 합시다",
    "9:2600:0": "싸움은 아직 계속된다\n병사들을 쉬게 해 두자",
    "9:2601:0": "지금이라면\n병사들을 쉬게 할 수 있겠군요",
    "9:2602:0": "지금 틈을 타\n쉬도록 할까",
    "9:2603:0": "전황이 보이질 않아!\n더 앞으로 나간다!",
    "9:2604:0": "원호하기에는 너무 멀군\n모두, 전진하라!",
    "9:2605:0": "전선의 상황이 보이지 않는다\n전진하라!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2586:0",
    "9:2586:1",
    "9:2590:0",
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
                "segment": "base_msggame_B001_S675",
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
