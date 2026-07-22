#!/usr/bin/env python3
"""Build Base authoring segment 359 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S359.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s359", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:875:0": "놈, 이 목숨이 다하더라도\n결코 충절을 저버리지 않고\n끝까지 싸워 보이리라!",
    "7:876:0": "·",
    "7:876:1": "……\n그 이름난 모략에 현혹되지 않도록\n경계를 엄중히",
    "7:877:0": "·",
    "7:877:1": "……잔꾀나 부리는군\n그 거창한 이명에 걸맞은지\n내 눈으로 확인해 보겠다",
    "7:877:2": "!",
    "7:878:0": "·",
    "7:878:1": "……\n승룡의 기세, 내 손으로 꺾어 보이",
    "7:878:2": "!",
    "7:879:0": "놈이 이런 곳까지 오다니!\n목숨 아까운 줄 모르는 저돌적인 무사 놈들에게\n내 성을 넘겨줄 수는 없다",
    "7:880:0": "이(가), 이런 곳까지 오다니!\n목숨 아까운 줄 모르는 거친 무사들에게\n어찌 맞서",
    "7:880:1": "인가……",
    "7:881:0": "·",
    "7:881:1": "인가!\n오니와코라 두려움을 산 창 솜씨를\n이 눈으로 보게 되",
    "7:881:2": "란……",
    "7:882:0": "설마, 그 「",
    "7:882:1": "」이(가)……\n앞으로의 거취를 생각해",
    "7:882:2": "……",
    "7:883:0": "예전부터 우리와 다투어 온 「",
    "7:883:1": "」의\n",
}

STATIC_COORDINATES: set[str] = set()


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S359", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
