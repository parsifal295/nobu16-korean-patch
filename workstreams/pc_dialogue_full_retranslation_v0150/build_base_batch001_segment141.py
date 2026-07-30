#!/usr/bin/env python3
"""Build Base authoring segment 141 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S141.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s141", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2635:0": "진중에 있더라도 한 단계 높은 곳에서\n전체를 내다보며 외교의 수를 두어야겠지요",
    "6:2636:0": "출병한 지 얼마 되지 않았지만\n외교에서 활로를 찾아봅시다",
    "6:2637:0": "싸움에만 눈을 두지 말고 바깥과의 교섭에서\n길을 찾는 것도 한 방법이려나",
    "6:2638:0": "병력을 움직인 때야말로 담판이\n순조롭게 풀리는 일도 있겠지",
    "6:2639:0": "앞으로 저놈들과 한판 붙어야 하니까\n그러려면 외교도 해내고 말겠어",
    "6:2640:0": "옆에서 훼방 놓는 건 질색이야\n바깥과의 교섭도 해 둬야겠군",
    "6:2641:0": "언젠가 전쟁이 벌어질 것은 틀림없다\n그에 대비해 교섭도 해 두어야겠군",
    "6:2642:0": "무력에 호소할 때는 반드시 온다. 그렇다면\n이에 대비하지 않는 것은 필부의 용맹일 뿐이다",
    "6:2643:0": "저 원수와 전쟁을 벌이는 것은 필연이다. 그렇다면\n그에 대비하는 것 또한 당연하도다",
    "6:2644:0": "눈앞에 적이 있는 와중에도 언변으로 길을\n낼 수 있다면 그보다 나은 일은 없겠지",
    "6:2645:0": "눈앞의 적에 대비하려면\n언변을 써야 할 것이야",
    "6:2646:0": "우리가 저 적과 싸우려면\n쓸 수 있는 수는 모두 써야 한다",
    "6:2647:0": "적과의 싸움이 기다리고 있으니\n걱정거리는 미리 매듭지어야겠군",
    "6:2648:0": "병마를 갖추는 것과 같은 이치다. 외교로도\n전쟁에 대비하지 않으면 말이 안 되지",
    "6:2649:0": "자, 우리의 언변이 적의 일군보다도 강하다는 것을\n보여 주도록 하세",
    "6:2650:0": "원수와 맞설 채비를 함은 지극히 당연한 일\n우선 외교로 판을 마련해 두지",
    "6:2651:0": "병사를 부리는 것만이 싸움은 아니다\n외교 또한 싸움임을 보여 주겠다",
    "6:2652:0": "저 적과 창칼을 맞대기 전에\n외교로 대비해 두어야 할 것이다",
    "6:2653:0": "적과의 싸움이 기다리고 있느니라\n교섭에도 힘써 두어야겠구나",
    "6:2654:0": "외교로도 대비해 두지 않으면\n적과의 싸움에서 뒤처지고 말겠지",
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
                     "semantic_review": "approved", "scope_classification": "retranslated",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S141", "decision_count": len(rows),
                             "retranslated": len(rows), "dynamic_runtime_review_pending": 0,
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
