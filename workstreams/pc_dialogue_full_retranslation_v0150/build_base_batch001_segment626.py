#!/usr/bin/env python3
"""Build Base authoring segment 626 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S626.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s626", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1634:0": "\n참으로 훌륭하시옵니다",
    "9:1635:0": "끝내 밀어붙이셨군요\n참으로 훌륭하십니다!",
    "9:1636:0": "밀리고 말았나……",
    "9:1637:0": "힘이 미치지 못했다…… 미안하다!",
    "9:1638:0": "기세가 어찌 이리 강한가…… 맞설 수 없다……!",
    "9:1639:0": "죄송합니다…… 역부족이었습니다",
    "9:1640:0": "설마 함께 밀려날 줄이야……!",
    "9:1641:0": "가세도 헛되이 밀려났는가……",
    "9:1642:0": "힘이 되어 주지 못하다니…… 부끄러울 따름……",
    "9:1643:0": "도움조차 되지 못하다니……",
    "9:1644:0": "힘이 미치지 못했습니다…… 죄송합니다……",
    "9:1645:0": "조금만 더 힘이 있었다면……",
    "9:1646:0": "큭…… 실패했습니까……",
    "9:1647:0": "힘이 미치지 못했군…… 원통하다",
    "9:1648:0": "지금 간다!\n기다려라!",
    "9:1649:0": "!\n지금 가겠노라!",
    "9:1650:0": "잠시만 더 버텨라!",
    "9:1651:0": "조금만 더 기다려 주시오!",
    "9:1652:0": "내가 대신하마! 서둘러라!",
    "9:1653:0": "의 곁으로\n향할까……",
    "9:1654:0": "맡겨 주시오\n",
    "9:1654:1": "이(가) 가겠소",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1634:0",
    "9:1649:0",
    "9:1653:0",
    "9:1654:0",
    "9:1654:1",
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
                "segment": "base_msggame_B001_S626",
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
