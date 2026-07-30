#!/usr/bin/env python3
"""Build Base authoring segment 485 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S485.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s485", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:131:0": "성하가 활기를 띠어 금전 수입이 늘었습니다",
    "8:132:0": "낭보입니다. 상인 마을의 수익이 늘었습니다",
    "8:133:0": "금전 수입이 늘었습니다",
    "8:134:0": "수익이 늘어 웃음이 멈추질 않는구먼!",
    "8:135:0": "상인 마을이 활기를 띠었습니다. 수익이 늘어날 듯합니다",
    "8:136:0": "마을이 활기를 띠어 금전 수입이 늘고 있습니다",
    "8:137:0": "성하가 활기를 띠어 금전 수입이 늘었습니다",
    "8:138:0": "상인 마을이 활기를 띠어 수익이 늘어날 듯합니다",
    "8:139:0": "군마 생산량이 늘었다! 돌보는 일도 만만치 않겠군!",
    "8:140:0": "군마 조달량이 늘어납니다. 조련은 맡겨 주십시오",
    "8:141:0": "군마 생산이 늘었습니다. 기대해 주십시오",
    "8:142:0": "말 생산량이 늘었습니다",
    "8:143:0": "군마 생산이 늘었습니다. 활기차군요!",
    "8:144:0": "낭보입니다. 군마 생산량이 늘었습니다",
    "8:145:0": "군마 생산이 늘었습니다. 돌볼 방도를 생각해야겠습니다……",
    "8:146:0": "군마 생산이 늘었구나. 오랜만에 말을 달려 볼까!",
    "8:147:0": "말을 더 많이 조달할 수 있게 되었습니다",
    "8:148:0": "말 조달량이 늘었습니다. 조련은 맡겨 주십시오",
    "8:149:0": "말 생산이 늘었습니다. 돌보는 일이 만만치 않겠군요",
    "8:150:0": "전보다 더 많은 말을 조달할 수 있을 듯합니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S485", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
