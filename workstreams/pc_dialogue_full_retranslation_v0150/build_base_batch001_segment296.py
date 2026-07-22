#!/usr/bin/env python3
"""Build Base authoring segment 296 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S296.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s296", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4435:0": "전선의 땅이라니, 가슴이 뛰는 기분",
    "6:4435:1": "\n부디 영주로 임명해 주",
    "6:4436:0": "창을 들고 무공을 세우는 것이야말로 내 본분\n이런 전선에 배속되는 데\n불만이 있을 리가",
    "6:4437:0": "이곳은 적 영지에 가까운 전선이니\n",
    "6:4437:1": "같은 무인이야말로\n영주로 적임일 듯하",
    "6:4438:0": "후방의 땅이야말로 내가 바라던 곳\n…하지만 「",
    "6:4438:1": "」에서는 이 솜씨도\n마음껏 발휘하지는 못하",
    "6:4438:2": "…",
    "6:4439:0": "후방에서 백성을 위해 힘쓰는 것이 내 본분\n부디 영주로 임명해 주십시오",
    "6:4440:0": "정무야말로 내가 가장 잘하는 일\n이런 후방에 배속되는 데\n불만이 있을 리가",
    "6:4441:0": "이곳은 적 영지에서 먼 땅이니\n정무에 능한 「",
    "6:4441:1": "」 같은 사람이야말로\n영주로 적임일 듯하",
    "6:4442:0": "우리 가문의 손길이\n아직 충분히 닿지 않은 땅",
    "6:4442:1": "…\n힘쓸 보람이 있을 듯하",
    "6:4443:0": "…할 일이 많아 보이는 땅",
    "6:4443:1": "\n영주로서의\n수완을 시험하기에 제격입니다",
    "6:4444:0": "참으로 안정된 땅",
    "6:4444:1": "\n안심하고 부임할 수 있을 듯하",
    "6:4445:0": "그 땅에 배속된다면\n할 일을 찾아야 하겠",
    "6:4445:1": "\n참으로 잘 정비된 땅",
}

STATIC_COORDINATES: set[str] = {"6:4439:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S296", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
