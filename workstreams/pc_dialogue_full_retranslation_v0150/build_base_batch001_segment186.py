#!/usr/bin/env python3
"""Build Base authoring segment 186 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S186.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s186", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3268:0": "알겠습니다\n",
    "6:3268:1": "은(는) 우리 가문의 병력으로 지키겠습니다",
    "6:3269:0": "잘 알겠소\n",
    "6:3269:1": "은(는) 우리가 지켜 주겠소",
    "6:3270:0": "이 또한 귀 가문을 위한 일이오\n",
    "6:3270:1": "으로(로) 병력을 보내 드리겠소",
    "6:3271:0": "귀 가문의 부탁이라면 거절할 수 없지\n",
    "6:3271:1": "의 수비를 맡아 주지",
    "6:3272:0": "여기서 빚 하나를 지워 두는 것도 좋겠군…\n",
    "6:3272:1": "은(는) 우리가 지켜 주마",
    "6:3273:0": "어려울 때일수록 서로 도와야지요…\n",
    "6:3273:1": "을(를) 지키러 가겠습니다",
    "6:3274:0": "잘 알겠소\n",
    "6:3274:1": "은(는) 우리가 지키겠소",
    "6:3275:0": "알겠습니다\n",
    "6:3275:1": "은(는) 우리가 지키겠습니다",
    "6:3276:0": "잘 알겠소\n",
    "6:3276:1": "은(는) 우리 병력으로 반드시 지켜 내겠소",
    "6:3277:0": "은(는) 맡겼다!\n부탁한다!",
    "6:3278:0": "의 공략을 맡아 주겠는가\n기대하고 있겠네",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S186", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
