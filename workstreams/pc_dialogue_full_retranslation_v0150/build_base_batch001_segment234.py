#!/usr/bin/env python3
"""Build Base authoring segment 234 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S234.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s234", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3794:3": "을(를) 확실히 맡",
    "6:3795:0": "이야기는 알겠",
    "6:3795:2": "의",
    "6:3795:3": "을(를) 확실히 맡",
    "6:3796:0": "이야기는 알겠",
    "6:3796:2": "의",
    "6:3796:3": "을(를) 확실히 맡",
    "6:3797:0": "자세한 사정은 알겠",
    "6:3797:2": "와(과) 귀 가문의 정전에 대해서는\n우리 가문이 책임지고 중재하",
    "6:3798:0": "혼인을 받아들여 주지\n이제부터 사이좋게 지내자고\n아무래도 한 가족이니까 말이야",
    "6:3799:0": "혼인 제의, 삼가 받겠소\n이제부터 오래도록 양가의 유대를 지켜 나가세",
    "6:3800:0": "혼인 제의를 받아들이지\n양가가 오래도록 교분을 이어 가세",
    "6:3801:0": "혼인 제의를 받아들이겠소\n이제부터는 인척으로서\n양가가 화목하게 난세를 헤쳐 나가세",
    "6:3802:0": "혼인 제의, 감사히 받겠소\n이 인연이 양가를 오래도록 이어 주기를",
    "6:3803:0": "혼인 제의를 받아들이지\n어쨌든 이제 걱정할 것 없겠군\n인척은 배신하는 법이 없으니…",
    "6:3804:0": "혼인 제의, 받아들이겠소\n이제부터 힘을 합쳐\n양가의 번영에 힘써 나가세",
    "6:3805:0": "혼인 제의, 받아들이겠소\n이제 우리는 인척지간\n서로 손을 맞잡고 나아갑시다",
    "6:3806:0": "혼인 제의를 받아들이겠습니다\n이제부터 우리는 한집안\n무슨 일이든 서로 도우며 나아갑시다",
    "6:3807:0": "혼인 제의를 받아들이지\n이제 우리는 한집안\n하나가 되어 난세를 헤쳐 나가세",
    "6:3808:0": "혼인 제의를 받아들이겠소\n이제 우리는 인척지간\n무슨 일이든 함께 힘써 나갑시다",
}

STATIC_COORDINATES: set[str] = {
    "6:3798:0",
    "6:3799:0",
    "6:3800:0",
    "6:3801:0",
    "6:3802:0",
    "6:3803:0",
    "6:3804:0",
    "6:3805:0",
    "6:3806:0",
    "6:3807:0",
    "6:3808:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S234", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
