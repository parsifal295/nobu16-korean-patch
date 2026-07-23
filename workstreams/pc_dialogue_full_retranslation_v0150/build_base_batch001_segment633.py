#!/usr/bin/env python3
"""Build Base authoring segment 633 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S633.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s633", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1780:0": "……지금은 울 수 없다\n병사들을 이끌 책임이 있다",
    "9:1781:0": "을(를) 감히……\n절대로 용서하지 않겠다!",
    "9:1782:0": "장렬한 최후로다!\n원수를 갚은 뒤 나도 뒤따라 죽으리!",
    "9:1783:0": "의 한은……\n",
    "9:1783:1": "이(가) 풀겠다",
    "9:1784:0": "을(를) 피의 제물로\n삼아 주마!",
    "9:1785:0": "용서하지 않으리……\n결코 용서하지 않으리!",
    "9:1786:0": "의 아픔을……\n백 배로 갚아 주마……!",
    "9:1787:0": "의 원수는……\n바로―",
    "9:1787:1": "이(가) 반드시 갚으리라",
    "9:1788:0": "우오오오!\n복수전이다아!",
    "9:1789:0": "용서하지 않겠습니다!\n",
    "9:1789:1": "의 원수를 갚겠습니다!",
    "9:1790:0": "을(를) 감히……!\n비싼 대가를 치르게 해 주마!",
    "9:1791:0": "있어서는 안 될 일……\n이 원한은 반드시……",
    "9:1792:0": "의 원수는\n반드시 갚으리라……!",
    "9:1793:0": "동료가 당했는데\n가만있을 수 있겠냐!",
    "9:1794:0": "…… 다음은\n네놈이 죽을 차례다!",
    "9:1795:0": "이 몸―",
    "9:1795:1": "\n결코 용서하지 않겠다",
    "9:1796:0": "의 원한은\n반드시 풀어 드리겠습니다……",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1781:0",
    "9:1783:0",
    "9:1783:1",
    "9:1784:0",
    "9:1786:0",
    "9:1787:0",
    "9:1787:1",
    "9:1789:0",
    "9:1789:1",
    "9:1790:0",
    "9:1792:0",
    "9:1794:0",
    "9:1795:0",
    "9:1795:1",
    "9:1796:0",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
                "segment": "base_msggame_B001_S633",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
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
