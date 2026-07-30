#!/usr/bin/env python3
"""Build Base authoring segment 586 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S586.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s586", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:775:0": "을(를)\n베어 쓰러뜨렸습니다!",
    "9:776:0": "\n베어 쓰러뜨렸노라!",
    "9:777:0": "을(를)\n베어 쓰러뜨렸습니다",
    "9:778:0": "을(를)\n베어 쓰러뜨렸습니다!",
    "9:779:0": "\n꼴좋다!",
    "9:780:0": "\n처단하였소!",
    "9:781:0": "의 야망은\n무너졌노라!",
    "9:782:0": "……\n마침내 베어 쓰러뜨렸군요",
    "9:783:0": "원수―",
    "9:783:1": "\n베어 쓰러뜨렸노라",
    "9:784:0": "……\n이것이 네 업보다……",
    "9:785:0": "하늘의 그물은 성긴 듯해도\n놓치는 법이 없다는 말이지요……",
    "9:786:0": "가증스러운 자―",
    "9:786:1": "을(를)\n베어 쓰러뜨렸도다",
    "9:787:0": "마침내―",
    "9:787:1": "을(를)\n베어 쓰러뜨렸습니다!",
    "9:788:0": "의 수급을\n분명히 거두었다!",
    "9:789:0": "……\n이제 작별입니다",
    "9:790:0": "을(를)\n베어 쓰러뜨릴 날이 오다니",
    "9:791:0": "을(를)\n붙잡았다!",
    "9:792:0": "을(를)\n포로로 삼았소!",
    "9:793:0": "을(를)\n생포했다!",
}

STATIC_COORDINATES: set[str] = {"9:785:0"}


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
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S586", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
