#!/usr/bin/env python3
"""Build Base authoring segment 162 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S162.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s162", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2922:1": "놈!\n우리를 배신했구나!",
    "6:2923:0": "…용서할 수 없습니다\n우리 가문의 산하를 떠나다니!",
    "6:2924:0": "이놈,", "6:2924:1": "!\n감히 우리를 배신하다니…",
    "6:2925:0": "이놈,", "6:2925:1": "!\n우리를 배신하다니!",
    "6:2926:0": "이놈,", "6:2926:1": "!\n어찌하여 배신했느냐!?",
    "6:2927:0": "으음…", "6:2927:1": "놈!\n지금까지의 은혜를 잊었느냐!",
    "6:2928:0": "이럴 수가…\n", "6:2928:1": "이(가) 나를 배신하다니…",
    "6:2929:0": "놈!\n이 굴욕은 전장에서 씻겠다!",
    "6:2930:0": "설마,", "6:2930:1": "이(가)…\n그토록 아껴 주었건만",
    "6:2931:0": "이놈,", "6:2931:1": "!\n우리를 배신하다니!",
    "6:2932:0": "제안 내용을 철회하고\n상대의 요구를 표시합니다\n계속하시겠습니까?",
    "6:2933:0": "이 정도 부탁이라면 쉬운 일이오\n헌데, 보답은 얼마나 주실는지요",
    "6:2934:0": "호오, 제법 큰 비용이 들 것이오\n보답은 기대해도 되겠지요?",
}

STATIC_COORDINATES = {"6:2923:0", "6:2932:0", "6:2933:0", "6:2934:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S162", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
