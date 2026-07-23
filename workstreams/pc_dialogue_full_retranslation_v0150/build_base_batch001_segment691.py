#!/usr/bin/env python3
"""Build Base authoring segment 691 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S691.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s691", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:2932:0": "적군은 소수 병력입니다\n마지막 공세에 나섭시다!",
    "9:2933:0": "병력 수에서 우위를 점했다!\n지금부터 총공격에 나선다",
    "9:2934:0": "병력 수에서 우위에 섰다\n마지막 일격을 가하라",
    "9:2935:0": "우리 병력이 우세하다\n여기서 승부를 건다!",
    "9:2936:0": "적의 병력은 새 발의 피다\n자, 돌격하라!",
    "9:2937:0": "적군은 이제 소수 병력뿐입니다\n모두, 공세에 나섭시다!",
    "9:2938:0": "병력 수로 질 리 없다\n전군, 마지막 일격을 가하라!",
    "9:2939:0": "적을 꽤 줄여 놓았군요\n승부를 결정지읍시다",
    "9:2940:0": "승부는 끝났군\n전군을 이끌고 추격하리라!",
    "9:2941:0": "투지가 충만하다!\n적을 쓸어버린다!",
    "9:2942:0": "전의가 충만하다\n적을 소탕하리라!",
    "9:2943:0": "기세가 드높다\n이대로 짓눌러라!",
    "9:2944:0": "흐름이 좋군요\n이대로 공세에 나서겠습니다",
    "9:2945:0": "전세의 흐름은 우리 편이다!\n단숨에 섬멸하리라!",
    "9:2946:0": "병사들의 사기가 높다\n공세에 나설 때는 지금이다!",
    "9:2947:0": "사기가 충천했다\n적을 칠 때는 지금이다!",
    "9:2948:0": "모두 의욕이 넘치는군!\n이 기세로 나아가자",
    "9:2949:0": "모두의 전의가 높습니다\n공세에 나서겠습니다",
    "9:2950:0": "사기가 충분하다\n여기서 격차를 벌린다!",
    "9:2951:0": "아군의 사기가 높습니다\n공세에 나섭시다!",
    "9:2952:0": "단숨에 요지를 장악해\n사기를 꺾는다!　전진!",
    "9:2953:0": "방비를 굳혀라!\n어떻게든 버텨라",
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
                "segment": "base_msggame_B001_S691",
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
