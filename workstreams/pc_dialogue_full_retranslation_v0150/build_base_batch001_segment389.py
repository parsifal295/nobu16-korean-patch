#!/usr/bin/env python3
"""Build Base authoring segment 389 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S389.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s389", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1360:0": ", 무른 요새로다\n형체도 남지 않게 산산이 부수어\n여러 다이묘에게 힘을 보이는 것도 상책이로다",
    "7:1361:0": "은(는) 함락하기 쉬운 성이나\n흥을 깨는 것은 멋없는 짓의 극치\n우리 군의 총력으로 맞서자꾸나",
    "7:1362:0": "은(는) 손쉬운 표적\n그러니 전군을 이끌고 공격하지 않으면\n너무 재미가 없지 않겠소",
    "7:1363:0": "은(는) 노릴 만한 곳\n노파심에서 말씀드리자면\n전군을 동원해 필승을 기해야 합니다",
    "7:1364:0": "은(는) 손쉬운 표적이지만\n전군으로 몰아쳐 함락한다면\n아군과 나누는 술맛도 달아지겠구먼",
    "7:1365:0": "은(는) 손쉬운 표적입니다\n모든 것은 주군의 지휘에 달렸사오나\n전군으로 확실히 함락해야 할 듯하옵니다",
    "7:1366:0": "은(는) 노려볼 만한 성입니다\n무슨 일이 있어도 함락해야 하니\n전군을 결집하는 것이 확실합니다",
    "7:1367:0": "은(는) 손쉬운 표적\n전군으로 밀어붙인다면\n곧 항복의 신호를 보낼 것이옵니다",
    "7:1368:0": "을(를) 공격하자꾸나\n아무리 약한 적이라도 전력으로 맞선다\n이것이 늘 이기는 길이니라",
    "7:1369:0": "의 점령은 어렵지 않습니다만\n전군으로 반격할 틈조차 주지 않고 함락하면\n백성도 다치지 않을 것입니다",
    "7:1370:0": "에\n우리 전군이 몰려간다면\n적도 피를 흘리기 전에 항복하겠지요",
    "7:1371:0": "은(는) 손쉬운 표적\n전력을 다한다면 아군의 승리는\n흔들리지 않을 것이옵니다",
    "7:1372:0": "을(를) 상대하더라도\n이 몸은 힘을 아끼지 않으리라\n전군으로 쳐들어가자꾸나",
    "7:1373:0": "을(를) 함락할 승산은 반반\n선수를 치면 우위에 설 수 있으리라",
    "7:1374:0": "의 수비는 견고하니\n샛길을 타고 기습을 가하자꾸나",
    "7:1375:0": "이라면 승산은 반반\n한발 앞서 손을 쓰시옵소서",
    "7:1376:0": "Cs1.CsName와(과)의 싸움은 선수필승\n위태천처럼 쏜살같이 몰아쳐 내려가자!",
    "7:1377:0": "와(과)의 싸움이 불안하다면\n적이 기세를 타기 전에 서둘러 공격하시오",
    "7:1378:0": "은(는) 제법 견고한 성\n여기서는 선수를 쳐 우위에 서야겠군",
    "7:1379:0": "을(를) 노린다면 선수필승\n더디게 잘하기보다 서툴러도 빠른 편이 낫다 하옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S389", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
