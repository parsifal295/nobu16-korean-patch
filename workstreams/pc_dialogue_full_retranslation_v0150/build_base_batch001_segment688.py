#!/usr/bin/env python3
"""Build Base authoring segment 688 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S688.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s688", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:2866:0": "적을 통과시키지 마라!\n요충지는 내주지 않겠다!",
    "9:2867:0": "버티십시오!\n요충지를 지키는 겁니다!",
    "9:2868:0": "버텨라!\n요충지를 내주지 마라!",
    "9:2869:0": "다른 곳으로 옮길까",
    "9:2870:0": "다른 곳으로\n이동을 시작한다",
    "9:2871:0": "이곳을 떠나기로 하자",
    "9:2872:0": "더 나은 위치로\n이동하겠습니다",
    "9:2873:0": "다른 곳으로 옮기자",
    "9:2874:0": "여기는 이제 됐다\n이동하겠다",
    "9:2875:0": "병력을 진군시키자",
    "9:2876:0": "이동하기로 하자",
    "9:2877:0": "맡은 위치를 떠나겠습니다",
    "9:2878:0": "좋은 위치로 이동한다",
    "9:2879:0": "다른 곳으로 이동하겠습니다",
    "9:2880:0": "여기서는 원호하기 어렵다\n이동하겠다",
    "9:2881:0": "녀석들아, 쉬어라\n당분간 여기 머문다",
    "9:2882:0": "지금은 기다리자\n반드시 기회는 온다",
    "9:2883:0": "상황을 파악한다\n여기서 대기하라",
    "9:2884:0": "전황을 살펴보겠습니다\n당분간 대기하겠습니다",
    "9:2885:0": "움직임을 살핀다\n여기서 대기한다",
    "9:2886:0": "지금 움직일 필요는 없다\n잠시 대기하라",
    "9:2887:0": "상황을 파악한 뒤\n움직이면 될 것이다",
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
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
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
                "segment": "base_msggame_B001_S688",
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
