#!/usr/bin/env python3
"""Build Base authoring segment 224 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S224.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s224", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3684:1": "으로(로) 천거해 주시다니\n",
    "6:3685:0": "을(를)",
    "6:3685:1": "으로(로)\n천거해 주신 것은\n뜻밖의 기쁨",
    "6:3686:0": "으로(로) 천거해 주시다니\n더없는 영광",
    "6:3687:0": "을(를)",
    "6:3687:1": "으로(로)\n천거해 주시니\n감사의 말도",
    "6:3688:0": "을(를)",
    "6:3688:1": "으로(로)?\n더없는 영광",
    "6:3689:0": "와(과)의 동맹도 2개월이 채 남지 않",
    "6:3689:1": "\n동맹을 이어 갈지 끝낼지\n깊이 생각해 보시기 바랍니다",
    "6:3690:0": "와(과)의 동맹도 2개월이 채 남지 않",
    "6:3690:1": "\n동맹을 이어 갈지 끝낼지\n깊이 생각해 보시기 바랍니다",
    "6:3691:0": "와(과)의 동맹도 2개월이 채 남지 않",
    "6:3691:1": "\n동맹을 이어 갈지 끝낼지\n깊이 생각해 보시기 바랍니다",
    "6:3692:0": "와(과)의 동맹도 2개월이 채 남지 않",
    "6:3692:1": "\n동맹을 이어 갈지 끝낼지\n깊이 생각해 보시기 바랍니다",
    "6:3693:0": "와(과)의 동맹도 2개월이 채 남지 않",
    "6:3693:1": "\n동맹을 이어 갈지 끝낼지\n깊이 생각해 보시기 바랍니다",
    "6:3694:0": "와(과)의 동맹도 2개월이 채 남지 않",
    "6:3694:1": "\n동맹을 이어 갈지 끝낼지\n깊이 생각해 보시기 바랍니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S224", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
