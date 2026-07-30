#!/usr/bin/env python3
"""Build Base authoring segment 603 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S603.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s603", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1140:0": "아직 승부는\n결정되지 않았습니다!",
    "9:1141:0": "분기하라!\n싸움은 이제부터다!",
    "9:1142:0": "마지막 순간까지\n승부는 결정되지 않습니다",
    "9:1143:0": "안 되겠군…… 모두 이길 의지를\n잃어 가고 있다……",
    "9:1144:0": "이래서는\n지고 말겠어……",
    "9:1145:0": "……미련 없이 스러질 뿐이다",
    "9:1146:0": "미련 없이 패배를\n인정해야 하는가……",
    "9:1147:0": "외통수인 듯하군요……",
    "9:1148:0": "……다들 왜 그러느냐?\n함성이 들리지 않는다!",
    "9:1149:0": "병사들의…… 마음이\n꺾이고 말았는가……",
    "9:1150:0": "그야말로 의기소침……\n이래서는……",
    "9:1151:0": "에잇, 포기하지 마라!\n아직 포기할 때가 아니다!",
    "9:1152:0": "사기가 오르지 않는다\n이대로는……",
    "9:1153:0": "이대로는\n싸울 형편이 못 된다……",
    "9:1154:0": "이제는\n시간문제겠군요……",
    "9:1155:0": "부디 나쁜 꿈이기를……",
    "9:1156:0": "이거 승산이 있다!\n공세를 늦추지 마라!",
    "9:1157:0": "기세를 타고\n무훈을 세워라!",
    "9:1158:0": "이 승기를\n놓칠 수는 없다!",
    "9:1159:0": "흐름을 잡았다\n이제 공격만 남았다!",
    "9:1160:0": "적이 주춤하고 있다\n지금이 공격할 때다!",
    "9:1161:0": "약점을 파고드는 것이\n싸움의 정석이다!",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S603", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
