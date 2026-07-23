#!/usr/bin/env python3
"""Build Base authoring segment 721 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S721.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s721", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3528:0": "방어는 우리의 소임\n빼앗길 수는 없다!",
    "9:3529:0": "지키러 가겠습니다!\n쉽사리 내주지는 않겠습니다",
    "9:3530:0": "우리는 요격에 나선다!\n반드시 지켜 내리라!",
    "9:3531:0": "요지 방어에 나선다\n놈들에게 내줄 수는 없으니 말이다",
    "9:3532:0": "우리는 수비에 나선다\n그곳을 쉽사리 내줄 수는 없다",
    "9:3533:0": ", 요격하겠다!\n끝까지 지켜 보이리라",
    "9:3534:0": "방어하러 가겠습니다!\n요지는 끝까지 지켜 내겠습니다!",
    "9:3535:0": "수비는 내게 맡겨라!\n적을 몰아내 보이겠다!",
    "9:3536:0": "적을 요격하겠습니다\n요지에는 접근조차 못 하게 하겠습니다",
    "9:3537:0": "지키러 가겠다!\n그곳은 결코 뚫리게 두지 않겠다",
    "9:3538:0": "여기서는 지킬 수 없다\n자리를 옮긴다",
    "9:3539:0": "이곳은 방어에 알맞지 않다\n더 좋은 위치로 옮기자",
    "9:3540:0": "여기서는 대응하기 어렵다\n방어하기 좋은 위치로 가자",
    "9:3541:0": "유연하게 대응할 수 있는 위치로\n이동하도록 하지요",
    "9:3542:0": "이런 곳에서는 대응할 수 없다\n지키기 쉬운 곳으로 나아간다",
    "9:3543:0": "수비하기에는 좋지 않은 위치군\n포진을 다시 짜도록 하지",
    "9:3544:0": "여기서는 방어할 수 없다\n다른 곳으로 옮기도록 하지",
    "9:3545:0": "여기는 좋지 않구나\n지키기 쉬운 위치로 가자",
    "9:3546:0": "이곳은 방어에 알맞지 않군요\n더 좋은 위치로 이동하겠습니다!",
    "9:3547:0": "이곳은 방어에 부적합하다\n포진을 바꾼다",
    "9:3548:0": "지키기에는 불편하군요\n더 좋은 곳으로 가도록 하지요",
    "9:3549:0": "여기서는 방어하기 어렵다\n포진 위치를 바꾼다",
    "9:3550:0": "고지를 차지하러 간다!\n사격은 내게 맡겨라!",
}

DYNAMIC_RUNTIME_COORDINATES = {"9:3533:0"}


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
                "segment": "base_msggame_B001_S721",
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
