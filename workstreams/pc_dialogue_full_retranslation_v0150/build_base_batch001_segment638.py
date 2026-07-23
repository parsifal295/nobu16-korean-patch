#!/usr/bin/env python3
"""Build Base authoring segment 638 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S638.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s638", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1883:0": "이럴 수가……\n",
    "9:1883:1": "마저 패했단 말인가",
    "9:1884:0": "으음……\n기어이 일을 저질렀구나……!",
    "9:1885:0": "그럴 수가……!\n",
    "9:1885:1": "만 한 장수마저……",
    "9:1886:0": "놈들도 제법 하는군……",
    "9:1887:0": "배로 되갚아 줍시다",
    "9:1888:0": "이 무슨 일이란 말인가……",
    "9:1889:0": "해냈잖아!\n정말 굉장한 녀석이군!",
    "9:1890:0": "훌륭하다!\n그 공명이 천하에 울려 퍼지리라!",
    "9:1891:0": "장하도다!\n그 이름은 역사에 남으리라",
    "9:1892:0": "전공 제일은\n정해졌군요!",
    "9:1893:0": "오오!\n적장의 수급을 취했는가!",
    "9:1894:0": "후후…… 이제\n",
    "9:1894:1": "의 쇠퇴는 피할 수 없겠군",
    "9:1895:0": "혁혁한 전과로다\n참으로 경하할 일이로다",
    "9:1896:0": "의 무운은\n얼마나 대단한가!",
    "9:1897:0": "용케도\n해내셨습니다!",
    "9:1898:0": "이로써 승리는\n정해진 것이나 다름없다",
    "9:1899:0": "용케도\n해내셨습니다!",
    "9:1900:0": "이제 이긴 것이나 다름없다!\n그 공을 치하하노라",
    "9:1901:0": "강하구나!\n그런 놈을 이기다니",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1883:0",
    "9:1883:1",
    "9:1885:0",
    "9:1885:1",
    "9:1894:0",
    "9:1894:1",
    "9:1896:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S638", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
