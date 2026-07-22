#!/usr/bin/env python3
"""Build Base authoring segment 409 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S409.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s409", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1671:0": "은(는) 약체화되어 있소\n지침을 철회해 주시오\n",
    "7:1671:1": "은(는) 차지합시다",
    "7:1672:0": "의 성—",
    "7:1672:1": "\n노려볼 만한 곳이겠지요\n지침 변경을 청하옵니다",
    "7:1673:0": "지침 변경을 요청합니다\n",
    "7:1673:1": "은(는) 두려워할 상대가 아닙니다\n",
    "7:1673:2": "을(를) 빼앗는 것입니다",
    "7:1674:0": "에게서—",
    "7:1674:1": "\n을(를) 빼앗는 것쯤 식은 죽 먹기\n명을 내려 주시오",
    "7:1675:0": "의 성—",
    "7:1675:1": "\n이라면 함락할 수 있을 것입니다\n지침 변경을 청하옵니다",
    "7:1676:0": "지침 변경을 검토해 주시옵소서\n",
    "7:1676:1": "의 성—",
    "7:1676:2": "\n은(는) 어렵지 않게 함락할 수 있사옵니다",
    "7:1677:0": "이(가) 어쨌다는 것이냐\n",
    "7:1677:1": "을(를) 무너뜨립시다\n지침 변경을 검토해 주시오",
    "7:1678:0": "따위\n두려워할 것 없소!\n",
    "7:1678:1": "을(를) 함락해야 할 듯하옵니다",
    "7:1679:0": "지침을 변경합시다\n",
    "7:1679:1": "의 성—",
    "7:1679:2": "이라면\n공격할 수 있습니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S409", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
