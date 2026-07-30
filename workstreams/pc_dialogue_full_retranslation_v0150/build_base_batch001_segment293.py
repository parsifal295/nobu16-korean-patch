#!/usr/bin/env python3
"""Build Base authoring segment 293 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S293.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s293", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4409:0": "공성의 요체를 잘 알고",
    "6:4409:2": "에",
    "6:4409:3": "을(를) 배속해도\n손해 볼 일은 없을 듯하",
    "6:4410:0": "당장 전투가 벌어질 성이 아니므로\n",
    "6:4410:1": "에게 맡겨 정무를 충실히 한다…\n그 의도는 이해하",
    "6:4410:2": "만…",
    "6:4411:0": "이런 후방의 땅이야말로\n제가 바라던 곳…부디",
    "6:4411:1": "에게 그 땅을 맡기고\n정무에 이바지하도록 명해 주",
    "6:4412:0": "싸움터에서 다소 먼 땅이니\n그야말로 제 정무 솜씨를 펼칠 곳\n기꺼이 배속을 받",
    "6:4413:0": "그 성에는",
    "6:4413:1": "와(과) 같은 특성을\n지닌 이가 있어, 그 점은 강점입니다\n다만 인선은 재고해 주시길 바라",
    "6:4414:0": "부디 배속을 명해 주",
    "6:4414:2": "와(과) 같은 특성을 지닌 이가\n그 성에 있으니, 도움이 되",
    "6:4415:0": "그 땅이 속한 「",
    "6:4415:1": "」에는\n",
    "6:4415:2": "와(과) 같은 특성을 지닌 이가 있으니…\n좋은 성과를 낼 수 있을 듯",
    "6:4416:0": "같은 특성을 지닌 동료가\n성 영내에 있는 듯",
    "6:4416:1": "\n제 강점을 발휘할 수 있을 듯합니다",
    "6:4417:0": "제 특성은 전선에서야말로 빛납니다…\n하지만 가능하다면 「",
    "6:4417:1": "」에 부임하라는 명만은\n",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S293", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
