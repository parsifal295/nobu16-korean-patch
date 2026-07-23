#!/usr/bin/env python3
"""Build Base authoring segment 680 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S680.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s680", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:2689:0": "원호가 필요하겠군?\n고지를 차지하러 간다!",
    "9:2690:0": "아군을 원호해야겠군\n먼저 고지를 장악한다",
    "9:2691:0": "고지를 확보하리라\n원호가 우리의 소임이다",
    "9:2692:0": "활의 원호가 필요하겠군요…\n고지를 차지하러 가겠습니다",
    "9:2693:0": "고지를 차지한다!\n활로 원호해 주마",
    "9:2694:0": "활 사격 지원이 필요하겠군\n고지를 확보해 주마",
    "9:2695:0": "고지가 필요하다\n활로 원호해야겠지",
    "9:2696:0": "고지로 향한다!\n활로 원호하겠다",
    "9:2697:0": "고지를 차지하겠습니다!\n아군을 원호해야 합니다!",
    "9:2698:0": "활로 원호해야겠지\n우리는 고지를 차지한다!",
    "9:2699:0": "활로 원호할 수 있도록\n고지를 확보하러 가겠습니다",
    "9:2700:0": "고지를 차지한다\n활로 원호하겠노라",
    "9:2701:0": "결정타가 부족하군\n요충지를 빼앗으러 간다",
    "9:2702:0": "요충지를 공략하라!\n형세를 뒤바꾸는 거다!",
    "9:2703:0": "우리는 요충지를 노린다\n교착을 끝내리라!",
    "9:2704:0": "요충지를 장악합시다\n형세를 바꾸는 겁니다",
    "9:2705:0": "요충지를 무너뜨린다!\n전황을 뒤바꾸는 거다!",
    "9:2706:0": "전황이 교착됐군… 그렇다면\n요충지를 무너뜨릴 때는 지금이다!",
    "9:2707:0": "요충지를 차지하고 싶군…\n그러면 형세를 바꿀 수 있다",
    "9:2708:0": "전황은 호각이다\n요충지를 함락해 기세를 올릴까",
    "9:2709:0": "저 요충지를 노리겠습니다\n형세를 바꾸는 겁니다!",
    "9:2710:0": "저 요충지를 함락한다\n우위를 점하는 거다!",
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
                "segment": "base_msggame_B001_S680",
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
