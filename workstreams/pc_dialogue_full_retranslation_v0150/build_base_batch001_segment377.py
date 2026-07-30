#!/usr/bin/env python3
"""Build Base authoring segment 377 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S377.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s377", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1138:0": "이(가) 쳐들어왔습니다\n우리는 열세이오나 무사에게는\n반드시 싸워야 할 때가 있사옵니다",
    "7:1139:0": "이(가) 쳐들어왔습니다\n전황은 중과부적…… 지금이야말로\n풍림화산의 병법을 펼쳐 보일 때입니다!",
    "7:1140:0": "이(가) 대군으로\n우리 영지를 침범하고 있사옵니다\n영민을 위해서라도 싸우십시다",
    "7:1141:0": "의 대군이 내습했습니다!\n싸움은 죽을 각오로 임해야 사는 법\n사력을 다해 물리치십시다",
    "7:1142:0": "이(가) 쳐들어왔습니다\n적은 대군…… 하지만 싸움은 수가 아닙니다\n운은 하늘에 있는 법……입니다",
    "7:1143:0": "이(가) 쳐들어왔소이다\n적이 강대하다고는 하나\n가문을 지키기 위해 일어서야 할 듯하옵니다",
    "7:1144:0": "이(가) 대군으로 접근 중이옵니다\n망설여 봐야 아무 소용 없으니\n속히 요격군을 내보내시옵소서",
    "7:1145:0": "이(가) 쳐들어왔는가\n수가 많다 한들 마른 나무 무리일 뿐\n이 열세를 뒤집어 보십시다!",
    "7:1146:0": "적이 대군으로 내습했습니다……\n하지만 「",
    "7:1146:1": "」이(가) 무슨 대수겠습니까\n물리쳐 이름을 떨치도록 하지요",
    "7:1147:0": "이(가) 내습했습니다\n아무리 강대한 적이라 해도\n맞서야 할 때가 있사옵니다",
    "7:1148:0": "적이 대군으로 다가오고 있습니다\n하지만 「",
    "7:1148:1": "」에게\n영민을 제멋대로 다루게 둘 수는 없사옵니다",
    "7:1149:0": "이(가) 쳐들어왔다더군\n수로 짓눌러 보겠다는 속셈이겠지만\n그렇게는 안 되지…… 그렇지?",
    "7:1150:0": "이(가) 쳐들어왔다고?\n게다가 아군은 소수에 적은 다수라……\n재미있는 싸움이 되겠군!",
    "7:1151:0": "이(가) 대군으로 접근 중이오……\n설령 죽는 한이 있더라도\n무사의 긍지를 걸고 맞서야 하오",
    "7:1152:0": "의 내습입니다!\n아무리 강대한 적이라 하더라도\n일격을 되갚아 주겠습니다",
    "7:1153:0": "이(가) 우리 영지에 난입했습니다……\n압도적인 적에게 맞서는 것은 어리석지만\n우리에게도 굽힐 수 없는 긍지가 있사옵니다",
    "7:1154:0": "이(가) 대군을 이끌고 진군 중이오\n호락호락 승리를 내주는 법은 없으니\n결사의 싸움을 보여 드리리다",
    "7:1155:0": "쳐들어오는 「",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S377", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
