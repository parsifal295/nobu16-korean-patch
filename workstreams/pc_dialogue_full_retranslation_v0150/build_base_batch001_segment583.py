#!/usr/bin/env python3
"""Build Base authoring segment 583 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S583.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s583", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:711:0": "각오는……\n하고 있었노라……",
    "9:712:0": "이런 곳에서……\n죽는다고……!?",
    "9:713:0": "스러질……때는……\n우아하게……",
    "9:714:0": "전장에서……죽는가……",
    "9:715:0": "……\n여기서 죽는 거구나……",
    "9:716:0": "전장에서 죽는 것이다……\n후회는 없다……",
    "9:717:0": "뒷일은……맡기겠습니다……",
    "9:718:0": "가문의 앞날이……\n마음에 걸리는구나……",
    "9:719:0": "삶든 굽든\n마음대로 해라!",
    "9:720:0": "살아서 치욕을 겪다니……\n원통하구나",
    "9:721:0": "베어라\n각오는 되어 있느니라",
    "9:722:0": "포로 신세로\n전락하다니……",
    "9:723:0": "에잇!\n놓아라, 어서 놓아라!",
    "9:724:0": "사로잡히다니……\n나도 영락했구나",
    "9:725:0": "포로라 해도 장수다……\n함부로 다루는 것은 용납 못 한다",
    "9:726:0": "여기까지로군……\n얌전히 포박에 응하겠다",
    "9:727:0": "손대지 마세요\n제 발로 걸을 수 있습니다……",
    "9:728:0": "마음대로 하라……\n저항하지 않겠다……",
    "9:729:0": "포박의 치욕을\n당하다니……",
    "9:730:0": "이제 틀렸구나……",
    "9:731:0": "명예로운 전상이잖아\n물러나 치료나 받아!",
    "9:732:0": "어서 물러나 치료를 받아라!",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS) - {"9:715:0"}


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
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S583", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
