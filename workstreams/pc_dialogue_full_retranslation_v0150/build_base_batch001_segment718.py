#!/usr/bin/env python3
"""Build Base authoring segment 718 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S718.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s718", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3465:0": ", 소수 병력이로군\n섬멸해 공으로 삼으리라",
    "9:3466:0": ", 병력이 적군요\n먼저 무찌르겠습니다!",
    "9:3467:0": ", 소수 병력이군\n먼저 짓눌러 주마",
    "9:3468:0": "의 병력이 적군요\n집중 공격하겠습니다",
    "9:3469:0": ", 소수 병력으로 보이는군\n쳐부숴 공으로 삼으리라",
    "9:3470:0": "지리적 이점이 필요하다\n요충지를 빼앗겠다!",
    "9:3471:0": "진지를 굳히는 것도 중요하다\n우리는 요충지를 제압하러 간다",
    "9:3472:0": "요충지를 확보해 두고 싶군\n목표를 변경한다",
    "9:3473:0": "요충지를 소홀히 할 수는 없습니다\n지금부터 제압하러 가겠습니다",
    "9:3474:0": "병사를 쓰러뜨리는 것만이 싸움은 아니다\n요충지를 확보하리라!",
    "9:3475:0": "목표는 요충지로 한다\n싸움은 지리적 이점을 얻어야 하는 법이지",
    "9:3476:0": "목표 변경, 요충지를 제압하러 간다\n지리적 이점 없이는 승리할 수 없다",
    "9:3477:0": "지금 필요한 것은 요충지다!\n목표를 바꾸고 제압에 나선다!",
    "9:3478:0": "진군 목표를 요충지로 변경하겠습니다\n먼저 지리적 이점을 얻읍시다",
    "9:3479:0": "요충지를 소홀히 할 수는 없다\n제압하러 간다!",
    "9:3480:0": "목표를 변경합시다\n지금은 요충지 확보가 최우선입니다",
    "9:3481:0": "목표를 요충지로 바꾼다\n지리적 이점을 얻는 것이 싸움의 정석이지",
    "9:3482:0": "오, 퇴각로를 노릴 수 있겠군\n퇴로를 쳐부숴 주마!",
    "9:3483:0": "목표를 퇴각로로 변경한다\n퇴로를 끊으면 사기를 꺾을 수 있으리라",
    "9:3484:0": "퇴로를 끊으면 유리해지겠지\n퇴각로를 파괴해 주마",
    "9:3485:0": "퇴각로를 노릴 수 있겠군요\n먼저 퇴로를 막도록 하지요",
}

DYNAMIC_RUNTIME_COORDINATES = {f"9:{record_id}:0" for record_id in range(3465, 3470)}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_"
                    "context_where_available"
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
                "segment": "base_msggame_B001_S718",
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
