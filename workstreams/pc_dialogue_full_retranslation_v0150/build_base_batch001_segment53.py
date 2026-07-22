#!/usr/bin/env python3
"""Build Base authoring segment 53 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S53.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s53", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:737:0": "이(가)\n참석하다니",
    "6:738:0": "에게 이 자리는\n어울리지 않는군",
    "6:739:0": "어찌하여",
    "6:739:1": "놈이\n이런 자리에…",
    "6:740:0": "놈\n내게 맞서고 싶은 모양이군",
    "6:741:0": "님께서 평정에…\n기절할 것 같아…",
    "6:742:0": "신참 특유의 패기가\n버겁구나…",
    "6:743:0": "발탁되어 득의양양한 얼굴이군\n",
    "6:743:1": "…",
    "6:744:0": "개인의 호오를 떠나\n가문을 위해… 으음…",
    "6:745:0": "어차피 혼자 정할 것을\n평정 따위가 왜 필요하냐",
    "6:746:0": "이건 뭐…\n어쩔 도리가 없구먼",
    "6:747:0": "주군은 우리의 말에\n귀를 기울여 주지 않는 것인가",
    "6:748:0": "이제 더는 아무 말 않으리\n긍지를 지키며 스러질 뿐…",
    "6:749:0": "주군의 기세가 너무 강하면\n가신은 의기소침해지는 법…",
    "6:750:0": "이 참상…\n이제는 돌이키기 어려운가",
    "6:751:0": "들을 귀 없는 주군 아래에서는\n어떤 좋은 계책도 무의미하니…",
    "6:752:0": "이 꼴로는\n어떤 좋은 계책도 무의미하다…",
    "6:753:0": "우리 가신들은\n그저 창 대신 쓰이는 존재인가",
    "6:754:0": "부질없는 발버둥은 그만두고\n마지막만큼은 깨끗하게…",
    "6:755:0": "가문은 변고 하나로\n한순간에 무너질 것이다",
    "6:756:0": "이토록 어려운 상황을 구할 계책이\n있을 리 없다…",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if 737 <= int(coordinate.split(":")[1]) <= 743
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
                "segment": "base_msggame_B001_S53",
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
