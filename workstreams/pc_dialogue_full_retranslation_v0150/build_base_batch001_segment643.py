#!/usr/bin/env python3
"""Build Base authoring segment 643 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S643.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s643", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1985:0": "도 느긋하게\n있을 수는 없겠군!",
    "9:1986:0": "훌륭한 무예로다!\n언젠가 겨루어 보고 싶구나",
    "9:1987:0": "함께 절차탁마할 상대가\n있다는 것은 좋은 일……",
    "9:1988:0": "도\n정진해야겠군……!",
    "9:1989:0": "내 무예도\n뒤지지 않는다!",
    "9:1990:0": "실로 대단한 무예로다……\n아군이라 다행이군",
    "9:1991:0": "머뭇거리다가는\n공을 가로채이겠군요",
    "9:1992:0": "마저\n피가 끓어오르는구나",
    "9:1993:0": "도 더욱\n분발해야겠어!",
    "9:1994:0": "언젠가 무예를 겨루게 해\n보고 싶구나",
    "9:1995:0": "그 무공의 덕을\n저도 보고 싶사옵니다",
    "9:1996:0": "은(는)…… 화려하구나……\n어지간히 차이가 벌어졌군……",
    "9:1997:0": "굉장하군……!\n대단한 놈이다",
    "9:1998:0": "큰 전공이로다\n참으로 장하도다!",
    "9:1999:0": "이토록 뛰어난\n인재였던가……",
    "9:2000:0": "그 거물을\n격파해 버리다니",
    "9:2001:0": "이겼다!\n이제 우리의 승리다!",
    "9:2002:0": "그럼 남은 적을\n마저 처치해 볼까……",
    "9:2003:0": "이 무슨 쾌거인가!\n훌륭한 활약이다!",
    "9:2004:0": "미덥지 못한 대장을 둔\n적이 가엾구나!",
    "9:2005:0": "이토록 강한 힘을\n지니셨다니……",
    "9:2006:0": "굉장하군……\n훌륭하다는 말밖에 나오지 않는군",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1985:0",
    "9:1988:0",
    "9:1992:0",
    "9:1993:0",
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
                "segment": "base_msggame_B001_S643",
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
