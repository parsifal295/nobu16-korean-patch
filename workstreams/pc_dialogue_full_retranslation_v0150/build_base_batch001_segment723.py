#!/usr/bin/env python3
"""Build Base authoring segment 723 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S723.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s723", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3573:0": "여기서 대기한다\n활로 요격한다",
    "9:3574:0": "고지를 확보했다!\n놈들을 조준해 쏴 주마!",
    "9:3575:0": "여기서 대기하라!\n적이 보이는 즉시 쏴라!",
    "9:3576:0": "자리를 잡았다\n이제 조준해 쏘기만 하면 된다",
    "9:3577:0": "여기서 대기하겠습니다\n지나가는 적을 쏘십시오",
    "9:3578:0": "고지를 장악했다\n화승에 불을 붙여라",
    "9:3579:0": "여기서 대기한다\n적이 오면 쏴라",
    "9:3580:0": "좋아, 자리를 잡았다\n이제 쏘기만 하면 된다",
    "9:3581:0": "고지를 차지했다\n철포에 탄환을 장전하라",
    "9:3582:0": "고지에 도착했습니다\n철포로 요격하겠습니다",
    "9:3583:0": "배치를 마쳤다\n철포로 지원하겠다",
    "9:3584:0": "고지로 이동했습니다\n철포로 원호하겠습니다",
    "9:3585:0": "여기서 대기한다\n철포로 요격한다",
    "9:3586:0": "활과 철포를 준비하라!\n있는 대로 모조리 퍼부어라!",
    "9:3587:0": "사수들은 앞으로!\n목표는 아래쪽의 적군이다!",
    "9:3588:0": "활을 준비하라!\n놈들을 남김없이 쏘아 쓰러뜨리리라!",
    "9:3589:0": "사수들을 대열에 세우십시오!\n아래로 쏘아 적의 사기를 꺾겠습니다!",
    "9:3590:0": "벼랑 아래의 적을 쏴라!\n모두, 강궁을 쓸 때다!",
    "9:3591:0": "사격 준비!\n아래쪽의 적을 쏘아 꼼짝 못 하게 하라!",
    "9:3592:0": "사수들은 벼랑 끝으로!\n활과 화살로 적을 친다!",
    "9:3593:0": "활을 벼랑 아래로 겨눠라!\n쉬지 말고 계속 쏴라!",
    "9:3594:0": "사수들을 모으십시오!\n벼랑 아래의 적을 노리겠습니다!",
}

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
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
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
                "segment": "base_msggame_B001_S723",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": 0,
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
