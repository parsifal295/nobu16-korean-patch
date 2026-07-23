#!/usr/bin/env python3
"""Build Base authoring segment 625 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S625.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s625", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1612:0": "그래!\n그럼 먼저 간다!",
    "9:1613:0": "홀로 가시게 두지는\n않겠사옵니다!",
    "9:1614:0": "알겠다……\n뒤처지지 마라!",
    "9:1615:0": "적을 격멸할 호기다!\n함께 밀어붙입시다!",
    "9:1616:0": "함께 나아가자!",
    "9:1617:0": "함께 가겠소……",
    "9:1618:0": "나란히 말을 몰아\n진군합시다",
    "9:1619:0": "함께 가겠사옵니다!",
    "9:1620:0": "이대로\n밀어붙입시다",
    "9:1621:0": "가세하겠다!\n밀어붙이자!",
    "9:1622:0": "함께 맞섭시다",
    "9:1623:0": "우리도 함께\n나아가겠소!",
    "9:1624:0": "!\n역시 강하구나!",
    "9:1625:0": "!\n멋지게 밀어붙였구나!",
    "9:1626:0": "물 흐르듯\n밀어붙였구나",
    "9:1627:0": "절묘한 지휘\n참으로 훌륭하십니다",
    "9:1628:0": "오오, 무력으로 압도했는가!",
    "9:1629:0": "흠……\n제법이로군……",
    "9:1630:0": "참으로 훌륭한\n활약이시옵니다",
    "9:1631:0": "!\n잘하였도다!",
    "9:1632:0": "과연 대단하십니다!\n",
    "9:1632:1": "!",
    "9:1633:0": "끝까지 밀어붙였는가!\n제법이군!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1624:0",
    "9:1625:0",
    "9:1631:0",
    "9:1632:0",
    "9:1632:1",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required" if static else "pending",
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available"
                ),
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
                "segment": "base_msggame_B001_S625",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
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
