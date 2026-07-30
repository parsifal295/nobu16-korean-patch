#!/usr/bin/env python3
"""Build Base authoring segment 664 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S664.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s664", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2384:0": "자, 진군이다!\n",
    "9:2384:1": "의 부대와 교대한다!",
    "9:2385:0": "우리 차례인 듯하군\n",
    "9:2385:1": "의 부대와 교대하자",
    "9:2386:0": "진군하라!\n",
    "9:2386:1": "의 부대와 교대한다",
    "9:2387:0": "의 진지로 가\n자리를 교대하겠습니다",
    "9:2388:0": "진군을 개시하라!\n",
    "9:2388:1": "의 부대와 교대다!",
    "9:2389:0": "이제\n",
    "9:2389:1": "을(를) 지원하러 진군할까",
    "9:2390:0": "드디어 우리 차례로군\n",
    "9:2390:1": "의 부대와 교대하겠다",
    "9:2391:0": "자, 진군하자!\n",
    "9:2391:1": "의 부대와 교대한다",
    "9:2392:0": "병사들을 진군시키겠습니다\n",
    "9:2392:1": "의 부대와 교대합니다",
    "9:2393:0": "진군하라!\n",
    "9:2393:1": "의 부대와 교대하겠다",
    "9:2394:0": "의 진지로!\n교대하러 갑시다",
    "9:2395:0": "나아가라!\n",
    "9:2395:1": "의 부대와 교대다",
    "9:2396:0": "버텨라!　녀석들아!\n원군이 올 때까지 조금만 더다!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2384:0",
    "9:2384:1",
    "9:2385:0",
    "9:2385:1",
    "9:2386:0",
    "9:2386:1",
    "9:2387:0",
    "9:2388:0",
    "9:2388:1",
    "9:2389:0",
    "9:2389:1",
    "9:2390:0",
    "9:2390:1",
    "9:2391:0",
    "9:2391:1",
    "9:2392:0",
    "9:2392:1",
    "9:2393:0",
    "9:2393:1",
    "9:2394:0",
    "9:2395:0",
    "9:2395:1",
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
                "segment": "base_msggame_B001_S664",
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
