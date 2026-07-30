#!/usr/bin/env python3
"""Build Base authoring segment 333 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S333.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s333", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:578:0": "미안하오, 「",
    "7:578:1": "」 님의 부탁이라도\n",
    "7:578:2": "와(과)는 싸울 수 없소\n병사는 물릴 테니 안심하시오",
    "7:579:0": "의 부탁이라도\n",
    "7:579:1": "와(과)는 싸울 수 없겠군\n미안하지만 여기서 물러나겠어",
    "7:580:0": "미안하오, 「",
    "7:580:1": "」 공의 부탁이라 해도\n",
    "7:580:2": "와(과)는 싸울 수 없소\n여기서는 물러나도록 하겠소",
    "7:581:0": "와(과) 맞서 싸우신단 말이오?\n으음, 송구하오나\n도와드릴 수는 없소이다",
    "7:582:0": "와(과) 싸우시는 겁니까?\n죄송합니다만\n이번에는 손을 떼겠습니다",
    "7:583:0": "님의 부탁이라 하여도\n",
    "7:583:1": "와(과)는 싸울 수 없소\n이번에는 물러나겠소",
    "7:584:0": "으음, 그렇게 말씀하셔도…\n",
    "7:584:1": "에게는 거스를 수 없소\n부디 이해해 주시오",
    "7:585:0": "아니, 미안하오. 이쪽에도 사정이 있어서…\n",
    "7:585:1": "와(과)는 싸울 수 없소\n다음에 다시 불러 주시오",
    "7:586:0": "아무리 「",
    "7:586:1": "」 공의 청이라 해도\n",
    "7:586:2": "와(과)도 친하게 지내는 사이니\n이 이야기는 없던 일로 해 주시게",
    "7:587:0": "의 병량이 고갈되어 병력 감소 중",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S333", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
