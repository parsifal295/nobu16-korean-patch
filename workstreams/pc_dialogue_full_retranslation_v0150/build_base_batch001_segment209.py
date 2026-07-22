#!/usr/bin/env python3
"""Build Base authoring segment 209 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S209.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s209", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3530:0": "훈공 1위는 당연하지\n가신 필두라 할 만한 지위에 있는 몸이다\n남에게 내줘서는 무문의 수치로다!",
    "6:3531:0": "훈공의 선두에 서게 되다니\n더없는 영광으로 여기",
    "6:3531:1": "\n앞으로도 우리 가문을 더욱 융성케 하",
    "6:3532:0": "은(는) 말하자면 가신들의 얼굴…\n훈공 1위를 차지하",
    "6:3532:1": "지 못해서는\n",
    "6:3532:2": "의 패업을 받들기에는 역부족",
    "6:3533:0": "의",
    "6:3533:1": "이(가) 일등",
    "6:3533:2": "\n더없이 감사한 일…이옵니다",
    "6:3533:3": "만\n아랫사람들도 더욱 분발해 주었으면 합니다",
    "6:3534:0": "신하의 도를 닦는 길에는 끝이 없으니…\n우리 가문의 앞날을 지켜보는 것이야말로\n",
    "6:3534:1": "의 천명이",
    "6:3535:0": "호오, 훈공 1위라…\n",
    "6:3535:1": "이(가) 되면 할 수 있는 일도 많으니\n활약하는 것도 당연",
    "6:3536:0": "훈공 1위",
    "6:3536:1": "…\n뭐, 거들먹거리기만 하는 것도 지겨워져서\n지위에 걸맞은 몫을 했을 뿐",
    "6:3537:0": "무슨 일이든",
    "6:3537:1": "을(를) 위하고\n보필하는 것이",
    "6:3537:2": "의 소임이니\n훈공 1위 따위는 그에 따라온 것일 뿐",
    "6:3538:0": "훈공 1위라니 주제넘은 일…\n",
}

STATIC_COORDINATES: set[str] = {
    "6:3530:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S209", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
