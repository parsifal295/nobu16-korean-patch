#!/usr/bin/env python3
"""Build Base authoring segment 148 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S148.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s148", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2733:0": "에 지금은 따르더라도\n영원토록 신종할 수는 없겠지",
    "6:2734:0": "우리 힘만으로는 어쩔 수 없다. 지금은\n",
    "6:2734:1": "의 아래에서 때를 기다릴 수밖에 없겠지",
    "6:2735:0": "지금 맞설 적은,",
    "6:2735:1": "이(가) 분명하니\n외교까지 동원해 옴짝달싹 못 하게 해 주마",
    "6:2736:0": "따위는 전쟁으로 끝장내\n버리고 싶지만 그리 쉽게 되진 않겠군",
    "6:2737:0": "무용에는 자신 있지만 그것만으로는\n",
    "6:2737:1": "을(를) 집어삼킬 수 없는가",
    "6:2738:0": "을(를) 쓰러뜨리려면 쓸 수 있는 수를\n모두 쓰지 않고서는 낭패를 보겠지",
    "6:2739:0": "당면한 적은,",
    "6:2739:1": "이겠지\n여기서는 외교로도 몰아붙여야 한다",
    "6:2740:0": "눈앞을 가로막는 것은,",
    "6:2740:1": "이(가) 분명하다. 그렇다면\n이 또한 그들을 쳐부수기 위한 포석이다",
    "6:2741:0": "외교도 싸움의 한 형태다. 이를\n",
    "6:2741:1": "에게 똑똑히 보여 줘야겠군",
    "6:2742:0": "을(를) 공략하기 위해 지금은\n언변의 칼날을 맞부딪쳐 보자꾸나",
    "6:2743:0": "이 몸을 무골이라,",
    "6:2743:1": "은(는) 여기고 있겠지만\n외교 하나쯤은 해내 보이겠노라",
    "6:2744:0": "무위로 쓰러뜨리는 것이 최선이지만,",
    "6:2744:1": "은(는)\n그것만으로 쓰러지지 않으니 어쩔 수 없군",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S148", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
