#!/usr/bin/env python3
"""Build Base authoring segment 593 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S593.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s593", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:923:0": "꼴사납구나……\n허둥대고 있도다",
    "9:924:0": "한바탕 휘저어\n놓았습니다!",
    "9:925:0": "당황해라, 갈팡질팡해라!",
    "9:926:0": "대혼란에 빠진 듯하군요",
    "9:927:0": "적군은 아비규환이옵니다!",
    "9:928:0": "쳇, 일을 그르쳤나!",
    "9:929:0": "큭!\n혼란시키지 못했나……!",
    "9:930:0": "으음……\n지독히 운 좋은 적이로구나",
    "9:931:0": "좀 더 단순한 방법이었다면\n성공했을까요……",
    "9:932:0": "무인답게 정정당당히\n맞서라는 뜻인가",
    "9:933:0": "이(가)\n혼란에 빠뜨리는 데 실패……했다고?",
    "9:934:0": "호오…… 겉보기보다\n제법 하는 적이로구나",
    "9:935:0": "이런!\n혼란에 빠뜨리지 못했구나",
    "9:936:0": "뜻대로 되지\n않았습니다……",
    "9:937:0": "큭, 실패인가!",
    "9:938:0": "실패한 듯합니다……",
    "9:939:0": "실패했습니다…… 죄송합니다",
    "9:940:0": "감쪽같이\n속여 넘겼다!",
    "9:941:0": "거짓 정보로\n적을 물러나게 하리라!",
    "9:942:0": "이것으로 적도\n움직이겠지",
    "9:943:0": "적은 내 손아귀에 있도다……",
    "9:944:0": "거짓 정보에 속아 썩 물러가라!",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS) - {"9:933:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S593", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
