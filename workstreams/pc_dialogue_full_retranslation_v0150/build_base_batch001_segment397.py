#!/usr/bin/env python3
"""Build Base authoring segment 397 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S397.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s397", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1513:0": "은(는) 탈취할 수 있을 듯하옵니다\n상당한 병력이 지키는 성이오나\n원군이 있다면 함락할 수 있을 것이옵니다",
    "7:1514:0": "은(는) 탈취할 수 있을 듯하옵니다\n다만 우리 힘만으로 공격하기는 다소 어려우니\n원군을 청하시옵소서",
    "7:1515:0": "을(를) 함락합시다\n우리 힘만으로는 고전할 적이오나\n원군이 있다면 우세하게 싸울 수 있습니다",
    "7:1516:0": "이라면 우리 힘만으로 공격하기보다\n다른 가문의 원군과 함께 공격하는 편이\n무난하겠지요",
    "7:1517:0": "은(는) 함락할 수 있을 듯하옵니다\n다만 우리만으로는 어려우니\n다른 가문의 원군이 필요할 것이옵니다",
    "7:1518:0": "은(는) 공략할 수 있사옵니다\n수비 병력이 우리와 대등하므로\n원군이 전제가 되겠사오나",
    "7:1519:0": "은(는) 공략할 수 있사옵니다\n다만 상당한 피해도 따를 싸움이니\n다른 가문의 원군이 필요하겠사옵니다",
    "7:1520:0": "을(를) 함락하시려면\n다른 가문의 원군과 함께 공격하는 편이\n주군의 병력 소모를 줄일 수 있을 듯하옵니다",
    "7:1521:0": "은(는) 수비를 얕볼 수 없사오나\n다른 가문의 원군이 있다면\n성은 주군의 손안에 들어올 것이옵니다",
    "7:1522:0": "의 공략은 가능합니다\n다만 아군과 대등한 병력이 지키는 성이니\n원군을 얻는 편이 좋겠습니다",
    "7:1523:0": "을(를) 손에 넣으시옵소서\n다른 가문의 원군과 함께 공격하면\n우세하게 싸움을 이끌 수 있을 것이옵니다",
    "7:1524:0": "은(는) 수비가 제법 견고하오나\n원군을 부르신다면\n성은 주군의 것이 될 것이옵니다",
    "7:1525:0": "을(를) 공략합시다\n적의 수비 병력은 우리와 대등하오나\n원군이 있다면 함락할 수 있을 듯하옵니다",
    "7:1526:0": "은(는) 점령할 수 있사옵니다\n우리 힘만으로는 고전을 면치 못하겠으나\n다른 가문의 원군이 있다면 이길 수 있을 것이옵니다",
    "7:1527:0": "을(를) 빼앗읍시다!\n다른 가문의 원군과 함께 공격하시옵소서\n우세하게 싸움을 이끌 수 있사옵니다",
    "7:1528:0": "을(를) 함락합시다\n우리 힘만으로는 고전할 적이오나\n원군이 있다면 반드시 이길 수 있을 것으로 아옵니다",
    "7:1529:0": "을(를) 공략합시다\n다만…… 공격은 수비보다 어렵다 하니\n다른 가문의 원군과 함께 공격하시옵소서",
    "7:1530:0": "을(를) 공격하는 것은 좋사오나\n적은 아군 못지않게 강하다 하니\n다른 가문에 원군을 청하시옵소서",
    "7:1531:0": "을(를) 공격합시다\n다른 가문에서 원군을 얻는다면\n우리와 호각인 적도 무찌를 수 있을 것입니다",
    "7:1532:0": "은(는) 공략할 수 있사옵니다\n다만 성의 수비는 얕볼 수 없으니\n다른 가문의 원군이 필요하옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S397", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
