#!/usr/bin/env python3
"""Build Base authoring segment 713 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S713.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s713", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3361:0": "님께서 포박되셨다…\n이 무슨 일이란 말인가…",
    "9:3362:0": "의 부대는 한낱 잡졸들뿐이야\n얼른 해치워 버리자고!",
    "9:3363:0": "의 부대 따위는 적수가 못 되오\n단숨에 처치하는 건 어떻소?",
    "9:3364:0": "의 부대는 약병뿐입니다\n먼저 쳐부수는 것도 한 방법이겠군요",
    "9:3365:0": "의 병사들은 오합지졸일 뿐\n노리면 금세 무너질 것이오",
    "9:3366:0": "의 부대는 적수가 못 되오\n병력을 보내 쓰러뜨려야 할 듯하오",
    "9:3367:0": "의 부대는 약병으로 보입니다\n먼저 쓰러뜨린다면 저들이겠군요",
    "9:3368:0": "의 병사들은 적수가 아니오\n노려 치는 것도 좋겠군요",
    "9:3369:0": "의 병사들은 허약하오\n단숨에 쓰러뜨리는 건 어떻소",
    "9:3370:0": "의 부대는 약병이옵니다\n집중 공격해 무너뜨립시다",
    "9:3371:0": "의 부대는 약병뿐이군요\n어서 쳐부숴야겠습니다",
    "9:3372:0": "의 부대는 약병뿐입니다\n공격하면 버티지 못할 것입니다",
    "9:3373:0": "의 부대는 약병으로 보입니다\n노리면 손쉽게 물리칠 수 있겠습니다",
    "9:3374:0": "의 부대를 치지 않겠어?\n병력이 적으니 노릴 만해",
    "9:3375:0": "의 병력은 얼마 되지 않습니다\n공격하기 좋은 상대인 듯합니다",
    "9:3376:0": "의 부대를 치는 건 어떻소?\n소수 병력이니 손쉽게 무너뜨릴 수 있소",
    "9:3377:0": "의 부대는 소수 병력으로 보입니다\n먼저 격파하는 건 어떻겠습니까",
    "9:3378:0": "의 부대를 노리는 건 어떻소\n저 정도 수라면 재빨리 무찌를 수 있소이다",
    "9:3379:0": "의 부대를 노리지 않겠소?\n소수 병력이니 격파하기도 쉽소",
    "9:3380:0": "의 부대를 공격하는 건 어떻겠소\n소수 병력이니 곧 격파할 수 있습니다",
    "9:3381:0": "의 병력은 얼마 되지 않는군\n먼저 치는 건 어떻소",
    "9:3382:0": "의 부대가 좋은 표적입니다\n수가 적어 금방 쓰러뜨릴 수 있습니다",
}

DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS)
STATIC_COORDINATES: set[str] = set()


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
                "segment": "base_msggame_B001_S713",
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
