#!/usr/bin/env python3
"""Build Base authoring segment 655 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S655.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s655", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2221:0": "으윽……",
    "9:2221:1": "……\n경계했는데도 이 꼴인가……",
    "9:2222:0": "……",
    "9:2222:1": "\n듣던 것보다 더한 위력이로다",
    "9:2223:0": "으음……",
    "9:2223:1": "……\n참으로 무지막지하구나……",
    "9:2224:0": "크윽……",
    "9:2224:1": "에\n속수무책으로 당하다니……",
    "9:2225:0": "의 오의……\n단단히 당했구나……",
    "9:2226:0": "크윽……",
    "9:2226:1": "의\n",
    "9:2226:2": "이지요……",
    "9:2227:0": "(이)라고?\n이렇게까지 당하는 건가?",
    "9:2228:0": "잘도 해 주는구나―\n",
    "9:2228:1": "!",
    "9:2229:0": "이 정도일 줄이야……\n이놈!",
    "9:2230:0": "제법 하는구나……",
    "9:2231:0": "만만치 않군요……",
    "9:2232:0": "……우리 병사를 이토록\n많이 해치웠구나!",
    "9:2233:0": "무시무시한 위력……\n……어서 대책을 세워야 한다",
    "9:2234:0": "전해 들은 것보다 강력하다……\n실로 압도적이군……!",
    "9:2235:0": "……주, 죽는 줄\n알았느니라",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2221:0",
    "9:2221:1",
    "9:2222:0",
    "9:2222:1",
    "9:2223:0",
    "9:2223:1",
    "9:2224:0",
    "9:2224:1",
    "9:2225:0",
    "9:2226:0",
    "9:2226:1",
    "9:2226:2",
    "9:2227:0",
    "9:2228:0",
    "9:2228:1",
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
                "segment": "base_msggame_B001_S655",
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
