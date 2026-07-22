#!/usr/bin/env python3
"""Build Base authoring segment 147 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S147.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s147", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2721:1": "이라면 어쩔 수 없지. 하지만 지금뿐이다",
    "6:2722:0": "놈, 우리 가문을 복종시키니 흡족하냐\n언젠가 하극상을 일으키고 말겠다",
    "6:2723:0": "겉으로 따르고 속으로 거스르는 건 성미에 맞지 않지만, 지금은\n",
    "6:2723:1": "에게 그렇게 믿도록 해야겠지",
    "6:2724:0": "에 복종하다니 한심한 일이지만\n지금은 와신상담을 각오할 수밖에 없다",
    "6:2725:0": "지금은,",
    "6:2725:1": "에 따를 수밖에 없겠구먼\n참아야지, 지금은 참아야 해…",
    "6:2726:0": "참고 견딘 끝에 무엇이 기다릴지는 모르지만\n",
    "6:2726:1": "에게 지금은 신종할 수밖에 없겠지",
    "6:2727:0": "신종하는 처지는 괴롭지만 언제까지나\n",
    "6:2727:1": "을(를) 따를 이유는 없습니다",
    "6:2728:0": "언젠가 반드시 종속된",
    "6:2728:1": "이(가)\n이 멍에를 벗어던질 것입니다",
    "6:2729:0": "힘이 모자라 굴욕의 길을 걷고 있지만\n언젠가",
    "6:2729:1": "을(를) 뛰어넘고 말겠다",
    "6:2730:0": "기댈 바에는 큰 나무 그늘이라지만\n그 나무인",
    "6:2730:1": "이(가) 꺾이고 썩지 않으리란 법은 없지",
    "6:2731:0": "지금은,",
    "6:2731:1": "의 비호에 기댈 수밖에 없지만\n언젠가는 스스로의 힘으로 서야 합니다",
    "6:2732:0": "에 종속한 이상 여기서는\n몸이 부서져라 일할 수밖에 없겠군요",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S147", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
