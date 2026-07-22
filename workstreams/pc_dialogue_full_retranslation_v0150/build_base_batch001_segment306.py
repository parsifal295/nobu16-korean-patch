#!/usr/bin/env python3
"""Build Base authoring segment 306 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S306.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s306", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:122:0": "여기서는 내 생각을\n모두에게 밝히도록 하겠다",
    "7:123:0": "여기서는 한눈팔지 말고\n곧장 그 땅으로 향해야 합니다",
    "7:124:0": "병법에서는 완벽함보다 졸속을 중시합니다.\n서둘러 향하는 것이 좋겠습니다",
    "7:125:0": "병법에서는 신속을 귀히 여기옵니다.\n곧장 향해야 할 줄 아뢰옵니다",
    "7:126:0": "여기서는 잔꾀를 부리지 말고,\n단숨에 향해야 하옵니다",
    "7:127:0": "그 땅까지 단숨에 내달리는 것이\n가장 좋은 계책인 줄 아뢰옵니다",
    "7:128:0": "서둘러 나아가면 상대의 허를\n찌를 수도 있을 것입니다",
    "7:129:0": "바람처럼 빠르게 적의 성으로\n공격해 들어가야 하옵니다",
    "7:130:0": "적의 성으로 향해야 할 듯합니다.\n지금은 완벽함보다 졸속이 중요합니다",
    "7:131:0": "누구보다 먼저 적의 성을 함락하면\n적은 아무것도 하지 못할 것이오",
    "7:132:0": "지금은 적의 성으로 향해,\n서둘러 함락해야 할 듯합니다",
    "7:133:0": "적의 성으로 진격합시다.\n이 기회를 놓치는 것은 하책입니다",
    "7:134:0": "단숨에 적의 성으로 향해\n우리 것으로 삼아야 하옵니다",
    "7:135:0": "적군이 움직이기 전에\n그 땅을 제압하고 오겠습니다",
    "7:136:0": "양군이 맞붙기 전에,\n그 땅을 손에 넣읍시다",
    "7:137:0": "적군과 일전을 치르더라도,\n먼저 이 땅을 제압해야 할 듯합니다",
    "7:138:0": "적이 움직이기 전에,\n재빨리 평정합시다",
    "7:139:0": "신속히 움직이면 적에게\n들키지 않고 빼앗을 수 있사옵니다",
    "7:140:0": "속히 손안에 넣읍시다.\n싸움조차 되지 않을 것입니다",
    "7:141:0": "적군이 들이닥치기 전에\n물리쳐야 할 것입니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S306", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
