#!/usr/bin/env python3
"""Build Base authoring segment 402 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S402.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s402", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1603:0": "의 수비를 보니\n정면 공격은 어려울 듯하군……\n지리적 이점이 필요하겠어",
    "7:1604:0": "의 수비는 빈틈없으나\n그렇다면 주변부터 빼앗아\n고립시키면 되는 것이외다",
    "7:1605:0": "을(를) 공격하기는\n힘깨나 들겠군요\n발판만 있다면 어찌해 볼 수도……",
    "7:1606:0": "급할수록 돌아가라\n",
    "7:1606:1": "은(는) 주변부터\n제압한 뒤에 공격합시다",
    "7:1607:0": "을(를) 함락하기는\n역시 어렵다\n하지만 지리적 이점을 얻는다면……",
    "7:1608:0": "이(가) 견고하다 해도\n주변부터 무너뜨리고 나면\n별것 아닐 터",
    "7:1609:0": "을(를) 함락하기는\n어려울지도 모릅니다\n주변부터 무너뜨려 갑시다",
    "7:1610:0": "을(를) 공격하기 전에\n주변부터 제압하는 건 어떻습니까?",
    "7:1611:0": "지금 우리 힘으로는—",
    "7:1611:1": "을(를) 함락하기 어렵습니다\n만약 공격한다면\n조금이라도 지리적 이점을 얻어야 합니다",
    "7:1612:0": "을(를) 공략하려면 애를 먹을 듯합니다\n기반을 다져 가며\n침공해야 한다고 생각합니다",
    "7:1613:0": "이(가) 노릴 만하겠군\n",
    "7:1613:1": "와(과)의 우호 관계를 끊기에도\n좋은 기회일지 모르겠군",
    "7:1614:0": "의 성—",
    "7:1614:1": "\n우리 가문의 것으로\n삼고 싶은데……",
    "7:1615:0": "이(가) 알맞은 표적이군요\n",
    "7:1615:1": "와(과)의 연이 끊어진다면\n함락시켜 보이겠습니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S402", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
