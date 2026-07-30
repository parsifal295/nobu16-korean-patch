#!/usr/bin/env python3
"""Build Base authoring segment 694 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S694.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s694", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:3000:0": "비가 그쳤는가\n화승을 준비하라!",
    "9:3001:0": "좋아, 눈이 그쳤다!\n철포를 쓸 수 있다!",
    "9:3002:0": "드디어 눈이 그쳤다\n화승에 불을 붙여라!",
    "9:3003:0": "눈이 그쳤는가\n철포를 들어라!",
    "9:3004:0": "눈이 그쳤군요\n이제 철포를 쓸 수 있습니다",
    "9:3005:0": "눈이 그쳤다!\n철포를 준비시켜라!",
    "9:3006:0": "눈이 그쳤구나\n드디어 철포가 나설 차례다",
    "9:3007:0": "눈이 그치면\n철포의 독무대다!",
    "9:3008:0": "눈이 그쳤구나\n철포의 활약을 기대해 보자!",
    "9:3009:0": "눈이 그쳤습니다\n철포를 준비시키겠습니다!",
    "9:3010:0": "눈이 그쳤다!\n철포는 언제든 쏠 수 있다",
    "9:3011:0": "눈이 그쳤습니다\n철포가 나설 차례군요",
    "9:3012:0": "눈이 그쳤는가\n화승을 준비하라!",
    "9:3013:0": "퇴각로에 적군이라고!?\n돌아가서 박살 낸다!",
    "9:3014:0": "퇴각로를 지켜라!\n전속력으로 달려라!",
    "9:3015:0": "퇴각로를 내줄 수는 없다!\n서둘러 후퇴하라!",
    "9:3016:0": "퇴각로에 적이…\n되돌아갑시다",
    "9:3017:0": "퇴각로의 적을 격파한다!\n전속력으로 되돌아가라!",
    "9:3018:0": "퇴각로에 적이라니…\n당장 돌아가야 한다!",
    "9:3019:0": "퇴각로의 적을 쓸어 버린다\n나를 따르라!",
    "9:3020:0": "퇴각로가 공격받고 있다\n어서 되돌아가라!",
    "9:3021:0": "퇴각로에 적군이!?\n당장 돌아가야 해!",
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
                "segment": "base_msggame_B001_S694",
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
