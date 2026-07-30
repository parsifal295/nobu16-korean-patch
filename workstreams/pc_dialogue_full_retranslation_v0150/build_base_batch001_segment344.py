#!/usr/bin/env python3
"""Build Base authoring segment 344 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S344.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s344", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:722:0": "을(를) 손에 넣었습니다",
    "7:723:0": "모두의 활약으로 「",
    "7:723:1": "」을(를) 제압할 수 있었습니다",
    "7:724:0": "은(는) 우리 것이다!",
    "7:725:0": "을(를) 함락시켰다!",
    "7:726:0": "이(가)\n",
    "7:726:1": "을(를) 함락시키",
    "7:726:2": "!",
    "7:727:0": "한낱 꿈이었구나…",
    "7:728:0": "여기까지라니…\n참으로 분하구나…",
    "7:729:0": "내 대망도 여기까지인가…",
    "7:730:0": "다케다의 이름도 땅에 떨어졌구나…",
    "7:731:0": "원통하구나…",
    "7:732:0": "모리의 이름을 남기지 못했구나",
    "7:733:0": "내 야망도 여기까지로구나…",
    "7:734:0": "물거품 같은 꿈이었던가…",
    "7:735:0": "제기랄, 여기까지란 말이냐!",
    "7:736:0": "내 무용이 미치지 못했구나…",
    "7:737:0": "성자필쇠라, 여기까지인가…",
    "7:738:0": "참으로 원통합니다…",
}

STATIC_COORDINATES: set[str] = {
    "7:727:0",
    "7:728:0",
    "7:729:0",
    "7:730:0",
    "7:731:0",
    "7:732:0",
    "7:733:0",
    "7:734:0",
    "7:735:0",
    "7:736:0",
    "7:737:0",
    "7:738:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S344", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
