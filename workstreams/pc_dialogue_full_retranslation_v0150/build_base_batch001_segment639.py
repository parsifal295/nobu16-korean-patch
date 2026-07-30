#!/usr/bin/env python3
"""Build Base authoring segment 639 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S639.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s639", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1902:0": "훌륭하다…… 강적을 베는 것은\n무사의 기쁨이로다",
    "9:1903:0": "마저 쓰러뜨리다니\n제법이군……",
    "9:1904:0": "라는 장수가\n아군이라 다행이군……",
    "9:1905:0": "그 강자를 쓰러뜨리다니……\n그 무운을 나누어 받고 싶구나!",
    "9:1906:0": "이로써 승리로 향하는 길이\n더욱 넓어졌구나……",
    "9:1907:0": "그 난적조차\n상대가 되지 않았는가",
    "9:1908:0": "그 맹장을 쓰러뜨리다니!\n가호로다, 가호로다!",
    "9:1909:0": "설마―",
    "9:1909:1": "마저\n쓰러뜨리다니……!",
    "9:1910:0": "훌륭하다!\n선수를 빼앗겼군……",
    "9:1911:0": "그 난적을\n쓰러뜨리다니……",
    "9:1912:0": "!?\n설마―",
    "9:1912:1": "마저!?",
    "9:1913:0": "을(를) 위해서였나……?\n……눈물 나게 하는군",
    "9:1914:0": "나의 원수를 용케도……!\n감사하오!",
    "9:1915:0": "에 얽힌 악연도\n끝났군…… 감사하오",
    "9:1916:0": "의 운명도\n여기서 다했군요……",
    "9:1917:0": "묵은 원한을 풀어 주셨으니\n깊이 감사드리오",
    "9:1918:0": "할 수만 있었다면 내 손으로\n쓰러뜨리고 싶었다만……",
    "9:1919:0": "덕분에\n묵은 원한도 풀렸습니다",
    "9:1920:0": "이제야 가슴속 응어리가 풀렸다고\n할 수 있겠구나!",
    "9:1921:0": "감사합니다!\n깊은 원한도 풀렸습니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1903:0",
    "9:1904:0",
    "9:1909:0",
    "9:1909:1",
    "9:1912:0",
    "9:1912:1",
    "9:1913:0",
    "9:1915:0",
    "9:1916:0",
    "9:1919:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S639", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
