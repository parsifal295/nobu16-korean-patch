#!/usr/bin/env python3
"""Build Base authoring segment 140 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S140.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s140", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2615:0": "출병한 지 얼마 되지도 않아 싸움에 집중하고 싶지만\n이쪽도 소홀히 할 수는 없겠군",
    "6:2616:0": "싸움만 할 수는 없나, 어쩔 수 없지.\n교섭도 해야 한다는 건가",
    "6:2617:0": "출진한 지 얼마 되지 않았으나\n그럴수록 외교를 소홀히 할 수 없다",
    "6:2618:0": "무용만으로 해결되지 않는 일도 있다\n이럴 때야말로 외교에도 힘써야 하느니라",
    "6:2619:0": "싸움은 병사로만 하는 것이 아니니, 말로 치르는 것 또한\n싸움의 한 형태이니라",
    "6:2620:0": "싸움만으로 해결되는 일만 있는 것은 아니다\n오히려 언변으로 끝낼 수 있는 일도 많다",
    "6:2621:0": "내 지혜를 살려야겠군\n싸움만이 능사는 아닐 테니",
    "6:2622:0": "병사를 부리는 무략도 좋으나\n언변을 펼치는 지략도 소홀히 할 수 없다",
    "6:2623:0": "출병한 이상 전의를 벼려야겠지만\n지금은 혀끝을 벼릴 때인가",
    "6:2624:0": "말이 아니라 칼과 창으로 모든 뜻을 전할 수 있다면\n무슨 일이든 편할 텐데 말이지",
    "6:2625:0": "병력을 냈으니 뒤에서도 움직이는 것이다\n이 이치를 모르는 자가 많지만 말이지",
    "6:2626:0": "원교근공, 이것이 바로 삼십육계의\n스물세 번째 계책이니, 똑똑히 보여 주마",
    "6:2627:0": "병마의 길을 걷는다 해도 그것만으로\n살아남을 수는 없다. 외교 또한 중요하다",
    "6:2628:0": "설령 출병 중이라 해도 타국과의 교섭을\n소홀히 해 어리석다 비웃음받고 싶지는 않군",
    "6:2629:0": "출진하자마자 타국과 교섭이라\n노회하다는 말을 들어도 어쩔 수 없겠군",
    "6:2630:0": "자, 전쟁에만 매달리고 있다가는\n나잇값도 못한다는 말을 듣겠구나",
    "6:2631:0": "전쟁이 이어지고 있습니다만\n그래도 교섭을 잊어서는 안 되겠지요",
    "6:2632:0": "싸움으로 자웅을 겨루는 것뿐 아니라\n담판을 벌이는 것도 하나의 수입니다",
    "6:2633:0": "싸움만으로는 병력이 모자라나. 내키지는 않지만\n여기서는 언변을 쓰는 것도 방법이겠군",
    "6:2634:0": "눈앞의 싸움만 계속 바라보는 것은\n다이묘가 할 일이 아니라는 건가",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S140", "decision_count": len(rows),
                             "retranslated": len(rows), "dynamic_runtime_review_pending": 0,
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
