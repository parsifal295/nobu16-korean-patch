#!/usr/bin/env python3
"""Build Base authoring segment 374 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S374.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s374", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1080:0": "이라면\n내 기책으로 보기 좋게\n허를 찔러 주마",
    "7:1081:0": ", 상대로 삼기에\n부족함이 없구나\n칼을 맞대는 것도 일흥이로다",
    "7:1082:0": "은(는) 나와 어깨를 나란히 하는 자\n그대로 활개 치게 두기에는\n조금 위험하지 않사옵니까",
    "7:1083:0": ", 상대로 삼기에\n부족함은 없겠구나\n늙었다지만 나 또한 무사다",
    "7:1084:0": "놈, 우리 영지를\n침범하다니 대단한 배짱이로구나\n본때를 보여 주마",
    "7:1085:0": ", 상대하기에\n딱 알맞은 부대입니다\n요격군을 내보내 보시지요",
    "7:1086:0": "을(를) 물리치는 날에는\n주군의 용맹한 명성도\n온 천하에 울려 퍼질 것입니다",
    "7:1087:0": "와(과)는 호각이니\n이기지 못할 적은 아니옵니다\n주군, 결단을 내려 주시옵소서",
    "7:1088:0": "은(는) 제거해야 할 위협\n먼저 쳐들어오다니\n바라마지않던 일이로다!",
    "7:1089:0": ", 우리가 상대하기에\n아무 문제가 없사옵니다\n맞아 싸우시는 것이 어떻겠습니까",
    "7:1090:0": "이(가) 침공해 왔습니다\n영민의 목숨을 지키려면\n반드시 격퇴해야 하옵니다",
    "7:1091:0": ", 그 힘은 우리와 대등하나\n방심하지 않는다면\n밀어붙여 이길 수 있사옵니다",
    "7:1092:0": "에게 침공당했사옵니다\n하지만 병력 차이는 근소하니\n지휘에 따라 격퇴할 수도 있사옵니다",
    "7:1093:0": "의 침공인가……\n다른 가문에 원군을 요청해\n필승을 기하는 것도 한 방법이오",
    "7:1094:0": "이(가) 쳐들어왔는가\n다른 가문의 원군을 맞서게 하라\n우호를 맺은 것이 무엇을 위해서더냐",
    "7:1095:0": "이(가) 쳐들어왔습니다\n지금이야말로 주군의 인연과 인맥을 활용해\n다른 가문의 원군에 의지할 때인 듯하옵니다",
    "7:1096:0": "의 습격이옵니다\n주군께 만에 하나라도 위험이 닥쳐서는……\n여기서는 원군을 청하옵시다",
    "7:1097:0": "의 침공이오\n다른 가문에 원군을 청한다면\n승기를 확실히 잡을 수 있을 것이오",
    "7:1098:0": "이(가) 난입했습니다!\n이 싸움은…… 한 치 앞을 알 수 없사옵니다\n신중을 기해 원군을 청해야 할 듯하옵니다",
    "7:1099:0": "이(가) 내습했사옵니다\n싸움은 필승의 계책을 세워 임하는 법\n얕보지 말고 원군을 청하는 것이 긴요하옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S374", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
