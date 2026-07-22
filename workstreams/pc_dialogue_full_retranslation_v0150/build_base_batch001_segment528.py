#!/usr/bin/env python3
"""Build Base authoring segment 528 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S528.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s528", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:698:0": "불온한 기운도\n자취를 감추었네요",
    "8:699:0": "도 꽤\n안정을 되찾았군",
    "8:700:0": "은(는) 이제\n조략에 현혹되지 않을 것이옵니다",
    "8:701:0": "은(는) 진정되었소\n안심하시오",
    "8:702:0": "점차 안정되고 있습니다\n잇키를 걱정하실 필요는 없습니다",
    "8:703:0": "이제는 다른 가문의 선동에도\n",
    "8:703:1": "은(는) 흔들리지 않소",
    "8:704:0": "이(가) 잇키의 위기에서\n이제 벗어난 모양입니다",
    "8:705:0": "불안정한 상황을 벗어났으니\n",
    "8:705:1": "도 이제는 안심해도 될 듯합니다",
    "8:706:0": "은(는) 이제야 겨우\n안정을 되찾았구려",
    "8:707:0": "제법 안정되었습니다\n걱정은 없을 듯합니다",
    "8:708:0": "민심도 일단 가라앉았다\n선동을 당해도 끄떡없다",
    "8:709:0": "의 민심이라면\n조금은 안심할 수 있겠군요",
    "8:710:0": "다른 가문의 잇키 선동을\n경계하시기를",
    "8:711:0": "잇키가 일어날 것 같아!\n조략을 조심하라고!",
    "8:712:0": "잇키 선동을 당하면\n위험해질 상황인가…",
    "8:713:0": "지금 다른 가문이 부추긴다면\n잇키가 일어남은 필연…",
    "8:714:0": "백성의 불만은 폭발 직전…\n다른 가문이 부추긴다면…",
    "8:715:0": "다른 가문의 조략이 파고들면\n잇키가 일어날 수도 있겠군…",
    "8:716:0": "아직 잇키가 일어나진 않겠으나\n다른 가문의 조략이 파고들면…",
    "8:717:0": "민심이 등을 돌렸으니, 이래서는\n잇키 선동에 더없는 토대",
}

STATIC_COORDINATES = {
    "8:698:0",
    "8:702:0",
    "8:707:0",
    "8:708:0",
    *(f"8:{record_id}:0" for record_id in range(710, 718)),
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S528", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
