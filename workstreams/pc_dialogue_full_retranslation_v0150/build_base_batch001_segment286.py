#!/usr/bin/env python3
"""Build Base authoring segment 286 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S286.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s286", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4352:1": "의 외교 자세와 신용이 악화되었습니다",
    "6:4353:0": "동맹을 맺은 우리 가문을 경계하여\n",
    "6:4353:1": "을(를) 포함한 총",
    "6:4353:2": "개 세력과의 외교 자세와\n신용이 악화되었습니다",
    "6:4354:0": "동맹을 맺은 우리 가문을 경계하여\n",
    "6:4354:1": "와(과)의 외교 자세가 악화되었습니다",
    "6:4355:0": "동맹을 맺은 우리 가문을 경계하여\n",
    "6:4355:1": "을(를) 포함한 총",
    "6:4355:2": "개 세력과의 외교 자세가\n악화되었습니다",
    "6:4356:0": "고민이 있으시다면 부디 이",
    "6:4356:1": "에게 맡겨 주십시오!\n취락 장악 같은 일은 눈 깜짝할 새에\n끝내",
    "6:4357:0": "에는",
    "6:4357:1": "보다 더 적임자가\n있을 듯합니다……",
    "6:4357:2": "은(는)\n지금 자리가 마음에 들어",
    "6:4358:0": "보람이 있을 법한 곳",
    "6:4358:2": "의 경우라면 그렇",
    "6:4358:3": "…\n우선 농촌 장악부터…",
    "6:4359:0": "승진한 성주 「",
    "6:4359:1": "」님께\n영지를 더 내리시면\n그 영지들도 더욱 번영하",
    "6:4360:0": "다행히 「",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S286", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
