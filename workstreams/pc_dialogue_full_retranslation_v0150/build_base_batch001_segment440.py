#!/usr/bin/env python3
"""Build Base authoring segment 440 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S440.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s440", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2140:0": "적이 다가오기 전에\n성을 함락하면 된다!",
    "7:2141:0": "적이 다가오고 있다\n서둘러 함락해야겠군",
    "7:2142:0": "적이 오고 있다!\n성 공략을 서둘러라!",
    "7:2143:0": "후원군이 온다면\n어서 함락하지 않으면 위험하다",
    "7:2144:0": "후원군이라니 성가시군\n성을 서둘러 함락해야 한다",
    "7:2145:0": "후원군이 도착하기 전에\n함락해 두고 싶군요",
    "7:2146:0": "후원군이 오는가\n시간을 지체할 수 없다",
    "7:2147:0": "후원군이 오기 전에\n성을 함락해 두고 싶군",
    "7:2148:0": "적이 다가오고 있다\n포위되기 전에 쳐부숴야 한다",
    "7:2149:0": "후원군을 보냈는가\n서둘러 끝내야겠군",
    "7:2150:0": "적의 원군인가?\n어서 성을 함락합시다",
    "7:2151:0": "후원군이라고?\n도착하기 전에 함락한다!",
    "7:2152:0": "적이 다가오고 있습니다\n어서 함락해야 합니다",
    "7:2153:0": "후원군이 다가오고 있다\n어서 함락하지 않으면 위험하다",
    "7:2154:0": "작은 성 따위로 막을 수 있겠느냐!\n노부나가 앞에 엎드려라!",
    "7:2155:0": "작은 성 따위 한입거리다!\n자, 짓눌러 버려라!",
    "7:2156:0": "이런 작은 성 따위\n힘으로 밀어붙이면 그만이다!",
    "7:2157:0": "성에 틀어박힌다 한들\n이런 작은 성으로는 어림없다!",
    "7:2158:0": "자비는 필요 없다\n통째로 집어삼켜라",
    "7:2159:0": "작은 성을 상대로 책략은 필요 없다\n힘으로 짓눌러 버려라",
}

STATIC_COORDINATES = set(TRANSLATIONS)


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "retranslated",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S440", "decision_count": len(rows),
                             "retranslated": len(rows), "dynamic_runtime_review_pending": 0,
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
