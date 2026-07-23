#!/usr/bin/env python3
"""Build Base authoring segment 679 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S679.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s679", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2668:0": "에게\n뒤처질 수는 없다",
    "9:2669:0": "의\n뒷모습만 보고 있을쏘냐",
    "9:2670:0": "에게\n지는 것은 분한 일이로군",
    "9:2671:0": "에게\n뒤처질 수는 없지",
    "9:2672:0": "따위에게\n질 수는 없다!",
    "9:2673:0": "의 뒤를\n따라 주십시오!",
    "9:2674:0": "에게\n뒤처질 수는 없다!",
    "9:2675:0": "의 뒤를\n따르도록 하지요",
    "9:2676:0": "의 뒤를\n따라 나아가라!",
    "9:2677:0": "놈의 부대는 빈틈투성이다\n협격해 버려라!",
    "9:2678:0": "협격을 노릴 수 있겠군\n서둘러 위치를 잡아라!",
    "9:2679:0": "적군을 에워싼다!\n신속히 이동하라",
    "9:2680:0": "아군과 연계합시다\n협격을 노리겠습니다",
    "9:2681:0": "협격해 주마!\n적의 측후방을 잡으리라!",
    "9:2682:0": "협격을 노릴 수 있겠다\n신속히 움직여라!",
    "9:2683:0": "서둘러 이동하라!\n적을 에워싼다!",
    "9:2684:0": "앞뒤를 잡으면 손쉬운 승리다!\n자, 진군을 시작하자!",
    "9:2685:0": "협격을 노리겠습니다!\n적의 뒤로 붙으세요!",
    "9:2686:0": "놈을 협격하리라!\n신속히 이동하라!",
    "9:2687:0": "적의 시선이 다른 데 쏠렸군요\n측면을 찌릅시다",
    "9:2688:0": "협격을 노린다\n신속히 움직여라!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2668:0",
    "9:2669:0",
    "9:2670:0",
    "9:2671:0",
    "9:2672:0",
    "9:2673:0",
    "9:2674:0",
    "9:2675:0",
    "9:2676:0",
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
                "segment": "base_msggame_B001_S679",
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
