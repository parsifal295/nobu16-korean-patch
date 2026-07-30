#!/usr/bin/env python3
"""Build Base authoring segment 416 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S416.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s416", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1778:0": "은(는) 방어할 필요가 없다\n이미 타국의 성이니라",
    "7:1779:0": "을(를) 구원하려던 수고가\n헛되이 되었구나!",
    "7:1780:0": "의 구원도\n소용없게 되고 말았는가",
    "7:1781:0": "은(는) 타국의 성이니\n지킬 필요 없다",
    "7:1782:0": "은(는) 우리 성이\n아니니…… 이만 실례!",
    "7:1783:0": "은(는) 타국의 성\n우리가 지킬 의리는 없다",
    "7:1784:0": "의 구원을 중지하고\n가장 가까운 성으로 서두르겠습니다",
    "7:1785:0": "은(는) 타국의 성\n이만 물러가겠소",
    "7:1786:0": "을(를) 지키는 것도\n이렇게 된 이상 무의미하군……",
    "7:1787:0": "이제—",
    "7:1787:1": "을(를)\n지킬 필요는 없으리라",
    "7:1788:0": "은(는) 지키지 않아도\n되겠구나",
    "7:1789:0": "이제—",
    "7:1789:1": "을(를)\n지킬 일도 없겠군요",
    "7:1790:0": "이제—",
    "7:1790:1": "을(를)\n지킬 필요는 없다",
    "7:1791:0": "은(는) 지켜 봐야\n소용없겠군요",
    "7:1792:0": "의 구원은 중지\n헛수고가 되고 말았구나",
    "7:1793:0": "을(를) 함락했다\n귀성한다!",
    "7:1794:0": "을(를) 공략하는 데 성공했다!\n귀성한다!",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S416", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
