#!/usr/bin/env python3
"""Build Base authoring segment 124 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S124.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s124", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2300:0": "교섭 또한 싸움이니\n",
    "6:2300:1": "을(를) 납득시켜 보시오",
    "6:2301:0": "호오… 농담으로 꺼낸 말이 아니라면\n그 진심을 보여 주시오",
    "6:2302:0": "…아무리 중대한 일도 대가에 달린 법\n자, 우리 가문의 결심을 얼마로 보셨소?",
    "6:2303:0": "하하, 이거 어려운 말씀을 하시는군\n어중간한 대가로는 도저히 응할 수 없소",
    "6:2304:0": "와하하하! 참으로 호방한 소망이로다!\n대가도 필시 호방하겠지",
    "6:2305:0": "그렇군요…\n그 각오를 보여 주시지요",
    "6:2306:0": "터무니없이 부르는군\n대가가 비쌀 텐데?",
    "6:2307:0": "어머, 너무 무리한 말씀이시네요\n그만한 대가는 받아야겠어요…",
    "6:2308:0": "이거 또 대단한 요구로군…\n그만큼의 대가는 받겠소",
    "6:2309:0": "제안 내용을 일단 모두 취하합니다\n진행하시겠습니까?",
    "6:2310:0": "이 정도로는\n납득하지 않겠지…",
    "6:2311:0": "이 정도로는 아직 무리다\n무사의 체면을 짓밟는 행위야",
    "6:2312:0": "이것만으로는",
    "6:2312:1": "님이\n받아들이지 않을 것이다…",
    "6:2313:0": "님을 움직이려면\n더 얹어야겠군…",
    "6:2314:0": "아직 제시할 수는 없겠군…\n도발하러 온 것이 아니다",
    "6:2315:0": "이걸 제시해 상대를 화나게 하는 것도 재미있겠지만…\n요구를 관철하려면 악수겠지",
    "6:2316:0": "아직 너무 강경한 제안이오\n상대도 조금은 체면을 세워 줘야 하오",
    "6:2317:0": "으음… 이걸로 받아 주지 않으려나?\n…역시 이 정도로는 안 되겠지",
    "6:2318:0": "이 정도로는",
    "6:2318:1": "님이\n납득하지 않으시겠지요…",
    "6:2319:0": "이 정도로",
    "6:2319:1": "님이\n고개를 끄덕일 리가 없겠군…",
}

DYNAMIC_COORDINATES = {
    "6:2300:0",
    "6:2300:1",
    "6:2312:0",
    "6:2312:1",
    "6:2313:0",
    "6:2318:0",
    "6:2318:1",
    "6:2319:0",
    "6:2319:1",
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
                "segment": "base_msggame_B001_S124",
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
