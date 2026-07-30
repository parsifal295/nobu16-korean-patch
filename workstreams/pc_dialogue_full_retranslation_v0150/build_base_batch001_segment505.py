#!/usr/bin/env python3
"""Build Base authoring segment 505 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S505.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s505", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
REPEATED_DEVASTATION = (
    "을(를) 비롯해 피해를 입은 군은 총",
    "개로,\n크게 황폐해져",
)
TRANSLATIONS = {
    "8:337:0": "영내에도 태풍 피해가 발생",
    "8:337:1": ",\n성하 시설을 건설한 덕분에\n일부 군은 화를 면한 모양",
    "8:338:0": "영내에도 태풍 피해가 발생",
    "8:338:1": ",\n정책이 효과를 발휘해\n일부 군은 화를 면한 모양",
    "8:339:0": "불행히도 태풍 피해를 입은 군이\n영내에",
    "8:339:1": "\n앞으로 상황이 악화",
    "8:340:0": ", 영내를 태풍이 덮쳐,\n큰 피해를 입은 군이",
    "8:340:1": "\n대책을 세워야 하",
    "8:341:0": "의 영내에서도\n태풍 피해가 발생하고",
    "8:341:1": "\n민심을 위무하는 것이 좋을 듯하",
    "8:342:0": "영내에 태풍 피해를 입은 군이",
    "8:342:1": "\n전답은 황폐하고 가옥도 무너진 상태",
    "8:342:2": "\n부디 유념해",
    "8:343:0": "태풍이",
    "8:343:1": "의 영내에서도\n거세게 몰아쳐,\n큰 피해를 입은 군이",
    **{
        f"8:{record_id}:{literal_id}": translation
        for record_id in range(344, 349)
        for literal_id, translation in enumerate(REPEATED_DEVASTATION)
    },
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
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S505", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
