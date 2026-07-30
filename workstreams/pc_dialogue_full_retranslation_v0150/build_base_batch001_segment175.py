#!/usr/bin/env python3
"""Build Base authoring segment 175 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S175.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s175", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3086:1": "\n이제부터는 종속이 아닌 대등한 동맹을 맺어\n서로 도우",
    "6:3087:0": "귀군은 충분한 힘을 길렀으니",
    "6:3087:1": "\n이제부터는 종속이 아닌 대등한 동맹을 맺어\n서로 도우",
    "6:3088:0": "귀군은 충분한 힘을 얻었으니",
    "6:3088:1": "\n이제부터는 종속이 아닌 대등한 동맹을 맺어\n서로 도우",
    "6:3089:0": "귀군은 충분한 힘을 얻었으니",
    "6:3089:1": "\n이제부터는 종속이 아닌 대등한 동맹을 맺어\n서로 도우",
    "6:3090:0": "귀군은 충분한 힘을 얻었으니",
    "6:3090:1": "\n이제부터는 종속이 아닌 대등한 동맹을 맺어\n서로 도우",
    "6:3091:0": "귀군은 충분한 힘을 얻었으니",
    "6:3091:1": "\n이제부터는 종속이 아닌 대등한 동맹을 맺어\n서로 도우",
    "6:3092:0": "귀군은 충분한 힘을 얻었으니",
    "6:3092:1": "\n이제부터는 종속이 아닌 대등한 동맹을 맺어\n서로 도우",
    "6:3093:0": "전봉할 성을 선택하십시오",
    "6:3094:0": "전봉 방식을 선택하십시오",
    "6:3095:0": "이동시킬 무장을 선택하십시오",
    "6:3096:0": "다른 한쪽 성을 선택하십시오",
    "6:3097:0": "두 성 사이에서 이동시킬 무장을 선택하십시오",
    "6:3098:0": "성주에게 지행으로 줄 군의 수를 정하십시오",
    "6:3099:0": "으로(로) 이동합니다",
}

STATIC_COORDINATES: set[str] = {
    "6:3093:0",
    "6:3094:0",
    "6:3095:0",
    "6:3096:0",
    "6:3097:0",
    "6:3098:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S175", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
