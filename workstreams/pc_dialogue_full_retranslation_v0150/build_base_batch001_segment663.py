#!/usr/bin/env python3
"""Build Base authoring segment 663 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S663.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s663", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2363:0": "칭찬을 받으니\n영광입니다",
    "9:2364:0": "이것이야말로\n내 무예로 이룬 업적이로다!",
    "9:2365:0": "급소를 찌르는 것은\n병법의 기본이기에……",
    "9:2366:0": "칭찬을 받자오니\n더없이 기쁘고 황송하옵니다",
    "9:2367:0": "후후, 으뜸가는 전공을\n세워 보겠다",
    "9:2368:0": "이 정도는 당연합니다!",
    "9:2369:0": "여기서는 자랑 좀\n하도록 하겠소",
    "9:2370:0": "모두의 지원이\n있었기에 가능한 일입니다",
    "9:2371:0": "아군에게 도움이\n된 모양이구려",
    "9:2372:0": "도 물러나겠다!",
    "9:2373:0": "뭐라고!\n후퇴한다!",
    "9:2374:0": "음\n물러나는 것이 상책이로다",
    "9:2375:0": "여기서는 후퇴하는 것이\n현명하겠군요",
    "9:2376:0": "방향을 돌려라!　전군 물러나라!",
    "9:2377:0": "계략인 듯하지만…… 홀로\n앞서 나가 봐야 득이 없다",
    "9:2378:0": "적군이라고!?\n우리도 물러난다!",
    "9:2379:0": "우리도 물러나자",
    "9:2380:0": "어쩔 수 없군요…",
    "9:2381:0": "그리할 수밖에 없는가……",
    "9:2382:0": "도\n물러나겠습니다",
    "9:2383:0": "우리도 물러나자!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2372:0",
    "9:2382:0",
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
                "segment": "base_msggame_B001_S663",
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
