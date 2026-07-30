#!/usr/bin/env python3
"""Build Base authoring segment 375 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S375.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s375", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1100:0": "이(가) 쳐들어왔습니다\n결코 방심할 수 없는 적이니\n다른 가문에 원군을 청해야 하지 않겠습니까?",
    "7:1101:0": "의 침공입니다\n다른 가문에서 원군을 얻는다면\n절반 이상의 승산이 보일 것입니다",
    "7:1102:0": "이(가) 우리 영지를 침범하는군\n다른 가문에서 원군을 얻어\n우세하게 싸움을 이끌어야 할 듯합니다",
    "7:1103:0": "놈이 쳐들어왔는가……\n무리하게 밀어붙이기보다\n다른 가문의 원군을 청하시오",
    "7:1104:0": "의 침공인가……\n다른 가문에서 원군을 불러\n승리를 확실히 하는 것이 어떻겠소",
    "7:1105:0": "우리 영토를 침범당하다니……\n현재 우리와 「",
    "7:1105:1": "」의 전력은 호각이니\n원군이 있다면 승산을 절반 이상으로 끌어올릴 수 있으리라",
    "7:1106:0": "의 침공은\n결코 얕볼 수 없으니\n원군을 불러 승리를 확실히 하시오",
    "7:1107:0": "에게 공격받았습니까\n원군을 청합시다\n승리를 확실히 하는 것이 상책입니다",
    "7:1108:0": "이(가) 침공해 왔습니다\n승기가 보이지 않는 채 싸워서는 안 되니\n다른 가문에 원군을 요청하시지요",
    "7:1109:0": "이(가) 쳐들어왔어!\n승산은 반반이지만 방심할 수 없어\n원군을 불러 승리를 굳히자고",
    "7:1110:0": "이(가) 쳐들어왔나!\n한시도 방심할 수 없겠군\n원군을 불러 두는 편이 나을지도 몰라",
    "7:1111:0": "의 침공입니다\n승패를 알 수 없는 싸움을 벌이기보다\n다른 가문의 원군을 청해야 할 듯합니다",
    "7:1112:0": "이(가) 내습했습니다!\n다른 가문에 원군을 청해도\n전혀 수치스럽지 않은 상대입니다",
    "7:1113:0": "이(가) 침공해 왔습니다\n승패의 저울이 어느 쪽으로 기울지……\n다른 가문의 원군이 승부를 가를 것입니다",
    "7:1114:0": "이(가) 난입했소\n저들을 격퇴할 열쇠는\n다른 가문의 원군에 있다고 보았소",
    "7:1115:0": "이(가) 쳐들어왔습니다\n승패의 확률은 반반\n다른 가문에서 원군을 부르는 것이 어떻겠습니까?",
    "7:1116:0": "이(가) 침공해 왔습니다\n쉽게 몰아낼 수는 없을 듯하니\n다른 가문에 원군을 청해야 하겠습니다",
    "7:1117:0": "이(가) 침공해 왔소\n결코 가벼이 여겨서는 안 되니\n다른 가문에서 원군을 부르는 것도 한 방법이오",
    "7:1118:0": "은(는)\n우리에게 결코 뒤지지 않는 적이니\n원군을 불러 싸움에 임해야 할 듯합니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S375", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
