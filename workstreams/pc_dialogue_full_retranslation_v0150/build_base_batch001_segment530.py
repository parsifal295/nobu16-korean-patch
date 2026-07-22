#!/usr/bin/env python3
"""Build Base authoring segment 530 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S530.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s530", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:738:0": "무장한 백성들이 집회를 열고 있습니다…\n잇키일지도 모르옵니다",
    "8:739:0": "영민의 눈에 살기가 서려 있군…\n잇키의 조짐이 느껴지는구나",
    "8:740:0": "백성의 신뢰가 땅에 떨어졌소…\n잇키를 경계해야 할 듯하오",
    "8:741:0": "백성들이 자포자기하였습니다\n잇키를 조심하십시오",
    "8:742:0": "마을 사람들이 노했구나\n잇키가 일어날 수도 있겠군",
    "8:743:0": "백성도 이제 한계입니다…\n이대로라면 잇키가…",
    "8:744:0": "백성의 불신이 극에 달했소…\n한바탕 소동이 벌어지겠군…",
    "8:745:0": "잇키가 일어날 듯합니다\n백성의 움직임을 경계하십시오",
    "8:746:0": "(이)라면\n수해도 막을 수 있겠지요",
    "8:747:0": "의 제방은 튼튼하다고\n태풍 따위에 질쏘냐!",
    "8:748:0": "은(는) 치수가\n빈틈없이 되어 있사옵니다",
    "8:749:0": "의 제방이라면\n어떤 폭풍도 적수가 아니다",
    "8:750:0": "은(는) 수해에 대한\n대비가 빈틈없군요",
    "8:751:0": "태풍아, 어디 한번 와 보아라!\n",
    "8:751:1": "은(는) 끄떡없이 견뎌 내리라",
    "8:752:0": "(이)라면 수해에도\n제법 견딜 수 있을 듯합니다",
    "8:753:0": "은(는) 수해에 강한\n마을이 잘 조성되어 있습니다",
    "8:754:0": "(이)라면\n수해 걱정도 없겠구나",
    "8:755:0": "의 제방은 견고하니\n태풍에도 끄떡없습니다",
    "8:756:0": "의 하천 정비는\n거의 완벽하다고 할 만하오",
    "8:757:0": "에서는 수해를\n걱정할 필요가 없겠군요",
}

STATIC_COORDINATES = {f"8:{record_id}:0" for record_id in range(738, 746)}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S530", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
