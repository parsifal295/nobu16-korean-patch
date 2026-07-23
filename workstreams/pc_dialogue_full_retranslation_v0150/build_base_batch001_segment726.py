#!/usr/bin/env python3
"""Build Base authoring segment 726 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S726.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s726", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3634:0": "진정하십시오!",
    "9:3635:0": "나를 얕봤구나!\n이 「오니미노」에게 잔꾀 따위는 통하지 않는다!",
    "9:3636:0": "이 「오니미노」에게\n잔꾀 따위는 통하지 않는다!",
    "9:3637:0": "내가 바로 「서국무쌍」이다!",
    "9:3638:0": "협격 따위 얄팍한 수작은 내게 통하지 않는다!",
    "9:3639:0": "내게 칠난팔고를 내려 주소서!",
    "9:3640:0": "이제 당분간 싸우지는 못하겠지…",
    "9:3641:0": "대장을 보좌하는 것이 부장의 본분이다!",
    "9:3642:0": "내 무용을 실컷 맛보아라!",
    "9:3643:0": "일번창이야말로 무사의 명예! 피가 끓는구나!",
    "9:3644:0": "계책으로 승리를 거머쥐겠습니다\n이 싸움은 이미 제 손바닥 안에 있습니다",
    "9:3645:0": "대, 한 발짝도 물러서지 마라!\n스테가마리로 활로를 연다!",
    "9:3646:0": "그런 공격은\n이 「야샤미노」에게 통하지 않는다!",
    "9:3647:0": "물러날 때를 헤아릴 줄 알아야\n난세에서 살아남을 수 있는 법이다",
    "9:3648:0": "상처 따위 소금이나 발라 두면 낫는다",
    "9:3649:0": "내가 그리 쉽게 목을 내줄 성싶으냐!",
    "9:3650:0": "적이다! 돌격하라!",
    "9:3651:0": "수많은 전장으로 단련된 「",
    "9:3651:1": "」에게\n도전하려거든 앞으로 나서라!",
    "9:3652:0": "무엇에도 얽매이지 않는다, 그것이 내 삶이다!",
    "9:3653:0": "쉴 틈 따위 내게는 필요 없다!",
    "9:3654:0": "아군이 위기에 처했군, 내가 시간을 벌겠다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:3645:0",
    "9:3651:0",
    "9:3651:1",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
                "segment": "base_msggame_B001_S726",
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
