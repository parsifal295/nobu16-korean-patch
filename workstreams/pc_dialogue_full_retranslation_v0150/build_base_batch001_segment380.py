#!/usr/bin/env python3
"""Build Base authoring segment 380 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S380.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s380", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1194:0": "강적 「",
    "7:1194:1": "」이(가) 침공해 온다 하옵니다\n정전을 청하시어\n권토중래를 기약하소서",
    "7:1195:0": "이(가) 다가오고 있습니다\n이길 가망은 희박합니다\n정전을 청해야 합니다",
    "7:1196:0": "이(가) 대군을 이끌고 침공합니다\n지금 싸워 봐야 헛되이 힘만 잃을 뿐\n정전하고 기회를 기다립시다",
    "7:1197:0": "이(가) 대군을 이끌고 침공합니다……\n이번 싸움은 단념하시오\n정전을 청해야 할 듯하옵니다",
    "7:1198:0": "이(가) 다가오고 있다 하옵니다\n무리하게 밀어붙여도 득이 없으니\n정전하시는 것이 좋을 듯하옵니다",
    "7:1199:0": "이(가) 대군을 이끌고 다가온다니\n주군의 신변에 무슨 일이라도 생기면……\n정전을 청하심이 어떠하올지",
    "7:1200:0": "이(가) 다가오고 있사옵니다\n정전을 청하시지요…… 강적과 맞서\n병력을 잃고 싶지는 않으실 터",
    "7:1201:0": "이(가) 다가오고 있사옵니다\n그 예봉은 당해 낼 수 없다 하니\n정전을 청해 잠시 피하시지요",
    "7:1202:0": "이(가) 다가오고 있다 하옵니다\n정전을…… 당해 낼 수 없는 적이라면\n우직하게 정면으로 맞설 필요는 없습니다",
    "7:1203:0": "이(가) 대군을 이끌고 왔다 하오\n정전을 청하시오\n살아 있으면 어떻게든 되는 법이오",
    "7:1204:0": "이(가) 다가오고 있사옵니다\n혈기에 휩쓸려 싸우는 것은 어리석은 일\n정전을 청하는 것이 길할 것이외다",
    "7:1205:0": "이(가) 침공해 옵니다\n아군이 압도적으로 불리합니다\n정전하셔야 할 것입니다",
    "7:1206:0": "이(가) 다가오고 있사옵니다\n강적과 싸우지 않는 것 또한 용기\n정전도 하나의 방책이겠지요",
    "7:1207:0": "이(가) 침공해 옵니다\n분하오나 아군에게 득이 없습니다……\n정전도 부득이할 듯합니다",
    "7:1208:0": "이(가) 다가오고 있사옵니다\n지금의 우리로서는 당해 낼 수 없는 상대……\n정전하고 때를 기다리시지요",
    "7:1209:0": "이(가) 대군을 이끌고 다가온다 하옵니다\n병사와 백성이 다치면 너무나 가엾사오니\n부디 정전하여 주시옵소서",
    "7:1210:0": "무시무시한 「",
    "7:1210:1": "」이(가) 쳐들어옵니다\n설령 물리치더라도 희생이 클 터……\n부디 정전을 청하여 주십시오",
    "7:1211:0": "의 침공이옵니다!\n지금의 우리로서는 도저히 당해 낼 수 없사오니\n정전을 청해야 하옵니다!",
}

STATIC_COORDINATES: set[str] = set()


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S380", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
