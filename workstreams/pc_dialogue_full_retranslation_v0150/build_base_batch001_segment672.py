#!/usr/bin/env python3
"""Build Base authoring segment 672 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S672.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s672", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:2539:0": "퇴각로를 노리다니…\n우리가 요격하러 간다",
    "9:2540:0": "퇴각로를 노리다니 괘씸하구나\n",
    "9:2540:1": "이(가) 나서겠노라",
    "9:2541:0": "퇴각로가 위험합니다!\n요격하겠습니다!",
    "9:2542:0": "퇴각로에 괴한이 나타났다!\n이 몸―",
    "9:2542:1": "이(가) 처단하리라!",
    "9:2543:0": "퇴각로를 지켜야 합니다\n적군을 요격하겠습니다",
    "9:2544:0": "퇴각로가 위태롭다\n요격한다!",
    "9:2545:0": "선봉대―",
    "9:2545:1": "이(가) 전투를 시작한다",
    "9:2546:0": "첫 공을 세운 이는 나,\n",
    "9:2546:1": "이다!",
    "9:2547:0": "이(가) 첫 공을 세웠다!\n따르라!　돌격하라!",
    "9:2548:0": "첫 공은 내가 차지했다!\n",
    "9:2548:1": "―나아간다!",
    "9:2549:0": "이 몸―",
    "9:2549:1": "이(가)\n첫 공을 세웠습니다!",
    "9:2550:0": "은(는)",
    "9:2550:1": "!\n이 전투의 첫 공은 내 것이다!",
    "9:2551:0": "이번 첫 공의 주인공은\n바로―",
    "9:2551:1": "이다!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2540:0",
    "9:2540:1",
    "9:2542:0",
    "9:2542:1",
    "9:2545:0",
    "9:2545:1",
    "9:2546:0",
    "9:2546:1",
    "9:2547:0",
    "9:2548:0",
    "9:2548:1",
    "9:2549:0",
    "9:2549:1",
    "9:2550:0",
    "9:2550:1",
    "9:2551:0",
    "9:2551:1",
}


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
                "segment": "base_msggame_B001_S672",
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
