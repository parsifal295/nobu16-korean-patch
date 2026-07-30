#!/usr/bin/env python3
"""Build Base authoring segment 716 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S716.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s716", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3428:0": "요충지를 제압할 호기입니다\n신속히 장악해 지리적 이점을 얻읍시다",
    "9:3429:0": "요충지 제압을 노려볼 만하오\n부대를 보내는 건 어떻소",
    "9:3430:0": "요충지를 제압할 수 있을 듯합니다\n부대를 보내시는 게 어떻겠습니까",
    "9:3431:0": "요충지 제압을 노려볼 만하오\n부대를 보내는 건 어떻소",
    "9:3432:0": "요충지를 제압할 수 있을 듯합니다\n부대를 보내시는 게 어떻겠습니까",
    "9:3433:0": "요충지 제압을 노려볼 만하오\n부대를 보내는 건 어떻소",
    "9:3434:0": "인가! 잘됐군\n자, 힘을 겨뤄 보자고!",
    "9:3435:0": "저자는 「",
    "9:3435:1": "」인가!\n좋은 승부가 되겠군! 쳐라!",
    "9:3436:0": "인가!\n훌륭한 상대다, 쳐라!",
    "9:3437:0": "의 모습을 발견했습니다\n제가 직접 처치해 보이겠습니다",
    "9:3438:0": "저자는 「",
    "9:3438:1": "」인가!\n「",
    "9:3438:2": "」, 직접 상대해 주마!",
    "9:3439:0": ", 여기 있었군\n그냥 지나칠 수는 없지, 간다!",
    "9:3440:0": "저자는 「",
    "9:3440:1": "」인가!\n베어 내 공으로 삼으리라!",
    "9:3441:0": ", 여기 있었느냐!\n훌륭한 상대로군, 쳐라!",
    "9:3442:0": ", 여기 있었군요\n겨뤄 보시지요! 갑니다!",
    "9:3443:0": "인가, 과연 그렇군\n",
    "9:3443:1": "에게 도전해 보라!",
    "9:3444:0": "저자는 「",
    "9:3444:1": "」…\n반드시 베어 넘기겠습니다",
}

STATIC_COORDINATES = {f"9:{record_id}:0" for record_id in range(3428, 3434)}
DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS) - STATIC_COORDINATES


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
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_"
                    "context_where_available"
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
                "segment": "base_msggame_B001_S716",
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
