#!/usr/bin/env python3
"""Build Base authoring segment 127 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S127.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s127", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2360:0": "이 이상은 소모적이니 마지막 교섭으로 하지\n이 조건은 어떠한가?",
    "6:2361:0": "…이걸 마지막으로 하지 않겠소?\n우리 가문으로서는 이만큼은 내놓으셔야 하오",
    "6:2362:0": "…이제 마지막으로 하지\n이건 어떤가?",
    "6:2363:0": "성과 없는 이야기를 계속해도 끝이 없지\n이걸로 성사되지 않으면 교섭을 깨겠다",
    "6:2364:0": "마지막만큼은 좋은 모습을 보여 주었으면 하네…\n이 조건은 어떠한가?",
    "6:2365:0": "성과 없는 이야기는 지치기만 하는군…\n이것이 마지막이다. 이 조건이라면 받아들이마",
    "6:2366:0": "다음 일정이 있으니\n이것을 마지막으로 해 주시겠습니까?",
    "6:2367:0": "이걸 마지막으로 하지 않겠나?\n우리에게도 사정이란 것이 있다",
    "6:2368:0": "후… 이 조건이라면 받아들이겠습니다만\n이 이상은 상대해 드릴 수 없습니다",
    "6:2369:0": "도 한가한 것은 아니오\n마지막 교섭이니 이 조건은 어떻소?",
    "6:2370:0": "그 부탁을 들어주려면\n이것도 모자랄 지경이야",
    "6:2371:0": "부탁을 들어주고 싶어도…\n그쪽 주머니 사정도 어려운 모양이군요",
    "6:2372:0": "그쪽 주머니 사정이 어려운 것은 알지만\n우리에게는 우리 사정이 있다",
    "6:2373:0": "적어도 이 정도는…\n아니, 좀 더 좋은 조건을 원합니다",
    "6:2374:0": "가소롭군… 겨우 그 정도라니\n하지만 그쪽 사정도 궁한 모양이군…",
    "6:2375:0": "우리 가문을 너무 얕보는군\n좀 더 좋은 조건을 갖추어 오면 좋겠소",
    "6:2376:0": "그쪽 주머니 사정은 헤아립니다만\n우리도 거저 부탁을 들어줄 수는 없소",
    "6:2377:0": "재미없는 농담이군. 웃을 수도 없어\n…그쪽 주머니도 웃지 못할 만큼 텅 빈 모양이군",
    "6:2378:0": "어렵군요…\n그쪽에 큰 기대를 하기도 어려운 듯하고",
    "6:2379:0": "좋은 조건을 내놓지 못하는 건 알지만\n우리도 여유가 있다고는 할 수 없소",
}

DYNAMIC_COORDINATES = {"6:2369:0"}


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
                "segment": "base_msggame_B001_S127",
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
