#!/usr/bin/env python3
"""Build Base authoring segment 579 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S579.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s579", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:627:0": "철수하겠다……우리 병사들의 원수를\n갚아 주게―",
    "9:628:0": "살았군……\n이만 물러나겠네",
    "9:629:0": "뒷일은……\n부디 부탁드리오",
    "9:630:0": "이래서는 싸울 수 없겠군……\n뒤는 맡기겠노라",
    "9:631:0": "죄송합니다\n뒤는 부탁드립니다",
    "9:632:0": "유감이지만……\n물러나도록 하겠습니다",
    "9:633:0": "죄송합니다\n뒤는 맡기겠습니다……",
    "9:634:0": "고맙소……\n이만 물러가겠소",
    "9:635:0": "모두 한꺼번에\n박살 내 주마!",
    "9:636:0": "적장의 목을 베어\n보이리라!",
    "9:637:0": "에\n도전할 자가 있느냐!",
    "9:638:0": "이(가) 나설\n차례인 듯하군요",
    "9:639:0": "바로―",
    "9:639:1": "이(가)\n상대해 주마",
    "9:640:0": "자…… 어찌 공격하고\n어찌 무너뜨릴까……?",
    "9:641:0": "이제부터는\n",
    "9:641:1": "이(가) 상대해 드리겠소",
    "9:642:0": "은(는)\n호락호락한 상대가 아니다!",
    "9:643:0": "마음대로 하게\n두지 않겠습니다!",
    "9:644:0": "내 차례인 듯하군\n간다!",
    "9:645:0": "만회할 기회는\n아직 있습니다",
    "9:646:0": "이제부터 상대할 자는―\n",
    "9:646:1": "이다!",
    "9:647:0": "저 대장 놈, 꽁무니를 빼고\n도망쳤구나!",
    "9:648:0": "대장이 등을 보이다니\n꼴사납도다!",
}

STATIC_COORDINATES: set[str] = {
    "9:628:0",
    "9:629:0",
    "9:630:0",
    "9:631:0",
    "9:632:0",
    "9:633:0",
    "9:634:0",
    "9:635:0",
    "9:636:0",
    "9:640:0",
    "9:643:0",
    "9:644:0",
    "9:645:0",
    "9:647:0",
    "9:648:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S579", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
