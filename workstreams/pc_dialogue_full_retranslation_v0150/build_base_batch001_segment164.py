#!/usr/bin/env python3
"""Build Base authoring segment 164 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S164.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s164", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2955:0": "이만큼이면\n조정도 부탁을 들어주겠지!",
    "6:2956:0": "이만큼이면\n조정도 매몰차게 거절하지는 않겠지요",
    "6:2957:0": "이만큼 마련했으니\n조정도 기뻐하겠지",
    "6:2958:0": "이만큼이나 조달했습니다\n조정도 기뻐할 것입니다",
    "6:2959:0": "이만큼이면\n조정도 기꺼이 부탁을 들어주겠지",
    "6:2960:0": "에게서\n친선 요청이 왔습니다\n확인해 주십시오",
    "6:2961:0": "에게서\n종속을 요구하는 사자가 왔습니다\n확인해 주십시오",
    "6:2962:0": "에게서\n우리 가문에 신종하기를 청하는 사자가\n왔습니다. 확인해 주십시오",
    "6:2963:0": "에게서\n단교 통고가 왔습니다!",
    "6:2964:0": "에게서\n교섭 요청이 왔습니다\n확인해 주십시오",
    "6:2965:0": "에게서\n",
    "6:2965:1": "을(를) 떠나 주군을 바꾸길 청하는 사자가\n왔습니다. 확인해 주십시오",
    "6:2966:0": "부탁할 것이 있다\n이걸 받고 승낙해 다오!",
    "6:2967:0": "이,",
    "6:2967:1": "은(는) 청할 일이 있소이다\n무사의 정으로… 부디 들어주시오",
    "6:2968:0": "우리 가문의 부탁을 들어주시길 바라오\n이것이 마음에 드셨으면 좋겠소만…",
    "6:2969:0": "오늘은 상의드릴 일이 있어 찾아왔습니다\n부디 이것을 받고 응해 주시겠습니까?",
    "6:2970:0": "을(를) 믿고 찾아왔네\n내 부탁을 들어주게",
    "6:2971:0": "좋은 이야기가 있어 찾아왔소\n이 또한 양가의 발전을 위한 일이니…",
    "6:2972:0": "송백의 지조라 하지. 이럴 때\n지조가 굳건한",
}

STATIC_COORDINATES = {
    "6:2955:0", "6:2956:0", "6:2957:0", "6:2958:0", "6:2959:0",
    "6:2966:0", "6:2968:0", "6:2969:0", "6:2971:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S164", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
