#!/usr/bin/env python3
"""Build Base authoring segment 711 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S711.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s711", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3328:0": "놈들이 꾸미는 것은…",
    "9:3328:1": "인 듯하옵니다\n경계해야 하겠사옵니다",
    "9:3329:0": "적이 노리는 것은…",
    "9:3329:1": "인가요\n미리 경계해 두지요",
    "9:3330:0": "놈들의 노림수는…",
    "9:3330:1": "인 듯하군…\n아군이 걸려들지 않아야 할 텐데",
    "9:3331:0": "적이 준비하는 것은…",
    "9:3331:1": "인 모양이군요\n빼앗아 오는 것도 한 방법이겠군요",
    "9:3332:0": "적이 노리는 것은…",
    "9:3332:1": "인가요\n미리 경계해 두지요",
    "9:3333:0": "놈들이 노리는 것은…",
    "9:3333:1": "인 듯하옵니다\n군자는 위태로운 곳에 가까이하지 않는 법이지요",
    "9:3334:0": "적이 노리는 것은…",
    "9:3334:1": "인가요\n조심해야겠군요",
    "9:3335:0": "적이 준비하는 것은…",
    "9:3335:1": "인 듯하옵니다\n경계가 필요할 듯하옵니다",
    "9:3336:0": "적이 노리는 것은…",
    "9:3336:1": "인가요\n조심해야겠군요",
    "9:3337:0": "적이 쓰려는 것은…",
    "9:3337:1": "인 듯하옵니다\n경계가 필요할 듯하옵니다",
    "9:3338:0": "님께서 전사하셨다고!?\n거짓말이다…",
    "9:3338:1": "은(는) 믿지 않는다!",
}

STATIC_COORDINATES: set[str] = set()
DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS)


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
                "segment": "base_msggame_B001_S711",
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
