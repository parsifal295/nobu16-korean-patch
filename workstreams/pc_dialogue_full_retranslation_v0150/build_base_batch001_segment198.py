#!/usr/bin/env python3
"""Build Base authoring segment 198 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S198.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s198", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3415:0": "미지행 군 가운데 병량 생산 효과를 지닌 군에\n정무 능력이 높은 무장을 우선 임명합니다\n계속하시겠습니까?",
    "6:3416:0": "미지행 군 가운데 금전 수입 효과를 지닌 군에\n정무 능력이 높은 무장을 우선 임명합니다\n계속하시겠습니까?",
    "6:3417:0": "미지행 군 가운데 병력 상승 효과를 지닌 군에\n정무 능력이 높은 무장을 우선 임명합니다\n계속하시겠습니까?",
    "6:3418:0": "미지행 군 가운데 군마 생산 효과를 지닌 군에\n정무 능력이 높은 무장을 우선 임명합니다\n계속하시겠습니까?",
    "6:3419:0": "미지행 군 가운데 철포 생산 효과를 지닌 군에\n정무 능력이 높은 무장을 우선 임명합니다\n계속하시겠습니까?",
    "6:3420:0": "모든 군의 지행 무장을 해임합니다\n계속하시겠습니까?",
    "6:3421:0": "이(가)",
    "6:3421:1": "의 임기에 따른\n충성 보정을 잃습니다. 계속하시겠습니까?",
    "6:3422:0": "의",
    "6:3422:1": "이(가) 제일이라고!?\n",
    "6:3422:2": "의 은혜가 뼛속까지 사무치는군…\n좋아, 올해도 죽어라 일해 주마!",
    "6:3423:0": "이(가) 훈공 1위라…\n아랫사람들의 활약도",
    "6:3423:1": "은(는) 지켜보고 계시는군\n더욱 힘써야겠다!",
    "6:3424:0": "의",
    "6:3424:1": "이(가) 제일인가…\n쑥스럽기는 하나 기쁜 일이로군\n올해도 힘써,",
    "6:3424:2": "의 힘이 되어 드리겠소이다",
    "6:3425:0": "이(가) 훈공 1위라니…\n미숙한 몸에 과분한 평가\n황공하기 그지없사옵니다",
    "6:3426:0": "이(가) 훈공 1위라니…\n이 미천한 몸은 그저 악착같이 땀 흘려\n가문에 보탬이 되려는 일념뿐이었소",
    "6:3427:0": "이(가) 훈공 1위라 해도 놀랄 일은 아니다\n오히려 놀라운 것은 이토록 낮은 자에게\n공을 세울 기회를 내린",
    "6:3427:1": "의 혜안이 아니겠는가…?",
}

STATIC_COORDINATES: set[str] = {
    "6:3415:0",
    "6:3416:0",
    "6:3417:0",
    "6:3418:0",
    "6:3419:0",
    "6:3420:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S198", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
