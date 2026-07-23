#!/usr/bin/env python3
"""Build Base authoring segment 717 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S717.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s717", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3445:0": "인가!\n훌륭한 상대다, 쳐라!",
    "9:3446:0": "부터 해치운다!\n약한 자는 방해만 되니까!",
    "9:3447:0": "부터 노리겠다\n손쉽게 무찌를 수 있을 테니!",
    "9:3448:0": "부터 친다\n저자라면 쉽게 물리칠 수 있겠지",
    "9:3449:0": "새 목표는 「",
    "9:3449:1": "」입니다\n약병이니 손쉽게 이길 수 있을 것입니다",
    "9:3450:0": ", 그쪽으로 향한다!\n약병부터 무찔러야 한다!",
    "9:3451:0": "노릴 거라면 「",
    "9:3451:1": "」부터다\n약한 적은 손이 덜 가서 좋구나",
    "9:3452:0": "부터 격파한다\n약병부터 쳐서 적의 수를 줄이리라",
    "9:3453:0": ", 그 정도라면 쉽게 칠 수 있겠구나\n서둘러 무너뜨리자",
    "9:3454:0": ", 그쪽을 노리겠습니다\n힘으로 밀어붙이기만 해도 이길 수 있습니다",
    "9:3455:0": "부터 집중 공격한다\n약한 적을 쓰러뜨려 적의 수를 줄이리라",
    "9:3456:0": "부터 공격하겠습니다\n약병이라도 공을 세울 수는 있겠지요",
    "9:3457:0": "의 부대를 노리자\n약한 적이지만 적장의 수급임에는 틀림없다",
    "9:3458:0": "부터 쳐부순다!\n병력이 적은 쪽부터 정리한다!",
    "9:3459:0": "의 병력은 적다\n서둘러 해치우자",
    "9:3460:0": ", 그쪽을 공격하기로 한다\n그저 병력 수로 짓누르면 된다",
    "9:3461:0": ", 다른 부대보다 규모가 작군요\n먼저 무찌르겠습니다",
    "9:3462:0": ", 소수 병력인가\n그렇다면 단숨에 짓밟아 주마",
    "9:3463:0": "부터 친다\n먼저 소수 병력을 치는 것이 정석이지",
    "9:3464:0": ", 소수 병력으로 보이는군\n쳐서 공으로 삼겠다",
}

DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS)
STATIC_COORDINATES: set[str] = set()


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
                "segment": "base_msggame_B001_S717",
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
