#!/usr/bin/env python3
"""Build Base authoring segment 407 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S407.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s407", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1654:0": "의 성—",
    "7:1654:1": "\n수비가 허술한 듯하오\n공격할 호기이기는 하오나……",
    "7:1655:0": "지침을 변경해 주시옵소서\n",
    "7:1655:1": "에게서 빼앗을 성—",
    "7:1655:2": "\n지금이라면 차지할 수 있을 것이오",
    "7:1656:0": "은(는)—",
    "7:1656:1": "에는\n어울리지 않으니\n공격해 함락해 버립시다",
    "7:1657:0": "은(는) 노려볼 만하오\n지침을 철회해 주시옵소서\n",
    "7:1657:1": "을(를) 차지하도록 합시다",
    "7:1658:0": "의 성—",
    "7:1658:1": "\n이번 기회에 차지하는 것도\n한 방법인 듯하옵니다",
    "7:1659:0": "도 쇠퇴했는가\n지침을 변경합시다\n",
    "7:1659:1": "을(를) 공격할 때로다",
    "7:1660:0": "의 성—",
    "7:1660:1": "\n눈엣가시를 제거하려면\n지금밖에 없겠군요",
    "7:1661:0": "지침을 철회해 주시옵소서\n",
    "7:1661:1": "에게서 빼앗을 성—",
    "7:1661:2": "\n반드시 차지해야 하옵니다",
    "7:1662:0": "의 성—",
    "7:1662:1": "\n시류를 타고 침공해야 할 듯하옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S407", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
