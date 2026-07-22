#!/usr/bin/env python3
"""Build Base authoring segment 49 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S49.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s49", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:657:0": "어쨌든 마을에서\n병사를 징발해야겠군",
    "6:658:0": "영민들이\n나를 두려워하는군…",
    "6:659:0": "영지를 다스리는 일도\n모두 빈틈없다",
    "6:660:0": "시끄러운 마을 관리의 악소문을\n퍼뜨려 주었지",
    "6:661:0": "영지를 경영하는 요령은\n아랫사람에게 맡기는 것",
    "6:662:0": "하급 관리들이 영지를 잘\n다스리고 있으려나요",
    "6:663:0": "마을 장로들과는\n잘 지내고 있느니라",
    "6:664:0": "요즘 마을 젊은것들은…\n옛날에는 더…",
    "6:665:0": "영지를 더 살기 좋게 할\n방법이 떠오르지 않으려나",
    "6:666:0": "아아, 영지 따위\n될 대로 되어라!",
    "6:667:0": "어쨌든 단련하라고\n내 영지에 엄명해야겠군",
    "6:668:0": "영민 전원을 병사로 삼고 싶다…",
    "6:669:0": "주군께 받은 영지\n힘써 다스립시다",
    "6:670:0": "영민 여러분이\n지나치게 눈치를 봅니다…",
    "6:671:0": "너그럽게 대하면\n백성은 기어오르니 말이다",
    "6:672:0": "엄하게 다스리면 달아나고…\n통치란 어려운 것이야",
    "6:673:0": "남들의 의지가 된다는 것도\n고달픈 일이구먼!",
    "6:674:0": "정말 바빠서\n못 해먹겠군!",
    "6:675:0": "가문을 위해서라면\n이 정도 바쁨쯤이야!",
    "6:676:0": "이 바쁜 나날도\n",
    "6:676:1": "에 대한 신뢰의 증표",
}

DYNAMIC_RUNTIME_COORDINATES = {"6:676:0", "6:676:1"}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S49",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
