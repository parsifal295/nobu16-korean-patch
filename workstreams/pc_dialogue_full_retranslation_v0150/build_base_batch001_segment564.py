#!/usr/bin/env python3
"""Build Base authoring segment 564 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S564.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s564", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:351:0": "자, 개전이다\n적군에 대비하라!",
    "9:352:0": "이 싸움, 무슨 수를 써서라도\n헤쳐 나가자!",
    "9:353:0": "더는 물러설 수 없다…\n모두, 힘을 빌려 다오",
    "9:354:0": "모두, 준비는 되었느냐\n미하타와 다테나시도 굽어살피소서!",
    "9:355:0": "모두, 대비하라\n비사문천의 가호가 함께하리라",
    "9:356:0": "삼도천을 건널 노잣돈은 있다\n모두, 두려워 말고 나아가라",
    "9:357:0": "이(가)",
    "9:357:1": "을(를) 발견",
    "9:358:0": "이(가) 전투를 시작",
    "9:359:0": "이(가)",
    "9:359:1": "을(를) 사격",
    "9:360:0": "이(가)",
    "9:360:1": "에게 사격당함",
    "9:361:0": ", 우세",
    "9:362:0": "을(를) 비롯한 총",
    "9:362:1": "개 부대가 우세",
    "9:363:0": "이(가) 밀려날 듯합니다",
    "9:364:0": "을(를) 비롯한 총",
    "9:364:1": "개 부대가 밀려날 듯합니다",
    "9:365:0": "의 활약으로 적군이 후퇴",
    "9:366:0": "을(를) 비롯한 총",
    "9:366:1": "개 부대의 활약으로 적군이 후퇴",
    "9:367:0": "이(가) 밀려 후퇴",
    "9:368:0": "을(를) 비롯한 총",
    "9:368:1": "개 부대가 밀려 후퇴",
}

STATIC_COORDINATES: set[str] = {
    "9:351:0",
    "9:352:0",
    "9:353:0",
    "9:354:0",
    "9:355:0",
    "9:356:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S564", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
