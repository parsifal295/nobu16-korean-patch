#!/usr/bin/env python3
"""Build Base authoring segment 129 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S129.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s129", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2400:0": "후… 이 이야기는 결론이 나지 않겠군\n일단 여기까지 하지",
    "6:2401:0": "이런, 이런. 끝이 나지 않는 이야기로군\n이 이야기는 여기까지다. 알겠나?",
    "6:2402:0": "이 요구에는 응할 수 없습니다\n다른 이야기는 있습니까?",
    "6:2403:0": "유감이지만 응할 수 없소\n다른 이야기를 들어 보지",
    "6:2404:0": "이 요구를 받아들일 수는 없습니다\n다른 이야기를 하지요",
    "6:2405:0": "미안하지만 이 요구는 받아들일 수 없소\n다른 요구는 있소?",
    "6:2406:0": "무슨 소리야…\n딱 한 번만 더 들어 주지",
    "6:2407:0": "…긍지를 걸고 그 요구에는 응할 수 없다\n마지막으로 다른 이야기라면 들어 보지",
    "6:2408:0": "허튼소리 마라\n다른 용건이 없다면 이만 끝내자",
    "6:2409:0": "농담은 됐습니다. 다음이 마지막입니다\n다른 용건이 있다면 듣겠습니다",
    "6:2410:0": "…아니, 단연코 안 된다\n이것이 마지막이다. 다른 용건이 있다면 듣겠다만?",
    "6:2411:0": "후… 성사되지 않을 이야기를 계속해 봐야 헛일\n이것이 마지막이다… 다른 이야기는 없나?",
    "6:2412:0": "유감이지만 말도 안 되는 요구로군\n이것이 마지막이다. 다른 요구를 들어 볼까",
    "6:2413:0": "이 일은 만족스러운 답이 나오지 않겠군\n이것이 마지막이지만 다른 이야기라면 들어 보지",
    "6:2414:0": "농담도 참…\n다른 이야기가 없다면 끝내지요",
    "6:2415:0": "농담은 싫다\n다른 이야기가 없다면 이만 끝이다",
    "6:2416:0": "말도 안 되는군요\n마지막으로 다른 이야기가 하나 있다면 듣지요",
    "6:2417:0": "이야기가 성사되지 않는 듯하군요\n다른 요구가 없다면 끝내지요",
    "6:2418:0": "오늘은 돌아가 줘\n…도무지 내키지 않는군",
    "6:2419:0": "무사의 마음을 모르시는 듯하군\n돌아가 주시겠소?",
}


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
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
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
                "segment": "base_msggame_B001_S129",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
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
