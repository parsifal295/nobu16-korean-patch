#!/usr/bin/env python3
"""Build Base authoring segment 715 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S715.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s715", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3405:0": "적이 협격을 꾀하고 있소\n다가오기 전에 발을 묶어 두고 싶소",
    "9:3406:0": "협격하려는 부대가 있습니다\n발을 묶을 병력을 보냅시다",
    "9:3407:0": "협격을 꾀하는 무리가 있소\n발을 묶는 데 병력을 돌려야 할 듯하오",
    "9:3408:0": "협격하려는 부대가 있습니다\n발을 묶을 병력을 보냅시다",
    "9:3409:0": "협격을 꾀하는 적 부대가 있습니다\n발을 묶는 건 어떻겠소",
    "9:3410:0": "놈들의 퇴각로가 텅 비었군\n노려 봐도 되지 않겠어?",
    "9:3411:0": "적의 퇴각로는 수비가 허술하오\n지금이야말로 퇴로를 끊읍시다",
    "9:3412:0": "놈들은 퇴각로 수비가 허술하군요\n파괴할 호기일 것입니다",
    "9:3413:0": "적의 퇴각로 수비가 허술합니다\n퇴로를 끊을 호기인 듯하옵니다",
    "9:3414:0": "놈들의 퇴각로가 허술해 보입니다\n파괴를 노리는 건 어떻습니까?",
    "9:3415:0": "적의 퇴각로 수비가 허술하군…\n퇴로를 끊을 호기일지도 모르겠군",
    "9:3416:0": "적의 퇴각로가 허술한 듯하오\n파괴를 노리는 것도 좋은 방책일 듯하오",
    "9:3417:0": "적의 퇴각로를 노리는 건 어떻소\n힘들이지 않고 퇴로를 끊을 수 있소이다",
    "9:3418:0": "적의 퇴로를 끊을 호기입니다!\n퇴각로 파괴를 노려 보는 건 어떻습니까?",
    "9:3419:0": "놈들은 퇴각로 수비가 허술하군요\n파괴할 호기일 것입니다",
    "9:3420:0": "적의 퇴로를 끊을 호기입니다!\n퇴각로 파괴를 노려 보는 건 어떻습니까?",
    "9:3421:0": "적의 퇴각로 수비가 허술합니다\n퇴로를 끊을 호기인 듯하옵니다",
    "9:3422:0": "요충지가 비어 있는 듯하군\n점령해 두는 것도 좋겠어",
    "9:3423:0": "요충지 제압을 노려볼 만하오\n부대를 보내는 건 어떻소",
    "9:3424:0": "요충지 제압을 노려볼 만하오\n부대를 보내는 건 어떻소",
    "9:3425:0": "요충지를 제압할 호기입니다\n신속히 장악해 지리적 이점을 얻읍시다",
    "9:3426:0": "요충지 제압을 노려볼 만하오\n부대를 보내는 건 어떻소",
    "9:3427:0": "요충지를 제압할 호기입니다\n신속히 장악해 지리적 이점을 얻읍시다",
}

DYNAMIC_RUNTIME_COORDINATES: set[str] = set()
STATIC_COORDINATES = set(TRANSLATIONS)


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
                "segment": "base_msggame_B001_S715",
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
