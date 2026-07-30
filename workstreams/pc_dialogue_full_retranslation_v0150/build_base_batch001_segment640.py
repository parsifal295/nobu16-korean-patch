#!/usr/bin/env python3
"""Build Base authoring segment 640 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S640.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s640", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1922:0": "내 손으로 쓰러뜨리고 싶었다만……\n그래도 감사하다는 말은 해 두지",
    "9:1923:0": "쓰러뜨려 주셨으니\n감사드립니다",
    "9:1924:0": "그 가증스러운 놈을\n쓰러뜨려 주셨습니까",
    "9:1925:0": "도움이 된 것 같아 기쁘군!",
    "9:1926:0": "지원한 보람이 있었군요!",
    "9:1927:0": "미력하나마 힘을 다했소",
    "9:1928:0": "조금이나마 도움이 되었을까요",
    "9:1929:0": "지원한 보람이 있었군요!",
    "9:1930:0": "지원한 보람이 있었군요!",
    "9:1931:0": "지원한 보람이 있었군요!",
    "9:1932:0": "지원한 보람이 있었군요!",
    "9:1933:0": "도움이 되었다니 다행입니다!",
    "9:1934:0": "조금은 도움이 되었군!",
    "9:1935:0": "함께할 수 있어 다행이었습니다!",
    "9:1936:0": "이번에 함께 싸운 일은 마음에 새겨 두겠소",
    "9:1937:0": "기분 좋게\n서로 겨룬 싸움이었어!",
    "9:1938:0": "훌륭한 수급이로다!\n빛나는 전공이로다!",
    "9:1939:0": "참으로 장한 전공이로다",
    "9:1940:0": "이번 전과는\n크군요",
    "9:1941:0": "의 무예가 어느 정도인지\n잘 보았다!",
    "9:1942:0": "모두 그 무공의 기세를\n이어받아라!",
    "9:1943:0": "의 활약에\n깊이 감사하노라",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1941:0",
    "9:1943:0",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S640", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
