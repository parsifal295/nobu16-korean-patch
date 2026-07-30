#!/usr/bin/env python3
"""Build Base authoring segment 182 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S182.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s182", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3202:0": "동맹 제의, 받아들이겠다\n당분간 벗으로 지내자\n그 뒤의 일은 그때 가서 보지",
    "6:3203:0": "동맹 제의, 받아들이겠습니다\n잠시 손을 잡고…\n그 뒤의 일은 훗날 다시…",
    "6:3204:0": "동맹 제의를 받아들이지\n당분간은 손을 잡도록 하세\n그 뒤의 일은 그때 가서 보세",
    "6:3205:0": "이제 당분간 우리는 맹우다!\n지난 원한은 서로 말끔히 털어 버리자고",
    "6:3206:0": "이제 당분간 우리는 맹우\n비 온 뒤에 땅이 굳는 법, 바로 이런 것이오",
    "6:3207:0": "우선 우리는 맹우일세\n적으로 돌리면 성가시나\n아군이 되면 든든한 법이지",
    "6:3208:0": "이제 당분간 우리는 맹우입니다\n묵은 원한은 우선 잊도록 하지요",
    "6:3209:0": "이제 당분간 우리는 맹우일세\n서로 지난 원한은 잊도록 하세",
    "6:3210:0": "이제 당분간 우리는 맹우가 되었소\n부디 뒤통수를 노리는 짓은 삼가시오",
    "6:3211:0": "이제 당분간 우리는 맹우요\n지난 일은 깨끗이 잊어 주시기 바라오",
    "6:3212:0": "이제 당분간은 우리도 맹우일세\n과거의 원한은 깨끗이 잊어 주게나",
    "6:3213:0": "이제 당분간은 서로 맹우입니다\n과거에 다투었던 일은 부디 잊어 주십시오",
    "6:3214:0": "이로써 우리는 맹우다\n묵은 원한을 잊고 맹약을 맺어 준 데\n감사한다",
    "6:3215:0": "흔쾌히 받아 주셨군요\n그 넓은 도량에 그저 감탄할 따름입니다",
    "6:3216:0": "이제부터 우리는 맹우일세\n지난 원한은 서로 깨끗이 잊도록 하세",
    "6:3217:0": "혼인을 받아들여 주지\n이제부터 사이좋게 지내자고\n아무래도 한 가족이니까 말이야",
    "6:3218:0": "혼인 제의, 삼가 받겠소\n이제부터 오래도록 양가의 유대를 지켜 나가세",
    "6:3219:0": "혼인 제의를 받아들이지\n양가가 오래도록 교분을 이어 가세",
    "6:3220:0": "혼인 제의를 받아들이겠소\n이제부터는 인척으로서\n양가가 화목하게 난세를 헤쳐 나가세",
    "6:3221:0": "혼인 제의, 감사히 받겠소\n이 인연이 양가를 오래도록 이어 주기를",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S182", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
