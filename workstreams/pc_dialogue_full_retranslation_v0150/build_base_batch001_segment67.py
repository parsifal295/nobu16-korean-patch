#!/usr/bin/env python3
"""Build Base authoring segment 67 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S67.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s67", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1003:0": "포상은 받고 싶다만…",
    "6:1004:0": "칭찬받고 싶은 법이지…",
    "6:1005:0": "무언가 포상을\n내려 주시려는 걸까",
    "6:1006:0": "혹시\n",
    "6:1006:1": "에게…?",
    "6:1007:0": "혹시…\n",
    "6:1007:1": "에게…?",
    "6:1008:0": "과연 어떤\n분부가 내려질지…",
    "6:1009:0": "혹시…\n경사라도 있는 건가?",
    "6:1010:0": "오\n누가 혼인하는 거지?",
    "6:1011:0": "좋은 인연이\n맺어지겠지요",
    "6:1012:0": "우리 가문에는 훌륭한 장수가\n있으니 말이오",
    "6:1013:0": "호오…\n좋은 혼담이 되기를",
    "6:1014:0": "좋은 날이\n될 듯하군요",
    "6:1015:0": "기쁜 일이\n되겠지요",
    "6:1016:0": "새로 맺어질 부부는\n분명 그들이겠지…",
    "6:1017:0": "우리 가문의 전환점이 될 것인가",
    "6:1018:0": "호오, 결연이라…",
    "6:1019:0": "사람 수만큼\n인연이 있는 법이지요",
    "6:1020:0": "과연 누가…",
    "6:1021:0": "어느 시대든\n경사스러운 이야기는 좋은 법",
    "6:1022:0": "그 사람과 그 사람이라면\n잘 어울리지 않겠습니까…",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "6:1006:0",
    "6:1006:1",
    "6:1007:0",
    "6:1007:1",
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
                "segment": "base_msggame_B001_S67",
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
