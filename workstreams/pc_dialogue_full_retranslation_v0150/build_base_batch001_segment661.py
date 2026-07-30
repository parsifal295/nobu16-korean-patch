#!/usr/bin/env python3
"""Build Base authoring segment 661 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S661.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s661", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2322:0": "……\n간파할 수 있었던 건 천우로군요",
    "9:2323:0": "(이)라기에\n무엇인가 했더니",
    "9:2324:0": "을(를) 속일 수 있다고\n생각했느냐!",
    "9:2325:0": "어리석은 계책에 의지하는 것은\n겁먹었다는 증거다!",
    "9:2326:0": "에게 이 같은\n하책으로 덤비다니",
    "9:2327:0": "을(를) 속이려 하다니\n무모한 짓입니다",
    "9:2328:0": "위보에 놀아날\n",
    "9:2328:1": "은(는) 아니야",
    "9:2329:0": "이런이런……\n케케묵은 수법이군",
    "9:2330:0": "생각이 얕은―",
    "9:2330:1": "이(가)\n떠올릴 법한 수로군",
    "9:2331:0": "아직 미숙하구나……\n그 수에는 속지 않느니라",
    "9:2332:0": "그 정보는 거짓이다!\n눈앞의 적에게 집중하라",
    "9:2333:0": "우리는 그런 책략에\n걸려들지 않는다!",
    "9:2334:0": "그것으로 속이려 하다니\n너무 안이한 생각이랍니다",
    "9:2335:0": "너무도 뻔한 위보라\n오히려 안심했소이다",
    "9:2336:0": "좋고말고!",
    "9:2337:0": "간다!",
    "9:2338:0": "알겠소!",
    "9:2339:0": "해 봅시다",
    "9:2340:0": "받아라!",
    "9:2341:0": "보아라……!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2322:0",
    "9:2323:0",
    "9:2324:0",
    "9:2326:0",
    "9:2327:0",
    "9:2328:0",
    "9:2328:1",
    "9:2330:0",
    "9:2330:1",
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
    print(ENGINE.json.dumps({"status":"ok", "segment":"base_msggame_B001_S661", "decision_count":len(rows),
                             "retranslated":len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending":len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed":False, "output":str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
