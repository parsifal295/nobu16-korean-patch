#!/usr/bin/env python3
"""Build Base authoring segment 181 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S181.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s181", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3182:0": "우리의 맹약도 더욱 굳건해졌소\n앞으로도 잘 부탁드리오",
    "6:3183:0": "우리의 맹약도 굳건해졌군\n앞으로도 잘 부탁하네",
    "6:3184:0": "우리의 맹약이 굳건해졌군요\n앞으로도 잘 부탁드립니다",
    "6:3185:0": "우리의 맹약도 이제 굳건해졌군\n앞으로도 잘 부탁하네",
    "6:3186:0": "우리의 맹약은 오래 이어질수록 굳건해지는 법\n앞으로도 함께 번영해 나가세",
    "6:3187:0": "우리의 동맹도 더욱 굳건해졌군\n앞으로도 잘 부탁하네",
    "6:3188:0": "이 동맹도 더욱 굳건해졌구나\n앞으로도 잘 부탁하네!",
    "6:3189:0": "동맹이 굳건해졌군요\n앞으로도 잘 부탁드립니다",
    "6:3190:0": "우리의 동맹은 굳건해졌다\n앞으로도 잘 부탁한다",
    "6:3191:0": "저희의 유대는\n한층 더 굳건해졌습니다\n앞으로도 의지하겠습니다",
    "6:3192:0": "우리의 동맹도 더욱 굳건해졌다\n앞으로도 잘 부탁하네",
    "6:3193:0": "재밌군, 손을 잡아 주지\n단, 잠시 동안만이다\n그 뒤의 일은 그때 가서 생각할란다",
    "6:3194:0": "동맹 제의, 잘 알겠다\n당분간 손을 잡도록 하지\n그다음 일은 그때 다시 논하세",
    "6:3195:0": "동맹 제의를 받아들이지\n잠시 맹약을 맺도록 하세\n그 뒤의 일은 그때 가서 보세",
    "6:3196:0": "동맹 제의, 잘 알겠습니다\n당분간 손을 잡도록 하지요\n그 뒤의 일은 그때 가서 이야기하지요",
    "6:3197:0": "맹약, 받아들이지\n당분간 손을 잡도록 하세\n그 뒤의 일은 그때 가서 보세",
    "6:3198:0": "동맹 제의를 받아들이지\n당분간은 손을 잡도록 하세\n그 뒤의 일은 그때 생각하면 될 터",
    "6:3199:0": "동맹 제의를 받아들이지\n당분간 손을 잡지 않겠나\n그 뒤의 일은 그때 가서 보세",
    "6:3200:0": "동맹 제의, 승낙했다\n당분간 손을 잡도록 하지\n그 뒤의 일은 그때 가서 보세",
    "6:3201:0": "동맹 제의, 받아들이겠습니다\n당분간은 손을 잡도록 하지요\n그 뒤의 일은 그때 다시 이야기해요",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S181", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
