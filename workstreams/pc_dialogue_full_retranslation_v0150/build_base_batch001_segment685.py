#!/usr/bin/env python3
"""Build Base authoring segment 685 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S685.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s685", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:2799:0": "퇴각로로 향하라\n적의 퇴로를 차단한다!",
    "9:2800:0": "퇴각로를 장악하겠습니다\n적의 동요를 유도하는 겁니다",
    "9:2801:0": "퇴각로를 장악하라!\n절대로 적을 놓치지 마라!",
    "9:2802:0": "퇴각로로 진격하라!\n한 방 먹여 주자",
    "9:2803:0": "퇴각로로 진군하라!\n적의 퇴로를 차단한다",
    "9:2804:0": "퇴각로로 급히 향하라!\n퇴로는 끊어 놓는 게 상책이지",
    "9:2805:0": "퇴각로를 장악하겠습니다!\n적도 동요하겠지요",
    "9:2806:0": "퇴각로를 봉쇄하라!\n적에게 평온 따위 허락하지 않겠다!",
    "9:2807:0": "퇴각로로 향하십시오\n퇴로를 차단하는 겁니다",
    "9:2808:0": "퇴각로를 장악한다!\n적을 독 안에 든 쥐로 만들어 버리자",
    "9:2809:0": "나아가라!\n아무것도 두려워하지 마라!",
    "9:2810:0": "진군하라!\n경계를 게을리하지 마라",
    "9:2811:0": "적과 마주칠 때에 대비해\n신중히 나아가야 한다",
    "9:2812:0": "자만하지 말고 신중히\n나아가도록 하지요",
    "9:2813:0": "언제든 덤벼라\n우리가 상대해 주마!",
    "9:2814:0": "긴장을 풀 수 있는 것도\n지금뿐이겠지",
    "9:2815:0": "경계하라\n곧 전투가 벌어질 것이다",
    "9:2816:0": "적은 어디에 있으려나\n신중히 나아가 볼까",
    "9:2817:0": "방심하지 말고\n나아갑시다",
    "9:2818:0": "덤벼라!\n내 칼의 녹이 되어라",
    "9:2819:0": "경계를 늦추지 말고\n나아가 주십시오",
    "9:2820:0": "신중히 나아가자\n경계를 게을리하지 마라",
    "9:2821:0": "퇴각로를 완전히 끊어 버려라!",
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
                "segment": "base_msggame_B001_S685",
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
