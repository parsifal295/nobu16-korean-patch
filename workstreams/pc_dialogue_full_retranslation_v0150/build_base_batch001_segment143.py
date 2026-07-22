#!/usr/bin/env python3
"""Build Base authoring segment 143 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S143.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s143", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2670:0": "이 판세를 바꾸려면,",
    "6:2670:1": "와(과)\n새로운 우호 관계를 맺어야겠군",
    "6:2671:0": "새로운 관계를 맺는 것도 한 수인가\n좋다,",
    "6:2671:1": "와(과)의 사이를 돈독히 하겠다",
    "6:2672:0": "싸움만이 내 재주는 아니다. 여기서는\n",
    "6:2672:1": "와(과) 친선을 다져야겠다",
    "6:2673:0": "합종연횡과 오월동주는 세상의 이치. 지금은\n",
    "6:2673:1": "와(과) 새로 친교를 맺어야 한다",
    "6:2674:0": "앞날은 모르나 지금 이 순간에는",
    "6:2674:1": "와(과)\n친해져 두는 것이 좋겠군",
    "6:2675:0": "와(과)는 가까워져 두자.\n그리 정했으면 움직여야지",
    "6:2676:0": "와(과)의 친선을 다져야겠군\n그렇다면 무엇부터 해야 하나…",
    "6:2677:0": "앞날을 생각하면,",
    "6:2677:1": "와(과)는\n좋은 사이로 지내고 싶구나",
    "6:2678:0": "와(과) 친분을 맺어 두는 것이\n좋은 포석이 되겠군",
    "6:2679:0": "우리 쪽 사정이기는 합니다만\n",
    "6:2679:1": "에게 우호를 청해야 합니다",
    "6:2680:0": "우리가 처한 형편을 생각하면\n",
    "6:2680:1": "와(과) 친해지는 것이 최선일 것입니다",
    "6:2681:0": "우리 가문의 앞날을 헤아리건대,",
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S143", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
