#!/usr/bin/env python3
"""Build Base authoring segment 423 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S423.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s423", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1897:0": "목표 부대는 이미 사라졌다\n진을 거두고 입성하라",
    "7:1898:0": "목표는 더는 없다\n귀성하도록 하지",
    "7:1899:0": "목표는 더는 없구나\n자, 군을 거두자꾸나",
    "7:1900:0": "목표는 달성했는가\n입성하도록 하지",
    "7:1901:0": "목표 부대는 더는 없군\n슬슬 돌아가자고!",
    "7:1902:0": "목표는 더는 없다\n모두 철수하라!",
    "7:1903:0": "이제 목표는 없다\n귀성한다!",
    "7:1904:0": "목표는 이미 자취를 감췄습니다\n자, 병사를 물릴까요",
    "7:1905:0": "목표는 더는 없느니라\n성으로 돌아간다",
    "7:1906:0": "목표가 더는 없다면\n귀성하는 것이 좋겠구나",
    "7:1907:0": "이제 목표는 없다\n돌아가도록 하지",
    "7:1908:0": "이제 목표는 없구나\n돌아가도 좋으리라",
    "7:1909:0": "목표는 더는 없군요\n지금 돌아가겠습니다",
    "7:1910:0": "목표 부대는 더는 없다\n귀로에 오른다",
    "7:1911:0": "목표는 더는 없군요\n돌아가도록 하지요",
    "7:1912:0": "목표 부대는 없다\n이제 돌아가도 되겠는가",
    "7:1913:0": "적 영지를 지나는 것은 위험하다\n",
    "7:1913:1": "으로 돌아가자",
    "7:1914:0": "자—",
    "7:1914:1": "의\n공략을 계속할까",
}

STATIC_COORDINATES: set[str] = {
    "7:1897:0", "7:1898:0", "7:1899:0", "7:1900:0", "7:1901:0", "7:1902:0",
    "7:1903:0", "7:1904:0", "7:1905:0", "7:1906:0", "7:1907:0", "7:1908:0",
    "7:1909:0", "7:1910:0", "7:1911:0", "7:1912:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S423", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
