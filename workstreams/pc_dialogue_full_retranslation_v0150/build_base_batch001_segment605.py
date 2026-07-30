#!/usr/bin/env python3
"""Build Base authoring segment 605 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S605.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s605", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1184:0": "쓰러진 모두의 원수를\n갚을 자는―",
    "9:1184:1": "이다!",
    "9:1185:0": "이건……\n각오를 굳혀야 하나",
    "9:1186:0": "이제 궤멸이나 다름없다……",
    "9:1187:0": "으으음……\n아무래도 여기까지인가",
    "9:1188:0": "이 흐름을……\n막을 수 없는 겁니까",
    "9:1189:0": "손쓸 방도가 없다\n……이 말인가",
    "9:1190:0": "상당히\n어려운 상황이군요……",
    "9:1191:0": "항복도 어쩔 수 없는가……",
    "9:1192:0": "적이 겁먹었다!\n이 기세로 가자!",
    "9:1193:0": "자, 남은 무훈을\n모조리 거두리라!",
    "9:1194:0": "싸움의 대세는 정해졌다!",
    "9:1195:0": "패주시킬 것이라면\n지금이 호기입니다!",
    "9:1196:0": "이대로 적을\n모조리 섬멸하라!",
    "9:1197:0": "이 기세를 타고\n승리를 거머쥐어라!",
    "9:1198:0": "여기까지 왔으니\n이제 궤멸시킬 일만 남았다",
    "9:1199:0": "적은 마음껏 쳐도 좋다!\n사양할 것 없다!",
    "9:1200:0": "기세가 좋군요!\n이대로 갑시다",
    "9:1201:0": "좋다!\n흐름은 우리 쪽에 있다!",
    "9:1202:0": "적의 기세가 꺾였습니다\n지금이야말로 호기입니다",
    "9:1203:0": "이 기세로\n적을 끝장내자",
    "9:1204:0": "꽤나 흩어 놓았지만\n끝까지 봐주진 않겠다",
}

DYNAMIC_RUNTIME_COORDINATES = {"9:1184:0", "9:1184:1"}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required" if static else "pending",
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available"
                ),
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S605",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
