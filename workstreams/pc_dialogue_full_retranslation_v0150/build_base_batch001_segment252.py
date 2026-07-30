#!/usr/bin/env python3
"""Build Base authoring segment 252 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S252.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s252", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4010:1": "\n하명만 내리시면 곧바로 싸울 채비를 갖추어\n우리 가문의 힘을 천하에 떨치",
    "6:4011:0": "을(를) 공략 목표에서 제외합니다\n괜찮으시겠습니까?",
    "6:4012:0": "공략",
    "6:4012:1": "\n우리 병력이 앞서 있",
    "6:4012:2": "지만\n위신에 압도되어 병사들이 위축되어 있",
    "6:4013:0": "공략",
    "6:4013:1": "\n병력은 대등… 그러나 위신에 압도되어\n우리 가문의 병사들이 위축되어 있",
    "6:4014:0": "공략",
    "6:4014:1": "\n병력에서 뒤지는 데다 위신에도 압도되어\n우리 가문의 병사들이 위축되어 있",
    "6:4015:0": "공략",
    "6:4015:1": "\n병력은 우세하지만 위신에서 뒤져\n병사들이 본래의 힘을 발휘하지 못하",
    "6:4016:0": "공략",
    "6:4016:1": "\n병력은 대등하지만 위신에서 뒤져\n병사들이 본래의 힘을 발휘하지 못하",
    "6:4017:0": "공략",
    "6:4017:1": "\n병력에서 뒤지는 데다 위신에서도 밀려\n병사들이 본래의 힘을 발휘하지 못하",
    "6:4018:0": "공략",
    "6:4018:1": "\n우리 가문의 병력이 앞서 있",
    "6:4019:0": "공략",
    "6:4019:1": "\n병력이 대등하게 맞서 있",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S252", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
