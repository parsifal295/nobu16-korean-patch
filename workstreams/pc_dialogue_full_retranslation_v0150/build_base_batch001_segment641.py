#!/usr/bin/env python3
"""Build Base authoring segment 641 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S641.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s641", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1944:0": "고위 무장의 수급을 취했는가!\n장하도다, 장하도다!",
    "9:1945:0": "참으로 훌륭한\n싸움이었습니다!",
    "9:1946:0": "훌륭한 무공이로다!",
    "9:1947:0": "의 공적은\n길이 회자되리라",
    "9:1948:0": "대단하군……",
    "9:1949:0": "질 수는 없다!\n",
    "9:1949:1": "도 누군가를 사로잡겠다!",
    "9:1950:0": "자존심을 걸고서라도\n질 수는 없다!",
    "9:1951:0": "훌륭하군……!\n우리도 뒤를 잇자",
    "9:1952:0": "제법 대단한 무운이군요\n그럼 우리도!",
    "9:1953:0": "뒤처질 수는 없다!",
    "9:1954:0": "저 전공의 뒤를 이어야겠군",
    "9:1955:0": "다음은―",
    "9:1955:1": "이(가)\n공을 세울 차례입니다",
    "9:1956:0": "이건 질 수 없구나!",
    "9:1957:0": "도\n질 수는 없겠군요!",
    "9:1958:0": "이러고 있을 때가 아니군!",
    "9:1959:0": "우리도 뒤를\n따르도록 합시다……!",
    "9:1960:0": "그 전공……\n부러울 따름이로다",
    "9:1961:0": "생포하다니\n제법이잖아!",
    "9:1962:0": "과연 대단한 수완이로다!",
    "9:1963:0": "좀처럼 해낼 수 있는 일이\n아니다, 훌륭하도다!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1947:0",
    "9:1949:0",
    "9:1949:1",
    "9:1955:0",
    "9:1955:1",
    "9:1957:0",
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
                "segment": "base_msggame_B001_S641",
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
