#!/usr/bin/env python3
"""Build Base authoring segment 696 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S696.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s696", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3044:0": "물러나라, 물러나라!\n이대로는 좋은 표적일 뿐이다!",
    "9:3045:0": "계속 사격당해서는…\n지금은 물러납시다",
    "9:3046:0": "이대로는 좋은 표적일 뿐이오…\n일단 물러나라!",
    "9:3047:0": "사격이 격렬합니다…\n여기서는 후퇴합시다",
    "9:3048:0": "사격에 눌려 나아갈 수 없다\n일단 후퇴한다",
    "9:3049:0": "협격할 셈이냐!\n그렇게는 못 한다!",
    "9:3050:0": "협격을 저지하라!\n적을 접근시키지 마라",
    "9:3051:0": "협격을 노리다니 어리석구나\n먼저 쳐부숴 주마",
    "9:3052:0": "측면은 내주지 않겠습니다\n적군을 저지하겠습니다",
    "9:3053:0": "에워싸이면 끝장이다\n그 전에 적을 치리라",
    "9:3054:0": "협격을 노리다니\n자, 요격하라!",
    "9:3055:0": "그렇게는 못 한다!\n측면을 내주지 마라",
    "9:3056:0": "적을 통과시키지 마라!\n협격을 저지하라",
    "9:3057:0": "협격은 허용하지 않겠습니다!\n저 적군을 저지하겠습니다!",
    "9:3058:0": "저 적을 친다!\n측면은 내주지 않는다!",
    "9:3059:0": "협격을 노린다고?\n그렇게는 두지 않겠습니다!",
    "9:3060:0": "저 적군을 막는다\n측면을 찌르게 두지 마라",
    "9:3061:0": "협격에는 당해낼 수 없다\n물러날 수밖에 없어!",
    "9:3062:0": "협격은 버티기 어렵군…\n일단 후퇴하라!",
    "9:3063:0": "협격당해서는 힘을 못 쓴다…\n물러나 재정비하라",
    "9:3064:0": "에워싸이면 불리합니다\n후방에서 재정비하겠습니다",
    "9:3065:0": "협격당해서는 이길 수 없다…\n일단 후퇴다!",
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
                "segment": "base_msggame_B001_S696",
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
