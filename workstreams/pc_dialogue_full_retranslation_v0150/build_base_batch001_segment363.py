#!/usr/bin/env python3
"""Build Base authoring segment 363 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S363.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s363", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:926:0": "이 승리가 천하에 널리 알려지리라!",
    "7:927:0": "우리의 승리를 온 세상에 드높여라!",
    "7:928:0": "우리의 이름이 천하에 널리 알려지리라!",
    "7:929:0": "우리의 승리를 온 세상에 널리 알려라",
    "7:930:0": "내 용맹한 명성이 온 천하에 울려 퍼져라!",
    "7:931:0": "우리의 승리가 천하에 울려 퍼지겠구먼",
    "7:932:0": "이 승리로 내 이름이 널리 퍼지리라!",
    "7:933:0": "바람이 우리의 승리를 널리 전해 주겠지요!",
    "7:934:0": "우리 가문의 이름이 천하에 울려 퍼지겠지요",
    "7:935:0": "바람에 실어 내 이름을 외쳐라!",
    "7:936:0": "우리가 누구인지 똑똑히 보여 주마!",
    "7:937:0": "우리의 이름이 온 세상에 알려지겠지요",
    "7:938:0": "이 바람이 온 세상을 뒤흔들 것입니다",
    "7:939:0": "이(가)",
    "7:939:1": "을(를) 꺾어 위풍이 발생",
    "7:940:0": "위풍으로 우리 가문과 주변 세력의 관계가 악화",
    "7:941:0": "따위에게 굴복하다니……\n",
    "7:941:1": "도 결국 오합지졸일 뿐\n이용할 가치조차 없구나",
    "7:942:0": "에게 이토록 참패해서야\n",
    "7:942:1": "은(는) 이제 글렀구먼\n앞으로 관계도 좀 다시 생각해 봐야겠구먼",
}

STATIC_COORDINATES: set[str] = {
    "7:926:0", "7:927:0", "7:928:0", "7:929:0", "7:930:0", "7:931:0", "7:932:0",
    "7:933:0", "7:934:0", "7:935:0", "7:936:0", "7:937:0", "7:938:0", "7:940:0",
}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S363", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
