#!/usr/bin/env python3
"""Build Base authoring segment 665 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S665.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s665", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2397:0": "구원이라니 살았구나!\n모두, 도착할 때까지 버텨라!",
    "9:2398:0": "곧 도우러 올 것이다!\n그때까지만 버티면 된다",
    "9:2399:0": "조금만 더 견디십시오\n우군을 기다립시다",
    "9:2400:0": "좋아, 원군이 온다!\n지금이 버텨 낼 고비다!",
    "9:2401:0": "계획대로 원군이 오는구나\n지금은 버텨 내도록 하자",
    "9:2402:0": "구원 소식이다!\n모두, 도착할 때까지 버텨라!",
    "9:2403:0": "도우러 온다고!\n이제 한숨 돌릴 수 있겠구나",
    "9:2404:0": "곧 구원대가 옵니다\n지금이 버텨 낼 고비입니다",
    "9:2405:0": "원군인가!\n이제 버티기만 하면 된다!",
    "9:2406:0": "도우러 오고 있습니다\n조금만 더 견디십시오",
    "9:2407:0": "도우러 올 것이다!\n그때까지만 버티면 된다",
    "9:2408:0": "잘 버텼구나!\n이제부터는 내게 맡겨라!",
    "9:2409:0": "가세하러 왔다!\n저 적군은 내게 맡겨라!",
    "9:2410:0": "이곳은 내가 맡겠다\n어서 철수하라",
    "9:2411:0": "오래 기다리게 했습니다\n이곳은 제가 이어받겠습니다",
    "9:2412:0": "이제 물러나시오\n나머지는 내게 맡기시오",
    "9:2413:0": "이제 교대할 때입니다\n뒷일은 염려 마십시오",
    "9:2414:0": "이제 물러나시는 게 좋겠습니다\n뒷일은 맡겨 주십시오",
    "9:2415:0": "제때 도착했군!\n어서 철수하시오",
    "9:2416:0": "이(가) 이어받겠습니다!\n안심하고 철수하십시오",
    "9:2417:0": "기다리게 했군\n이곳은 내가 이어받겠다",
    "9:2418:0": "무사하셔서 참으로 다행입니다\n뒷일은 걱정하지 마십시오",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2416:0",
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
                "segment": "base_msggame_B001_S665",
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
