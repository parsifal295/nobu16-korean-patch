#!/usr/bin/env python3
"""Build Base authoring segment 580 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S580.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s580", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:649:0": "목숨이 아까워 달아났나……\n가련한 자로군",
    "9:650:0": "달아났습니까……\n겁이 많은 대장이군요",
    "9:651:0": "대장의 부대가 무너졌다!\n지금이 호기다!",
    "9:652:0": "대장의 부대가 무너졌군……\n이미 이긴 것이나 다름없다",
    "9:653:0": "대장이라는 자가……\n부끄러운 줄도 모르는군",
    "9:654:0": "도망치다니 비겁하군!\n대장을 추격하라!",
    "9:655:0": "어머, 대장이\n도망가는군요",
    "9:656:0": "도망치지 마라!\n",
    "9:656:1": "와(과) 싸워라!",
    "9:657:0": "대장이 도망치다니\n꼴사납군……",
    "9:658:0": "보아라, 적의 대장이\n도망칠 채비를 한다!",
    "9:659:0": "빌어먹을……\n물러난다!",
    "9:660:0": "이래서는 싸움이 안 된다……\n물러나라!",
    "9:661:0": "질 싸움에 나서는 것은 어리석다……\n물러난다",
    "9:662:0": "더 싸워도 이득이 없습니다\n철수를 시작합니다",
    "9:663:0": "이…… 이래서는 싸울 수 없다!\n물러나라!",
    "9:664:0": "병력이 무너졌다고……\n으음…… 물러나라!",
    "9:665:0": "이렇게까지 몰렸으니\n……큭, 물러나라",
    "9:666:0": "이제 싸울 상황이 아니다\n……물러나거라",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS) - {"9:656:0", "9:656:1"}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S580", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
