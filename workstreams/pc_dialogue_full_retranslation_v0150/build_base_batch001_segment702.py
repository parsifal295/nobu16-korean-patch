#!/usr/bin/env python3
"""Build Base authoring segment 702 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S702.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s702", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3175:0": "퇴로가 끊기다니…\n하지만 포기하기에는 이르다",
    "9:3176:0": "퇴각로를 잃다니…\n",
    "9:3176:1": "도 이제 끝인가…",
    "9:3177:0": "퇴로가 끊기다니!\n힘겨운 싸움이 되겠군요…",
    "9:3178:0": "퇴로가…!?\n이제 쓰러지는 순간까지 싸울 뿐…!",
    "9:3179:0": "설마 퇴로를 잃다니…\n각오를 굳힐 때가 왔군요",
    "9:3180:0": "퇴로가 끊겼다고!?\n힘겨운 싸움이 되겠군…",
    "9:3181:0": "퇴각로가 파괴됐다고!?\n큭, 제때 도착하지 못하다니!",
    "9:3182:0": "이(가) 늦게 출발한 탓에\n퇴각로를 잃었나…",
    "9:3183:0": "퇴각로가 무너졌나…\n지키지 못하다니 면목없군…",
    "9:3184:0": "제때 도착하지 못했습니까…\n이제 퇴로는 끊겼습니다…",
    "9:3185:0": "퇴각로가 파괴됐나…\n조금만 더 빨랐더라면…",
    "9:3186:0": "퇴각로가!?\u3000늦었나…\n방어조차 못 하다니…",
    "9:3187:0": "퇴로가 끊겼다…\n제때 도착하지 못한 건 실책이군…",
    "9:3188:0": "퇴각로가 파괴되고 말았구먼…\n제때 도착하지 못하다니 면목없구먼…",
    "9:3189:0": "퇴각로가 파괴됐다고!?\n도착하기도 전에… 벌써!?",
    "9:3190:0": "퇴각로가 파괴됐다…\n발이 느렸던 걸 원망할 뿐이다…",
    "9:3191:0": "퇴각로가 파괴됐습니다…\n더 일찍 움직였더라면 이런 일은…",
    "9:3192:0": "퇴각로가 파괴됐나…\n방어에 제때 도착하지 못하다니 불찰이군",
    "9:3193:0": "이만큼 빼앗기고는 이길 수 없다…\n철수하라!",
    "9:3194:0": "적이 너무 깊숙이 들어왔다…\n전군, 철수하라!",
    "9:3195:0": "이제 전세를 뒤집을 수 없다…\n각자 철수하라!\u3000붙잡히지 마라",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:3176:0",
    "9:3176:1",
    "9:3182:0",
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
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
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
                "segment": "base_msggame_B001_S702",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
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
