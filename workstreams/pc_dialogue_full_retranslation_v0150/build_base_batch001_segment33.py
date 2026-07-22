#!/usr/bin/env python3
"""Build Base authoring segment 33 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S33.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s33", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:367:0": "정책 문안을\n다듬읍시다",
    "6:368:0": "우리 가문의 정책은\n이것이 최선일까…",
    "6:369:0": "이 또한 백성을 위해\n필요한 일",
    "6:370:0": "괜찮지 않겠나\n…아마도",
    "6:371:0": "깊이 생각하신 일이니\n명 받들겠습니다",
    "6:372:0": "백성의 이해를 얻는 것이\n",
    "6:372:1": "의 책무…",
    "6:373:0": "과연\n우리 가문의 방침은 이러하군",
    "6:374:0": "으음, 달마다\n그만한 돈이…",
    "6:375:0": "거래의 요령은\n인색하게 굴지 않는 거야",
    "6:376:0": "쳇…\n좀 더 깎아 달라고",
    "6:377:0": "전쟁에 대비하려면\n거래도 필요하다",
    "6:378:0": "훌륭한 거래인 듯합니다…!",
    "6:379:0": "이번 거래는\n좋은 판단이신 듯합니다",
    "6:380:0": "상인도 이익을 보아야\n장사가 성립하는 법",
    "6:381:0": "흠, 적어도 대등한\n거래는 했다고 본다",
    "6:382:0": "이 거래는\n예상한 바입니다",
    "6:383:0": "거래하느라 고생 많았겠소",
    "6:384:0": "숨 막히는 공방…\n상인도 제법이구나",
    "6:385:0": "거래의 결과를\n어찌 살릴 것인가",
    "6:386:0": "한 방 먹었다 해도\n손해는 만회할 수 있다",
}

DYNAMIC_RUNTIME_COORDINATES = {"6:372:0", "6:372:1"}


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
                "segment": "base_msggame_B001_S33",
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
