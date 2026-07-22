#!/usr/bin/env python3
"""Build Base authoring segment 247 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S247.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s247", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3949:0": "오오, 그러한가!\n천황께서 그대를",
    "6:3949:1": "에 임명하신다고 하네\n앞으로도 근왕의 뜻을 잊지 말게",
    "6:3950:0": "그래, 그래. 마련해 주겠는가!\n",
    "6:3950:1": "님의 뜻을 분명히 전하겠네\n훗날 임관될 수 있도록 주선하겠네",
    "6:3951:0": "그 가문은 인척이므로 오랜 동맹 관계를 맺고 있",
    "6:3951:2": "등의",
    "6:3951:3": "협력을 염두에 두고\n친선을 시작하",
    "6:3952:0": "양가의 동맹 관계를 바탕으로,\n",
    "6:3952:1": "등의",
    "6:3952:2": "협력을 받을 것을 염두에 두고\n친선을 시작하",
    "6:3953:0": "그 가문과는 과거에 힘을 합친 사이\n",
    "6:3953:1": "등의",
    "6:3953:2": "협력을 받을 것을 염두에 두고\n친선을 시작하",
    "6:3954:0": "이(가) 우리 가문과의",
    "6:3954:1": "개월간의 친선을 시작",
    "6:3955:0": "이(가) 우리 가문과의",
    "6:3955:1": "개월간의 친선을 시작",
    "6:3956:0": "이(가) 우리 가문과의",
    "6:3956:1": "개월간의 친선을 시작",
    "6:3957:0": "이(가) 제안한",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S247", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
