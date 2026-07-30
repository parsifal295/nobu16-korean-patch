#!/usr/bin/env python3
"""Build Base authoring segment 698 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S698.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s698", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:3088:0": "더는 버틸 수 없소…\n우리는 철수하겠소, 미안하오",
    "9:3089:0": "이래서는 버티지 못한다…\n철수할 수밖에 없겠군",
    "9:3090:0": "병력 소모가 심하다…\n이제 물러날 수밖에 없다",
    "9:3091:0": "병력을 이렇게 잃어서야…\n어쩔 수 없다, 철수하겠소",
    "9:3092:0": "이래서는 버티지 못한다…\n어쩔 수 없구나, 철수한다",
    "9:3093:0": "더는 싸울 수 없겠군요…\n이만 물러나겠습니다",
    "9:3094:0": "이래서는 버티지 못한다…\n철수할 수밖에 없겠군",
    "9:3095:0": "병력 소모가 심합니다…\n물러날 수밖에 없겠군요",
    "9:3096:0": "병력을 너무 많이 잃었나…\n이만 철수하겠소",
    "9:3097:0": "이제 충분히 싸웠군\n철수한다!",
    "9:3098:0": "의리는 다했다\n이제 철수한다!",
    "9:3099:0": "이대로면 전사하고 만다\n우리는 철수한다!",
    "9:3100:0": "의리는 다했을 터\n먼저 철수하겠소",
    "9:3101:0": "이제 충분히 싸웠을 터\n철수한다!",
    "9:3102:0": "전사만은 사양하겠소\n이만 물러나도록 하지",
    "9:3103:0": "병사들을 헛되이 잃을 수는 없다\n신속히 철수하라!",
    "9:3104:0": "철수할 때다!\n목숨까지 걸 의리는 없겠지",
    "9:3105:0": "의리는 다했겠지요\n이제 철수하겠습니다!",
    "9:3106:0": "아직 죽을 수 없다…\n우리는 철수한다!",
    "9:3107:0": "목숨을 헛되이 버릴 수는 없습니다\n이만 물러나겠습니다!",
    "9:3108:0": "병사들을 헛되이 잃을 수는 없다…\n먼저 철수하겠소",
    "9:3109:0": "싸우는 시늉 정도는 했으니\n얼른 내빼자!",
}

DYNAMIC_RUNTIME_COORDINATES: set[str] = set()
STATIC_COORDINATES = set(TRANSLATIONS)


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
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_"
                    "context_where_available"
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
                "segment": "base_msggame_B001_S698",
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
