#!/usr/bin/env python3
"""Build Base authoring segment 724 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S724.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s724", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3595:0": "사수들은 위치를 잡아라\n활을 쏘아 원호한다",
    "9:3596:0": "사수들을 모으십시오!\n벼랑 아래의 적을 노리겠습니다!",
    "9:3597:0": "사수들은 앞으로!\n적이 보이는 즉시 쏴라!",
    "9:3598:0": "일어서라!\u3000쉬는 건\n죽은 뒤에나 해라!",
    "9:3599:0": "움직일 수 있는 자는 당장 대열을 갖춰라\n싸움은 이제부터다",
    "9:3600:0": "움직일 수 있는 자는 당장 대열을 갖춰라\n싸움은 이제부터다",
    "9:3601:0": "즉시 부대를 재정비하라\n쉴 틈은 없다",
    "9:3602:0": "움직일 수 있는 자는 당장 대열을 갖춰라\n싸움은 이제부터다",
    "9:3603:0": "움직일 수 있는 자는 당장 대열을 갖춰라\n승부처는 지금부터다",
    "9:3604:0": "즉시 부대를 재정비하라\n쉴 틈은 없다",
    "9:3605:0": "움직일 수 있는 자는 당장 대열을 갖춰라\n싸움은 이제부터니라",
    "9:3606:0": "움직일 수 있는 자는 대열을 갖추십시오\n승부처는 지금부터입니다",
    "9:3607:0": "움직일 수 있는 자는 당장 대열을 갖춰라\n싸움은 이제부터다",
    "9:3608:0": "움직일 수 있는 자는 대열을 갖추십시오\n승부처는 지금부터입니다",
    "9:3609:0": "즉시 부대를 재정비하라\n쉴 틈은 없다",
    "9:3610:0": "적을 쓰러뜨릴 방법이야\n얼마든지 있지",
    "9:3611:0": "자, 다음 계책은\n어찌할꼬",
    "9:3612:0": "자, 다음 계책은\n어찌할꼬",
    "9:3613:0": "자, 다음 계책은\n어찌할꼬",
    "9:3614:0": "자, 다음 계책은\n어찌할꼬",
    "9:3615:0": "적을 농락할 방책이라면\n셀 수 없이 지니고 있지",
    "9:3616:0": "자, 다음 계책은\n어찌할꼬",
    "9:3617:0": "자, 다음 계책은\n어찌할꼬",
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
                "segment": "base_msggame_B001_S724",
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
