#!/usr/bin/env python3
"""Build Base authoring segment 692 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S692.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s692", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:2954:0": "사기가 낮군…\n수비하며 버텨 낸다",
    "9:2955:0": "전황의 흐름을 잡지 못했나…\n지금은 버틸 때다",
    "9:2956:0": "형세가 좋지 않습니다…\n지금은 버텨 봅시다",
    "9:2957:0": "사기가 떨어지고 있다…\n수비에 집중해야겠군",
    "9:2958:0": "전황이 좋지 않다…\n지금은 지킬 뿐이다!",
    "9:2959:0": "형세가 불리하다…\n지금은 참고 견딜 때다!",
    "9:2960:0": "사기가 떨어졌군\n지금이 버텨야 할 고비다!",
    "9:2961:0": "전황이 좋지 않습니다…\n지금은 버틸 때입니다!",
    "9:2962:0": "사기가 영 오르지 않는군…\n수세로 전환하자",
    "9:2963:0": "사기가 낮습니다…\n지금은 수비에 전념합시다",
    "9:2964:0": "지금이 버틸 때다!\n물러서지 말고 싸워라!",
    "9:2965:0": "비라고!?\n이래서는 철포를 쓸 수 없다",
    "9:2966:0": "비라니…\n철포는 포기할 수밖에 없나",
    "9:2967:0": "비가 내릴 줄이야…\n철포 사용은 포기하라",
    "9:2968:0": "눈이라니 운도 없군\n철포 없이 싸워야겠어…",
    "9:2969:0": "비가 온다는 말은 못 들었는데…\n철포에는 기대할 수 없겠군",
    "9:2970:0": "비라면 어쩔 수 없지\n철포 없이 싸우자",
    "9:2971:0": "비인가…\n철포를 쓸 수 없겠군",
    "9:2972:0": "비가 오면 못 쓰는가\n철포란 참 쓸모없구나",
    "9:2973:0": "비가 내리다니…\n철포를 쓸 수 없습니다…",
    "9:2974:0": "비인가…\n철포는 쓸 수 없겠군",
    "9:2975:0": "비라면 어쩔 수 없군요\n철포는 포기합시다",
    "9:2976:0": "이런, 비인가…\n이래서는 철포를 쓸 수 없다",
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
                "segment": "base_msggame_B001_S692",
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
