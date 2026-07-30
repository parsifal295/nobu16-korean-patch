#!/usr/bin/env python3
"""Build Base authoring segment 562 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S562.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s562", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:1200:0": "알겠",
    "8:1200:1": "\n또한",
    "8:1200:2": "에게 다시 맡기실 때에는\n성하 방침에서 명령해 주",
    "8:1201:0": "알겠",
    "8:1202:0": "의 성하 방침 달성",
    "8:1203:0": "의 성하 방침 해제",
    "8:1204:0": "성 능력이 저하되어―",
    "8:1204:1": "의 성하 방침이",
    "8:1204:2": "(으)로",
    "8:1205:0": "성주 해임으로―",
    "8:1205:1": "의 성하 방침을 해제",
    "9:318:0": "봐줄 것 없다!\n마음껏 날뛰어라!",
    "9:319:0": "똑똑히 보여 주자고\n우리의 힘을 말이야!",
    "9:320:0": "녀석들아!\n",
    "9:320:1": "을(를) 믿고 돌진하라!",
    "9:321:0": "우리의 각오를\n천하에 보이리라!",
    "9:322:0": "적을 쳐라!\n무공을 널리 떨쳐라!",
    "9:323:0": "떨쳐 일어나라!\n승리를 대의에 바치리라!",
    "9:324:0": "이 싸움을 지배할 이는\n",
    "9:324:1": "이다!",
    "9:325:0": "진중의 북을 울려라!\n전투의 시작이다!",
    "9:326:0": "앞길을 막는 자는\n모두 베어 버려라!",
    "9:327:0": "우리와 싸우는 어리석음을\n똑똑히 깨닫게 해 드리지요",
}

STATIC_COORDINATES: set[str] = {
    "9:318:0",
    "9:319:0",
    "9:321:0",
    "9:322:0",
    "9:323:0",
    "9:325:0",
    "9:326:0",
    "9:327:0",
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
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S562", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
