#!/usr/bin/env python3
"""Build Base authoring segment 538 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S538.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s538", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:873:0": "이 땅을 맡은 지도 제",
    "8:873:1": "년,\n여러 가지 일이 있었습니다…",
    "8:874:0": "다스린 지도 벌써 제",
    "8:874:1": "년이로군\n마을 사람들과도 모두 안면을 텄지",
    "8:875:0": "년이나 지나니\n마을 모습도 몰라보게 달라졌습니다",
    "8:876:0": "부임한 지도 제",
    "8:876:1": "년,\n성과가 나타나고 있을 터",
    "8:877:0": "년이나 지내다 보니\n애착이 생기네요",
    "8:878:0": "어느덧 제",
    "8:878:1": "년…\n세월은 쏜살같군요",
    "8:879:0": "년이나 다스렸다니\n나도 제법 해냈구먼!",
    "8:880:0": "년을 앞만 보고 내달렸지\n돌이켜 보면 한순간이야…",
    "8:881:0": "마침내 제",
    "8:881:1": "년인가…\n기나긴 여정이었구나",
    "8:882:0": "년이나 다스리다니…\n제 자신이 자랑스럽습니다",
    "8:883:0": "년을 끝까지 지켜 냈나…\n이 나날이 오래 이어지기를",
    "8:884:0": "이곳에서도 어느덧 제",
    "8:884:1": "년인가… 훗\n감상에 젖다니 나답지 않군",
    "8:885:0": "어느덧 이곳에서 제",
    "8:885:1": "번째로\n꽃을 보았군요",
    "8:886:0": "이곳을 다스린 지도 제",
    "8:886:1": "년,\n마을 사람들은 자식이나 손주나 다름없지",
    "8:887:0": "년이나 지났습니까\n참으로 좋은 곳이군요",
    "8:888:0": "년 동안 이곳을 다스려 냈다\n조금은 자랑스러워해도 되겠지",
}

STATIC_COORDINATES: set[str] = set()


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S538", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
