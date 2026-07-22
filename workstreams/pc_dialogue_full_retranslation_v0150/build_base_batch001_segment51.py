#!/usr/bin/env python3
"""Build Base authoring segment 51 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S51.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s51", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:697:0": "딱딱해 보이는 곳이군\n적응할 수 있으려나",
    "6:698:0": "나도 저 녀석처럼\n거드름 좀 피우고 있어야지",
    "6:699:0": "아직 익숙하지 않은 자리라\n긴장되는구나",
    "6:700:0": "평정중의 면면들과\n하루라도 빨리 어울려야 하는데",
    "6:701:0": "자, 이곳의 방식을\n배워 보도록 할까",
    "6:702:0": "낭비가 많지만…\n아직 의견을 낼 수는 없군",
    "6:703:0": "고참들이 성가실 듯하니\n얌전히 있는 게 낫겠군요",
    "6:704:0": "역시 긴장되는군요\n조금…이지만",
    "6:705:0": "신참이라 해도\n얕보게 두지 않겠다",
    "6:706:0": "고참 놈들…\n다가오면 벤다!",
    "6:707:0": "이 평정에\n새바람을 불어넣겠다",
    "6:708:0": "나를 평정중에 발탁하신\n주군의 뜻이 내게 있다",
    "6:709:0": "선배님들의\n솜씨를 지켜볼까…",
    "6:710:0": "과연… 역학 관계는\n이렇게 되어 있군요…",
    "6:711:0": "이 중에서는 내가 풋내기\n…라는 것이로군",
    "6:712:0": "자리에는 나름의 법도가 있다\n그에 따라야겠군",
    "6:713:0": "어서 평정중 분들께\n인정받고 싶구나",
    "6:714:0": "평정중의 일원이니\n힘써야만 하겠지",
    "6:715:0": "나라의 의사 결정에\n참여했노라",
    "6:716:0": "이 평정을\n언젠가 내가 장악하리라…!",
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
                "segment": "base_msggame_B001_S51",
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
