#!/usr/bin/env python3
"""Build Base authoring segment 610 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S610.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s610", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1295:0": "가세하러 왔는가\n참으로 기특하구나",
    "9:1296:0": "가세해 주셔서\n감사드립니다!",
    "9:1297:0": "도우러 와 주다니\n고맙소!",
    "9:1298:0": "가세해 주시니 큰 도움이 됩니다",
    "9:1299:0": "음, 든든하구나\n부탁하마",
    "9:1300:0": "으아아악!\n네놈, 기어이 저질렀구나……!",
    "9:1301:0": "크으윽,\n떠내려가고 만다!",
    "9:1302:0": "으윽……!\n이 무슨 참상인가!",
    "9:1303:0": "탁류가……!\n으아아악!",
    "9:1304:0": "으으윽!\n병사들이 떠내려가는구나!",
    "9:1305:0": "으으음, 수공인가!?",
    "9:1306:0": "안 됩니다!\n물살에 부대가……!",
    "9:1307:0": "엄청난 물살이로다!\n병사들이 휩쓸려 간다!",
    "9:1308:0": "돌발 홍수라니!?\n당했군요……",
    "9:1309:0": "큭, 어찌 이런 짓을……",
    "9:1310:0": "물을 다루다니\n제법이군요……",
    "9:1311:0": "두, 둑을 터뜨리다니\n말도 안 돼!",
    "9:1312:0": "어, 어이!\n",
    "9:1312:1": "이(가) 아직……!",
    "9:1313:0": "크으윽,\n휘말린다……!",
    "9:1314:0": "이럴 수가,\n휘말렸는가……!",
    "9:1315:0": "이…… 이것은\n예상 밖입니다……!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1312:0",
    "9:1312:1",
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
                "segment": "base_msggame_B001_S610",
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
