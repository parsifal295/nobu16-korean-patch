#!/usr/bin/env python3
"""Build Base authoring segment 157 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S157.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s157", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2857:0": "흠, 알았다\n우리는,", "6:2857:1": "을(를) 공격하겠다",
    "6:2858:0": "분부 받들겠습니다\n저희는,", "6:2858:1": "을(를)\n공격하겠습니다",
    "6:2859:0": "흠, 알았다\n우리는,", "6:2859:1": "을(를) 공격하기로 하지",
    "6:2860:0": "노릴 것은,", "6:2860:1": "이다\n잊지 마라, 알겠나?",
    "6:2861:0": "공략을 맡아 주겠는가\n진심으로 감사하네",
    "6:2862:0": "그렇다면,", "6:2862:1": "을(를) 공격한다는 약조를\n반드시 지키도록 하시오",
    "6:2863:0": "공격의 밀약을\n반드시 지켜 주시기를",
    "6:2864:0": "공격하기로 한 약조를 잊지 마시오",
    "6:2865:0": "공격을 반드시 실행하라\n…알겠느냐",
    "6:2866:0": "을(를) 공격하기로 한 일은\n반드시 이루어 내시기를",
    "6:2867:0": "공격하기로 한 약속을\n잊어서는 아니 되오",
    "6:2868:0": "공략은 맡기겠습니다\n부디 잊지 말아 주세요",
    "6:2869:0": "을(를) 공격해 주겠는가\n참으로 든든하구나",
    "6:2870:0": "을(를) 공격해 주시는군요\n감사할 따름입니다",
    "6:2871:0": "을(를) 공격하기로 한 일에\n부디 어긋남이 없으시기를",
}

STATIC_COORDINATES = {"6:2861:0", "6:2863:0", "6:2864:0", "6:2865:0", "6:2867:0", "6:2868:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S157", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
