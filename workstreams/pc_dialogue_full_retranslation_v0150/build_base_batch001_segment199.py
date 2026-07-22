#!/usr/bin/env python3
"""Build Base authoring segment 199 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S199.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s199", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3428:0": "이(가) 훈공 1위입니까, 감사드립니다\n낭중지추라 하듯 낮은 자리에 있으면서도\n주군의 눈에 든 것이야말로 망외의 기쁨",
    "6:3429:0": "이(가) 훈공 1위입니까, 감사드립니다\n낭중지추라 하듯 낮은 자리에 있으면서도\n",
    "6:3429:1": "의 눈에 든 것이야말로 망외의 기쁨",
    "6:3430:0": "이(가) 제일이군요\n지난 한 해 애쓴 보람이 있었습니다!",
    "6:3431:0": "말단의",
    "6:3431:1": "이(가) 제일인가\n제법 총애를 받고 있는 모양이군",
    "6:3432:0": "따위를 눈여겨봐 주시다니\n올해도 쉬지 않고 정진하겠사와요",
    "6:3433:0": "이럴 수가,",
    "6:3433:1": "이(가) 제일이라니…\n아직도 실감이 나지 않으나\n기대를 받는 것은 기쁜 일이로군",
    "6:3434:0": "훈공 1위라니, 고맙구먼!\n이 기세로 높으신 놈들도 제치고\n정상까지 치고 올라가 주마!",
    "6:3435:0": "훈공 1위는 무문의 영예\n한결같이 충의를 다해 온…\n보람이 있었다 하겠소…",
    "6:3436:0": "훈공 1위라니 경사스럽구나\n아직 미숙한 몸이나 한 걸음씩 정진하여\n우리 가문에 이바지하겠소",
    "6:3437:0": "이(가) 제일이라니 기쁘군요\n앞으로도 이 영예에 자만하지 않고\n스스로를 엄히 다스려 나가겠습니다",
    "6:3438:0": "이(가) 훈공 1위인가\n그저 무인의 길 하나만을 닦았을 뿐인데\n그것이 이토록 큰 영예가 될 줄이야",
    "6:3439:0": "이(가) 훈공 1위라고요?\n그저,",
    "6:3439:1": "을(를) 위해\n힘써 왔을 뿐인데…?",
    "6:3440:0": "이(가) 훈공 1위란 말씀이옵니까\n우리 같은 자들이 중심이 되어 힘쓰지 않으면\n우리 가문의 번영도 없을 터이니 말이오",
    "6:3441:0": "오오,",
    "6:3441:1": "이(가) 훈공 1위인가!\n",
    "6:3441:2": "으로(로)서 앞장서 본을 보이지 않으면\n아랫사람들이 따라오지 않을 테니 말이오",
}

STATIC_COORDINATES: set[str] = {
    "6:3434:0",
    "6:3435:0",
    "6:3436:0",
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S199", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
