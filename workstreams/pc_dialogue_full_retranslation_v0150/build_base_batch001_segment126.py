#!/usr/bin/env python3
"""Build Base authoring segment 126 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S126.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s126", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2340:0": "이걸로 성의는 전해지겠지\n상대 체면을 지나치게 세워 준 감은 있지만",
    "6:2341:0": "틀림없이 교섭이 성립할 게다!\n원, 요즘 것들은 욕심이 많아 탈이야",
    "6:2342:0": "이걸로 성의는 보였을 테니\n",
    "6:2342:1": "님을 믿어 봅시다!",
    "6:2343:0": "이만큼 얹으면\n",
    "6:2343:1": "님도 받아들이겠지",
    "6:2344:0": "이걸로",
    "6:2344:1": "님도\n우리 뜻을 헤아려 주실 거예요",
    "6:2345:0": "이 정도면",
    "6:2345:1": "님도\n승낙하실 터…",
    "6:2346:0": "어이, 농담이 지나치잖아!\n이 정도면 어때?",
    "6:2347:0": "그 조건으로는 아무래도…\n이 조건이라면 받아들일 수 있는데, 어떠한가?",
    "6:2348:0": "그 조건으로는 우리 가문의 체면이 서지 않소\n이 조건은 어떻소?",
    "6:2349:0": "…무리한 요구를 하시는군요\n적어도 이 정도는 어떻습니까?",
    "6:2350:0": "가소롭군… 겨우 그 정도라니\n적어도 이만큼은 내놓아야 한다",
    "6:2351:0": "우리 가문을 너무 얕보는군\n그에 걸맞은 대가란 이 정도를 말하는 것이다",
    "6:2352:0": "좀 더 알아줄 만한 인물인가 했더니…\n적어도 이 정도의 성의는 보여 주셔야겠소",
    "6:2353:0": "재미없는 농담이군. 웃을 수도 없어\n이 정도라면 들어주지 못할 것도 없지",
    "6:2354:0": "어렵군요…\n이 조건이라면 괜찮습니다만",
    "6:2355:0": "헛소리를…\n이 정도라면 생각해 보지 못할 것도 없다",
    "6:2356:0": "재미있는 말씀을 하시는군요\n이만큼은 내놓으셔야…",
    "6:2357:0": "이거 쉽지 않군요…\n이 정도로는 안 되겠습니까?",
    "6:2358:0": "안 돼, 안 돼! 이번이 마지막이야!\n이 정도면 어때?",
    "6:2359:0": "우리에게도 양보할 수 없는 긍지가 있소\n이 정도면 어떻겠소… 이것이 마지막이오",
}

DYNAMIC_COORDINATES = {
    "6:2342:0",
    "6:2342:1",
    "6:2343:0",
    "6:2343:1",
    "6:2344:0",
    "6:2344:1",
    "6:2345:0",
    "6:2345:1",
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
                "segment": "base_msggame_B001_S126",
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
