#!/usr/bin/env python3
"""Build Base authoring segment 303 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S303.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s303", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4595:0": "대체 무엇을 내어 주시는 것",
    "6:4595:1": "인가…",
    "6:4596:0": "이 정도로는 아직 부족하",
    "6:4597:0": "조금만 더 주시면 충분합니다",
    "6:4598:0": "이 정도면 충분하겠지요",
    "6:4599:0": "이 정도 조건으로 응할 리가 없지",
    "6:4600:0": "…아니, 이 정도로는 아직 부족하군",
    "6:4601:0": "어쩔 수 없군. 이 정도라면 받아 주지",
    "6:4602:0": "이래서는 가신들 앞에 체면이 서지 않는다…",
    "6:4603:0": "조금만 더 고려해 줄 수 없겠는가",
    "6:4604:0": "이 조건으로 받아들이도록 하지",
    "6:4605:0": "께서는 무엇을 고민하고 계신",
    "6:4606:0": ", 비가 내리기 시작한 듯하",
    "6:4612:0": "누군가 눈치채기 전에 간단히 끝내고 싶군…",
    "6:4613:0": "이 위압감… 이분이 바로 「",
    "6:4613:1": "」의 당주…",
    "6:4614:0": "이것이 「",
    "6:4614:1": "」라 불리는 자의 위압감인가…",
    "6:4615:0": "음, 방금 그 소리는… 새의 날갯짓",
    "6:4615:1": "…",
}

STATIC_COORDINATES: set[str] = {
    "6:4597:0", "6:4598:0", "6:4599:0", "6:4600:0", "6:4601:0",
    "6:4602:0", "6:4603:0", "6:4604:0", "6:4612:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S303", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
