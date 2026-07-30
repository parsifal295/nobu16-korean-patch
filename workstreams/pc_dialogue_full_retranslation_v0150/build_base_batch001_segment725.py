#!/usr/bin/env python3
"""Build Base authoring segment 725 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S725.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s725", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3618:0": "다음에는 어떤 방법으로\n적을 현혹해 볼까요",
    "9:3619:0": "자, 다음 계책은\n어찌할꼬",
    "9:3620:0": "다음에는 어떤 방법으로\n적을 현혹해 볼까요",
    "9:3621:0": "자, 다음 계책은\n어찌할꼬",
    "9:3622:0": "그 요충지는 그저 미끼일 뿐\n",
    "9:3622:1": "의 계략에 빠져 보아라!",
    "9:3623:0": "약해, 너무 약해!　누구든 좋다, 이 「",
    "9:3623:1": "」에게\n생채기라도 내 보아라!",
    "9:3624:0": "비사문천의 가호가 함께한다!\n쳐라!　나를 따르라!",
    "9:3625:0": "비사문천의 가호가 함께한다!",
    "9:3626:0": "!\n자, 자웅을 겨루자!",
    "9:3627:0": "적군을 격파했다!\n「가메와리」라 불리는 「",
    "9:3627:1": "」에게 맞설 자는 없다!",
    "9:3628:0": "노릴 것은 적장 「",
    "9:3628:1": "」!\n나도 죽는 한이 있어도 그 목을 베리라!",
    "9:3629:0": "의 강함은 병력의 수에 있지 않다.\n자, 적진을 꿰뚫어 주마!",
    "9:3630:0": "다들, 진정하라!\n이 몸 「",
    "9:3630:1": "」, 여기 있노라!",
    "9:3631:0": "다들, 진정하라!\n이 몸 「",
    "9:3631:1": "」, 여기 있노라!",
    "9:3632:0": "님, 진정하십시오!\n대장이라면 태연히 임하셔야 합니다!",
    "9:3633:0": "진정하라!",
}

STATIC_COORDINATES = {
    "9:3618:0",
    "9:3619:0",
    "9:3620:0",
    "9:3621:0",
    "9:3624:0",
    "9:3625:0",
    "9:3633:0",
}
DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS) - STATIC_COORDINATES


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
                "segment": "base_msggame_B001_S725",
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
