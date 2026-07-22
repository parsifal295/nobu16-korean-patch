#!/usr/bin/env python3
"""Build Base authoring segment 34 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S34.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s34", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:387:0": "거래가 성사되었으니\n우선 다행…이군요",
    "6:388:0": "우리도 상인도\n이익을 보면 되는 겁니다",
    "6:389:0": "거래가 무사히 끝나\n다행이구려",
    "6:390:0": "그 상인은 고약하구먼\n정말이지 번번이…",
    "6:391:0": "좋은 거래를\n하신 듯합니다",
    "6:392:0": "나도…\n뭔가 사고 싶었는데…",
    "6:393:0": "이 거래도 전쟁 준비겠지\n분명 그럴 것이다",
    "6:394:0": "씀씀이가 거칠다고… 아니!\n호방해야 우리 주군답지",
    "6:395:0": "훌륭한 거래를\n성사시키셨사옵니다",
    "6:396:0": "거래를 마친\n상인의 미소가 눈부시군",
    "6:397:0": "좋은 거래가\n되었기를 바라오만",
    "6:398:0": "그 상인의 웃는 얼굴…\n과연 진심인가 거짓인가",
    "6:399:0": "이제 빈 성 따윈\n없겠…지?",
    "6:400:0": "괜찮은 배치\n아니야?",
    "6:401:0": "성에 누구를 배치하느냐가\n공격과 수비 모두에 중요하다",
    "6:402:0": "이 배치면 괜찮지\n않을까 합니다",
    "6:403:0": "흠… 전쟁에 대비하셨나",
    "6:404:0": "깊이 생각하고\n계시는군요",
    "6:405:0": "과연\n이런 전술입니까",
    "6:406:0": "역시 이런 식으로\n사람을 배치하셨군요",
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
                "segment": "base_msggame_B001_S34",
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
