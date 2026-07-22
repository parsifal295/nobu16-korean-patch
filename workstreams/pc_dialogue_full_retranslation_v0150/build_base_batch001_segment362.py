#!/usr/bin/env python3
"""Build Base authoring segment 362 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S362.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s362", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:906:0": "다케다군의 강함을 천하에 떨치리라!",
    "7:907:0": "승리로써 세상에 의를 보이리라!",
    "7:908:0": "내 뜻이여, 폭풍이 되어 휘몰아쳐라!",
    "7:909:0": "이름을 알리는 것도 계략이니, 널리 울려 퍼져라!",
    "7:910:0": "우리의 승리를 널리 알리고 드높여라!",
    "7:911:0": "하늘로 오르는 독안룡의 이름을 똑똑히 들어라!",
    "7:912:0": "바람이여, 내 이름을 싣고 사납게 울부짖어라!",
    "7:913:0": "천하의 평온을 위해 내 이름을 떨치리라!",
    "7:914:0": "내 승리를 천하에 보이리라!",
    "7:915:0": "우리의 승리를 세상에 울려 퍼뜨리리라!",
    "7:916:0": "우리의 이름이 바람과 함께 널리 퍼지리라!",
    "7:917:0": "이 바람이 우리 시대를 불러올 거다!",
    "7:918:0": "내 이름을 세상에 떨쳐 주마!",
    "7:919:0": "바람이여, 내 이름을 실어 나르라!",
    "7:920:0": "우리의 승전보를 똑똑히 들어라!",
    "7:921:0": "승리를 외쳐라, 세상에 알려라!",
    "7:922:0": "내 이름을 천하에 울려 퍼뜨려라!",
    "7:923:0": "우리의 승리를 온 세상에 널리 알려라!",
    "7:924:0": "우리의 이름을 널리 떨쳐 주리라!",
    "7:925:0": "우리의 용맹한 명성이 세상에 울려 퍼지리라!",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S362", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
