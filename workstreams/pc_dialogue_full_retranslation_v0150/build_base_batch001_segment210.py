#!/usr/bin/env python3
"""Build Base authoring segment 210 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S210.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s210", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3538:1": "의 마음을 헤아려 충의를 다했을 뿐\n치하받을 만한 일은 하지 않",
    "6:3539:0": "더없이 감사할 따름이옵니다\n",
    "6:3539:1": "의 지위에 있으면서도 훈공 1위조차 차지하지 못한다면\n그 지위를 훔친 것이나 다름없사옵니다",
    "6:3540:0": "훈공 1위라니 쑥스럽구려\n이 정도는 늘 해 오던 일",
    "6:3540:2": "도 잘 아실 터",
    "6:3540:3": "인데",
    "6:3541:0": "라 하",
    "6:3541:1": "나\n",
    "6:3541:2": "은(는) 아직 한창 젊으니 말이오\n훈공 1위는 다른 자에게 넘",
    "6:3541:3": "!",
    "6:3542:0": "에잇, 아랫것들이 해이해졌구나!\n",
    "6:3542:1": "님께 훈공 1위를 내주다니 어쩔 셈이냐!\n더 악착같이 공을 세우지 못하겠느냐!",
    "6:3543:0": "좋아!",
    "6:3543:1": "의 체면은 세웠",
    "6:3543:2": "요\n…",
    "6:3543:3": "라 하면 나이가 든 것 같아서\n그리 기분이 좋",
    "6:3543:4": "만…",
    "6:3544:0": "으로(로)서 훈공 1위…\n최고의 영예라 할 수 있",
    "6:3544:1": "\n앞으로도 늘 이 자리를 지키고 싶",
    "6:3544:2": "!",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S210", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
