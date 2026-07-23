#!/usr/bin/env python3
"""Build Base authoring segment 551 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S551.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s551", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:997:0": "의 공략을 앞둔 지금\n이 땅을 맡은 의미를 되새기며\n힘껏 정진하",
    "8:998:0": ", 맡겨",
    "8:998:1": "\n반드시 풍요로운 땅으로 만들어 보이",
    "8:999:0": "이 영지, 분명히 맡",
    "8:999:2": "기대에 부응해 보이",
    "8:1000:0": "이 땅을 풍요롭게 하기 위해\n미력하나마 힘쓰",
    "8:1001:0": "\n적의 표적이 될 전선의 성이니\n내 장기인 방비도 손보",
    "8:1002:0": "전선의 성을 맡게 되어 영광",
    "8:1002:1": "\n적의 침공을 막는 일은 자신 있는 바\n",
    "8:1002:2": "의 수완을 기대하",
    "8:1003:0": "어떻게 다스리고, 어떻게 지킬 것인가…\n전선의 성주로서, 나의 수성술을\n남김없이 발휘하",
    "8:1004:0": "주변 세력의 위협은 없어 보이",
    "8:1004:1": "\n당분간 내정에 힘을 쏟아\n차분히 자리 잡고 임지를 발전시키",
    "8:1005:0": "\n언제 전장에 불려가더라도\n채비를 빈틈없이 갖추",
    "8:1006:0": "성주로서 내 무예를 떨칠 수 있다니\n감사의 말도",
    "8:1006:1": "\n반드시 무공으로 이어 보이",
    "8:1007:0": "그 성, 분명히 맡",
    "8:1007:1": "\n내 본분인 무공을 떨칠 수 있도록\n통치에 힘쓸 생각",
    "8:1008:0": "적국으로 원정하기에는 어려운 땅",
    "8:1008:1": "\n차분히 자리 잡고, 우선 이 땅에서\n적과 맞설 수 있는 국력을 갖추",
    "8:1009:0": "\n내 지략으로 이 성을 활용해\n전선을 지원해 보이",
}

STATIC_COORDINATES: set[str] = set()


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S551", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
