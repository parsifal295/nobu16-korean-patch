#!/usr/bin/env python3
"""Build Base authoring segment 393 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S393.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s393", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1436:0": "을(를) 지금 공격한다면\n함락할 가능성이 큽니다\n전력을 다해 공략합시다",
    "7:1437:0": "은(는) 공략할 수 있사옵니다\n지금은 팽팽히 맞서는 적의 전력도\n총력을 결집하면 무너뜨릴 수 있사옵니다",
    "7:1438:0": "전력이 팽팽한 곳—",
    "7:1438:1": "\n주군의 허락만 있다면\n아군을 결집해 함락할 수 있사옵니다",
    "7:1439:0": "전력이 팽팽한 상대—",
    "7:1439:1": "을(를) 공략하는 일입니다\n주군께서도 아시겠지만\n총력을 기울이면 수월할 듯합니다",
    "7:1440:0": "은(는) 함락할 수 있사옵니다\n평범하게 공격해도 승산은 반반\n……그렇다면 총공격을 한다면?",
    "7:1441:0": "은(는) 함락할 수 있사옵니다\n주변 전력을 모아 수로 밀어붙이면 그만\n……다소 흥이 떨어지긴 하옵니다만",
    "7:1442:0": "을(를) 지키는 우리와 대등한 적에게\n총력을 결집해 부딪쳐 보는 것도\n한바탕 즐길 거리……일지도 모르겠구먼",
    "7:1443:0": "에 관한 일이옵니다\n분명 지금은 병력이 호각이오나\n총력을 결집하면 공략할 수 있을 듯하옵니다",
    "7:1444:0": "은(는) 함락할 수 있사옵니다\n지금의 팽팽한 형세도\n전 병력을 쏟아부으면 무너질 것이옵니다",
    "7:1445:0": "와(과)는 전력이 호각이오나\n주변의 병력을 결집하면\n분명 공략할 수 있을 것입니다",
    "7:1446:0": "전력이 팽팽한 곳—",
    "7:1446:1": "……\n주변 병력을 집결시켜\n총력을 다해 공격한다면 어쩌면",
    "7:1447:0": "을(를) 공략하려면\n총력을 다해 공격해야 가능할 듯하오니\n부디 출진 명령을 내려 주시옵소서!",
    "7:1448:0": "은(는) 우리와 호각이옵니다\n전선이 교착될 우려가 있사오니\n전력을 다해 맞섭시다",
    "7:1449:0": "은(는) 함락할 수 있을지도……\n지금은 호각인 적도 부근의 병력을\n모아 총공격한다면 분명……",
    "7:1450:0": "전력이 팽팽한 곳—",
    "7:1450:1": "\n공략해 함락하지 못할 곳은 아니옵니다\n다만 총력을 기울여야 하겠사오나……",
    "7:1451:0": "와(과)는 전력이 호각\n하지만 승산은 있사옵니다\n우리의 총력으로 공격하는 것이옵니다",
    "7:1452:0": "을(를) 탈취할 계책이 있사옵니다\n지금은 전력이 팽팽하오나\n전력을 다해 맞서면 이길 수 있을 것이옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S393", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
