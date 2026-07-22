#!/usr/bin/env python3
"""Build Base authoring segment 400 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S400.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s400", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1573:0": "지금의 힘으로는—",
    "7:1573:1": "을(를) 함락할 수 없다\n그렇다면 지리적 이점을 확보해\n맞서면 그만이다!",
    "7:1574:0": "은(는) 차지하고 싶지만……\n먼저 주변부터 무너뜨리지 않으면\n고전을 면치 못하리라",
    "7:1575:0": "을(를) 함락하기에는\n다소 힘이 부족하옵니다\n하지만 지리적 이점을 얻는다면……",
    "7:1576:0": "정면으로 치는 것만이 전쟁은 아니다\n",
    "7:1576:1": "의 주변을\n제압하는 것부터 시작하는 게다!",
    "7:1577:0": "지금의 우리 힘으로는—",
    "7:1577:1": "을(를) 함락하기가\n어려울 것이오\n우선 지리적 이점을 얻어야 하오",
    "7:1578:0": "무슨 일에든 순서가 있사옵니다\n",
    "7:1578:1": "의 주변 지역을 장악하고\n공성은 그다음이 좋을 듯하옵니다",
    "7:1579:0": "을(를) 당장\n공격해서는 아니 되옵니다\n모든 일은 지리적 이점을 얻은 뒤에 하시지요",
    "7:1580:0": "의 주변 지역에 병력을 보내\n발판을 다져 두면\n애먹을 상대는 아니옵니다",
    "7:1581:0": "사람을 쏘려거든 먼저 말을 쏘라\n",
    "7:1581:1": "을(를) 지탱하는 지역부터\n공격해야 하오",
    "7:1582:0": "을(를) 공략하는 일은 난항을 겪겠구나\n주변 지역을 제압한다면\n활로를 찾을 수 있으리라",
    "7:1583:0": "은(는) 단숨에 함락되지 않을 터\n주변을 차근차근 장악한 뒤\n공성에 나서야 할 것이오",
    "7:1584:0": "을(를) 공격하려면\n먼저 기반을 다지는 것이 긴요하니\n주변 제압을 서두르십시다",
    "7:1585:0": "을(를) 함락하기는\n어려울 것이오\n허나 지리적 이점이 없을 때의 이야기요",
    "7:1586:0": "서두를 필요는 없으리라\n",
    "7:1586:1": "의 주변부터 무너뜨려\n완전히 무방비로 만들면 되는 것이다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S400", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
