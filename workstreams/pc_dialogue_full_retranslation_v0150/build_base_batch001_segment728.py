#!/usr/bin/env python3
"""Build Base authoring segment 728 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S728.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s728", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3673:0": "양군의 전력은 팽팽히 맞서",
    "9:3673:1": ", 하지만\n적진에는 지장·",
    "9:3673:2": "의 모습이 보이는군\n전장에서도 무언가 수를 써 올지 모르네",
    "9:3674:0": "양군의 전력은 팽팽히 맞서",
    "9:3674:1": ", 하지만\n적진에 이름난 장수는",
    "9:3674:2": "\n정면으로 싸우면 이길 수 있",
    "9:3675:0": "아군의 우세는 흔들림이 없다\n단숨에 몰아쳐\n반격할 틈을 주지 않는 것이 긴요",
    "9:3676:0": "아군의 우세는 분명",
    "9:3676:1": ", 하지만\n적진에는 맹장·",
    "9:3676:2": "도 참전한 모양입니다\n부디",
    "9:3676:3": "방심하지 않",
    "9:3676:4": "도록 하십시오",
    "9:3677:0": "아군의 우세는 확고합니다\n",
    "9:3677:1": ", 지장·",
    "9:3677:2": "의 지략은 널리 알려졌으니\n전장을 휘저으면 성가실 것입니다",
    "9:3678:0": "아군은 상당히 열세",
    "9:3678:1": "\n적 부대를 하나씩 격파하",
    "9:3678:2": "\n협격과 사격도 활용하",
    "9:3678:3": "…",
    "9:3679:0": "아군은 상당히 열세",
    "9:3679:1": "\n게다가 맹장·",
    "9:3679:2": "까지 출진하다니…\n",
    "9:3679:3": "의 기세를 막아야 활로가 열리",
}

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
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
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
                "segment": "base_msggame_B001_S728",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "confirmed_non_display": 0,
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
