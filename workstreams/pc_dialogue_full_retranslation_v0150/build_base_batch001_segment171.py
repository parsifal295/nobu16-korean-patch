#!/usr/bin/env python3
"""Build Base authoring segment 171 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S171.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s171", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3057:0": "은(는) 이제 우리 식구가 아니니\n혼인 동맹도 앞으로",
    "6:3057:1": "개월 뒤면\n끝나 버린다고. 이제 어쩔 셈이야?",
    "6:3058:0": "와(과)는 이제 인척 관계가\n끝났으므로, 혼인 동맹도\n앞으로",
    "6:3058:1": "개월 뒤면 끝나게 되옵니다",
    "6:3059:0": "인척 관계가 끝났으므로,",
    "6:3059:1": "와(과)의\n혼인 동맹도",
    "6:3059:2": "개월 후에는\n효력을 잃사오니, 부디 유념하시옵소서",
    "6:3060:0": "참으로 유감스럽게도, 인척 관계가 끝났으므로\n",
    "6:3060:1": "와(과)의 동맹 또한",
    "6:3060:2": "개월 후에는\n사라지고 말 것이옵니다",
    "6:3061:0": "와(과)는 인척 관계가 끝났으므로\n동맹도",
    "6:3061:1": "개월 후에는 끝나옵니다.\n그때는 전쟁이 벌어질지도 모르겠군요",
    "6:3062:0": "와(과)의 혼인 관계가 끝났으므로\n동맹도 앞으로",
    "6:3062:1": "개월 뒤면 끝나옵니다.\n앞으로의 관계를 생각해야겠군요",
    "6:3063:0": "인연이 끊어졌으므로,",
    "6:3063:1": "와(과)의\n동맹도",
    "6:3063:2": "개월 후에는 끝나옵니다.\n설마 이리될 줄이야…",
    "6:3064:0": "관계가 끊어졌으므로,",
    "6:3064:1": "와(과)는\n",
    "6:3064:2": "개월 뒤면 동맹 관계도 끝나옵니다.\n양가의 관계를 어찌할지는",
}

STATIC_COORDINATES: set[str] = set()


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S171", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
