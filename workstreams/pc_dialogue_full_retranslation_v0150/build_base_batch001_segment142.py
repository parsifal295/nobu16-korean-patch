#!/usr/bin/env python3
"""Build Base authoring segment 142 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S142.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s142", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2655:0": "언젠가 전쟁이 벌어질 것은 뻔합니다\n그에 대비하려면 외교도 필요합니다",
    "6:2656:0": "언젠가 병력을 이끌고 싸운다 해도 외교로\n판을 정돈해 두는 것은 유용할 것입니다",
    "6:2657:0": "우리의 원수와는 전쟁으로 자웅을 겨루겠지만\n그러려면 타국과 교류하는 일도 헛되지는 않으리라",
    "6:2658:0": "다가올 싸움에서 온전히 움직이려면\n외교에도 힘써야겠군",
    "6:2659:0": "싸워야 할 상대도 있는 법이니\n외교로 대비하는 것은 당연한 일이지요",
    "6:2660:0": "원수라 부를 상대를 앞에 두고\n교섭으로 끝낼 일을 뒤로 미룰 수는 없습니다",
    "6:2661:0": "적 세력에 맞서려면 대비가 필요하다\n그렇다면 교섭에도 손을 써야겠지",
    "6:2662:0": "적과의 싸움에 만전을 기하려면\n외교도 내버려 둘 수 없는 일이지",
    "6:2663:0": "의 녀석들과는 어떻게든\n친하게 지내 둬야겠군",
    "6:2664:0": "친선을 다지는 거다,",
    "6:2664:1": "의\n우리 가문에 대한 인상을 좋게 해야 해",
    "6:2665:0": "무용만으로는 살아남을 수 없다,",
    "6:2665:1": "와(과)의 관계를\n돈독히 해야겠군",
    "6:2666:0": "함께 싸울 정도까지는 아니더라도\n",
    "6:2666:1": "와(과)는 가까워져야 할 것이다",
    "6:2667:0": "앞날을 생각하면",
    "6:2667:1": "와(과)의\n우호 관계를 다져야 하겠군",
    "6:2668:0": "와(과) 친밀한 사이가 되면\n앞으로의 길도 열릴 것이다",
    "6:2669:0": "이참에,",
    "6:2669:1": "와(과)는 손을 맞잡고\n일에 임하고 싶군",
}

DYNAMIC_COORDINATES = {
    "6:2663:0", "6:2664:0", "6:2664:1", "6:2665:0", "6:2665:1", "6:2666:0",
    "6:2666:1", "6:2667:0", "6:2667:1", "6:2668:0", "6:2669:0", "6:2669:1",
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        dynamic = coordinate in DYNAMIC_COORDINATES
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved",
                     "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                     "layout_review": "unchanged_from_current", "runtime_review": "pending" if dynamic else "not_required",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S142", "decision_count": len(rows),
                             "retranslated": len(rows) - len(DYNAMIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
