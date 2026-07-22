#!/usr/bin/env python3
"""Build Base authoring segment 332 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S332.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s332", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:566:0": "더는 「",
    "7:566:1": "」에 힘을 보탤\n이유가 없습니다. 철수합시다",
    "7:567:0": "이제 「",
    "7:567:1": "」의 편을 들 수는 없겠소\n그렇다면, 무운을 빌겠소",
    "7:568:0": "와(과) 맺은 인연도 여기까지인 듯하구먼……\n이제 철수하도록 하지",
    "7:569:0": "와(과)는 싸울 수 없소……\n미안하지만 우리는 여기서 철수하겠소",
    "7:570:0": "의 부탁이라 해도 「",
    "7:570:1": "」와(과)는 싸울 수 없겠군!\n이쯤에서 작별이다, 잘 있으라고!",
    "7:571:0": "을(를) 위해서라도 「",
    "7:571:1": "」와(과)는\n싸울 수 없다. 철수한다!",
    "7:572:0": "아무래도 도울 수 있는 건 여기까지인 듯하다\n",
    "7:572:1": "와(과)는 싸울 수 없다. 모두, 퇴각한다!",
    "7:573:0": "이제 여기까지다……\n",
    "7:573:1": "와(과)는 싸울 수 없다. 철수한다!",
    "7:574:0": "미안하지만 너희를 위해\n",
    "7:574:1": "와(과)는 싸울 수 없겠군. 얘들아, 물러난다!",
    "7:575:0": "의 적에게 힘을 보탤\n이유가 없습니다. 철수합시다",
    "7:576:0": "의 적이라면 「",
    "7:576:1": "」의 편을 들 수는 없겠소\n그렇다면, 무운을 빌겠소",
    "7:577:0": "에 맞서는 것은 하책이로군\n철수하도록 하지",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S332", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
