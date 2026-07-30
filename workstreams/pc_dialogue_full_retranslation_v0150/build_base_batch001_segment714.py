#!/usr/bin/env python3
"""Build Base authoring segment 714 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S714.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s714", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3383:0": "의 부대부터 처리해야 할 듯하오\n소수 병력이니 격파하기 쉽소",
    "9:3384:0": "의 병력은 얼마 되지 않습니다\n우선 공격할 상대일 것입니다",
    "9:3385:0": "의 부대를 노리지 않겠소?\n소수 병력이니 격파하기도 쉽소",
    "9:3386:0": "일방적으로 사격당하고 있소!\n고지에 부대를 보내 주시오!",
    "9:3387:0": "고지에서 쏟아지는 사격이 버겁습니다…\n부대를 보내 저지합시다",
    "9:3388:0": "사격 피해가 커지기만 하는군…\n부대를 보내 저지합시다",
    "9:3389:0": "사격 피해가 커지고 있습니다\n고지에 부대를 보내 제압합시다",
    "9:3390:0": "참으로 성가신 사격이군…\n부대를 보내 저지합시다",
    "9:3391:0": "참으로 성가신 사격이오…\n고지에 부대를 보내 제압해야 할 듯하오",
    "9:3392:0": "이렇게 사격이 거세서야…\n고지를 빼앗을 부대를 보내야 할 듯합니다",
    "9:3393:0": "일방적으로 사격당하고 있군…\n고지를 빼앗지 않으면 피해가 늘어날 것이오",
    "9:3394:0": "적의 사격을 저지하지 않으면 피해가…\n고지를 공격해 제압합시다",
    "9:3395:0": "고지의 사격으로 피해가 막심합니다…\n제압 부대의 파견을 요청합니다",
    "9:3396:0": "사격 피해가 커지고 있습니다\n병력을 보내 저지합시다",
    "9:3397:0": "적의 사격으로 피해가 막심합니다\n부대를 보내 저지합시다",
    "9:3398:0": "협격을 노리는 놈들이 있군…\n발을 묶어야 하지 않겠어?",
    "9:3399:0": "적의 노림수는 협격이군요\n요격할 부대가 필요할 듯합니다",
    "9:3400:0": "적은 협격을 꾀하고 있습니다\n요격 부대를 파견합시다",
    "9:3401:0": "협격하려고 적이 이동 중입니다\n즉시 요격해야 할 듯합니다",
    "9:3402:0": "적의 노림수는 협격인 듯하오\n아군 부대에 저지를 맡기는 건 어떻소",
    "9:3403:0": "적은 협격을 꾀하는 모양입니다\n발을 묶는 것이 상책이겠습니다",
    "9:3404:0": "협격을 꾀하는 부대가 있습니다\n부대를 보내 발을 묶는 건 어떻겠습니까",
}

DYNAMIC_RUNTIME_COORDINATES = {f"9:{record_id}:0" for record_id in range(3383, 3386)}
STATIC_COORDINATES = set(TRANSLATIONS).difference(DYNAMIC_RUNTIME_COORDINATES)


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
                "segment": "base_msggame_B001_S714",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
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
