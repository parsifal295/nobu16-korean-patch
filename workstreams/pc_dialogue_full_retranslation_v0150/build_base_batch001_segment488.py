#!/usr/bin/env python3
"""Build Base authoring segment 488 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S488.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s488", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:189:0": "제게 영지를 맡겨 주시다니……\n열심히 해야겠어요!",
    "8:190:0": "확실히 맡았다!\n후회하게 만들지는 않겠다!",
    "8:191:0": "주군께서 나를\n마음 써 주시는구나……",
    "8:192:0": "인심을 사로잡지 못하면\n다스릴 수 없지요",
    "8:193:0": "황송하옵니다\n반드시 기대에 부응하겠사옵니다",
    "8:194:0": "옛, 맡겨 주시옵소서!\n훌륭한 땅으로 일구어 보이겠사옵니다!",
    "8:195:0": "받을 수 있는 것만으로도 기쁜 일이로군……",
    "8:196:0": "이곳이 전장입니다!\n진을 치겠습니다!",
    "8:197:0": "여기가 「",
    "8:197:1": "」……\n모두, 전투 준비를 하십시오!",
    "8:198:0": "싸움을 시작하겠습니다\n모두, 각오를 굳히십시오",
    "8:199:0": "자, 싸움이다!\n진을 쳐라!",
    "8:200:0": "인가\n제법 좋은 전장이로군",
    "8:201:0": "한바탕 붙어 보자!\n창을 나란히 세우고 활시위를 당겨라!",
    "8:202:0": "우리의 깃발을 내걸어라!\n놈들에게 똑똑히 보여 줘라",
    "8:203:0": "병사들이여, 기세를 드높여라!\n이 싸움은 우리가 이긴다!",
    "8:204:0": "싸움을 시작한다!\n모두, 준비하라!",
    "8:205:0": "모두, 공성전입니다!\n",
    "8:205:1": "을(를) 우리 손에 넣읍시다!",
    "8:206:0": "을(를) 공격합니다!\n모두, 따라오십시오!",
}

STATIC_COORDINATES: set[str] = {
    *(f"8:{record_id}:0" for record_id in range(189, 197)),
    "8:198:0", "8:199:0",
    *(f"8:{record_id}:0" for record_id in range(201, 205)),
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S488", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
