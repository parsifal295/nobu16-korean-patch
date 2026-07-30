#!/usr/bin/env python3
"""Build Base authoring segment 254 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S254.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s254", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4030:1": "따위는 우리의 적수가 아니다!",
    "6:4031:0": "을(를) 공략할 때가 왔다\n한시라도 빨리 싸울 채비를 갖춰라!",
    "6:4032:0": "의 직, 감사히 받",
    "6:4033:0": "으로(로) 임명되어\n",
    "6:4033:1": "의 국인중이 우리 가문에 완전히 종속되었습니다",
    "6:4034:0": "다른 세력이 취임 중인 역직입니다",
    "6:4035:0": "상대의 위신이 부족합니다",
    "6:4036:0": "슈고직 또는 상대가 보유한 역직보다 상위인 역직만 선택할 수 있습니다",
    "6:4037:0": "상대가 필요국의 성을 하나도 통치하고 있지 않습니다",
    "6:4038:0": "상대가 필요 지방의 성을",
    "6:4038:1": "% 이상 통치하고 있지 않습니다",
    "6:4039:0": "고가 아시카가 가문이 아니면 취임할 수 없습니다",
    "6:4040:0": "쉽사리 수여할 수 없는 역직입니다",
    "6:4041:0": "다른 세력이 취임 중인 역직입니다",
    "6:4042:0": "슈고직 또는 우리 가문이 보유한 역직보다 한 단계 위인 역직만 선택할 수 있습니다",
    "6:4043:0": "필요국의 성을 모두 통치해야 합니다",
    "6:4044:0": "필요 지방의 성을 모두 통치해야 합니다",
    "6:4045:0": "고가 아시카가 가문이 아니면 취임할 수 없습니다",
    "6:4046:0": "쉽사리 수여할 수 없는 역직입니다",
    "6:4047:0": "헌상할 금전이 부족합니다",
}

STATIC_COORDINATES: set[str] = {
    "6:4034:0",
    "6:4035:0",
    "6:4036:0",
    "6:4037:0",
    "6:4039:0",
    "6:4040:0",
    "6:4041:0",
    "6:4042:0",
    "6:4043:0",
    "6:4044:0",
    "6:4045:0",
    "6:4046:0",
    "6:4047:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S254", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
