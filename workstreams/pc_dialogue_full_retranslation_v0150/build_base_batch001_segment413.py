#!/usr/bin/env python3
"""Build Base authoring segment 413 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S413.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s413", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1722:0": "이거 곤란하게 됐군\n장기전이 되면 병량이 부족하겠어……",
    "7:1723:0": "병량 없이는 싸움이 되지 않사옵니다\n출진을 취소하고\n더 사 두어야 할 듯하옵니다",
    "7:1724:0": "병량고를 살펴 주시옵소서\n이 정도로는\n싸움에서 이길 수 없사옵니다",
    "7:1725:0": "공성에 쓸 병량이 부족합니다\n추가로 구입하는 것이 어떻겠습니까?",
    "7:1726:0": "병량이 불안하군요……\n성을 함락하려면\n더 사 두는 것도 검토합시다",
    "7:1727:0": "병량이 부족하군\n이래서는 어느 성도 함락할 수 없을 터\n추가 구입을 권하오",
    "7:1728:0": "병량 없이 싸움에 나서는 것은\n다소 무모한 일인지도\n모르옵니다",
    "7:1729:0": "병량이 부족한 듯합니다\n추가로 구입하는 것이 어떻겠습니까",
    "7:1730:0": "출진 전에 확인해 주십시오\n병량이 상당히 부족합니다",
    "7:1731:0": "성을 공격하기에는\n병량이 부족하옵니다\n추가로 구입하는 것이 어떻겠습니까",
    "7:1732:0": "주군, 잠시 기다려 주십시오\n병량 없이는\n싸움에서 이길 수 없습니다",
    "7:1733:0": "에 입성할 수 없는가\n어쩔 도리가 없군",
    "7:1734:0": "에는 입성할 수 없겠구나\n다른 곳으로 가자꾸나",
    "7:1735:0": "은(는) 입성할 수 없다\n그렇다면 다른 곳을 알아볼 뿐이다",
    "7:1736:0": "에 갈 수 없는가\n그렇다면 다음 성이다",
    "7:1737:0": "에는 입성할 수 없다……\n진로를 바꿔라, 다음 성으로 향한다",
    "7:1738:0": "에서 쉴 수 없는가\n그렇다면 차선책을 써야겠군",
    "7:1739:0": "에 입성할 수 없는가\n어쩔 수 없지, 다음 성이다!",
    "7:1740:0": "에 입성할 수 없다……\n다른 곳으로 갈 수밖에 없겠군",
    "7:1741:0": "에는 입성 못 하겠군\n별수 없지, 다음이다",
}

STATIC_COORDINATES: set[str] = {
    "7:1722:0", "7:1723:0", "7:1724:0", "7:1725:0", "7:1726:0", "7:1727:0",
    "7:1728:0", "7:1729:0", "7:1730:0", "7:1731:0", "7:1732:0",
}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S413", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
