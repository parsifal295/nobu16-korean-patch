#!/usr/bin/env python3
"""Build Base authoring segment 484 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S484.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s484", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2803:0": "전령!",
    "7:2803:1": "와(과) 벌인 전투로,\n",
    "7:2803:2": "이(가) 부상하고 군세도 괴멸했다 하옵니다!",
    "7:2804:0": "이(가) 부상하고 군세가 괴멸",
    "7:2805:0": "을(를) 부상시키고 격파",
    "8:115:0": "병량을 더 많이 얻을 수 있게 됐다!",
    "8:116:0": "병량 수입이 늘었습니다. 개간의 성과입니다",
    "8:117:0": "개간이 진척되어 병량 수확량이 늘었구나",
    "8:118:0": "병량 수확량이 늘어난 듯합니다",
    "8:119:0": "모두의 노력 덕분에 예년보다 쌀 수확량이 늘었다!",
    "8:120:0": "낭보입니다. 병량 수확량이 늘었습니다",
    "8:121:0": "모두의 노력으로 병량 수확량이 늘었습니다",
    "8:122:0": "병량미를 잔뜩 거둘 수 있게 되었습니다",
    "8:123:0": "전답이 개간되어 병량 수확량이 늘었습니다",
    "8:124:0": "병량 수입이 늘었습니다. 개간의 성과로군요",
    "8:125:0": "여러분 덕분에 수확량이 늘었군요",
    "8:126:0": "전답 개발로 병량 수확량이 늘었습니다",
    "8:127:0": "좋았어! 수입이 늘었다!",
    "8:128:0": "마을이 활기를 띠면서 금전 수입이 늘고 있사옵니다",
    "8:129:0": "마을이 활기를 띠고 금전 수입이 늘고 있구나",
    "8:130:0": "상인 마을에서 얻는 수익이 늘어난 듯합니다",
}

STATIC_COORDINATES: set[str] = {
    "8:115:0",
    "8:116:0",
    "8:117:0",
    "8:118:0",
    "8:119:0",
    "8:120:0",
    "8:121:0",
    "8:122:0",
    "8:123:0",
    "8:124:0",
    "8:125:0",
    "8:126:0",
    "8:127:0",
    "8:128:0",
    "8:129:0",
    "8:130:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S484", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
