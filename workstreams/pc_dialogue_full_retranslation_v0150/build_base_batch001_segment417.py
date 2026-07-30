#!/usr/bin/env python3
"""Build Base authoring segment 417 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S417.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s417", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1795:0": "은(는) 함락되었다\n이제 귀성할까",
    "7:1796:0": "자—",
    "7:1796:1": "은(는) 차지했다\n귀성할까",
    "7:1797:0": "의 공략 완료\n자, 귀성하세",
    "7:1798:0": "은(는) 우리 손안에……\n귀성하자꾸나",
    "7:1799:0": "을(를) 빼앗았도다!\n귀성한다!",
    "7:1800:0": "은(는) 공략했노라\n그럼 귀성한다",
    "7:1801:0": "을(를) 빼앗았다\n귀성하자고",
    "7:1802:0": "을(를) 함락했다\n귀성한다!",
    "7:1803:0": "은(는) 수중에 있다\n귀성하라",
    "7:1804:0": "의 공략을 마쳤습니다\n귀성하겠습니다",
    "7:1805:0": "을(를) 점령했다!\n그럼 귀성한다",
    "7:1806:0": "을(를) 평정했다\n귀성할까",
    "7:1807:0": "을(를) 함락했다\n귀성하자",
    "7:1808:0": "의 공략은 끝났다\n귀성할까",
    "7:1809:0": "의 공략을 마쳤습니다\n귀성하겠습니다",
    "7:1810:0": "을(를) 공략했다\n귀성한다",
    "7:1811:0": "은(는) 함락되었다\n귀성합니다",
    "7:1812:0": "을(를) 함락했다\n귀성한다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S417", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
