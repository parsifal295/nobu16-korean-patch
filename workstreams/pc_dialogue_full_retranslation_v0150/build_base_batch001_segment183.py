#!/usr/bin/env python3
"""Build Base authoring segment 183 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S183.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s183", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3222:0": "혼인 제의를 받아들이지\n어쨌든 이제 걱정할 것 없겠군\n인척은 배신하는 법이 없으니…",
    "6:3223:0": "혼인 제의, 받아들이겠소\n이제부터 힘을 합쳐\n양가의 번영에 힘써 나가세",
    "6:3224:0": "혼인 제의, 받아들이겠소\n이제 우리는 인척지간\n서로 손을 맞잡고 나아갑시다",
    "6:3225:0": "혼인 제의를 받아들이겠습니다\n이제부터 우리는 한집안\n무슨 일이든 서로 도우며 나아갑시다",
    "6:3226:0": "혼인 제의를 받아들이지\n이제 우리는 한집안\n하나가 되어 난세를 헤쳐 나가세",
    "6:3227:0": "혼인 제의를 받아들이겠소\n이제 우리는 인척지간\n무슨 일이든 함께 힘써 나갑시다",
    "6:3228:0": "혼인 제의를 받아들이지\n이제 우리는 인척이 되었군\n오래도록 좋은 교분을 이어 가세",
    "6:3229:0": "이제 우리도 인척인가!\n앞으로도 줄곧 사이좋게 지내고 싶군!",
    "6:3230:0": "이로써 우리는 친족이 되었군\n오래도록 좋은 관계를 이어 가고 싶네",
    "6:3231:0": "혼례가 성사되어 참으로 경사스럽구나!\n이 인연은 오래도록 이어질 것이 분명하다",
    "6:3232:0": "이제 우리는 친척…이군요\n오래도록 좋은 관계를 이어 가지요",
    "6:3233:0": "이로써 우리는 친척이 되었군\n오래도록 좋은 관계가 이어지길 바랄 뿐이네",
    "6:3234:0": "이로써 우리는 친척이 되었구나…\n죽는 날까지 좋은 관계를 이어 가세",
    "6:3235:0": "이로써 양가는 하나가 되었소\n앞으로도 오래도록 잘 부탁하오",
    "6:3236:0": "이로써 우리도 인척일세\n오래도록 좋은 관계를 이어 가세",
    "6:3237:0": "이제 우리는 친척이군요\n힘을 합쳐 난세를 헤쳐 나갑시다",
    "6:3238:0": "이로써 우리는 인척지간\n앞으로도 오래도록 잘 부탁하네",
    "6:3239:0": "이로써 우리는 친척지간\n앞으로도 오래도록\n잘 부탁드리겠습니다",
    "6:3240:0": "이로써 우리는 인척지간\n오래도록 좋은 관계를 이어 가세",
    "6:3241:0": "뭐라고, 우리와 단교하겠다고!",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S183", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
