#!/usr/bin/env python3
"""Build Base authoring segment 46 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S46.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s46", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:612:0": "…자\n이길 것인가… 질 것인가…?",
    "6:613:0": "라면\n이길 수 있을 겁니다",
    "6:614:0": "라면\n이길 수 있다고 믿읍시다",
    "6:615:0": "이(가)\n이기면 좋겠군",
    "6:616:0": "이(가)\n이기면 좋겠구먼…",
    "6:617:0": "…\n이겨 주세요!",
    "6:618:0": "…\n부디 이겨 주세요!",
    "6:619:0": "…\n얼빠진 적을 짓밟아라",
    "6:620:0": "…\n적을 남김없이 쳐부숴라",
    "6:621:0": "…\n무사히 개선하시기를…",
    "6:622:0": "…\n아무쪼록 무사하시기를…",
    "6:623:0": "의 전투\n그저 무운을 빌 뿐",
    "6:624:0": "이(가)\n이기리라 믿어 보자",
    "6:625:0": "이(가) 수상하군\n우리를 노리고 있어",
    "6:626:0": "조심해\n",
    "6:626:1": "이(가) 온다",
    "6:627:0": "에서 움직임이…\n우리 가문을 노리는 건가",
    "6:628:0": "공격해 오는가",
    "6:628:1": "\n상대로 부족함이 없다",
    "6:629:0": "놈\n우리 가문을 표적으로 삼았는가",
    "6:630:0": "와의 전쟁이\n눈앞에 닥쳤구나",
    "6:631:0": "이(가) 우리 가문을\n노리고 있는 듯합니다",
}

DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS).difference({"6:612:0"})


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
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
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
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
                "segment": "base_msggame_B001_S46",
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
