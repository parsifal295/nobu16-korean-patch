#!/usr/bin/env python3
"""Build Base authoring segment 146 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S146.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s146", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2708:1": "은(는) 가장 중요한\n상대라 할 수 있지요. 각별히 신경 써야 합니다",
    "6:2709:0": "와(과)의 관계는 좋구나\n함께 손잡고 오래도록 지내고 싶다",
    "6:2710:0": "와(과)는 잘 지내고 있다\n앞으로도 그러하기를 바라노라",
    "6:2711:0": "힘없는 자는 살아남지 못하는 시대다\n지금은",
    "6:2711:1": "의 밑에서 버틸 수밖에 없어",
    "6:2712:0": "에게 복종하다니 화가 치미는군\n흥, 어디 두고 보자",
    "6:2713:0": "무력과 정치에서 미치지 못한다면 따를 수밖에\n",
    "6:2713:1": "의 아래에 서는 것도 어쩔 수 없겠지",
    "6:2714:0": "의 밑에 서는 것은 지금뿐이라 믿고\n여기서 힘을 길러 언젠가 되갚아 주겠다",
    "6:2715:0": "힘이 미치지 못해,",
    "6:2715:1": "에 따르고 있지만\n언젠가 이를 뒤집을 호기도 오겠지",
    "6:2716:0": "강자가 약자를 거느리는 것은 세상의 이치. 하지만\n앞으로도",
    "6:2716:1": "에 따르리란 법은 없지",
    "6:2717:0": "에게 눌리고 말았지만\n지금은 보호막으로 삼는다고 생각해 둘까",
    "6:2718:0": "턱짓에 부림받는 건 아니꼽지만,",
    "6:2718:1": "에는\n따를 수밖에 없겠지… 지금만은 말이다",
    "6:2719:0": "우리 가문이 약한 탓이다,",
    "6:2719:1": "에\n따르기 싫다면 강해지는 수밖에",
    "6:2720:0": "이(가) 남의 밑에 서는 것은 분하지만\n지금은 여기서 힘을 기를 수밖에 없다",
    "6:2721:0": "남의 밑에 서는 것은 성미에 맞지 않지만, 상대가\n",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S146", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
