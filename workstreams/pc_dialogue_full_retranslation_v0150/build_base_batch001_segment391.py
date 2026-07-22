#!/usr/bin/env python3
"""Build Base authoring segment 391 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S391.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s391", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1400:0": "을(를) 함락할 수 있을지는 계책에 달렸소\n앞서 움직이면 계책을 짤 여유도 있으리다",
    "7:1401:0": "을(를) 함락할 수 있을지는 운에 달렸소\n먼저 움직여 운을 우리 편으로 만드시오",
    "7:1402:0": "을(를) 함락할 승산은 반반\n격식에는 어긋나오나 서둘러 나아가겠소",
    "7:1403:0": "은(는) 견고하오나\n선수를 치면 길도 열릴 것이옵니다",
    "7:1404:0": "을(를) 함락하시려면\n앞서 움직여 적의 허를 찌르시오",
    "7:1405:0": "은(는) 만만치 않습니다\n최단 경로로 재빨리 공격하소서",
    "7:1406:0": "을(를) 함락할 승산은 반반\n주군, 서둘러 출진하시옵소서",
    "7:1407:0": "을(를) 노린다면\n당장 행동에 나서야 하옵니다",
    "7:1408:0": "을(를) 공격하신다면\n선수를 치는 것이 상책이옵니다",
    "7:1409:0": "이라면\n선수를 치지 않으면 고전을 피하기 어려울 것입니다",
    "7:1410:0": "을(를) 공격하시는군요\n선수를 치면 병사의 부담도 줄어들 것이옵니다",
    "7:1411:0": "을(를) 함락할 승산은 반반\n뒤늦게 움직이면 불리해질 것이옵니다",
    "7:1412:0": "의 수비는 뛰어납니다\n샛길로 내달려 적의 의표를 찌르시오",
    "7:1413:0": "을(를) 공략한다\n피아의 전력은 호각…… 허나\n병력을 아끼지 않으면 이길 수 있으리라",
    "7:1414:0": "지금이 「",
    "7:1414:1": "」을(를) 빼앗을 기회로다\n호각이니 우리가 공격하리라 생각지 못할 터\n병력을 집결해 쳐들어가자꾸나",
    "7:1415:0": "의 공략입니다만\n병력을 긁어모아 공격하면 가능할 듯하오\n뭐, 대등한 상대에게 무리수를 두는 셈입니다만",
    "7:1416:0": "은(는)…… 빼앗을 수 있을 듯하오\n현재 병력이 호각이니\n병력을 집중해 공격한다면……",
    "7:1417:0": "을(를) 빼앗을 기회는 지금인 듯하오\n병력을 모아 일제히 공격하는 것이오\n신중한 계책만으로는 살아남을 수 없소이다",
    "7:1418:0": "은(는) 함락할 수 있사옵니다\n지금 피아의 병력이 팽팽하니\n병력을 결집하면 승기가 있을 듯하옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S391", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
