#!/usr/bin/env python3
"""Build Base authoring segment 111 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S111.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s111", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1971:0": "교섭 재료로 선택할 금전이 부족합니다",
    "6:1972:0": "상대는 금전이 부족하지 않아 받아들이지 않을 것입니다",
    "6:1973:0": "이미 금전을 교섭 재료로 선택했습니다",
    "6:1974:0": "교섭 재료로 선택할 군량이 부족합니다",
    "6:1975:0": "상대는 군량이 부족하지 않아 받아들이지 않을 것입니다",
    "6:1976:0": "이미 군량을 교섭 재료로 선택했습니다",
    "6:1977:0": "교섭 재료로 선택할 군마가 부족합니다",
    "6:1978:0": "상대는 군마가 부족하지 않아 받아들이지 않을 것입니다",
    "6:1979:0": "이미 군마를 교섭 재료로 선택했습니다",
    "6:1980:0": "교섭 재료로 선택할 철포가 부족합니다",
    "6:1981:0": "상대는 철포가 부족하지 않아 받아들이지 않을 것입니다",
    "6:1982:0": "이미 철포를 교섭 재료로 선택했습니다",
    "6:1983:0": "철포?… 그것이 무엇입니까?",
    "6:1984:0": "선택할 수 있는 가보가 없습니다",
    "6:1985:0": "가보는 5개까지 선택할 수 있습니다",
    "6:1986:0": "선택할 수 있는 군이 없습니다",
    "6:1987:0": "군은 5개까지 선택할 수 있습니다",
    "6:1988:0": "군을 정전 조건으로 제시할 수 없습니다",
    "6:1989:0": "월경지가 되는 군은 선택할 수 없습니다",
    "6:1990:0": "성은 군으로 선택할 수 없습니다",
    "6:1991:0": "전쟁에 휘말릴 가능성이 있어 선택할 수 없습니다",
    "6:1992:0": "이미 선택한 군입니다",
    "6:1993:0": "이미 선택한 성의 통치하에 있습니다",
    "6:1994:0": "선택할 수 있는 성이 없습니다",
    "6:1995:0": "이미 성을 선택했습니다",
    "6:1996:0": "거점을 정전 조건으로 제시할 수 없습니다",
    "6:1997:0": "월경지가 되는 성은 선택할 수 없습니다",
    "6:1998:0": "전쟁에 휘말릴 가능성이 있어 선택할 수 없습니다",
    "6:1999:0": "원군 요청 대상인 성은 선택할 수 없습니다",
    "6:2000:0": "상대의 영지를 분단하게 되므로 선택할 수 없습니다",
    "6:2001:0": "선택할 수 있는 관직이 없습니다",
    "6:2002:0": "교전 중인 상대는 관직만으로 정전에 응하지 않을 것입니다",
    "6:2003:0": "이미 관직을 선택했습니다",
    "6:2004:0": "맹약 파기 대상으로 선택할 수 있는 세력이 없습니다",
    "6:2005:0": "우호도가 「친밀」에 이르지 않아 맹약 파기를 선택할 수 없습니다",
    "6:2006:0": "종속 세력에는 맹약 파기를 교섭 재료로 제시할 수 없습니다",
    "6:2007:0": "상대는 맹약 파기 교섭을 거부하고 있습니다",
    "6:2008:0": "우리 가문과 상대 양쪽의 아군입니다",
    "6:2009:0": "혼인 동맹 중인 세력은 선택할 수 없습니다",
    "6:2010:0": "종속 세력과는 단교할 수 없습니다",
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
                "segment": "base_msggame_B001_S111",
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
