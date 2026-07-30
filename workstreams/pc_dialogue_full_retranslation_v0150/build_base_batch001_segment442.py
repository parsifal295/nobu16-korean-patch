#!/usr/bin/env python3
"""Build Base authoring segment 442 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S442.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s442", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2180:0": "이런 성 따위는 그저\n힘으로 밀어붙여 짓눌러라!",
    "7:2181:0": "포위보다 강공하는 편이\n더 빨리 성을 함락할 수 있으리라",
    "7:2182:0": "이건 힘으로 밀어붙이는 게\n무조건 빠르다고!",
    "7:2183:0": "시간을 허비할 수 없다\n강공으로 함락시켜라!",
    "7:2184:0": "여기서는 힘으로 밀어붙여야\n쉽게 함락할 수 있으리라",
    "7:2185:0": "이 성은 포위보다\n힘으로 밀어붙이는 편이 효과적이겠군요",
    "7:2186:0": "포위는 번거롭다\n힘으로 밀어붙여 함락시켜라!",
    "7:2187:0": "이 성은 힘으로 밀어붙여야\n더 빨리 함락할 수 있다!",
    "7:2188:0": "포위에는 시간이 걸린다\n여기서는 강공해야 한다!",
    "7:2189:0": "이 성은 힘으로 밀어붙여야\n쉽게 함락할 수 있겠구나",
    "7:2190:0": "포위는 그만둡시다\n힘으로 밀어붙이는 편이 빠릅니다!",
    "7:2191:0": "시간을 허비할 수 없다\n성을 강공하라!",
    "7:2192:0": "강공하는 편이\n효과적일 듯합니다",
    "7:2193:0": "이 성은 힘으로 밀어붙여야\n더 빨리 함락할 수 있겠군",
    "7:2194:0": "후원군도 있다\n강공으로 빼앗아라!",
    "7:2195:0": "후원군 병력도 대기 중이다\n힘으로 밀어붙여 굴복시키는 게다",
    "7:2196:0": "상황을 고려하면\n힘으로 밀어붙여야 하오!",
    "7:2197:0": "이만한 병력이 있다면\n힘으로 밀어붙이는 편이 효과적이겠군",
    "7:2198:0": "포위는 필요 없다, 대군으로\n정면에서 공격하라",
    "7:2199:0": "병력은 충분하고도 남는다…… 그렇다면\n강공으로 끝장을 내라",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S442", "decision_count": len(rows),
                             "retranslated": len(rows), "dynamic_runtime_review_pending": 0,
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
