#!/usr/bin/env python3
"""Build Base authoring segment 437 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S437.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s437", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2080:0": "의 병량이\n바닥날 때까지 대기하라!",
    "7:2081:0": "의 병량은\n얼마 없다. 기다려야 한다",
    "7:2082:0": "의 병량이\n떨어질 때까지 기다리자고",
    "7:2083:0": "의 병량은\n얼마 없다. 포위하라!",
    "7:2084:0": "의 병량은\n얼마 없다. 지금은 기다리자",
    "7:2085:0": "의 병량이\n바닥나기를 기다리겠습니다",
    "7:2086:0": "의 병량은\n얼마 없다. 여기서는 포위다",
    "7:2087:0": "의 병량은\n얼마 없다. 기다리도록 하지",
    "7:2088:0": "의 비축 병량은\n미미하다. 포위해 주마",
    "7:2089:0": "의 병량은\n얼마 없다. 포위할까",
    "7:2090:0": "의 병량은\n얼마 없습니다. 기다리겠습니다",
    "7:2091:0": "의 병량은\n얼마 없다. 포위하라!",
    "7:2092:0": "의 비축 병량은\n얼마 없습니다. 기다립시다",
    "7:2093:0": "의 병량은\n얼마 없다. 기다리도록 하지",
    "7:2094:0": "에 적이라고?\n하지만 우선은 이 성이다",
    "7:2095:0": "의 위기다\n서둘러 끝내야겠군",
    "7:2096:0": "이(가) 위태롭군\n이 성은 서둘러 함락한다!",
    "7:2097:0": "이(가) 위험하다니\n속히 이 성을 함락시켜야겠군",
    "7:2098:0": "에 적이?\n신속히 쳐 없애리라",
    "7:2099:0": "이(가) 위태롭군\n어서 끝내야겠어",
}

STATIC_COORDINATES: set[str] = set()


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S437", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
