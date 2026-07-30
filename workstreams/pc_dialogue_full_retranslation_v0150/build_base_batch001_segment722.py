#!/usr/bin/env python3
"""Build Base authoring segment 722 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S722.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s722", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3551:0": "지금부터 고지를 확보한다\n사격으로 원호하리라!",
    "9:3552:0": "고지를 확보해 두고 싶군\n사격으로 지원하리라",
    "9:3553:0": "고지를 확보해 둡시다\n사격이라면 제게 맡겨 주십시오",
    "9:3554:0": "고지를 차지해 둘까\n사격 원호라면 자신 있다",
    "9:3555:0": "고지를 제압하는 것이 상책이다\n사격으로 놈들을 견제해 주마",
    "9:3556:0": "고지로 이동을 시작한다\n사격이라면 손쉽게 적병을 줄일 수 있으리라",
    "9:3557:0": "지금부터 고지로 향한다!\n적군을 사격으로 꼼짝 못 하게 해 주마",
    "9:3558:0": "고지 제압에 나서겠습니다\n사격으로 적을 쓰러뜨려 보이겠습니다",
    "9:3559:0": "지금부터 고지로 향한다!\n사격은 내게 맡겨라!",
    "9:3560:0": "고지로 향합시다\n사격으로 견제하는 겁니다",
    "9:3561:0": "사격은 내게 맡기시오\n놈들을 쏘아 꼼짝 못 하게 하겠소",
    "9:3562:0": "고지를 확보했다!\n활을 준비해 둬라",
    "9:3563:0": "여기서 대기하라!\n적이 보이는 즉시 활을 쏴라!",
    "9:3564:0": "자리를 잡았다\n화살 수를 세어 둬라",
    "9:3565:0": "여기서 대기하겠습니다\n지나가는 적에게 활을 쏘십시오",
    "9:3566:0": "고지를 장악했다\n이제 적을 기다리기만 하면 된다",
    "9:3567:0": "여기서 대기한다\n적이 오면 활을 쏴라",
    "9:3568:0": "좋아, 자리를 잡았다\n이제 적에게 활을 쏘기만 하면 된다",
    "9:3569:0": "고지를 차지했다\n적이 올 때까지 대기하라",
    "9:3570:0": "고지에 도착했습니다\n활로 요격하겠습니다",
    "9:3571:0": "배치를 마쳤다\n활로 지원하겠다",
    "9:3572:0": "고지로 이동했습니다\n활로 원호하겠습니다",
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
                "segment": "base_msggame_B001_S722",
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
