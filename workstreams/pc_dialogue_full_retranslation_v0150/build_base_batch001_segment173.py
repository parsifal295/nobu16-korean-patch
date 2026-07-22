#!/usr/bin/env python3
"""Build Base authoring segment 173 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S173.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s173", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3072:0": "참으로 유감스럽게도",
    "6:3072:1": "이(가) 우리 가문을\n떠나셨으므로,",
    "6:3072:2": "와(과)의 동맹도\n앞으로",
    "6:3072:3": "개월만 남았사옵니다",
    "6:3073:0": "이(가) 우리 가문을 떠나, 인척이었던\n",
    "6:3073:1": "와(과)의 동맹은",
    "6:3073:2": "개월 후면\n효력을 잃게 되었사옵니다",
    "6:3074:0": "이(가) 우리 가문을 떠나, 혼인 관계에\n있던",
    "6:3074:1": "와(과)의 동맹도\n이제",
    "6:3074:2": "개월밖에 남지 않았사옵니다",
    "6:3075:0": "뿐만 아니라",
    "6:3075:1": "와(과)의\n혼인 동맹도 앞으로",
    "6:3075:2": "개월 후면\n끝나므로, 손을 쓰려면 지금뿐이옵니다",
    "6:3076:0": "을(를) 잃은 것뿐 아니라, 이제\n",
    "6:3076:1": "와(과)의 동맹도",
    "6:3076:2": "개월 후면\n끝나 버리는 것도 큰 타격이옵니다",
    "6:3077:0": "을(를) 잃은 것도 뼈아프거늘, 그뿐 아니라\n",
    "6:3077:1": "와(과)의 인척 관계도 끊어져\n",
    "6:3077:2": "개월 후에는 동맹마저 끝나니 상황이 심각합니다",
    "6:3078:0": "으음,",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S173", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
