#!/usr/bin/env python3
"""Build Base authoring segment 367 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S367.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s367", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:974:1": "」!\n",
    "7:974:2": "은(는) 강한 자를 좋아한다",
    "7:975:0": "에게 이기다니, 믿을 만하군\n아니……",
    "7:975:1": "의 기세는 경계해야 하나\n어쨌든 호의를 보여 두는 편이 낫겠군",
    "7:976:0": "호오……",
    "7:976:1": "에게 이겼는가\n이런 기화는 미리 손에 넣어 두는 법이지\n",
    "7:976:2": "은(는) 높이 평가해 두지",
    "7:977:0": "에게 이겼는가!\n무사는 이기는 것이 근본이지\n",
    "7:977:1": "은(는) 이를 잘 알고 있구나",
    "7:978:0": "에게 이겨 버리다니!\n",
    "7:978:1": "도 제법이군요\n앞으로 잘 지내고 싶은 상대입니다",
    "7:979:0": "이(가) 「",
    "7:979:1": "」에게 이겼다고!?\n그 정도의 세력이라고는 생각지 못했군……\n앞으로는 생각을 고쳐야겠어",
    "7:980:0": "에게 승리하다니……\n",
    "7:980:1": "의 강함은 진짜인 듯합니다\n관계를 재고해 보지요",
    "7:981:0": "에게 이기다니!\n",
    "7:981:1": "을(를) 이용하면\n우리도 천하에 가까워질지 모른다!",
    "7:982:0": "위풍으로 주변 국인중의 우리 가문에 대한 종속도 하락",
    "7:983:0": "에게 져 버렸군……\n",
    "7:983:1": "은(는) 우리가 생각했던 것보다\n훨씬 약한 것 아닌가……?",
}

STATIC_COORDINATES: set[str] = {"7:982:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S367", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
