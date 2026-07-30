#!/usr/bin/env python3
"""Build Base authoring segment 646 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S646.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s646", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2043:0": "싸울 생각에 몸이 떨리는구나!",
    "9:2044:0": "슬슬\n내가 나설 차례인가?",
    "9:2045:0": "드디어인가?\n팔이 근질거리는군!",
    "9:2046:0": "나설 준비는\n되어 있사옵니다",
    "9:2047:0": "출진 준비는\n갖추어져 있사옵니다",
    "9:2048:0": "좋았어!\n맡겨 두라고!",
    "9:2049:0": "오오오오!\n이 힘으로 적을 치리라!",
    "9:2050:0": "후후, 마음껏\n힘을 발휘할 수 있겠군",
    "9:2051:0": "알겠습니다…… 진정한 힘을\n보여 드리지요",
    "9:2052:0": "나의 무예는\n더욱 갈고닦였도다!",
    "9:2053:0": "후후…… 후후후……!\n감각이 살아나는군",
    "9:2054:0": "차오른다……\n이 힘만 있다면……",
    "9:2055:0": "힘이 솟구치는구나!",
    "9:2056:0": "감사합니다!",
    "9:2057:0": "참으로 든든하다!",
    "9:2058:0": "이제 싸울 수 있습니다!",
    "9:2059:0": "오오, 감사드리오!",
    "9:2060:0": "좋았어, 지금이다!\n박살 내 주마!",
    "9:2061:0": "무작정 덤비기만 하는 것은\n병법이라 할 수 없지",
    "9:2062:0": "적의 기세도 온데간데없군\n자, 단숨에 짓밟아 버리자!",
    "9:2063:0": "의 지원을\n승리로 이어 가겠습니다!",
    "9:2064:0": "좋다!\n단숨에 무너뜨리자!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2063:0",
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
                "segment": "base_msggame_B001_S646",
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
