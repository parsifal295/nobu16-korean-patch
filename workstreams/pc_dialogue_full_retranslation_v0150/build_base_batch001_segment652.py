#!/usr/bin/env python3
"""Build Base authoring segment 652 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S652.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s652", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2165:0": "그 수에는 속지 않는다!",
    "9:2166:0": "그런 수에 걸려들 줄\n알았습니까?",
    "9:2167:0": "그 수에 말려들지는 않는다",
    "9:2168:0": "후방이 걱정되는군……\n확인하러 가 볼까!",
    "9:2169:0": "물러나라!　퇴각로가\n위험하다는 전갈이다!",
    "9:2170:0": "음…… 만일을 위해\n퇴로를 확인해 둘까",
    "9:2171:0": "퇴로에 적의 모습이……?\n요격해야 한다",
    "9:2172:0": "적이 퇴각로를 노리고 있군\n에잇, 돌아가자!",
    "9:2173:0": "뭐라, 퇴각로가?\n적의 책략인가…… 아니, 돌아가라",
    "9:2174:0": "퇴각로를 빼앗기면……\n서둘러 지키러 가자",
    "9:2175:0": "퇴각로가 위험하다고!?\n돌아가라, 어서 돌아가!",
    "9:2176:0": "퇴로를 노리고 있다고?\n물러나야 한다!",
    "9:2177:0": "후방이 염려되는군……\n물러나자",
    "9:2178:0": "가슴이 술렁이는군요……\n물러납시다",
    "9:2179:0": "퇴각로가 위태롭다는 보고……\n물러나겠사옵니다",
    "9:2180:0": "의 계책은\n내가 간파해 냈다!",
    "9:2181:0": "거기까지다!\n",
    "9:2181:1": "을(를) 간파했다",
    "9:2182:0": "우리에게는 통하지 않는다\n",
    "9:2182:1": "!",
    "9:2183:0": "의 계략을\n간파했습니다!",
    "9:2184:0": "도\n이 몸에게는 통하지 않는다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2180:0",
    "9:2181:0",
    "9:2181:1",
    "9:2182:0",
    "9:2182:1",
    "9:2183:0",
    "9:2184:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S652", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
