#!/usr/bin/env python3
"""Build Base authoring segment 295 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S295.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s295", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4428:0": "성에 있는 이들의 사기를 높이는 일은\n분명 제 장기입니다만…\n",
    "6:4428:1": "에 부임하라는 명만은,",
    "6:4428:2": "면해 주십시오…",
    "6:4429:0": "이 일은 부디",
    "6:4429:1": "에게",
    "6:4429:2": "맡겨 주십시오\n성에 있는 이들의 사기를 높여\n전력을 크게 끌어올리",
    "6:4430:0": "사람들의 화합을 지키는 일에는\n",
    "6:4430:1": "은(는) 다소 자신이 있습니다…\n모두의 힘을 끌어올려 보이",
    "6:4431:0": "성주 「",
    "6:4431:1": "」님과는\n분명 마음이 잘 맞",
    "6:4431:2": "만…",
    "6:4432:0": "을(를) 배속해 주",
    "6:4432:1": "\n성주 「",
    "6:4432:2": "」님과 함께라면\n잘 지낼 자신이 있",
    "6:4433:0": "성주 「",
    "6:4433:1": "」님과는\n어쩐지 마음이 잘 맞",
    "6:4433:2": "\n꼭 함께 일하고 싶",
    "6:4434:0": "전선의 땅이야말로 제가 바라던 곳입니다\n…하지만 「",
    "6:4434:1": "」에서는 그 솜씨를\n충분히 발휘할 수 있",
    "6:4434:2": "…",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S295", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
