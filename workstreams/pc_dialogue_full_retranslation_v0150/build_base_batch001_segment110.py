#!/usr/bin/env python3
"""Build Base authoring segment 110 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S110.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s110", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1931:0": "상대 세력과 이미 혼인 관계를 맺고 있습니다",
    "6:1932:0": "혼인할 수 있는 공주나 무장이 없습니다",
    "6:1933:0": "우리 가문에 종속된 세력과는 혼인 동맹을 맺을 수 없습니다",
    "6:1934:0": "상대와 단교하도록 요청할 수 있는 세력이 없습니다",
    "6:1935:0": "우리 가문은 다른 가문에 종속되어 있어 관계 파기를 요청할 수 없습니다",
    "6:1936:0": "상대는 맹약 파기 교섭을 거부하고 있습니다",
    "6:1937:0": "우리 가문의 아군입니다",
    "6:1938:0": "혼인 동맹 중인 세력과 단교하도록 요구할 수 없습니다",
    "6:1939:0": "종속 세력과 단교하도록 요구할 수 없습니다",
    "6:1940:0": "칙명 강화로 맺은 관계는 파기시킬 수 없습니다",
    "6:1941:0": "상대와 원군을 주고받는 중이므로 단교시킬 수 없습니다",
    "6:1942:0": "상대 세력과 맺은 외교 관계가 없습니다",
    "6:1943:0": "상대가 새 표적으로 삼게 할 세력이 없습니다",
    "6:1944:0": "상대가 현재 표적으로 삼은 세력과 교전 중이므로 표적 변경을 교섭할 수 없습니다",
    "6:1945:0": "우리 가문은 다른 가문에 종속되어 있어 표적 세력 변경을 교섭할 수 없습니다",
    "6:1946:0": "우리 가문과 적대 중이 아닙니다",
    "6:1947:0": "상대와 인접하지 않았습니다",
    "6:1948:0": "원래 상대가 표적으로 삼은 세력입니다",
    "6:1949:0": "상대와 적대 중이 아닙니다",
    "6:1950:0": "우리 가문 외의 세력에 종속된 상대에게는 원군을 요청할 수 없습니다",
    "6:1951:0": "이미 상대와 원군을 주고받고 있습니다",
    "6:1952:0": "원군을 요청할 수 있는 성이 없습니다",
    "6:1953:0": "상대는 원군을 보낼 여력이 없습니다",
    "6:1954:0": "상대의 병량이 부족합니다",
    "6:1955:0": "그 성은 이미 교섭 재료로 제시되어 있습니다",
    "6:1956:0": "상대가 교전할 수 없는 세력에는 원군을 보낼 수 없습니다",
    "6:1957:0": "상대는 그 성까지 원군을 파견할 수 없습니다",
    "6:1958:0": "상대는 그 거점으로 출진할 병량이 부족합니다",
    "6:1959:0": "상대와 파기할 만한 외교 관계가 없습니다",
    "6:1960:0": "칙명 강화로 맺은 관계는 파기할 수 없습니다",
    "6:1961:0": "상대의 공주를 받아들였으므로 단교할 수 없습니다",
    "6:1962:0": "상대에게 공주를 보냈으므로 단교할 수 없습니다",
    "6:1963:0": "원군 요청 기간 중이므로 단교할 수 없습니다",
    "6:1964:0": "우리 가문의 종주 가문과 동맹인 세력에는 귀순할 수 없습니다",
    "6:1965:0": "상대는 우리 가문이 이미 따르고 있는 세력입니다",
    "6:1966:0": "우리 가문은 독립 상태이므로 주군을 바꿀 수 없습니다",
    "6:1967:0": "상대를 새 주군으로 삼기에는 우리 가문의 규모가 너무 큽니다",
    "6:1968:0": "대가가 필요하지 않은 교섭 재료를 요구하고 있습니다",
    "6:1969:0": "우리 가문의 종주 가문 외의 세력과는 거래할 수 없습니다",
    "6:1970:0": "현재는 이 내용을 선택할 수 없습니다",
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
                "segment": "base_msggame_B001_S110",
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
