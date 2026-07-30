#!/usr/bin/env python3
"""Build Base authoring segment 651 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S651.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s651", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2146:0": "이(가) 꾸민\n책략이라고?　가소롭군!",
    "9:2147:0": "은(는)…… 어떻게든\n제가 간파했습니다만",
    "9:2148:0": "마음을 비우면\n",
    "9:2148:1": "도 나를 흔들 수 없다",
    "9:2149:0": "도\n실패하면 무의미하다",
    "9:2150:0": "은(는) 실패……\n그런 셈입니까",
    "9:2151:0": "라는\n이름이 아깝구나",
    "9:2152:0": "후후―",
    "9:2152:1": "\n무슨 속셈입니까",
    "9:2153:0": "가소롭기 짝이 없구나!\n생각이 얕다―",
    "9:2154:0": "속셈은 전부 간파했습니다\n",
    "9:2155:0": "을(를) 쓸 상대를\n잘못 골랐군!",
    "9:2156:0": "이따위 것에\n누가 놀라겠느냐?",
    "9:2157:0": "혼란 따위는 일으키게 두지 않는다!",
    "9:2158:0": "조금이라도 방심했다면\n위험할 뻔했군",
    "9:2159:0": "그런 수법은\n이미 지겹도록 보았습니다",
    "9:2160:0": "……대체 어떤\n속셈이었던 것이냐?",
    "9:2161:0": "이 몸―",
    "9:2161:1": "이(가)\n혼란에 빠질 줄 알았나?",
    "9:2162:0": "허허……\n참으로 진부한 수법이군",
    "9:2163:0": "통하지 않는구나……\n안됐구나!",
    "9:2164:0": "그런 수법에 놀랄 줄\n알았습니까?",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2146:0",
    "9:2147:0",
    "9:2148:0",
    "9:2148:1",
    "9:2149:0",
    "9:2150:0",
    "9:2151:0",
    "9:2152:0",
    "9:2152:1",
    "9:2153:0",
    "9:2154:0",
    "9:2155:0",
    "9:2161:0",
    "9:2161:1",
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
    print(ENGINE.json.dumps({"status": "ok","segment": "base_msggame_B001_S651", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
