#!/usr/bin/env python3
"""Build Base authoring segment 378 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S378.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s378", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1155:1": "」은(는) 강대하군요\n하지만 앉아서 죽음을 기다릴……\n수는 없는 노릇이지요",
    "7:1156:0": "이(가) 대군으로 내습한다는군요\n놈들에게 부드러움이 강함을 제압하는 이치를\n가르쳐 주지 않겠습니까",
    "7:1157:0": "의 내습이오\n중과부적…… 그야말로 절체절명이니\n죽음으로 이름을 남길 때는 지금이오",
    "7:1158:0": "의 대군이 침공했습니다……\n각오를 굳히셨다면\n요격 명령을 내려 주시옵소서",
    "7:1159:0": "이(가) 쳐들어왔습니다\n적에게는 강대한 전력이 있사오나\n우리에게는 주군과 제 재주가 있사옵니다",
    "7:1160:0": "강대한 「",
    "7:1160:1": "」이(가) 접근 중이옵니다\n부디 요격을 명해 주시옵소서!\n어떻게든 해낼 수 있을지도 모르옵니다",
    "7:1161:0": "의 대군이 접근한다 하옵니다\n주군의 명이라면\n강적을 상대로 산화하는 것도 흥이겠지요",
    "7:1162:0": "이(가) 대군으로 내습한다 하옵니다\n부디 출진 명령을 내려 주시옵소서\n강적에게 겁먹는 법은 알지 못하옵니다",
    "7:1163:0": "의 침공은 강력하오\n하지만 포기하지 않으면 어떻게든 될 것이니\n출진 명령을 내려 주시오",
    "7:1164:0": "이(가) 다가오고 있다 하옵니다\n승산이 희박한 싸움이오나\n치고 나가지 않으면 패배는 확실하옵니다",
    "7:1165:0": "이(가) 다가오고 있다 하옵니다\n아무리 강대한 적이라 해도\n그저 사력을 다할 뿐입니다",
    "7:1166:0": "이(가) 내습했습니다!\n적은 압도적이오나 우리 영지를\n마음대로 유린하게 둘 수는 없사옵니다",
    "7:1167:0": "이(가) 대군으로 침공한다 하옵니다\n각오는 이미 마쳤사오니\n출격을 명해 주시옵소서",
    "7:1168:0": "이(가) 다가오고 있사옵니다\n당해 내지 못할 상대일지도 모르오나\n그래도 한칼만이라도……!",
    "7:1169:0": "이(가) 대군으로 내습한다 하옵니다\n설령 적과 함께 죽는 한이 있더라도\n영민을 지키고 싶사옵니다",
    "7:1170:0": "의 침공입니다\n중과부적이오나…… 호락호락\n적이 제멋대로 하게 두지는 않겠습니다",
    "7:1171:0": "은(는) 강대합니다!\n이대로 잠자코 지켜보기만 하면\n놈들의 먹잇감이 되고 말 것이옵니다",
    "7:1172:0": "의 침공입니다!\n피아의 전력 차이는 막대합니다!\n서둘러 요격하지 않으면……!",
    "7:1173:0": "이(가) 다가오고 있군\n승산은 희박하니\n정전을 청하는 것이 상책이겠지",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S378", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
