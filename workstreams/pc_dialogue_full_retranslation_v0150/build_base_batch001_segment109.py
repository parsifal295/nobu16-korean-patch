#!/usr/bin/env python3
"""Build Base authoring segment 109 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S109.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s109", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1891:0": "상대의 철포가 부족합니다",
    "6:1892:0": "철포?… 그것이 무엇입니까?",
    "6:1893:0": "철포 보유 상한을 초과합니다",
    "6:1894:0": "가보를 더 요구할 수 없습니다",
    "6:1895:0": "상대 다이묘가 가보를 보유하고 있지 않습니다",
    "6:1896:0": "군을 더 요구할 수 없습니다",
    "6:1897:0": "상대에게 요구할 수 있는 군이 없습니다",
    "6:1898:0": "우리 가문의 영지와 인접한 군이 없습니다",
    "6:1899:0": "우리 가문은 다른 가문과 교전 중이므로 군을 요구할 여유가 없습니다",
    "6:1900:0": "우리 가문은 다른 가문에 종속되어 있어 군을 요구할 수 없습니다",
    "6:1901:0": "우리 가문의 영지와 이어지지 않은 군은 요구할 수 없습니다",
    "6:1902:0": "성은 군으로 요구할 수 없습니다",
    "6:1903:0": "전쟁에 휘말릴 가능성이 있어 요구할 수 없습니다",
    "6:1904:0": "이미 요구한 군입니다",
    "6:1905:0": "이미 요구한 거점의 통치하에 있습니다",
    "6:1906:0": "상대에게 요구할 수 있는 성이 없습니다",
    "6:1907:0": "우리 가문의 영지와 인접한 성이 없습니다",
    "6:1908:0": "우리 가문은 다른 가문과 교전 중이므로 성을 요구할 여유가 없습니다",
    "6:1909:0": "우리 가문은 다른 가문에 종속되어 있어 성을 요구할 수 없습니다",
    "6:1910:0": "상대는 성을 내주기를 거부하고 있습니다",
    "6:1911:0": "우리 가문의 영지와 이어지지 않은 성은 요구할 수 없습니다",
    "6:1912:0": "전쟁에 휘말릴 가능성이 있어 요구할 수 없습니다",
    "6:1913:0": "상대의 영지를 분단하게 되므로 선택할 수 없습니다",
    "6:1914:0": "상대는 정전에 응할 뜻이 없습니다",
    "6:1915:0": "아군과 정전할 필요는 없습니다",
    "6:1916:0": "우리 가문은 다른 가문에 종속되어 있어 정전 교섭을 할 수 없습니다",
    "6:1917:0": "군이나 거점을 내주면 6개월간 정전을 맺을 수 있습니다",
    "6:1918:0": "우리 가문에 노골적인 적의를 드러내며 지배에 응하지 않습니다",
    "6:1919:0": "우리 가문이 너무 멀리 있어 지배받을 뜻이 없는 듯합니다",
    "6:1920:0": "우리 가문은 다른 가문에 종속되어 있어 다른 가문을 지배할 수 없습니다",
    "6:1921:0": "우리 가문은 상대를 지배할 만큼 크지 않습니다",
    "6:1922:0": "이미 상대를 지배하고 있습니다",
    "6:1923:0": "상대에게 종속되기에는 우리 가문의 규모가 너무 큽니다",
    "6:1924:0": "우리 가문은 다른 가문에 종속되어 있어 새로 종속될 수 없으며 주군만 바꿀 수 있습니다",
    "6:1925:0": "이미 상대와 종속 관계를 맺고 있습니다",
    "6:1926:0": "상대는 동맹에 응할 뜻이 없습니다",
    "6:1927:0": "우리 가문은 다른 가문에 종속되어 있어 동맹 교섭을 할 수 없습니다",
    "6:1928:0": "상대 세력과 이미 장기 동맹을 맺고 있습니다",
    "6:1929:0": "상대는 혼인에 응할 뜻이 없습니다",
    "6:1930:0": "우리 가문은 다른 가문에 종속되어 있어 혼인 교섭을 할 수 없습니다",
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
                "segment": "base_msggame_B001_S109",
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
