#!/usr/bin/env python3
"""Build Base authoring segment 21 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S21.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s21", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:608:0": "늘 고생만 시키는구나\n",
    "2:608:1": "의 공을 잊지 않으마",
    "2:609:0": "의 말이 옳다!\n내 공은 곧 우리 둘의 공이다",
    "2:610:0": "의",
    "2:610:1": "님께서\n덧없이 황천으로 떠나셨습니다\n고인의 명복을 함께 빕시다",
    "2:611:0": "적은 증오스러운",
    "2:611:1": "다메노부",
    "2:611:2": "!\n",
    "2:611:3": "을 얕본 대가를 치러라",
    "2:612:0": "귀신",
    "2:612:1": "이 나가신다",
    "2:612:2": "!\n",
    "2:612:3": "다테",
    "2:612:4": "의 애송이에게 본때를 보여 주마",
    "2:613:0": "독안룡이 귀신",
    "2:613:1": "사타케",
    "2:613:2": "를 제압해 보이겠다\n모두 들어라, 지금이 고비다!",
    "2:614:0": "어리석은 쇼군이여\n이",
    "2:614:1": "이 여는 새 시대에 네놈은 필요 없다",
    "2:615:0": "여기는 내게 맡겨 줘!\n이 화승총으로",
    "2:615:1": "노부나가",
    "2:615:2": "에게 한 방 먹여 주마",
    "2:616:0": "적은 서국무쌍의 무장으로 이름 높은",
    "2:616:1": "스에",
    "2:616:2": "\n온갖 계책을 다해 맞서라",
    "2:617:0": "명문",
    "2:617:1": "이치조",
    "2:617:2": "가문이라 해도 겁낼 것 없다\n이",
    "2:617:3": "의 이름 아래 하극상을 이루리라",
    "2:618:0": "지금이야말로 호기다\n",
    "2:618:1": "오토모",
    "2:618:2": "를 무너뜨리고 이 규슈에서 패권을 잡으리라",
    "2:619:0": "어리석은",
    "2:619:1": "시마즈",
    "2:619:2": "여\n놈들에게 신의 위광을 보여 주어라",
}

DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS)


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
                "segment": "base_msggame_B001_S21",
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
