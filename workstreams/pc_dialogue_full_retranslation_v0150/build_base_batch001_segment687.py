#!/usr/bin/env python3
"""Build Base authoring segment 687 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S687.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s687", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:2844:0": "요충지를 제압하는 거다!",
    "9:2845:0": "퇴각로의 적을 격파하라!\n절대로 통과시키지 마라!",
    "9:2846:0": "퇴각로를 사수하라!\n여기서 끝장내라!",
    "9:2847:0": "퇴각로를 파괴하게 둘 수는 없다!\n반드시 처치하라!",
    "9:2848:0": "퇴각로의 적은 반드시\n제거하겠습니다",
    "9:2849:0": "퇴각로는 우리가\n끝까지 지켜 내겠다!",
    "9:2850:0": "퇴각로를 노리는 불한당은\n여기서 처치해야겠군",
    "9:2851:0": "퇴각로를 사수하라!\n적을 섬멸하라!",
    "9:2852:0": "퇴각로의 적은\n이 몸이 처치해 주마",
    "9:2853:0": "퇴각로로 다가오는 적을\n제거하겠습니다!",
    "9:2854:0": "퇴각로를 사수하라!\n적을 격파하라!",
    "9:2855:0": "퇴각로를 잃을 수는\n없습니다!",
    "9:2856:0": "퇴각로를 사수한다!\n절대로 돌파를 허용하지 마라!",
    "9:2857:0": "밀어내라!\n요충지는 안 내준다!",
    "9:2858:0": "지금이 버틸 때다!\n요충지에는 접근도 못 하게 하겠다!",
    "9:2859:0": "요충지를 노리다니\n적도 제법 아는군",
    "9:2860:0": "그리 쉽게 요충지를\n내줄 수는 없습니다!",
    "9:2861:0": "여기서 막아라!\n요충지에는 접근도 못 하게 하라!",
    "9:2862:0": "적을 저지하라!\n요충지는 내줄 수 없으니",
    "9:2863:0": "적을 막아라!\n요충지에 접근시키지 마라",
    "9:2864:0": "지금이 고비다!\n요충지는 내주지 않겠다!",
    "9:2865:0": "요충지는 내주지 않겠습니다!\n끝까지 버티는 겁니다!",
}

DYNAMIC_RUNTIME_COORDINATES: set[str] = set()


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
                "segment": "base_msggame_B001_S687",
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
