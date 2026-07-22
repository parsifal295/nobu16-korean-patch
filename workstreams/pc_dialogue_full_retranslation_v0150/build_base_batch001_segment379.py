#!/usr/bin/env python3
"""Build Base authoring segment 379 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S379.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s379", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1174:0": "의 대군이 들이닥쳤다\n망설여도 승산은 없다\n정전을 청해 다음 기회를 노려라",
    "7:1175:0": "의 침공\n적의 기세가 거세옵니다…… 황공하오나\n정전을 청해 훗날 재전을 기약하심이……",
    "7:1176:0": "이(가) 대군을 이끌고 다가옵니다……\n싸워 봐야 손해만 볼 뿐이외다\n정전으로 위기를 넘기는 것이 상책이오",
    "7:1177:0": "이(가) 다가오고 있사옵니다\n중과부적이니 지금은 견뎌야 할 때\n정전을 청하심이 어떠하올지",
    "7:1178:0": "의 대군이 침공해 옵니다……\n정전 외에는 길이 없을 듯하오……\n와신상담…… 지금은 견디시지요",
    "7:1179:0": "이(가) 대군을 이끌고 쳐들어왔소\n압도적인 적에게 맞서는 것은 어리석은 일\n정전을 청하는 것 또한 병법이외다",
    "7:1180:0": "의 대군이 다가옵니다……\n훗날 권토중래를 기약하려면\n지금은 정전이 상책일 듯하옵니다",
    "7:1181:0": "이(가) 다가오고 있사옵니다\n아군의 열세는 부정할 수 없으니\n정전을 청하심이 어떠하올지",
    "7:1182:0": "의 대군이 침공해 왔습니다\n사지에서 활로를 찾을 계책은\n정전 외에는 없을 듯하옵니다……",
    "7:1183:0": "이(가) 대군을 이끌고 다가옵니다……\n싸워 봐야 병력만 잃을 뿐\n정전하고 때를 기다리시오",
    "7:1184:0": "의 대군이 쳐들어왔다 하오\n정전을 청하시오\n한때의 명예보다 실리를 취해야 하오",
    "7:1185:0": "이(가) 침공해 옵니다\n지금 우리에게 승산은 희박하니……\n정전을 청해…… 때를 기다립시다",
    "7:1186:0": "이(가) 대군을 이끌고 쳐들어옵니다\n……부디 정전하시옵소서\n하늘 높이 나는 용도 깊은 못에 몸을 숨기는 법……",
    "7:1187:0": "이(가) 대군을 이끌고 침공합니다\n정전합시다…… 그리하면\n뒷일은 어떻게든 할 수 있습니다",
    "7:1188:0": "의 대군이 곳곳을 휩쓸고 있습니다……\n서둘러 정전을 청해야 합니다\n영내 백성이 고통받기 전에",
    "7:1189:0": "이(가) 대군을 이끌고 왔다고?\n정전이다, 정전!\n질 게 뻔한 싸움을 어떻게 하겠나",
    "7:1190:0": "이(가) 대군으로 침공해 왔나……\n지금은…… 정전할 수밖에\n언젠가 이 빚은 갚아 주마",
    "7:1191:0": "이(가) 다가오고 있사옵니다\n유감이오나 아군이 불리하니\n정전을 청해야…… 할 듯하옵니다",
    "7:1192:0": "이(가) 대군으로 침공해 왔사옵니다\n각오를 다해 일전을 벌이고 싶사오나\n허나…… 정전도 부득이할 듯하옵니다……",
    "7:1193:0": "의 대군이 쳐들어왔습니다\n적은 병력으로 볼썽사납게 맞서느니\n정전을 청해야 할 줄로 아뢰옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S379", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
