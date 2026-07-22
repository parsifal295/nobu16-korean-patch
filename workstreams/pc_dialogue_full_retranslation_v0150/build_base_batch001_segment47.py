#!/usr/bin/env python3
"""Build Base authoring segment 47 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S47.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s47", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:632:0": "…역시\n우리 가문을 공격할 생각입니까",
    "6:633:0": "놈…\n수상한 움직임을",
    "6:634:0": "은(는)\n당장이라도 쳐들어오겠지",
    "6:635:0": "의 노림수는\n아무래도 우리 가문인 듯합니다…",
    "6:636:0": "어리석은",
    "6:636:1": "은(는)\n우리 가문을 이길 수 있다고 여기는 모양이다",
    "6:637:0": "의 사람들은\n우리에게 도전하고 싶은 모양",
    "6:638:0": "의 무리는\n우리를 사냥할 셈이군요",
    "6:639:0": "놈은\n금방이라도 쳐들어오겠구나",
    "6:640:0": "건방지구나",
    "6:640:1": "\n우리 가문을 노리고 있군",
    "6:641:0": "의 움직임이\n심상치 않습니다… 주의하십시오!",
    "6:642:0": "와의 전쟁은\n피하기 어려울 듯합니다…",
    "6:643:0": "이(가) 우리 가문을\n노린다… 좋아, 받아 주지",
    "6:644:0": "의 움직임…\n놈들과의 싸움이 머지않았군",
    "6:645:0": "아아…",
    "6:645:1": "이(가)\n쳐들어올 것 같습니다",
    "6:646:0": "의 무리는\n우리 가문을 노리고 있습니다",
    "6:647:0": "은(는)\n우리 가문을 노리는 눈치다",
    "6:648:0": "아무래도",
    "6:648:1": "에서\n수상한 움직임이",
    "6:649:0": "우리 마을 꼬맹이…\n감기는 좀 나았으려나",
    "6:650:0": "내 영지의 녀석들에게\n얕보이지 않도록 해야지",
    "6:651:0": "주군께서 맡기신 영지\n제대로 다스려야 해…",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if 633 <= int(coordinate.split(":")[1]) <= 648
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
                "segment": "base_msggame_B001_S47",
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
