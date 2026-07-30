#!/usr/bin/env python3
"""Build Base authoring segment 300 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S300.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s300", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4501:0": "아내인 「",
    "6:4501:1": "」이(가) 신세를 지고 있다",
    "6:4502:0": "아내인 「",
    "6:4502:1": "」을(를) 저버릴 수는 없다",
    "6:4503:0": "남편인 「",
    "6:4503:1": "」이(가) 신세를 지고 있다",
    "6:4504:0": "남편인 「",
    "6:4504:1": "」을(를) 저버릴 수는 없다",
    "6:4505:0": "내 자식인 「",
    "6:4505:1": "」이(가) 신세를 지고 있다",
    "6:4506:0": "내 자식인 「",
    "6:4506:1": "」을(를) 저버릴 수는 없다",
    "6:4507:0": "이(가) 신세를 지고 있다",
    "6:4508:0": "을(를) 저버릴 수는 없다",
    "6:4509:0": "이(가) 신세를 지고 있다",
    "6:4510:0": "을(를) 저버릴 수는 없다",
    "6:4511:0": "지금 주군과는 친하지 않다",
    "6:4512:0": "지금 주군이 마음에 들지 않는다",
    "6:4513:0": "지금 주군을 신뢰하지 않는다",
    "6:4514:0": "그대와는 마음이 맞을 듯하다",
}

STATIC_COORDINATES: set[str] = {"6:4511:0", "6:4512:0", "6:4513:0", "6:4514:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S300", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
