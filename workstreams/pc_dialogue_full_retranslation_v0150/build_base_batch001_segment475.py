#!/usr/bin/env python3
"""Build Base authoring segment 475 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S475.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s475", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2697:0": "이만하면 됐다……이토록 공을 세울 수 있었던 것도\n미하타와 다테나시의 가호 덕분이다",
    "7:2698:0": "음, 훌륭한 전공이로다",
    "7:2699:0": "공은 발에 있다……음",
    "7:2700:0": "백만일심……모두의 전과가 모여\n오늘의 승리를 이룬 것이로군",
    "7:2701:0": "화려하진 않아도 묵직한 활약……이라 할 만하군",
    "7:2702:0": "어떠냐, 내 전공도 뒤지지 않는다!",
    "7:2703:0": "아쉽게도 전공 제일은 놓쳤지만\n제법 큰 공이로다",
    "7:2704:0": "제법 큰 공을 세울 수 있었군",
    "7:2705:0": "내 공이 태평한 세상으로 나아가는 확실한 한 걸음이 되겠지요",
    "7:2706:0": "이 몸도 승리를 위해\n제법 힘썼다고?",
    "7:2707:0": "뭐, 대충 이런 거지!",
    "7:2708:0": "무명을 떨치기에는\n내 무훈이 아직 부족한가",
    "7:2709:0": "보아라, 나의 무훈이 이와 같도다!",
    "7:2710:0": "그자의 공, 그리고 모두의 공이 있었기에\n오늘의 승리를 거둔 것이다",
    "7:2711:0": "무훈은 그럭저럭이군\n이 결과를 겸허히 받아들이자",
    "7:2712:0": "도 나름대로\n도움이 된 모양이군요",
    "7:2713:0": "전공 제일에는 이르지 못했지만\n승리에 공헌할 수 있었던 듯합니다",
    "7:2714:0": "내 무공도 상당한 편이다만……\n그자에게는 미치지 못하는군",
    "7:2715:0": "충분한 공이로다\n승리만 거두면 그만이다",
    "7:2716:0": "무공도 좋지만\n지휘야말로 칭찬해야 하지 않겠소?",
}

STATIC_COORDINATES: set[str] = {
    "7:2697:0",
    "7:2698:0",
    "7:2699:0",
    "7:2700:0",
    "7:2701:0",
    "7:2702:0",
    "7:2703:0",
    "7:2704:0",
    "7:2705:0",
    "7:2706:0",
    "7:2707:0",
    "7:2708:0",
    "7:2709:0",
    "7:2710:0",
    "7:2711:0",
    "7:2713:0",
    "7:2714:0",
    "7:2715:0",
    "7:2716:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S475", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
