#!/usr/bin/env python3
"""Build Base authoring segment 128 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S128.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s128", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2380:0": "어렵군요…\n다른 부탁이라면 들어주지 못할 것도 없습니다만",
    "6:2381:0": "그쪽도 주머니 사정이 어려운 모양이군요…\n우리도 타협할 수는 없습니다만",
    "6:2382:0": "안 돼, 안 돼! 이번이 마지막이야!\n하지만 내놓을 조건이 이래서야…",
    "6:2383:0": "이것이 마지막이오\n그 부탁, 들어주지 않겠다는 것은 아니지만…",
    "6:2384:0": "이 이상은 소모적이니 마지막 교섭으로 하지\n하지만 내놓을 수 있는 조건이 이것뿐이라면…",
    "6:2385:0": "…이걸 마지막으로 하지 않겠소?\n우리 가문도 이 교섭에 흥미는 있소만…",
    "6:2386:0": "…이제 마지막으로 하지\n그렇다 해도,",
    "6:2386:1": "도 타협할 수는 없다",
    "6:2387:0": "이걸로 성사되지 않으면 교섭을 깨겠다\n조건을 양보할 생각은 없지만",
    "6:2388:0": "마지막만큼은 좋은 모습을 보여 주길 바랐건만…\n그렇다고 만족할 조건을 내놓지도 못하는군",
    "6:2389:0": "성과 없는 이야기는 지치기만 하는군\n하지만 이보다 나은 조건도 바라기 어렵겠어…",
    "6:2390:0": "그쪽 주머니 사정은 이해합니다\n하지만 이걸 마지막으로 하겠습니다",
    "6:2391:0": "이걸 마지막으로 하지 않겠나?\n그쪽 사정을 모르는 바는 아니지만…",
    "6:2392:0": "후… 좋은 조건은 기대하기 어려운 듯하군요\n이 이상은 상대해 드릴 수 없습니다",
    "6:2393:0": "도 바쁜 몸이니 이것이 마지막입니다\n그쪽 사정도 짐작은 합니다만…",
    "6:2394:0": "하아… 이제 그만 좀 하지…\n다른 건 뭐 없어?",
    "6:2395:0": "이제 됐다… 이 이야기는 여기까지다\n다른 일이라면 교섭에 응하지",
    "6:2396:0": "미안하지만 이 요구에는 응할 수 없군\n다른 이야기를 들어 보지",
    "6:2397:0": "이 요구는 받아들일 수 없군요\n하지만 다른 화제라면 들어 보지요",
    "6:2398:0": "언제까지 끝없는 이야기를 할 셈이냐!?\n다른 이야기를 하든 돌아가든 마음대로 해라",
    "6:2399:0": "…시간 낭비였던 모양이군\n이 이야기는 끝까지 평행선이겠지",
}

DYNAMIC_COORDINATES = {"6:2386:0", "6:2386:1", "6:2393:0"}


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
        dynamic = coordinate in DYNAMIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
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
                "segment": "base_msggame_B001_S128",
                "decision_count": len(rows),
                "retranslated": len(rows) - len(DYNAMIC_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_COORDINATES),
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
