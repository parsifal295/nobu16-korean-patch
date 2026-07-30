#!/usr/bin/env python3
"""Build Base authoring segment 401 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S401.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s401", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1587:0": "당장—",
    "7:1587:1": "을(를) 공격하는 것은\n상책이 아니옵니다\n먼저 지리적 이점을 확보하십시다",
    "7:1588:0": "의 주변부터\n무너뜨리는 것이 좋을 듯하옵니다\n그리하면 공성도 수월해질 것입니다",
    "7:1589:0": "을(를) 함락하기는\n상당히 어렵겠군\n우선 주변부터 차지해 볼까",
    "7:1590:0": "이(가) 탐나는군\n주변을 빼앗은 뒤\n공격해야 할까……",
    "7:1591:0": "을(를) 함락하는 것은\n지금 우리 힘으로는 어렵사오니\n조금이라도 지리적 이점을 얻어야 할 듯하옵니다",
    "7:1592:0": "을(를) 공격하려면\n주변 지역부터\n제압한 뒤에 나서는 것이 좋을 듯하오",
    "7:1593:0": "을(를) 공략하기는\n쉽지 않을 터\n먼저 주변 지역을 장악해야 한다",
    "7:1594:0": "을(를) 공격하려면\n주변을 평정한 뒤에 나서야\n한결 수월할 것입니다",
    "7:1595:0": "을(를) 쉽게\n함락할 수 있으리라 생각지 않사옵니다\n지리적 이점을 얻은 뒤가 좋을 듯하옵니다",
    "7:1596:0": "이곳에서는 신중히 나아갑시다\n",
    "7:1596:1": "의 주변부터\n제압한 뒤에 공격해야 합니다",
    "7:1597:0": "당장—",
    "7:1597:1": "을(를) 공격해도\n함락하기는 어려우니\n먼저 지리적 이점을 확보합시다",
    "7:1598:0": "을(를) 확실히 공략하려면\n주변 지역을 장악한 뒤\n공격하는 것이 좋을 듯하옵니다",
    "7:1599:0": "지금 전력으로—",
    "7:1599:1": "을(를)\n함락하기는 어렵지만\n지리적 이점을 얻는다면 어쩌면……",
    "7:1600:0": "을(를) 공격하려면\n주변부터 무너뜨린 뒤에\n나서는 것을 권하옵니다",
    "7:1601:0": "을(를) 공략하기는\n쉽지 않을 것입니다\n기반 다지기부터 시작합시다",
    "7:1602:0": "을(를) 차지하려면\n주변을 제압하는 것보다\n나은 방도는 없사옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S401", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
