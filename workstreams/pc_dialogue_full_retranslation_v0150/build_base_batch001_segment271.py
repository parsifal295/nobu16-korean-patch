#!/usr/bin/env python3
"""Build Base authoring segment 271 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S271.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s271", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4170:0": "정보를 표시할 군단이 없습니다",
    "6:4171:0": "우리 군단에서\n일부 부대를 파견하",
    "6:4172:0": "주명에 맞는 계책을 가신들에게서 모",
    "6:4172:1": "\n실행 가능한 제안이 있는 듯하니\n확인한 뒤 결재해",
    "6:4173:0": "주명을 가신들에게 알렸더니\n방침에 부합할 만한 제안이 있",
    "6:4173:1": "\n승인할지 말지 확인해",
    "6:4174:0": "유감스럽게도 주명에 부합하는 제안은\n가신들 사이에서 나오지",
    "6:4174:1": "…",
    "6:4175:0": "주명에 맞는 계책을 가신들에게서 모",
    "6:4175:1": "만\n실행 가능한 제안은",
    "6:4175:2": "\n면목 없는 일",
    "6:4175:3": "…",
    "6:4176:0": "운용할 수 있는 금전이 적어서인지\n유효한 제안은",
    "6:4177:0": "동원할 수 있는 노동력이 적어서인지\n유효한 제안은",
    "6:4178:0": "알겠습니다",
    "6:4178:1": "\n반드시 주명에 걸맞은 성과를\n우리 가문에 가져오",
    "6:4179:0": ", 알겠",
    "6:4179:1": "\n우리 가문을 위해 주명을 완수하도록\n전력을 다하",
    "6:4180:0": "에 착수하",
    "6:4180:1": "\n훌륭히 일한 자에게는 상을 내리",
}

STATIC_COORDINATES: set[str] = {"6:4170:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S271", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
