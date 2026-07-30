#!/usr/bin/env python3
"""Build Base authoring segment 693 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S693.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s693", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:2977:0": "눈이라고!?\n이래서는 철포를 쓸 수 없다",
    "9:2978:0": "눈이라니…\n철포는 포기할 수밖에 없나",
    "9:2979:0": "눈이 내릴 줄이야…\n철포 사용은 포기하라",
    "9:2980:0": "눈이라니 운도 없군\n철포 없이 싸워야겠어…",
    "9:2981:0": "눈이 온다는 말은 못 들었는데…\n철포에는 기대할 수 없겠군",
    "9:2982:0": "눈이라면 어쩔 수 없지\n철포 없이 싸우자",
    "9:2983:0": "눈인가…\n철포를 쓸 수 없겠군",
    "9:2984:0": "눈이 오면 못 쓰는가\n철포란 참 쓸모없구나",
    "9:2985:0": "눈이 내리다니…\n철포를 쓸 수 없습니다…",
    "9:2986:0": "눈인가…\n철포는 쓸 수 없는가",
    "9:2987:0": "눈이라면 어쩔 수 없군요\n철포는 포기합시다",
    "9:2988:0": "이런, 눈인가…\n이래서는 철포를 쓸 수 없다",
    "9:2989:0": "좋아, 비가 그쳤다!\n철포를 쓸 수 있다!",
    "9:2990:0": "드디어 비가 그쳤다\n화승에 불을 붙여라!",
    "9:2991:0": "비가 그쳤는가\n철포를 들어라!",
    "9:2992:0": "비가 그쳤군요\n이제 철포를 쓸 수 있습니다",
    "9:2993:0": "비가 그쳤다!\n철포를 준비시켜라!",
    "9:2994:0": "비가 그쳤구나\n드디어 철포가 나설 차례다",
    "9:2995:0": "비가 그치면\n철포의 독무대다!",
    "9:2996:0": "비가 그쳤구나\n철포의 활약을 기대해 보자!",
    "9:2997:0": "비가 그쳤습니다\n철포를 준비시키겠습니다!",
    "9:2998:0": "비가 그쳤다!\n철포는 언제든 쏠 수 있다",
    "9:2999:0": "비가 그쳤습니다\n철포가 나설 차례군요",
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
                "segment": "base_msggame_B001_S693",
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
