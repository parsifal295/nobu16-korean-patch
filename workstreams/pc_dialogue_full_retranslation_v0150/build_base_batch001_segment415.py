#!/usr/bin/env python3
"""Build Base authoring segment 415 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S415.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s415", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1759:0": "에 대한 공략을 중단한다\n뜻대로 되지 않는 법이군",
    "7:1760:0": "에 대한 공격을 중단한다\n병사들을 성에서 쉬게 해야 한다",
    "7:1761:0": "이래서는—",
    "7:1761:1": "은(는)\n공격할 수 없겠군",
    "7:1762:0": "을(를) 공략하는 일은……\n이제 이루지 못하는가",
    "7:1763:0": "에 대한 공격을 중단한다\n성에서 병사들을 쉬게 하라",
    "7:1764:0": "에 대한 공략을 중단한다\n우리는 철수한다",
    "7:1765:0": "은(는) 이제 됐다\n병사들을 물린다",
    "7:1766:0": "에 대한 공격을 중단한다\n물러나라…… 병량이 아깝다",
    "7:1767:0": "은(는) 공격할 수\n없군. 귀환한다",
    "7:1768:0": "에 대한 공격은\n중단하고 돌아가야겠군……",
    "7:1769:0": "은(는) 공격할 수\n없겠네요. 돌아가겠습니다",
    "7:1770:0": "에 대한 공격을\n중단한다. 돌아간다",
    "7:1771:0": "은(는) 공격할 수\n없습니다. 돌아갑시다",
    "7:1772:0": "을(를) 공략할 수 없다\n철수한다",
    "7:1773:0": "은(는)…… 지켜야 할\n성이 아니게 되었는가",
    "7:1774:0": "은(는) 이제\n지키지 않아도 된다…… 철수!",
    "7:1775:0": "은(는) 이제 됐다\n병사들을 쉬게 하자꾸나",
    "7:1776:0": "은(는) 방어할 필요가 없다\n병력을 거두어 비용을 줄인다",
    "7:1777:0": "에 대한 방어를 중단한다\n병사들을 물려라",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S415", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
