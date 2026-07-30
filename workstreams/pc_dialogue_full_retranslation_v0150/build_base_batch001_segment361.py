#!/usr/bin/env python3
"""Build Base authoring segment 361 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S361.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s361", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:889:2": "」을(를) 노리고 있",
    "7:890:0": "이(가) 병력 「",
    "7:890:1": "」을(를) 이끌고\n우리 세력의 「",
    "7:890:2": "」을(를) 노리고 있",
    "7:891:0": "여기서는 배수진을 칠 각오로\n맞섭시다",
    "7:892:0": "여기서는 배수진을 칠 각오로\n맞섭시다",
    "7:893:0": "여기서는 배수진을 칠 각오로\n맞섭시다",
    "7:894:0": "여기서는 배수진을 칠 각오로\n맞섭시다",
    "7:895:0": "여기서는 배수진을 칠 각오로\n맞섭시다",
    "7:896:0": "여기서는 배수진을 칠 각오로\n맞섭시다",
    "7:897:0": "여기서는 배수진을 칠 각오로\n맞섭시다",
    "7:898:0": "이(가) 「",
    "7:898:1": "」으로(로) 진군을 개시했습니다",
    "7:899:0": "이 승리는 새로운 시대를 부르는 바람이로다!",
    "7:900:0": "이 바람이 낡은 질서를 모조리 집어삼키리라!",
    "7:901:0": "내 이름을 천하에 떨치겠노라!",
    "7:902:0": "이 바람이 새로운 시대를 이끌리라!",
    "7:903:0": "바람이여, 하늘을 가르며 내 이름을 전하라!",
    "7:904:0": "이 승리가 누구의 것인지 바람에게 물어라!",
    "7:905:0": "바람처럼 빠르게 승리를 전하라!",
}

STATIC_COORDINATES: set[str] = {
    "7:891:0",
    "7:892:0",
    "7:893:0",
    "7:894:0",
    "7:895:0",
    "7:896:0",
    "7:897:0",
    "7:899:0",
    "7:900:0",
    "7:901:0",
    "7:902:0",
    "7:903:0",
    "7:904:0",
    "7:905:0",
}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S361", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
