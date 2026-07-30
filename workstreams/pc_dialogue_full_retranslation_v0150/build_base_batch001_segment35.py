#!/usr/bin/env python3
"""Build Base authoring segment 35 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S35.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s35", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:407:0": "수비든 공격이든\n성을 맡은 장수에게 달렸다",
    "6:408:0": "호오, 훌륭한 배치로다",
    "6:409:0": "전쟁이 임박했다…\n그런 뜻인가?",
    "6:410:0": "앞날을 내다보아야겠군요",
    "6:411:0": "실수로 빈 성을\n남기지 않도록 하십시오",
    "6:412:0": "주군의 배치에는\n빈틈이 없구나",
    "6:413:0": "성을 지키는 병력은\n공수의 요체이니라",
    "6:414:0": "참으로 절묘한 배치를\n생각해 내셨구려",
    "6:415:0": "장수의 배치를 바꾼다…\n전쟁 때문일까요",
    "6:416:0": "그런 배치로\n나오셨군요",
    "6:417:0": "요충지의 성에는\n훌륭한 장수를 두셔야 하오",
    "6:418:0": "최고의 전장을\n마련해 주기 바란다",
    "6:419:0": "대비해 두면\n공격받기 어려울 테니",
    "6:420:0": "그렇게까지 내다본\n배치라니",
    "6:421:0": "비어 있는 성 따위는\n없겠지요",
    "6:422:0": "여기서 배치를 바꾸다니\n훌륭하구려",
    "6:423:0": "부럽구나\n나도 힘 좀 내 볼까",
    "6:424:0": "흥\n꼴좋구나",
    "6:425:0": "소인도 그와 같은 영예를\n누리고 싶소이다",
    "6:426:0": "모난 돌이\n정 맞는 법…",
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
                "segment": "base_msggame_B001_S35",
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
