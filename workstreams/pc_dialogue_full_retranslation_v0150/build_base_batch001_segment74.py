#!/usr/bin/env python3
"""Build Base authoring segment 74 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S74.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s74", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1141:0": "늘 고맙습니다\n이번에는 풍작이라 쌀이 아주 쌉니다!",
    "6:1142:0": "늘 고맙습니다\n이번에는 흉작이라 쌀값이 비쌉니다",
    "6:1143:0": "늘 고맙습니다\n지금은 가보도 취급하고 있습니다",
    "6:1144:0": "늘 고맙습니다\n단골손님을 위해\n상등품 가보를 준비했습니다",
    "6:1145:0": "늘 고맙습니다, 덕분에\n구매 가격을 낮춰 드리고 있습니다",
    "6:1146:0": "늘 고맙습니다, 덕분에\n거래 가능량이 늘었습니다",
    "6:1147:0": "구매하시는군요\n얼마나 필요하십니까",
    "6:1148:0": "구매하시는군요\n어느 것으로 하시겠습니까",
    "6:1149:0": "먼저 남만 상관을 지어 주세요오\n이야기는 그다음이에요오",
    "6:1150:0": "안녕하세요오\n철포는 얼마나 필요하세요오",
    "6:1151:0": "구매해 주셔서 감사합니다\n병량",
    "6:1151:1": "을 받아 주십시오",
    "6:1152:0": "구매해 주셔서 감사합니다\n군마",
    "6:1152:1": "를 받아 주십시오",
    "6:1153:0": "구매해 주셔서 감사해요오\n철포",
    "6:1153:1": "를 받아 주세요오",
    "6:1154:0": "구매해 주셔서 감사합니다\n",
    "6:1154:1": "을(를) 받아 주십시오",
    "6:1155:0": "구매해 주셔서 감사합니다\n",
    "6:1155:1": "들",
    "6:1155:2": "점을 받아 주십시오",
    "6:1156:0": "매입이군요\n수량은 얼마나 됩니까",
    "6:1157:0": "가보를 파시는군요\n어느 것을 매입할까요",
    "6:1158:0": "그럼 매입하겠습니다\n금",
    "6:1158:1": "을 받아 주십시오",
    "6:1159:0": "틀림없이",
    "6:1159:1": "을(를) 매입했습니다\n금",
    "6:1159:2": "을 받아 주십시오",
    "6:1160:0": "틀림없이",
    "6:1160:1": "들",
    "6:1160:2": "점을 매입했습니다\n금",
    "6:1160:3": "을 받아 주십시오",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "6:1151:0",
    "6:1151:1",
    "6:1152:0",
    "6:1152:1",
    "6:1153:0",
    "6:1153:1",
    "6:1154:0",
    "6:1154:1",
    "6:1155:0",
    "6:1155:1",
    "6:1155:2",
    "6:1158:0",
    "6:1158:1",
    "6:1159:0",
    "6:1159:1",
    "6:1159:2",
    "6:1160:0",
    "6:1160:1",
    "6:1160:2",
    "6:1160:3",
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
                "segment": "base_msggame_B001_S74",
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
