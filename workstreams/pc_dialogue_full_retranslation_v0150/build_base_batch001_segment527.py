#!/usr/bin/env python3
"""Build Base authoring segment 527 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S527.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s527", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:678:0": "을(를) 위해서라면…\n돌려드리는 것도 마다하지 않겠다",
    "8:679:0": "아아, 어쩔 수 없군\n가져가라",
    "8:680:0": "그 땅을 내놓는 것은 쓸쓸하기도 합니다만\n어쩔 수 없지요…",
    "8:681:0": "께 하사받은 것이니\n돌려드리는 데 무슨 불만이 있겠습니까",
    "8:682:0": "이는 필요한 조치일 것이오\n괘념치 마시고 거두어 주시오",
    "8:683:0": "주명을 거스를 수는 없는 법\n뜻하시는 대로",
    "8:684:0": "의 가신:",
    "8:684:1": "명이 승진",
    "8:685:0": "(으)로 부임한 기간에 따라 「",
    "8:685:1": "」의 훈공+",
    "8:686:0": "의 백성은\n주군을 공경하고 있사옵니다",
    "8:687:0": "의 녀석들\n주군께 홀딱 반했어",
    "8:688:0": "우리 가문의 정치는 「",
    "8:688:1": "」에서\n지지를 받고 있사옵니다",
    "8:689:0": "의 사람들은\n주군을 신뢰하고 있사옵니다",
    "8:690:0": "에서 주군의 동상이\n인기인 듯합니다",
    "8:691:0": "은(는) 당가를 지지하는 쪽으로\n돌아섰사옵니다",
    "8:692:0": "의 많은 이들이\n주군을 따르게 되어…",
    "8:693:0": "의 사람들은\n주군의 정치에 만족한 모양입니다",
    "8:694:0": "의 사람들은\n잘 따르게 되었구려",
    "8:695:0": "의 백성은\n주군을 따르고 있사옵니다!",
    "8:696:0": "은(는) 안정되었소\n이 또한 주군의 위광 덕인가",
    "8:697:0": "의 영민은\n주군을 무척 좋아하는 듯합니다",
}

STATIC_COORDINATES = {
    "8:679:0",
    "8:680:0",
    "8:682:0",
    "8:683:0",
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
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S527", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
