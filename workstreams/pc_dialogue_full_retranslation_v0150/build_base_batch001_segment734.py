#!/usr/bin/env python3
"""Build Base authoring segment 734 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S734.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s734", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3778:0": "다다무네",
    "9:3778:1": "!　",
    "9:3778:2": "도시히사",
    "9:3778:3": "!\n너희는 샛길에 병력을 매복시켜라!",
    "9:3779:0": "분부대로 하겠사옵니다……",
    "9:3780:0": "맡겨 주시오!\n그런데, 정작 유인 역할은 누가 맡소?",
    "9:3781:0": "혼고",
    "9:3781:1": "공, 위험한 역할이지만 맡아 주겠는가\n아군 진영 깊숙이 적을 유인해야 하네",
    "9:3782:0": "알겠소!　이 몸도",
    "9:3782:1": "시마즈",
    "9:3782:2": "일문의 말석\n이 중책을 훌륭히 완수해 보이겠소이다",
    "9:3783:0": "요시히로",
    "9:3783:1": "는 강가에 진을 치고\n복병을 들키지 않도록 하라",
    "9:3784:0": "계책이 무사히 성공하면\n",
    "9:3784:1": "이에히사",
    "9:3784:2": "에게도 출격해 달라고 하겠다",
    "9:3785:0": "이런 소수 병력이 선봉이라니 가소롭구나!\n당장 쓸어버려 주마!!",
    "9:3786:0": "놈들, 미끼를 물었군……\n더 깊이 끌어들인다!　퇴각을 시작하라!",
    "9:3787:0": "놓치지 마라! 추격하라!",
    "9:3788:0": "혼고",
    "9:3788:1": "공은 잘하고 있군……\n전 부대, 반전 준비!",
}

STATIC_COORDINATES = set(TRANSLATIONS)
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
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
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
                "segment": "base_msggame_B001_S734",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
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
