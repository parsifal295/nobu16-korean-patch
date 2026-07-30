#!/usr/bin/env python3
"""Build Base authoring segment 313 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S313.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s313", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:253:0": "충절을 다하겠습니다",
    "7:254:0": "좋다, 섬기겠다!",
    "7:255:0": "내 활약을 보여 드리겠소!",
    "7:256:0": "섬기겠사옵니다",
    "7:257:0": "몸이 닳도록 일하겠습니다",
    "7:258:0": "귀공을 섬기겠습니다",
    "7:259:0": "이제부터 충성을 다해 힘쓰겠사옵니다",
    "7:260:0": "……이렇게 된 이상 어쩔 수",
    "7:260:1": "\n이후로는 귀 가문을 섬기",
    "7:261:0": "의 아량에 감사",
    "7:261:1": "\n이제부터 충성을 다해 힘쓰",
    "7:262:0": "권유에 감사",
    "7:262:1": "\n포박의 치욕을\n공을 세워 씻어 내 보이",
    "7:263:0": "을(를) 위해 일할 수 있다면\n마다할 이유가",
    "7:263:1": "\n기꺼이 힘을 다하",
    "7:264:0": "을(를) 따르는 데\n무슨 이의가 있",
    "7:264:1": "인가",
    "7:265:0": "귀 가문의 부름을 감사히 받",
    "7:265:2": "을(를) 위해서라면\n이 몸을 아끼지 않고 일하",
    "7:266:0": "이제 주군을 잃은 몸이니\n지난날의 적이라 해도 원한은 없소\n삼가",
}

STATIC_COORDINATES: set[str] = {
    "7:253:0", "7:254:0", "7:255:0", "7:256:0", "7:257:0", "7:258:0", "7:259:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S313", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
