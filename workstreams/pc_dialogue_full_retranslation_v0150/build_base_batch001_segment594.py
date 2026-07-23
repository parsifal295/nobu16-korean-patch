#!/usr/bin/env python3
"""Build Base authoring segment 594 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S594.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s594", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:945:0": "자, 거짓 정보에 놀아나라……!",
    "9:946:0": "거짓 정보로\n적을 물러나게 하겠습니다",
    "9:947:0": "거짓 정보로다……\n자, 어떻게 나올 테냐?",
    "9:948:0": "거짓 정보를 흘려\n주었습니다!",
    "9:949:0": "거짓 정보에\n속아 넘어가다니!",
    "9:950:0": "큰 소동이 벌어질 겁니다",
    "9:951:0": "거짓 정보를\n흘려 주었소이다!",
    "9:952:0": "윽!\n간파해 버리다니!",
    "9:953:0": "거짓 정보가……\n간파당했는가……!",
    "9:954:0": "거짓 정보를 간파하다니……\n재미있군",
    "9:955:0": "적진에도 지혜로운 자가\n있군요",
    "9:956:0": "흥, 빈틈없는 적이로구나",
    "9:957:0": "내 거짓 정보가 통하지\n않는다고!?",
    "9:958:0": "속임수에 기대서는\n안 되었던 걸까요",
    "9:959:0": "으음…… 물러나\n주길 바랐건만……",
    "9:960:0": "거짓 정보는 실패입니다……",
    "9:961:0": "그리 쉽게는\n되지 않는가……",
    "9:962:0": "적도 영리한 듯하군요……",
    "9:963:0": "으으음……\n거짓 정보에 휘둘리지 않다니",
    "9:964:0": "마음대로 하게 두진 않겠다!",
    "9:965:0": "힘을 발휘하게 두지 않겠다!",
    "9:966:0": "조용히 해 주겠나?",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S594", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
