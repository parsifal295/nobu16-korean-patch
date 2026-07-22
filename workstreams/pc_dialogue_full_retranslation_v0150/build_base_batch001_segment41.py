#!/usr/bin/env python3
"""Build Base authoring segment 41 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S41.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s41", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:512:0": "당연한 응보이지요",
    "6:513:0": "가문을 위한\n좋은 판단이십니다",
    "6:514:0": "처단해야 할 자를…\n참 자비로우시군",
    "6:515:0": "이 처분이\n가문에 도움이 되기를",
    "6:516:0": "두 번 다시\n뵙는 일이 없기를",
    "6:517:0": "엄중한 처분이군…\n내일은 내 차례인가",
    "6:518:0": "지금 와서 생각하면\n추방당해 마땅한 자로다",
    "6:519:0": "과연\n그렇게 나온다 이거지",
    "6:520:0": "군단을 손보는 걸\n좋아하시는군…",
    "6:521:0": "군단을 맡는 것은\n명예로운 일이나…",
    "6:522:0": "군단을 훌륭히\n조정하셨습니다",
    "6:523:0": "군단은 운용이 중요하다",
    "6:524:0": "군단을 어찌 손보느냐가\n우리 가문의 장래를 결정하리…",
    "6:525:0": "상황을 잘\n보고 계시는군요",
    "6:526:0": "역시 군단을\n손보셨군요",
    "6:527:0": "어디에 있든\n무인의 본분을 다할 뿐",
    "6:528:0": "참으로 훌륭한\n조정 솜씨로다",
    "6:529:0": "어찌 세력을 넓힐 것인가\n그 열쇠가 군단이다만…",
    "6:530:0": "군단을 자주 손보는 것\n그 또한 진리",
    "6:531:0": "이렇게 하셨습니까\n그것도 재미있겠군요",
}

DYNAMIC_RUNTIME_COORDINATES: set[str] = set()


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
                "segment": "base_msggame_B001_S41",
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
