#!/usr/bin/env python3
"""Build Base authoring segment 591 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S591.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s591", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:878:0": "공격하려면 지금입니다!",
    "9:879:0": "마음껏 싸우거라",
    "9:880:0": "이제 적 따위는\n두려워할 것도 없으리라",
    "9:881:0": "강화해 두었소,\n부디 마음껏 싸우시오",
    "9:882:0": "이것으로 적을\n쳐부수는 게다!",
    "9:883:0": "공세로 전환합시다!",
    "9:884:0": "이것으로 끝내라!",
    "9:885:0": "단숨에 나아갑시다!",
    "9:886:0": "자, 나아가겠소!",
    "9:887:0": "센나리뵤탄이 보이느냐?\n내가 왔노라, 떨쳐 일어나라!",
    "9:888:0": "네 뜻대로 되게 두진 않겠다!",
    "9:889:0": "우쭐대는 것도\n여기까지다!",
    "9:890:0": "기세를 꺾어 주마",
    "9:891:0": "나쁘게 생각하진\n말아 주세요",
    "9:892:0": "마음대로 하게 두지 않겠다!",
    "9:893:0": "얌전히 있어\n주셔야겠소……",
    "9:894:0": "마음껏 움직이게 두면\n방해가 되니 말이다",
    "9:895:0": "시끄러운 아이로구나\n행실 바르게 굴어라!",
    "9:896:0": "마음대로 하게 두지 않겠어!",
    "9:897:0": "얌전히 있게 해 주마!",
    "9:898:0": "멋대로 하게\n두지 않겠습니다!",
    "9:899:0": "멋대로 굴게 두지 않겠다!",
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
                "segment": "base_msggame_B001_S591",
                "decision_count": len(rows),
                "retranslated": len(rows),
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
