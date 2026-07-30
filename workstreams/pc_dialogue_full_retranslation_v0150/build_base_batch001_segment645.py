#!/usr/bin/env python3
"""Build Base authoring segment 645 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S645.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s645", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2023:0": "아니, 모두의 활약이\n있었기에 얻은 행운이오",
    "9:2024:0": "날마다 단련해 온\n결실이지요",
    "9:2025:0": "보아라, 나의 공을!\n나의 무예를!",
    "9:2026:0": "자……\n승리를 결정지으시오",
    "9:2027:0": "칭찬해 주시니\n더없는 영광이옵니다",
    "9:2028:0": "모두―",
    "9:2028:1": "의\n공훈을 이어라!",
    "9:2029:0": "간신히\n따라붙었습니다!",
    "9:2030:0": "늘 이러했으면\n좋겠군",
    "9:2031:0": "어머\n기쁜 말씀이시군요!",
    "9:2032:0": "그 정도까지는……\n아니지 않겠습니까",
    "9:2033:0": "벼락도 베어 냈거늘, 너희를\n베지 못할 리 있겠느냐",
    "9:2034:0": "쇼군의 손에 죽는 영예를\n황천에서 자랑하거라",
    "9:2035:0": "다키교요 문장 다음에는\n무엇을 받게 되려나?",
    "9:2036:0": "의 차례인가!?",
    "9:2037:0": "드디어\n출격할 때인가!",
    "9:2038:0": "우리는 의기충천!\n출격 준비도 만전이다!",
    "9:2039:0": "언제든\n출진할 수 있습니다",
    "9:2040:0": "내 무기가 울부짖는구나",
    "9:2041:0": "자…… 슬슬\n나설 때가 되었는데",
    "9:2042:0": "전장에는 이 몸―",
    "9:2042:1": "이(가)\n필요하지 않겠나?",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2028:0",
    "9:2028:1",
    "9:2036:0",
    "9:2042:0",
    "9:2042:1",
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
                "segment": "base_msggame_B001_S645",
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
