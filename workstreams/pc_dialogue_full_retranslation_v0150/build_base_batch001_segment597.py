#!/usr/bin/env python3
"""Build Base authoring segment 597 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S597.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s597", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1011:0": "반응은 있었는데……",
    "9:1012:0": "적을 속이는 것도\n재미있구먼!",
    "9:1013:0": "후방 경계가 소홀한\n모양이군!",
    "9:1014:0": "눈에 보이지 않는 적……\n어찌 대처할 테냐",
    "9:1015:0": "불안을 부추겨\n드리지요",
    "9:1016:0": "후후, 퇴로 경계는\n소홀히 하지 말게나",
    "9:1017:0": "왜 그러느냐, 배후가\n불안하지 않은가?",
    "9:1018:0": "여기서―",
    "9:1018:1": "을(를)\n상대하고 있어도 되겠나",
    "9:1019:0": "너무 깊이 나선 것 아니냐?",
    "9:1020:0": "후방이 걱정되기\n시작했겠지요?",
    "9:1021:0": "거짓 정보로 적을\n물러나게 해 주마!",
    "9:1022:0": "어머어머\n후방을 비워 둔 모양이네",
    "9:1023:0": "싸우지 않고\n물러나게 해 주마!",
    "9:1024:0": "속지 않는단 말이냐!\n제법이구나!",
    "9:1025:0": "큭!\n거짓 정보가 통하지 않는가……!",
    "9:1026:0": "동요하지 않는가……\n적이지만 장하도다",
    "9:1027:0": "내 계책을 간파하다니……",
    "9:1028:0": "으음…… 빈틈이 없군",
    "9:1029:0": "내 계책이 통하지 않다니……\n이럴 수가……",
    "9:1030:0": "거짓 정보에 넘어가지 않다니\n……얕볼 수 없군",
    "9:1031:0": "이놈, 영악한 놈 같으니",
    "9:1032:0": "아무래도\n속아 주지는 않는군요……",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS) - {"9:1018:0", "9:1018:1"}


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
                "segment": "base_msggame_B001_S597",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
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
