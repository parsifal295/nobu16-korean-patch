#!/usr/bin/env python3
"""Build Base authoring segment 657 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S657.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s657", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2256:0": "대혼란이로다……",
    "9:2256:1": "\n제법 골치 아프게 하는구나……!",
    "9:2257:0": "……!\n우리 병사들마저 현혹하는가……",
    "9:2258:0": "도무지 통제가 되지 않는군……\n이것이―",
    "9:2258:1": "……",
    "9:2259:0": "에잇……",
    "9:2259:1": "에\n완전히 농락당하고 말았구나",
    "9:2260:0": "아뿔싸!\n",
    "9:2260:1": "이었군……!",
    "9:2261:0": "이것이―",
    "9:2261:1": "인가\n한 수 당했군……!",
    "9:2262:0": "의 뜻대로\n",
    "9:2262:1": "에 당하다니…… 아아!",
    "9:2263:0": "의 책략이라니!\n용서할 수 없다!",
    "9:2264:0": "놀아나지 마라!\n침착해!",
    "9:2265:0": "진정하라!\n놀아나지 마라!",
    "9:2266:0": "이 꼴로는\n섣불리 움직일 수 없군……",
    "9:2267:0": "적의 책략에\n빠지다니, 불찰이로다!",
    "9:2268:0": "에잇!\n손쓸 도리가 없구나……!",
    "9:2269:0": "서둘러 전열을 정비하라……\n그렇지 않으면 적이……!",
    "9:2270:0": "이 상황은……\n좋지 않구려……",
    "9:2271:0": "으아아!\n그야말로 아수라장이로다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2256:0",
    "9:2256:1",
    "9:2257:0",
    "9:2258:0",
    "9:2258:1",
    "9:2259:0",
    "9:2259:1",
    "9:2260:0",
    "9:2260:1",
    "9:2261:0",
    "9:2261:1",
    "9:2262:0",
    "9:2262:1",
    "9:2263:0",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S657", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
