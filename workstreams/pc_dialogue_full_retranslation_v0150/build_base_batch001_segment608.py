#!/usr/bin/env python3
"""Build Base authoring segment 608 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S608.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s608", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1251:0": "이번 싸움!\n우리 것으로 만들자!",
    "9:1252:0": "공격을 시작한다, 이 녀석들아!",
    "9:1253:0": "가자, 비탈 돌격이다!",
    "9:1254:0": "나의 비탈 돌격을\n똑똑히 맛보아라!",
    "9:1255:0": "적의 허를\n찔러 줍시다!",
    "9:1256:0": "돌격!\n맞서는 자는 모조리 쓸어버려라!",
    "9:1257:0": "단숨에 몰아쳐\n유린하라!",
    "9:1258:0": "돌격! 이 기세는\n누구도 막을 수 없다",
    "9:1259:0": "비탈 돌격이다!\n적을 단번에 물리쳐라!",
    "9:1260:0": "자, 적을\n후려쳐 떨어뜨리세요!",
    "9:1261:0": "지금이다! 비탈 돌격을\n보여주마!",
    "9:1262:0": "급습을 감행합니다!\n뒤따르세요!",
    "9:1263:0": "가파른 벼랑이지만……\n각오를 다져라!",
    "9:1264:0": "적이라고!?\n어디서 튀어나온 거냐!",
    "9:1265:0": "물러나라!\n저곳에 복병이……!",
    "9:1266:0": "저건 적인가……!\n모두 물러나라!",
    "9:1267:0": "복병!? 설마,\n그럴 리가……",
    "9:1268:0": "마, 말도 안 돼!\n적의 증원인가!?",
    "9:1269:0": "있을 수 없다……\n저 군세는 대체 무엇이냐!?",
    "9:1270:0": "아, 저건……?\n적의 복병입니까",
    "9:1271:0": "물러나라!\n하마터면 복병의 먹이가 될 뻔했구나",
    "9:1272:0": "적이라고!? 어느새……",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


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
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
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
                "segment": "base_msggame_B001_S608",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
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
