#!/usr/bin/env python3
"""Build Base authoring segment 621 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S621.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s621", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1528:0": "괜찮나!? 지원하러 왔다!",
    "9:1529:0": "지원하겠습니다! 버텨 주십시오!",
    "9:1530:0": "지원하러 가겠다. 버틸 수 있겠나?",
    "9:1531:0": "지원하겠습니다. 부디 지금은 버텨 주십시오!",
    "9:1532:0": "원호하리라…… 버텨 다오―",
    "9:1533:0": ", 지원하겠다",
    "9:1534:0": "지원하겠소! 부디 버티시오",
    "9:1535:0": "도와주겠노라…… 버텨라!",
    "9:1536:0": "괜찮으십니까!? 지원하겠습니다!",
    "9:1537:0": "지원하겠다! 버텨라!",
    "9:1538:0": "지원하겠습니다. 굳세게 버텨 주십시오",
    "9:1539:0": "지원하겠소! 버텨 주시오!",
    "9:1540:0": "버티는 수밖에 없어……!",
    "9:1541:0": "큭……\n버티는 수밖에 없나……!",
    "9:1542:0": "바위처럼 굳건히\n견뎌 내라……!",
    "9:1543:0": "버티며 반격할 때를\n기다리는 겁니다!",
    "9:1544:0": "큭…… 두고 보아라……!",
    "9:1545:0": "버텨라…… 원거리 공격은\n전투의 기본이다",
    "9:1546:0": "크윽…… 지금이 버틸 때다……",
    "9:1547:0": "으음…… 버티는 게다!",
    "9:1548:0": "지금은 버텨야 한다……",
    "9:1549:0": "주춤하지 마라!\n끝까지 버텨 내라!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1532:0",
    "9:1533:0",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S621", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
