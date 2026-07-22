#!/usr/bin/env python3
"""Build Base authoring segment 250 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S250.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s250", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3983:0": "적군의 압도적인 위신에 병사들이\n위축된 모양이다. 병력이 앞선다 해도\n이래서는 제 실력을 발휘할 수 있을지…",
    "6:3984:0": "적군의 압도적인 위신에 병사들이\n위축된 모양이다. 병력이 앞선다 해도\n이래서는 제 실력을 발휘할 수 있을지…",
    "6:3985:0": "적군의 압도적인 위신에 병사들이\n위축된 모양이다. 병력이 앞선다 해도\n이래서는 제 실력을 발휘할 수 있을지…",
    "6:3986:0": "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n승패가 좌우될 것이다",
    "6:3987:0": "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n승패가 좌우될 것이다",
    "6:3988:0": "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n승패가 좌우될 것이다",
    "6:3989:0": "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n승패가 좌우될 것이다",
    "6:3990:0": "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n승패가 좌우될 것이다",
    "6:3991:0": "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n승패가 좌우될 것이다",
    "6:3992:0": "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n승패가 좌우될 것이다",
    "6:3993:0": "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n승패가 좌우될 것이다",
    "6:3994:0": "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n승패가 좌우될 것이다",
    "6:3995:0": "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n승패가 좌우될 것이다",
    "6:3996:0": "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n승패가 좌우될 것이다",
    "6:3997:0": "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n승패가 좌우될 것이다",
    "6:3998:0": "공략에는 그만한 각오가 필요할 듯합니다.\n병력이 충분치 않으니 조략도 활용하면서\n만반의 준비를",
    "6:3998:1": "…",
    "6:3999:0": "공략에는 그만한 각오가 필요할 듯합니다.\n병력이 충분치 않으니 조략도 활용하면서\n만반의 준비를",
    "6:3999:1": "…",
    "6:4000:0": "공략에는 그만한 각오가 필요할 듯합니다.\n병력이 충분치 않으니 조략도 활용하면서\n만반의 준비를",
}

STATIC_COORDINATES: set[str] = {f"6:{record_id}:0" for record_id in range(3983, 3986)}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S250", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
