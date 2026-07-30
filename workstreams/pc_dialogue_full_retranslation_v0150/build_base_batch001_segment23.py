#!/usr/bin/env python3
"""Build Base authoring segment 23 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S23.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s23", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:631:0": "나의 힘을 똑똑히 보아라!",
    "2:632:0": "나의 힘을 똑똑히 보아라!",
    "2:633:0": "나의 힘을 똑똑히 보아라!",
    "2:634:0": "나의 힘을 똑똑히 보아라!",
    "2:635:0": "나의 힘을 똑똑히 보아라!",
    "2:636:0": "나의 힘을 똑똑히 보아라!",
    "2:637:0": "나의 힘을 똑똑히 보아라!",
    "2:638:0": "나의 힘을 똑똑히 보아라!",
    "2:639:0": "나의 힘을 똑똑히 보아라!",
    "2:640:0": "나의 힘을 똑똑히 보아라!",
    "2:641:0": "맡겨 주십시오!\n",
    "2:641:1": "에서 발생 중인",
    "2:641:2": "을(를)\n해결하고 돌아오겠습니다",
    "2:642:0": "군단장이 자리를 비워\n",
    "2:642:1": "군단이 해산되었습니다",
    "2:643:0": "에 속한\n",
    "2:643:1": "에서의",
    "2:643:2": "의 개발에는\n앞으로",
    "2:643:3": "일 정도 걸릴 전망입니다",
    "2:644:0": "에서 건설 중인\n",
    "2:644:1": "(LV",
    "2:644:2": ")가 완성되려면\n앞으로",
    "2:644:3": "일 정도 걸릴 전망입니다",
    "2:645:0": "정책 「",
    "2:645:1": "(LV",
    "2:645:2": ")」이 발령되려면\n앞으로",
    "2:645:3": "일 정도 걸릴 전망입니다",
    "2:646:0": "은(는) 앞으로",
    "2:646:1": "일 정도\n걸릴 전망입니다",
    "2:647:0": "에 관한 진언 진행 중",
    "2:648:0": "은(는) 앞으로",
    "2:648:1": "일 정도\n걸릴 전망입니다",
    "2:649:0": "에 속한",
    "2:649:1": "에서의\n",
    "2:649:2": "은(는)\n앞으로",
    "2:649:3": "일 정도 걸릴 전망입니다",
    "2:650:0": "에 대한 친선은\n",
    "2:650:1": "개월 후 완료될 예정입니다",
    "2:651:0": "조정과의 친선은\n",
    "2:651:1": "개월 후 완료될 예정입니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) >= 641
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
                "segment": "base_msggame_B001_S23",
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
