#!/usr/bin/env python3
"""Build Base authoring segment 112 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S112.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s112", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2011:0": "칙명 강화 중인 세력은 선택할 수 없습니다",
    "6:2012:0": "원군을 주고받는 세력은 선택할 수 없습니다",
    "6:2013:0": "관계없는 세력입니다",
    "6:2014:0": "대상 세력에 우호도 상승만 요구합니다",
    "6:2015:0": "대상 세력에 금전을 요구합니다",
    "6:2016:0": "대상 세력에 병량을 요구합니다",
    "6:2017:0": "대상 세력에 군마를 요구합니다",
    "6:2018:0": "대상 세력에 철포를 요구합니다",
    "6:2019:0": "대상 세력에 다이묘가 보유한 가보를 5개까지 요구합니다",
    "6:2020:0": "대상 세력에 군을 5개까지 요구합니다\n외교 관계가 없는 상태에서 군을 주고받으면 6개월간 정전이 체결됩니다",
    "6:2021:0": "대상 세력에 성을 요구합니다\n외교 관계가 없는 상태에서 성을 주고받으면 6개월간 정전이 체결됩니다",
    "6:2022:0": "대상 세력에 6개월간 정전 체결 또는 연장을 요구합니다",
    "6:2023:0": "대상 세력에 우리 가문으로 종속될 것을 요구합니다",
    "6:2024:0": "대상 세력에 상대에게 종속되기를 청합니다",
    "6:2025:0": "대상 세력에 6~60개월간 동맹 체결 또는 연장을 제안합니다",
    "6:2026:0": "대상 세력에 혼인 동맹 체결을 제안합니다",
    "6:2027:0": "대상 세력에 다른 세력과 단교하도록 요청합니다",
    "6:2028:0": "대상 세력에 다른 세력을 표적으로 삼도록 요청합니다",
    "6:2029:0": "대상 세력에 성과 병력을 지정하여 공략 또는 방어 원군을 요청합니다",
    "6:2030:0": "대상 세력과의 외교 관계를 해소합니다",
    "6:2031:0": "대상 세력을 새 주군으로 삼겠다고 청합니다",
    "6:2032:0": "요구 내용을 일단 모두 취하합니다",
    "6:2033:0": "제안 내용을 일단 모두 취하합니다",
    "6:2034:0": "요구 내용에 대한 대가를 자동으로 설정합니다",
    "6:2035:0": "대상 세력에 금전을 양도하겠다고 제안합니다",
    "6:2036:0": "대상 세력에 병량을 양도하겠다고 제안합니다",
    "6:2037:0": "대상 세력에 군마를 양도하겠다고 제안합니다",
    "6:2038:0": "대상 세력에 철포를 양도하겠다고 제안합니다",
    "6:2039:0": "대상 세력에 다이묘가 보유한 가보를 5개까지 양도하겠다고 제안합니다",
    "6:2040:0": "대상 세력에 군을 5개까지 양도하겠다고 제안합니다\n외교 관계가 없는 상태에서 군을 주고받으면 6개월간 정전이 체결됩니다",
    "6:2041:0": "대상 세력에 성을 양도하겠다고 제안합니다\n외교 관계가 없는 상태에서 성을 주고받으면 6개월간 정전이 체결됩니다",
    "6:2042:0": "대상 세력에 다이묘가 보유한 관직을 양도하겠다고 제안합니다",
    "6:2043:0": "대상 세력에 다른 세력과 단교하겠다고 제안합니다",
    "6:2044:0": "대상 세력에 금전을 요구합니다",
    "6:2045:0": "대상 세력에 병량을 요구합니다",
    "6:2046:0": "대상 세력에 군마를 요구합니다",
    "6:2047:0": "대상 세력에 철포를 요구합니다",
    "6:2048:0": "대상 세력에 다이묘가 보유한 가보를 5개까지 요구합니다",
    "6:2049:0": "대상 세력에 군을 5개까지 요구합니다",
    "6:2050:0": "대상 세력에 성을 요구합니다",
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
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
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
                "segment": "base_msggame_B001_S112",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
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
