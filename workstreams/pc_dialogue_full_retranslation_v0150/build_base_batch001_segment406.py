#!/usr/bin/env python3
"""Build Base authoring segment 406 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S406.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s406", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1645:0": "은(는) 수비가 허술한 듯하옵니다\n",
    "7:1645:1": "와(과)의 우호 관계\n지침을 재검토할 때인 듯하옵니다",
    "7:1646:0": "의 성—",
    "7:1646:1": "\n방심하고 있는 듯합니다\n공격하려면 지금일 듯하군요",
    "7:1647:0": "은(는) 수비가 허술하옵니다\n",
    "7:1647:1": "을(를) 공격해야 하옵니다!\n지침 변경을 청하옵니다",
    "7:1648:0": "의 성—",
    "7:1648:1": "\n지금 함락하지 않는다면\n언제 함락하겠습니까",
    "7:1649:0": "은(는) 함락하기 쉬울 듯하옵니다\n",
    "7:1649:1": "와(과)는 단교하십시다\n지침 변경을 청하옵니다",
    "7:1650:0": "이제는—",
    "7:1650:1": "에\n마음 쓰실 필요 없사옵니다\n",
    "7:1650:2": "을(를) 함락합시다",
    "7:1651:0": "은(는) 수비가 허술해 노릴 만하옵니다\n",
    "7:1651:1": "와(과)의 우호 지침을\n변경해야 하지 않겠사옵니까?",
    "7:1652:0": "우호 관계인 가문—",
    "7:1652:1": "\n지금이야말로 인연을 끊고\n",
    "7:1652:2": "을(를) 공격해야 할 듯하옵니다",
    "7:1653:0": "따위는 겁쟁이에 불과하오\n",
    "7:1653:1": "을(를) 빼앗을 때는 지금이오\n지침을 변경하시옵소서",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S406", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
