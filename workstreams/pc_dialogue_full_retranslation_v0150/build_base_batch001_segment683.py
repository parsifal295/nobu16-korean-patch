#!/usr/bin/env python3
"""Build Base authoring segment 683 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S683.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s683", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:2755:0": "요충지는 내줄 수 없다\n방어하러 간다",
    "9:2756:0": "요충지에 수비가 필요한가\n그럼, 서두르자",
    "9:2757:0": "서두르십시오\n요충지를 지키겠습니다!",
    "9:2758:0": "요충지로 진격하라!\n놈들에게 내줄 수는 없다!",
    "9:2759:0": "요충지로 향하겠습니다\n수비는 맡겨 주십시오",
    "9:2760:0": "서둘러라!\n요충지의 방비를 굳힌다",
    "9:2761:0": "명령에 따를 뿐이다!",
    "9:2762:0": "뜻하시는 대로",
    "9:2763:0": "소임을 다하겠다",
    "9:2764:0": "명령하신 대로",
    "9:2765:0": "명령을 이행한다!",
    "9:2766:0": "신뢰에 반드시 부응하겠다",
    "9:2767:0": "하명에 따라\n행동할 뿐이다",
    "9:2768:0": "소인에게 맡겨 주시오",
    "9:2769:0": "명령하신 대로\n소임을 다하겠습니다!",
    "9:2770:0": "기필코 이루어 내겠다!",
    "9:2771:0": "반드시 완수하겠습니다",
    "9:2772:0": "하명에 따르겠나이다",
    "9:2773:0": "음, 잘 생각해서\n명령을 내려야겠군",
    "9:2774:0": "전황 전체를 살펴\n병력을 움직여야겠군",
    "9:2775:0": "승리를 향한 집념이\n승패를 가르는 법이다",
    "9:2776:0": "전황의 흐름만 읽으면\n싸움은 어렵지 않습니다",
    "9:2777:0": "적을 무찌른다\n오직 그뿐이다",
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
                "segment": "base_msggame_B001_S683",
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
