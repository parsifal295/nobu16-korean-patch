#!/usr/bin/env python3
"""Build Base authoring segment 108 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S108.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s108", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1861:0": "그 세력의 교섭을 결렬시켰으므로 외교에 응하지 않습니다",
    "6:1862:0": "그 세력의 교섭을 결렬시켰으므로 외교에 응하지 않습니다\n",
    "6:1862:1": "개월 뒤에 다시 외교할 수 있습니다",
    "6:1863:0": "그 세력의 교섭을 결렬시켰으므로 외교에 응하지 않습니다\n",
    "6:1863:1": "일 뒤에 다시 외교할 수 있습니다",
    "6:1864:0": "우리 가문과 상대의 악명 차이가 70 이상이므로 어떤 제안에도 응하지 않을 것입니다",
    "6:1865:0": "우호도가 부족하여 요구할 수 없습니다",
    "6:1866:0": "우호도가 부족하여 요구할 수 없습니다",
    "6:1867:0": "단교 상태인 세력에는 요구할 수 없습니다",
    "6:1868:0": "가치가 너무 높아 교섭이 성립될 가능성이 없습니다",
    "6:1869:0": "현재 요구하려는 내용과 동시에 요구할 수 없습니다",
    "6:1870:0": "이 교섭 재료는 이미 요구했습니다",
    "6:1871:0": "이 교섭 재료에는 대가가 필요하지 않습니다",
    "6:1872:0": "이미 대가로 제시한 교섭 재료이므로 요구할 수 없습니다",
    "6:1873:0": "우리 가문의 종주 가문 외의 세력과 거래할 수 없습니다",
    "6:1874:0": "우호도가 「친밀」에 미치지 않아 요구할 수 없습니다",
    "6:1875:0": "우호도가 「우호」에 미치지 않아 요구할 수 없습니다",
    "6:1876:0": "우호도가 「평상」에 미치지 않아 요구할 수 없습니다",
    "6:1877:0": "상대와의 악명 차이가 30 이상이므로 요구할 수 없습니다",
    "6:1878:0": "상대와의 악명 차이가 40 이상이므로 요구할 수 없습니다",
    "6:1879:0": "상대와의 악명 차이가 70 이상이므로 요구할 수 없습니다",
    "6:1880:0": "우리 가문이 너무 멀리 있어 종속될 뜻이 없는 듯합니다",
    "6:1881:0": "현재는 이 내용을 요구할 수 없습니다",
    "6:1882:0": "우호도를 더 높일 수 없습니다",
    "6:1883:0": "우리 가문의 종주 가문 외의 세력과는 친선할 수 없습니다",
    "6:1884:0": "상대의 금전이 부족합니다",
    "6:1885:0": "금전 보유 상한을 초과합니다",
    "6:1886:0": "상대의 군량이 부족합니다",
    "6:1887:0": "상대는 군량을 내줄 여유가 없는 듯합니다",
    "6:1888:0": "군량 보유 상한을 초과합니다",
    "6:1889:0": "상대의 군마가 부족합니다",
    "6:1890:0": "군마 보유 상한을 초과합니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "6:1862:0",
    "6:1862:1",
    "6:1863:0",
    "6:1863:1",
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
                "segment": "base_msggame_B001_S108",
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
