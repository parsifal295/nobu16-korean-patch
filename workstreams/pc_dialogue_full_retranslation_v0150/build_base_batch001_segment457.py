#!/usr/bin/env python3
"""Build Base authoring segment 457 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S457.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s457", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2427:0": "이만한 병력이라면—",
    "7:2427:1": "을(를)\n지켜 내기는 쉬운 일",
    "7:2428:0": "이 병력으로—",
    "7:2428:1": "을(를) 지키기는\n상당한 난제가 될 것이다",
    "7:2428:2": "\n게다가 병량도 충분하다고는 할 수 없",
    "7:2429:0": "이 병력으로—",
    "7:2429:1": "을(를) 지키기는\n상당한 난제가 될 것이다",
    "7:2430:0": "이 병력으로—",
    "7:2430:1": "을(를) 지켜 낼 수 있을지는\n지휘에 달렸다는 것인가",
    "7:2430:2": "\n병량 부족도 마음에 걸리는 바",
    "7:2431:0": "이 병력으로—",
    "7:2431:1": "을(를) 지켜 낼 수 있을지는\n지휘에 달렸다는 것인가",
    "7:2432:0": "적군의 병력과 휴대 병량을 고려하면\n굳이 출진하지 않아도\n",
    "7:2432:1": "은(는) 지켜 낼 수 있으리라",
    "7:2433:0": "이 거리에서는—",
    "7:2433:1": "이(가) 함락되기 전에\n구원이 제때 닿지 못하",
    "7:2433:2": "일지도 모르",
    "7:2434:0": "즉시—",
    "7:2434:1": "을(를) 제압하러 향해",
    "7:2434:2": "\n병량이 바닥나지 않게 주의",
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
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S457", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
