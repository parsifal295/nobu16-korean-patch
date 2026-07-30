#!/usr/bin/env python3
"""Build Base authoring segment 370 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S370.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s370", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1004:1": "」을(를) 따르는 것이\n옳은 선택인 듯하군요",
    "7:1005:0": "에게 이기다니……\n평소에도 해낼 줄은 알았다만\n",
    "7:1005:1": "을(를) 다시 보게 되었노라",
    "7:1006:0": "에게 이겼군요\n우리의 비호자는 「",
    "7:1006:1": "」 외에는\n달리 없사옵니다",
    "7:1007:0": "에게 이기다니!\n우리가 살아남을 길은\n",
    "7:1007:1": "에 있다고 보았다!",
    "7:1008:0": "이대로 싸우면 우리 측이 이길 것으로 보입니다\n합전을 직접 지휘하시겠습니까?",
    "7:1009:0": "이대로 싸워도 승산이 희박합니다\n",
    "7:1009:1": "와(과) 합전을 벌이시겠습니까?",
    "7:1010:0": "와(과)의 싸움에서는\n아군이 다소 유리할 것으로 보입니다\n합전을 벌이시겠습니까?",
    "7:1011:0": "와(과)의 싸움에서는\n아군이 다소 불리할 것으로 보입니다\n합전을 벌이시겠습니까?",
    "7:1012:0": "와(과)의 싸움은 호각입니다\n승패는 지휘에 달렸을 것입니다\n합전을 벌이시겠습니까?",
    "7:1013:0": "따위에게\n천하로 가는 길을 막게 두지는 않겠다",
    "7:1014:0": "은(는) 어리석은 자로다\n이 노부나가를 적으로 돌리다니",
    "7:1015:0": "라면\n문제없이 이길 수 있겠지",
    "7:1016:0": "은(는) 약소하나\n쳐들어온 이상 내버려 둘 수 없다",
    "7:1017:0": "라면\n그리 수고롭지 않을 터",
    "7:1018:0": "따위는\n방심하지만 않으면 쉽게 물리칠 수 있으리라",
    "7:1019:0": "을(를) 상대로\n전력을 다할 필요는 없을 것이오",
}

STATIC_COORDINATES: set[str] = {"7:1008:0"}


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
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S370", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
