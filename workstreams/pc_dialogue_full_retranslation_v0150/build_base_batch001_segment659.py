#!/usr/bin/env python3
"""Build Base authoring segment 659 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S659.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s659", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2288:0": "그런 수가\n",
    "9:2288:1": "에게 통하겠냐!",
    "9:2289:0": "투지로 혼란 따위\n떨쳐 내겠다!",
    "9:2290:0": "의 담력을\n얕보지 마라!",
    "9:2291:0": "이 정도로―",
    "9:2291:1": "이(가)\n흐트러질 줄 알았나?",
    "9:2292:0": "잔재주 따위는 통하지 않는다!\n다시 수련하고 오너라!",
    "9:2293:0": "흥, 마무리가\n너무 허술하구나",
    "9:2294:0": "정연한 우리 대열을\n무너뜨리기란 불가능하다",
    "9:2295:0": "아직 멀었다, 멀었어!\n모두 꿰뚫어 보았느니라",
    "9:2296:0": "너무 얕보인\n모양이군요",
    "9:2297:0": "잔재주가\n통할 성싶으냐!",
    "9:2298:0": "우리 부대의 통솔을\n흐트러뜨릴 수는 없답니다",
    "9:2299:0": "위험했군……\n하지만 거짓임을 갈파했다!",
    "9:2300:0": "물러나면 되는 거로군!\n고맙다!",
    "9:2301:0": "퇴각로가 위험하다고?\n서둘러 돌아가자!",
    "9:2302:0": "후방을 확인하라고……\n확실히 일리가 있군",
    "9:2303:0": "후방이 위험하다고……?\n물러납시다",
    "9:2304:0": "퇴각로를 노린다고?\n돌아가서 기다렸다가 치자",
    "9:2305:0": "책략일지도 모르나……\n일단 돌아가자",
    "9:2306:0": "퇴각로가!?\n서둘러 돌아가야 한다!",
    "9:2307:0": "퇴각로가 위험하다!\n돌아가자!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2288:0",
    "9:2288:1",
    "9:2290:0",
    "9:2291:0",
    "9:2291:1",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S659", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
