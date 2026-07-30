#!/usr/bin/env python3
"""Build Base authoring segment 460 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S460.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s460", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2458:0": "모든 것이 한바탕 꿈이로다",
    "7:2459:0": "이런 최후도 나쁘지 않군",
    "7:2460:0": "이 몸이 스러지다니!",
    "7:2461:0": "내 목을 취한 것을 영예로 여겨라!",
    "7:2462:0": "여기까지인가. 잘 있거라!",
    "7:2463:0": "내 여정도 여기까지인가",
    "7:2464:0": "원통하기 그지없구나!",
    "7:2465:0": "이 목을 가져가라!",
    "7:2466:0": "전장에서 죽는가. 나쁘지 않군",
    "7:2467:0": "전장에서 스러지는 것이 무사의 길이다!",
    "7:2468:0": "내 뜻은 남으리라. 잘 있거라!",
    "7:2469:0": "나의 최후를 후세에 전하라!",
    "7:2470:0": "저승에서 기다리겠다!",
    "7:2471:0": "내 목숨도 여기까지인가!",
    "7:2472:0": "뜻을 이루지 못한 채 쓰러지다니……",
    "7:2473:0": "전장에서 죽는 것은 영예로다!",
    "7:2474:0": "지옥의 귀신들과 싸워 보자꾸나!",
    "7:2475:0": "이런 곳에서 끝나다니!",
    "7:2476:0": "모든 방책이 다한 것인가!",
    "7:2477:0": "이것이야말로 무사의 삶이로다",
}

STATIC_COORDINATES = set(TRANSLATIONS)


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S460", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
