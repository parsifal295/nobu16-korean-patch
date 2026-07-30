#!/usr/bin/env python3
"""Build Base authoring segment 121 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S121.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s121", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2216:0": "이런,",
    "6:2216:1": "이군…\n이번에는 무슨 용건인가",
    "6:2217:0": "이런, 잘 오셨소\n그래,",
    "6:2217:1": "님은 무엇을 바라시오",
    "6:2218:0": "이런,",
    "6:2218:1": "의 당주께서 오셨군\n오늘은 무슨 용건이시오?",
    "6:2219:0": "에서 당주께서 몸소 오셨군\n그래, 무슨 용건이시오?",
    "6:2220:0": "님\n오늘은 무슨 용건이신지요?",
    "6:2221:0": "님\n허심탄회하게 이야기해 보세",
    "6:2222:0": "자, 거리낌 없이 말씀하시지요",
    "6:2223:0": "우리 가문이 할 수 있는 일이라면\n힘이 되어 드리겠소",
    "6:2224:0": "무슨 용건이지?",
    "6:2225:0": "의 당주가\n이곳에 온 목적을 들어 보지",
    "6:2226:0": "용건을 들어 보지",
    "6:2227:0": "용건을 들어 볼까요?",
    "6:2228:0": "…용건이 뭐지?\n빨리 말해",
    "6:2229:0": "나도 바쁜 몸이다\n이득이 될 이야기는 가져왔겠지?",
    "6:2230:0": "뜻밖이군요… 우리 가문에 용무라니\n그래, 무슨 용건입니까?",
    "6:2231:0": "흠, 누구였더라… 아아\n",
    "6:2231:1": "이었군… 일부러 와 주다니 수고가 많네",
    "6:2232:0": "우리 가문에 무슨 용건이십니까?",
    "6:2233:0": "왔군\n오늘은 무슨 용건인가?",
    "6:2234:0": "그래, 무슨 용건이시오?",
    "6:2235:0": "오늘은 무슨 용건이오?",
}

DYNAMIC_COORDINATES = {
    "6:2216:0",
    "6:2216:1",
    "6:2217:0",
    "6:2217:1",
    "6:2218:0",
    "6:2218:1",
    "6:2219:0",
    "6:2220:0",
    "6:2221:0",
    "6:2225:0",
    "6:2231:0",
    "6:2231:1",
}


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
        dynamic = coordinate in DYNAMIC_COORDINATES
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
                "segment": "base_msggame_B001_S121",
                "decision_count": len(rows),
                "retranslated": len(rows) - len(DYNAMIC_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_COORDINATES),
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
