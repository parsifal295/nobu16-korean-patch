#!/usr/bin/env python3
"""Build Base authoring segment 311 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S311.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s311", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:215:0": "등용에 응하지 않는 무장입니다",
    "7:216:0": "처단할 수 없는 무장입니다",
    "7:217:0": "적장을 포박하",
    "7:217:1": "\n포박한 무장의 처우를 정해 주",
    "7:218:0": "이(가)\n적장을 포박하",
    "7:218:1": "\n포박한 무장의 처우를 정해 주",
    "7:219:0": "처단할 무장을 선택하십시오.\n처단하지 않는 자는 해방됩니다",
    "7:220:0": "귀공을 섬기는 것도 한 가지 흥취로군",
    "7:221:0": "이 노부나가를 복종시켜 보아라",
    "7:222:0": "이 몸의 활약을 똑똑히 지켜보시오!",
    "7:223:0": "목숨이 다할 때까지 모시겠습니다!",
    "7:224:0": "목숨을 걸고 모시겠소",
    "7:225:0": "귀공의 곁에서 배우겠소",
    "7:226:0": "섬길 만한 주군이로군",
    "7:227:0": "좋다, 솜씨를 지켜보겠다",
    "7:228:0": "섬기기로 하지",
    "7:229:0": "귀공을 위해 일하겠소",
    "7:230:0": "무엇이든 분부해 주소서",
    "7:231:0": "내 지혜를 모두 쏟아 섬기겠다",
    "7:232:0": "좋아, 귀공을 섬기겠다!",
}

STATIC_COORDINATES: set[str] = {
    "7:215:0", "7:216:0", "7:219:0", "7:220:0", "7:221:0", "7:222:0", "7:223:0", "7:224:0",
    "7:225:0", "7:226:0", "7:227:0", "7:228:0", "7:229:0", "7:230:0", "7:231:0", "7:232:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S311", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
