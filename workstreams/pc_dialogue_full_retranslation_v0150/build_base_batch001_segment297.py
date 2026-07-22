#!/usr/bin/env python3
"""Build Base authoring segment 297 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S297.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s297", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4446:0": "우리 가문을 섬긴 지 얼마 되지 않은 몸이나\n분골쇄신하여 일에 임하겠습니다",
    "6:4447:0": "신참인 이 몸에게 영지를…\n참으로 황공하",
    "6:4448:0": "오랜 세월 우리 가문에서 갈고닦은 수완을\n마음껏 발휘하",
    "6:4449:0": "내 뛰어남은 섬긴 세월만이 아님을\n증명해 보이겠",
    "6:4450:0": "머, 멀군…\n",
    "6:4450:1": ", 명이 내리면 곧바로\n길 떠날 채비를 갖추겠",
    "6:4451:0": "딱히 염려되는 바는",
    "6:4451:1": "만\n",
    "6:4451:2": "의 배속에는\n거리가 멀어 부임에 시간이 걸릴 듯합니다…",
    "6:4452:0": "그 땅은 가까운 곳이니\n곧바로 부임할 수 있",
    "6:4453:0": "가까운 땅이니, 「",
    "6:4453:1": "」에게 그 땅을 맡기면\n영주 부재 기간을\n최소로 줄일 수 있",
    "6:4454:0": "하고 성주 「",
    "6:4454:1": "」의 사이는\n특별히 좋지도 나쁘지도 않아\n문제없이 일할 수 있을 듯합니다",
    "6:4455:0": "하고 성주 「",
    "6:4455:1": "」의 사이는 원만하여\n만사를 순조롭게 진행할 수 있",
    "6:4456:0": "어느 땅에서든 우리 가문을 위해\n전력을 다하겠습니다",
    "6:4457:0": "성주 「",
    "6:4457:1": "」님이\n겸임하",
    "6:4457:2": "는 것은 어떻습니까?",
}

STATIC_COORDINATES: set[str] = {"6:4446:0", "6:4456:0"}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S297", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
