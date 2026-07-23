#!/usr/bin/env python3
"""Build Base authoring segment 649 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S649.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s649", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2106:0": "으으윽……\n상당한 타격입니다……",
    "9:2107:0": "은(는) 자비도\n손속도 모르는가!",
    "9:2108:0": "아직 한참 더 싸울 수 있어!",
    "9:2109:0": "통하지 않는군……\n이것이 무예의 격차다",
    "9:2110:0": "호오…… 그렇게 나왔는가",
    "9:2111:0": "그 수는 흥미롭군……",
    "9:2112:0": "이 몸―",
    "9:2112:1": "에게\n작으나마 타격을……",
    "9:2113:0": "……감당할 만한 수준이다\n소란 떨지 마라!",
    "9:2114:0": "다행히 피해는\n그리 크지 않은 모양입니다",
    "9:2115:0": "후우…… 이 정도로\n끝났는가……",
    "9:2116:0": "그 수를 택하셨군요",
    "9:2117:0": "통했다고 할 수도 없구나",
    "9:2118:0": "이 정도로는\n흔들리지 않습니다",
    "9:2119:0": "더 과감하게\n공격해 와라!",
    "9:2120:0": "이게 대체 뭐야!\n",
    "9:2120:1": "의 탓이냐!",
    "9:2121:0": "은(는) 가공할 만하구나\n병사들이 완전히 혼란에 빠졌다",
    "9:2122:0": "의 책략이라니……\n약삭빠르고 건방지구나……!",
    "9:2123:0": "의 소행이라니\n마음에 들지 않는군요",
    "9:2124:0": "…… 담대한\n우리 병사들마저 이 꼴인가!",
    "9:2125:0": "이것은―",
    "9:2125:1": "……!\n그야말로 혼란의 지옥이로다!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2107:0",
    "9:2112:0",
    "9:2112:1",
    "9:2120:0",
    "9:2120:1",
    "9:2121:0",
    "9:2122:0",
    "9:2123:0",
    "9:2124:0",
    "9:2125:0",
    "9:2125:1",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S649", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
