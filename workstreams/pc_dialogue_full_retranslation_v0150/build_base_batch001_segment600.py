#!/usr/bin/env python3
"""Build Base authoring segment 600 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S600.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s600", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1075:0": "다시…… 되찾아\n오도록 하지요",
    "9:1076:0": "내가 방심했구나……",
    "9:1077:0": "이건…… 좋지 않군……",
    "9:1078:0": "당했군요……",
    "9:1079:0": "에잇, 아군은 대체 무얼\n하고 있었단 말이냐!",
    "9:1080:0": "설마 빼앗길 줄은……",
    "9:1081:0": "큭, 빼앗겼는가……",
    "9:1082:0": "빼앗기고\n말았군요……",
    "9:1083:0": "그곳을 빼앗기다니……",
    "9:1084:0": "해냈잖아!\n적이 새파랗게 질렸어!",
    "9:1085:0": "퇴로를 빼앗으면\n승부는 우리 것이다!",
    "9:1086:0": "훌륭하다! 이 기세로\n계속 무너뜨려 가자!",
    "9:1087:0": "퇴로를 파괴하다니\n훌륭한 활약입니다",
    "9:1088:0": "큰 공을 세웠도다!\n참으로 장한 활약이로다",
    "9:1089:0": "훌륭하구나……\n전세가 크게 바뀌겠구나",
    "9:1090:0": "눈부신 활약이오\n전황이 바뀌었구려",
    "9:1091:0": "장하구나,",
    "9:1091:1": "!\n큰 공을 세웠도다!",
    "9:1092:0": "훌륭합니다!\n적도 크게 당황했군요",
    "9:1093:0": "장하구나,\n퇴로를 끊어 주었도다!",
    "9:1094:0": "퇴로를 끊다니\n훌륭합니다!",
    "9:1095:0": "급소를 찔려\n적은 의기소침했구나!",
}

DYNAMIC_RUNTIME_COORDINATES = {"9:1091:0", "9:1091:1"}
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
                "segment": "base_msggame_B001_S600",
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
