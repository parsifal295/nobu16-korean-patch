#!/usr/bin/env python3
"""Build Base authoring segment 602 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S602.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s602", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1118:0": "당했습니다…… 아니!\n싸움은 이제부터입니다!",
    "9:1119:0": "큰일이군……\n퇴로를 잃다니……",
    "9:1120:0": "이건 쉽지 않겠군……",
    "9:1121:0": "목숨과 맞바꿔서라도\n승리를 내줄 수는 없다!",
    "9:1122:0": "이 지경까지\n몰리다니……",
    "9:1123:0": "끝까지 포기하고 싶지는\n않습니다만……",
    "9:1124:0": "이건…… 어떻게든\n전세를 뒤집어야……",
    "9:1125:0": "아주 제대로\n농락당했구나……",
    "9:1126:0": "이 지경까지\n몰리게 될 줄이야",
    "9:1127:0": "뭐라!\n이제 끝인가……!",
    "9:1128:0": "이래서는 병사들의 사기가……",
    "9:1129:0": "으음, 퇴로가……\n여의치 않군……",
    "9:1130:0": "각오를 굳혀야\n하겠군요……",
    "9:1131:0": "으으…… 이미 패배가\n결정된 것이나 다름없구나……",
    "9:1132:0": "네놈들,\n벌써 지쳐 쓰러지지 마라!",
    "9:1133:0": "기세에 눌리지 마라!\n끝까지 싸워라!",
    "9:1134:0": "여기서 꺾여서는\n무사의 이름에 먹칠이니라!",
    "9:1135:0": "온갖 수단을\n다 써야 합니다……!",
    "9:1136:0": "어림없다!\n아직 끝나지 않았다!",
    "9:1137:0": "사기가 걱정되는구나……",
    "9:1138:0": "아군의 분위기가……\n가라앉았군……",
    "9:1139:0": "이까짓 일에 주춤해서야\n세상의 웃음거리가 되리라",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S602", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
