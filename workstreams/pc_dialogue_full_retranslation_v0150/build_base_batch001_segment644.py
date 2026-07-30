#!/usr/bin/env python3
"""Build Base authoring segment 644 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S644.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s644", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2007:0": "이토록 강한 힘을\n지니고 계셨다니……",
    "9:2008:0": "하하, 승전 연회가\n기대되는구려!",
    "9:2009:0": "두고 봐라…… 다음에는\n",
    "9:2009:1": "이(가) 해치워 주마!",
    "9:2010:0": "내 무예마저\n빛을 잃을 활약이로다……",
    "9:2011:0": "뒤따르라!\u3000",
    "9:2011:1": "도\n무공을 세우리라",
    "9:2012:0": "다음에는 이 몸―",
    "9:2012:1": "이(가)\n공을 세울 차례로군요",
    "9:2013:0": "제법이군……\n내 솜씨도 보여 줘야겠군",
    "9:2014:0": "제법이군……\n뒤처질 수는 없다",
    "9:2015:0": "저 활약에 자극받아\n우리도 분발해야 한다!",
    "9:2016:0": "잘한다, 잘해!\n질 수는 없느니라!",
    "9:2017:0": "다음에는―",
    "9:2017:1": "도\n활약해 보이겠습니다",
    "9:2018:0": "이번에는―",
    "9:2018:1": "이(가)\n공을 세워 보이겠다",
    "9:2019:0": "다음에는―",
    "9:2019:1": "도\n전력으로 임하겠습니다",
    "9:2020:0": "도\n성과를 내고 말겠다……!",
    "9:2021:0": "해냈다……\n기분 최고다아!",
    "9:2022:0": "나야말로―",
    "9:2022:1": "\n대장을 쳐부수었도다!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2009:0",
    "9:2009:1",
    "9:2011:0",
    "9:2011:1",
    "9:2012:0",
    "9:2012:1",
    "9:2017:0",
    "9:2017:1",
    "9:2018:0",
    "9:2018:1",
    "9:2019:0",
    "9:2019:1",
    "9:2020:0",
    "9:2022:0",
    "9:2022:1",
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
                "segment": "base_msggame_B001_S644",
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
