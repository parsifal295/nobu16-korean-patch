#!/usr/bin/env python3
"""Build Base authoring segment 310 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S310.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s310", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:195:0": "이(가) 적군의\n핵심인 듯하니, 무찔러야 합니다",
    "7:196:0": "의 병력이\n많으니, 이를 제압해야 합니다",
    "7:197:0": "의 병력이\n많으니, 제거해야 합니다",
    "7:198:0": "이(가) 적군의\n핵심이니, 공격해야 할 듯합니다",
    "7:199:0": "의 부대를\n무찌르지 않으면 이길 수 없을 것입니다",
    "7:200:0": "의 군대야말로\n가장 먼저 토벌해야 합니다",
    "7:201:0": "의 병력이\n적으니, 노려야 할 듯합니다",
    "7:202:0": "의 군대는\n소수이니, 먼저 치는 것이 상책입니다",
    "7:203:0": "은(는)\n병력이 적어 무찌르기 쉬울 듯합니다",
    "7:204:0": "이(가) 이끄는\n병력은 적으니, 노릴 만합니다",
    "7:205:0": "은(는)\n병력이 적어 적군의 약점인 듯합니다",
    "7:206:0": "의 병력은\n미미하니, 그 약점을 찌릅시다",
    "7:207:0": "이쪽에서 먼저 공격하는 것이\n상책이라 생각합니다",
    "7:208:0": "이대로 공격하는 것이 좋겠습니다.\n어떻습니까",
    "7:209:0": "그쪽에서 공격하는 방안이\n좋을 듯합니다",
    "7:210:0": "이쪽을 제압하는 것이 좋다고\n생각합니다",
    "7:211:0": "그 땅을 제압해야 할 듯합니다.\n어떻게 생각하십니까",
    "7:212:0": "그 땅을 얻으면\n우리 가문에 도움이 될 것입니다",
    "7:213:0": "등용할 무장을 선택하십시오",
    "7:214:0": "처단할 무장을 선택하십시오",
}

STATIC_COORDINATES: set[str] = {
    "7:207:0", "7:208:0", "7:209:0", "7:210:0", "7:211:0", "7:212:0", "7:213:0", "7:214:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S310", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
