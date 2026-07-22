#!/usr/bin/env python3
"""Build Base authoring segment 71 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S71.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s71", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1081:0": "군단을 편성하는 건가?\n재미있겠군",
    "6:1082:0": "은(는) 어느 군단에\n들어가게 되려나",
    "6:1083:0": "군단을 편성하시는군요",
    "6:1084:0": "좋은 군단에\n들어가고 싶군",
    "6:1085:0": "호오, 군단을…",
    "6:1086:0": "좋은 군단에\n들어가고 싶군",
    "6:1087:0": "편제 재검토라\n좋은 생각이라 봅니다",
    "6:1088:0": "과연\n어떤 편제로…",
    "6:1089:0": "군단을 다시 짜는 것도\n하나의 방책이겠지",
    "6:1090:0": "군단 구성에야말로\n전략이 드러나겠지",
    "6:1091:0": "어떤 편제가\n될지 궁금하군",
    "6:1092:0": "군단 구성에야말로\n전략이 드러나겠지",
    "6:1093:0": "편제 재검토라\n좋은 생각이라 봅니다",
    "6:1094:0": "과연\n어떤 편제로…",
    "6:1095:0": "군단 편제는\n정기적으로 재검토해야지",
    "6:1096:0": "자,",
    "6:1096:1": "은(는)\n어느 군단으로…",
    "6:1097:0": "편제 재검토라\n좋은 생각이라 봅니다",
    "6:1098:0": "어느 군단이든\n최선을 다할 뿐",
    "6:1099:0": "끝까지 싸워 나가려면\n군단은 필수다",
    "6:1100:0": "어느 군단이든\n최선을 다할 뿐",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "6:1082:0",
    "6:1096:0",
    "6:1096:1",
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
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
                "segment": "base_msggame_B001_S71",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
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
