#!/usr/bin/env python3
"""Build Base authoring segment 699 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S699.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s699", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:3110:0": "슬슬 철수한다!\n더 싸워 줄 의리도 없다",
    "9:3111:0": "물러난다\n더 싸워야 할 이유도 없다",
    "9:3112:0": "제대로 싸워 줄 의리도 없습니다\n이만 물러나겠습니다",
    "9:3113:0": "제대로 싸워 줄 의리도 없다\n우리는 물러나겠소!",
    "9:3114:0": "싸우는 시늉 정도는 했을 터\n그럼, 이만 물러나도록 하지",
    "9:3115:0": "철수할 때로군\n필사적으로 싸워 줄 의리도 없다",
    "9:3116:0": "슬슬 철수할 때다!\n목숨까지 걸 의리는 없겠지",
    "9:3117:0": "철수할 때인 듯합니다\n필사적으로 싸워 줄 의리도 없습니다",
    "9:3118:0": "물러난다\n더 싸워야 할 이유도 없다",
    "9:3119:0": "철수할 때인 듯합니다\n필사적으로 싸워 줄 의리도 없습니다",
    "9:3120:0": "슬슬 철수한다!\n더 싸워 줄 의리도 없다",
    "9:3121:0": "이곳은 전장에서 너무 멀군\n좀 더 앞에서 대기한다!",
    "9:3122:0": "전선은 더 앞인가\n원호하기 좋은 위치에 자리 잡자",
    "9:3123:0": "전장까지 멀군\n원호할 수 있는 위치로 이동하자",
    "9:3124:0": "여기서는 원호할 수 없습니다\n좀 더 앞으로 나가도록 하지요",
    "9:3125:0": "여기서는 전투에 참가할 수 없다\n원호할 수 있는 곳으로 나간다!",
    "9:3126:0": "후방에서는 아무것도 할 수 없다\n바로 참전할 수 있는 곳으로 가자",
    "9:3127:0": "여기서는 지원할 수 없다\n우리도 앞으로 나간다",
    "9:3128:0": "후방에 있으면 비웃음을 산다\n전선 가까이까지 이동하도록 하지",
    "9:3129:0": "여기서는 원호할 수 없습니다\n더 앞으로 나갑시다!",
    "9:3130:0": "전선에서 너무 멀어졌다\n원호할 수 있는 곳으로 나가야 한다!",
    "9:3131:0": "적과 너무 멀어졌습니다\n좀 더 앞에서 대기합시다",
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
                "segment": "base_msggame_B001_S699",
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
