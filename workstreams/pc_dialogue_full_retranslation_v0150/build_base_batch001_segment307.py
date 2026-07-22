#!/usr/bin/env python3
"""Build Base authoring segment 307 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S307.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s307", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:142:0": "우리 땅을 넘본 것을\n후회하게 해 주지요",
    "7:143:0": "우리 땅이 짓밟히기 전에\n적군을 밀어냅시다",
    "7:144:0": "백성을 생각한다면,\n선수를 쳐야 합니다",
    "7:145:0": "영지가 유린당하게 두는 것은 하책,\n먼저 적을 쳐서 물리쳐야 한다",
    "7:146:0": "서둘러 적을 토벌합시다.\n한 치의 땅도 내주지 않겠소",
    "7:147:0": "의 협력을 얻는다면\n전투에서 우위를 점할 수 있을 것입니다",
    "7:148:0": "성을 공격하기에 앞서 먼저\n",
    "7:148:1": "의 협력을 얻어야 합니다",
    "7:149:0": "의 협력을 얻으면\n성 공략도 수월해질 것입니다",
    "7:150:0": "의 협력을 얻은 뒤,\n싸우는 것이 좋겠습니다",
    "7:151:0": "공성에 「",
    "7:151:1": "」의 힘이\n보태진다면 백 명의 힘을 얻는 셈입니다",
    "7:152:0": "의 힘이야말로\n공성에 필요할 것입니다",
    "7:153:0": "의 힘이야말로\n우리 가문의 앞날에 긴요합니다",
    "7:154:0": "지금 해야 할 일은 「",
    "7:154:1": "」의 복종을 받아 내는\n것입니다",
    "7:155:0": "의 복종을 받아 낸다면\n우리에게 이익이 될 것입니다",
    "7:156:0": "의 협력을 얻는다면\n우리 가문에 큰 도움이 될 것입니다",
    "7:157:0": "의 협력을 얻는다면\n우리 가문의 위세도 커질 것입니다",
    "7:158:0": "저 「",
}

STATIC_COORDINATES: set[str] = {
    "7:142:0", "7:143:0", "7:144:0", "7:145:0", "7:146:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S307", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
