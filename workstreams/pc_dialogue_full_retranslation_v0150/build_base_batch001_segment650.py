#!/usr/bin/env python3
"""Build Base authoring segment 650 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S650.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s650", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2126:0": "의 탓에\n공황 상태입니다!",
    "9:2127:0": "로 인해\n야단법석이로구나!",
    "9:2128:0": "이런…… 이래서는\n",
    "9:2128:1": "의 뜻대로다",
    "9:2129:0": "의 책략인가……\n당했군……",
    "9:2130:0": "크윽……",
    "9:2130:1": "에게\n한 수 제대로 당했군요……",
    "9:2131:0": "!\n두고 보자!",
    "9:2132:0": "이, 이거 큰일이군……\n이제 완전히 엉망이야!",
    "9:2133:0": "크윽……!\n당황하지 마라!",
    "9:2134:0": "병사들을 뜻대로\n통솔할 수 없군……",
    "9:2135:0": "이 혼란 자체가\n노림수였습니까……",
    "9:2136:0": "에잇, 진정하라!\n진정하라고 하지 않느냐!",
    "9:2137:0": "우리 군이 혼란에 빠졌다\n……고?",
    "9:2138:0": "이건…… 병사들이 완전히\n동요하고 있지 않은가……!",
    "9:2139:0": "이놈, 병사들이\n명령을 듣지 않는구나!",
    "9:2140:0": "진정하십시오!\n적의 계책입니다!",
    "9:2141:0": "당했군!\n이래서는 움직일 수 없어……",
    "9:2142:0": "감쪽같이\n당하고 말았군요……",
    "9:2143:0": "병사들이 명령을 듣지 않는구나!",
    "9:2144:0": "!\n안됐구나!",
    "9:2145:0": "후우……",
    "9:2145:1": "\n무사히 피했군",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2126:0",
    "9:2127:0",
    "9:2128:0",
    "9:2128:1",
    "9:2129:0",
    "9:2130:0",
    "9:2130:1",
    "9:2131:0",
    "9:2144:0",
    "9:2145:0",
    "9:2145:1",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S650", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
