#!/usr/bin/env python3
"""Build Base authoring segment 149 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S149.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s149", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2745:0": "적은,",
    "6:2745:1": "이다. 그 무리에게\n싸움은 붓과 언변으로도 하는 것임을 알려 주자꾸나",
    "6:2746:0": "을(를) 옭아매고 몰아붙이기 위해\n이 언변으로 활로를 찾아볼까",
    "6:2747:0": "우리 가문을,",
    "6:2747:1": "도 주시하고 있겠지만\n이 외교는 막지 못할 것이다",
    "6:2748:0": "이 난세에 정정당당히 싸우는 것은 어리석다. 지금은\n",
    "6:2748:1": "에 맞서 외교의 한 수를 두어야 한다",
    "6:2749:0": "그저 싸우기만 하는 것은 누구나 할 수 있지\n",
    "6:2749:1": "에는 외교로 맞서는 것이 연륜의 힘이다",
    "6:2750:0": "우리 가문이,",
    "6:2750:1": "와(과) 싸우려면\n이번 교섭에서 한 수 앞서야 한다",
    "6:2751:0": "에 맞설 때는\n쓸 수 있는 것을 무엇이든 써야 하옵니다",
    "6:2752:0": "앞으로,",
    "6:2752:1": "와(과) 다툴 때를 대비해\n외교에서 활로를 찾고자 하옵니다",
    "6:2753:0": "무력이 아닌 외교로 맞서는 것은 본의가 아니지만\n",
    "6:2753:1": "을(를) 집어삼키려면 어쩔 수 없다",
    "6:2754:0": "우리 가문이,",
    "6:2754:1": "와(과) 맞서기에는 무력만으로 다소 불안하다\n여기서는 외교에서 활로를 찾아야 한다",
    "6:2755:0": "와(과) 맞서려면 외교로\n대업을 이루는 것도 필요할 것입니다",
    "6:2756:0": "모든 일을 병력으로 해결할 수는 없습니다.\n외교로",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S149", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
