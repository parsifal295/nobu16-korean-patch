#!/usr/bin/env python3
"""Build Base authoring segment 616 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S616.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s616", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1423:0": "승리합시다!",
    "9:1424:0": "옛!!",
    "9:1425:0": "나아갑시다",
    "9:1426:0": "그럼, 마음껏",
    "9:1427:0": "죽을 각오로 나선다!",
    "9:1428:0": "갑시다!",
    "9:1429:0": "오직 벨 뿐!",
    "9:1430:0": "각오는 되어 있습니다",
    "9:1431:0": "끝까지 싸우겠소!",
    "9:1432:0": "!\n진심으로 겨뤄 보자!",
    "9:1433:0": "와(과)의 싸움을\n내 긍지로 삼으리라!",
    "9:1434:0": "세상에 길이 회자될\n싸움을 벌여 보자!",
    "9:1435:0": "뜻밖이지만\n싸울 수 있어 기쁩니다",
    "9:1436:0": "바라지도 못했던 대결……\n기쁨에 온몸이 떨리는구나!",
    "9:1437:0": "(이)라니……\n기뻐해야 할지 탄식해야 할지",
    "9:1438:0": "좋은 기회로다!\n",
    "9:1438:1": ", 나오시오",
    "9:1439:0": "사양할 것 없다\n어서 덤벼라!",
    "9:1440:0": "\n한 수 배우겠습니다!",
    "9:1441:0": "우리 앞에\n나타나다니!",
    "9:1442:0": "싸워야 할 운명……\n그런 것이군요……",
    "9:1443:0": "싸우고 싶지는 않지만\n이곳은 전장…… 나서겠다!",
    "9:1444:0": "좋다……\n덤벼 봐라!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1432:0",
    "9:1433:0",
    "9:1437:0",
    "9:1438:0",
    "9:1438:1",
    "9:1440:0",
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
                "segment": "base_msggame_B001_S616",
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
