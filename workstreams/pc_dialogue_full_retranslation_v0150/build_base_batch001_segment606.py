#!/usr/bin/env python3
"""Build Base authoring segment 606 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S606.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s606", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1205:0": "방심하지 마라…… 적의 수는\n줄어도 투지는 꺾이지 않는다",
    "9:1206:0": "강행 돌파할 수도\n있다만……",
    "9:1207:0": "적이 무르군요……\n조심하며 나아갈까요",
    "9:1208:0": "마지막 한 병사를 벨 때까지\n긴장을 늦추지 마라!",
    "9:1209:0": "아무리 적병을 줄였다 해도\n싸움은 예측불허…… 신중하라",
    "9:1210:0": "백 리를 가는 자는 구십 리를\n절반으로 여긴다…… 방심은 금물이다",
    "9:1211:0": "적이 줄어든 지금이야말로\n방심해서는 안 된다",
    "9:1212:0": "적은 약졸입니다!\n지금이 공격할 때입니다!",
    "9:1213:0": "지금이라면 힘으로 밀어붙일 수도 있겠군",
    "9:1214:0": "궁지에 몰린 쥐도 고양이를 문다고\n하지 않습니까",
    "9:1215:0": "하하하, 낙승이군, 낙승……\n아니지, 방심은 금물이다",
    "9:1216:0": "어이, 언제까지\n기다리라는 거냐!",
    "9:1217:0": "언제든 출격할 수\n있사옵니다!",
    "9:1218:0": "이 시간을…… 다른 데\n쓰고 싶은데 말이지",
    "9:1219:0": "분부만 내리시면\n즉시 움직이겠사오나……",
    "9:1220:0": "분부를 기다릴 뿐……\n싸울 때는 올 것이다",
    "9:1221:0": "내 재주…… 아직 쓸 때가\n아니라는 것인가",
    "9:1222:0": "속절없이 시간만 흘러가는군……",
    "9:1223:0": "분부는 아직인가……",
    "9:1224:0": "언제든 움직일 수 있습니다……",
    "9:1225:0": "언제까지\n기다려야 하는가……",
    "9:1226:0": "기다리는 것도\n지루하군요……",
    "9:1227:0": "바둑이라도 둘까……",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


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
                "segment": "base_msggame_B001_S606",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
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
