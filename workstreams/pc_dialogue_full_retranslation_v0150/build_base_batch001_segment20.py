#!/usr/bin/env python3
"""Build Base authoring segment 20 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S20.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s20", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:585:0": "천하포무라니 불손하기 이를 데 없구나\n비사문천을 대신해 쳐 없애 주마!",
    "2:586:0": "이 또한 난세의 이치…\n의형님, 부디 각오하시오!",
    "2:587:0": "에게 활을 겨누다니 가소롭구나\n결국 벼락출세한 자에 불과한가!",
    "2:588:0": "수많은 굴욕은 잊을 수 없다…\n용서할 수 없으니 토벌할 뿐이다!",
    "2:589:0": "왜 그러느냐, 애송이\n다기가 탐나거든 내 목을 노려 보아라",
    "2:590:0": "백부님, 무례를 범하겠습니다!\n길을 이 독안룡에게 내주십시오!",
    "2:591:0": "적이 가이의 호랑이라 해도\n",
    "2:591:1": "의 깃발 아래 패배는 용납되지 않는다",
    "2:592:0": "적은 가이의 호랑이인가…\n무, 무사로서 떨림이 멎질 않는구나",
    "2:593:0": "늙은 호랑이가 얼마나 대단한지 보자!\n새로운 싸움이 무엇인지 보여 주마",
    "2:594:0": "적이 군신이라면 이편은 마왕이다\n길을 막는 적은 모조리 걷어찰 뿐!",
    "2:595:0": "미카와 무사여, 맞서는 기개는 갸륵하다\n가이의 호랑이가 싸우는 법을 똑똑히 보여 주마",
    "2:596:0": "미카와의 너구리도 제법 살이 올랐구나…\n모두 단단히 각오하고 맞서라!",
    "2:597:0": "불구대천의 원수와 마주하다니…\n달이여, 나의 싸움을 지켜보라!",
    "2:598:0": "약아빠진 원숭이 놈…\n이 손으로 짓뭉개 주마!",
    "2:599:0": "녀석들아, 결코 방심하지 마라\n적은 지략가이니 겹겹의 함정을 경계하라",
    "2:600:0": "서방님, 다녀오세요\n부디 무리만은 하지 마세요…",
    "2:601:0": "빈집은 맡겨 주십시오\n거처는 이",
    "2:601:1": "이 지켜 드리겠습니다",
    "2:602:0": "님…\n여기서 돌아오시기를 기다리겠습니다",
    "2:603:0": "님, 출진하시는군요\n이",
    "2:603:1": "이 할 수 있는 일이라면 무엇이든…",
    "2:604:0": "님과 이",
    "2:604:1": "\n둘이서 공을 세웁시다!",
    "2:605:0": "! 늘 고맙다\n집은 부탁하마",
    "2:606:0": "배웅하느라 수고했다\n그 단도는 한시도 몸에서 떼지 말거라",
    "2:607:0": "야, 언제나 배웅해 줘서 고맙다\n싸움의 승리를 그대에게 바치마",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {587, 591, 601, 602, 603, 604, 605, 607}
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
                "segment": "base_msggame_B001_S20",
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
