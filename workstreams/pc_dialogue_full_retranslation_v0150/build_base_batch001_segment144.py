#!/usr/bin/env python3
"""Build Base authoring segment 144 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S144.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s144", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2681:1": "와(과)\n우호 관계를 맺어야 할 것이오",
    "6:2682:0": "이 난세에 진정한 우의를 나누기 어렵더라도\n",
    "6:2682:1": "와(과)는 친교를 다져야 하리라",
    "6:2683:0": "새로 관계를 맺을 상대라면",
    "6:2683:1": "이(가)\n바람직한 것은 분명하겠지요",
    "6:2684:0": "새로 맺을 상대는,",
    "6:2684:1": "와(과) 우호를 다집시다\n그 관계가 오래 이어지면 좋겠습니다만…",
    "6:2685:0": "와(과)는 무슨 수를 써서라도\n친해져야 하는데, 어찌하면 좋을꼬",
    "6:2686:0": "지금은,",
    "6:2686:1": "와(과) 새로 친교를\n다져 두어야 할 때일 것이다",
    "6:2687:0": "의 무리와는 잘 지내고 있군\n믿음직한 아군이란 좋은 법이지",
    "6:2688:0": "한번쯤,",
    "6:2688:1": "와(과)는 겨뤄 보고 싶지만\n지금의 좋은 관계를 깨고 싶지는 않군",
    "6:2689:0": "와(과) 우리 가문의 사이는 좋다\n이 관계를 지켜 나가고 싶구나",
    "6:2690:0": "믿을 수 있는 상대와 오래 손잡는 것이 상책\n바라건대,",
    "6:2690:1": "이(가) 그런 상대이기를",
    "6:2691:0": "와(과)는 앞으로도 지금의\n좋은 관계를 유지하고 싶구나",
    "6:2692:0": "우리와,",
    "6:2692:1": "와(과)의 굳은 유대가\n훗날까지 이어지기를 기원하겠소",
    "6:2693:0": "와(과)의 우호는 무엇보다 좋은 일.\n그것이 우의인지 사주인지 알 수는 없지만",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S144", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
