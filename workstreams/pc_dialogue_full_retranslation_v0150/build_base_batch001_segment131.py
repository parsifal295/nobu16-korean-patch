#!/usr/bin/env python3
"""Build Base authoring segment 131 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S131.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s131", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2440:0": "아무래도 그 청에는 응할 수 없어요\n저희 사정도 부디 이해해 주세요",
    "6:2441:0": "아무래도 이 조건으로는 교섭할 수 없소\n우리 가문더러 망하라는 것과 같으니…",
    "6:2442:0": "을(를) 쫓아내다니 배짱 한번 좋군\n좋아, 그럴 셈이라면\n우리도 생각이 있다!",
    "6:2443:0": "님,",
    "6:2443:1": "을(를) 쫓아낸 일을\n후회하지 않으면 좋겠군",
    "6:2444:0": "님을 믿고 찾아왔건만\n설마 쫓겨날 줄이야…\n",
    "6:2444:1": "의 사람 보는 눈도 아직 멀었군",
    "6:2445:0": "부탁을 들어주지 않다니 참으로 유감이군\n교섭 조건이 나빴던 것인가,\n애초에 의지할 상대를 잘못 골랐나…",
    "6:2446:0": "은(는) 믿고 있었건만…!\n이만 실례하겠소!",
    "6:2447:0": "이렇게 될 줄 알기는 했습니다만…\n",
    "6:2447:1": "은(는) 의지할 만한 상대가\n아니었던 모양이군요",
    "6:2448:0": "어쩔 수 없군…\n뭐,",
    "6:2448:1": "은(는) 우리 가문의 이야기를\n들을 생각이 없다는 걸 안 것만으로도 수확인가",
    "6:2449:0": "흠… 이",
    "6:2449:1": "을(를) 박대한 일을\n나중에 후회하지 않으면 좋겠군",
    "6:2450:0": "교섭을 거절당하다니 참으로 유감입니다…\n실례하겠습니다",
    "6:2451:0": "부탁을 들어주지 않다니,\n이 무슨 치욕인가…!　",
    "6:2451:1": "따위를\n의지하는 게 아니었어!",
    "6:2452:0": "그쪽에도 사정이 있겠지만\n교섭을 거절당하다니 참으로 유감입니다…",
    "6:2453:0": "뭐라고!\n",
    "6:2453:1": "의 부탁을 들어주지 않다니!\n으음, 어찌해야 하나…",
    "6:2454:0": "지금 나가면 교섭에 실패한 것이 되어\n우호도가 떨어지고 맙니다\n정말 외교 화면에서 나가시겠습니까?",
    "6:2455:0": "이 내용으로 교섭을 제안합니다\n진행하시겠습니까?",
    "6:2456:0": "성공률이 100%가 아닙니다\n진행하시겠습니까?\n실패하면 상대가 노하여 교섭이 난항을 겪습니다",
    "6:2457:0": "성공률이 100%가 아닙니다\n진행하시겠습니까?\n실패하면 교섭이 중단되고 맙니다",
    "6:2458:0": "와(과)의 교섭이 성립하면\n우리 가문의 「공략 목표」가 해제됩니다\n정말 진행하시겠습니까?",
    "6:2459:0": "화나게 해 버렸군…\n곤란하게 됐어…",
}

DYNAMIC_COORDINATES = {
    "6:2442:0",
    "6:2443:0",
    "6:2443:1",
    "6:2444:0",
    "6:2444:1",
    "6:2446:0",
    "6:2447:0",
    "6:2447:1",
    "6:2448:0",
    "6:2448:1",
    "6:2449:0",
    "6:2449:1",
    "6:2451:0",
    "6:2451:1",
    "6:2453:0",
    "6:2453:1",
    "6:2458:0",
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
                "segment": "base_msggame_B001_S131",
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
