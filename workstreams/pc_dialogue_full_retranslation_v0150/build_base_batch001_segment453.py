#!/usr/bin/env python3
"""Build Base authoring segment 453 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S453.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s453", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2374:0": "을(를) 노리는가\n무엄한 자는 쳐부숴라",
    "7:2375:0": "은(는) 내줄 수 없다\n끝까지 지켜 내거라!",
    "7:2376:0": "의 수비는\n내게 맡겨 주게",
    "7:2377:0": "은(는) 요지다\n적에게 내줄 수 없겠군",
    "7:2378:0": "의 방어는\n우리가 맡겠다",
    "7:2379:0": "을(를) 잃을\n수는 없겠군",
    "7:2380:0": "을(를) 지켜라!\n적에게 내줄 수는 없다!",
    "7:2381:0": "의 수비를\n맡도록 하지",
    "7:2382:0": "은(는) 내주지 않겠다!\n반드시 끝까지 지켜 내겠다!",
    "7:2383:0": "을(를) 넘겨\n줄 수는 없다!",
    "7:2384:0": "(으)로 향하라\n적에게서 끝까지 지켜 내라",
    "7:2385:0": "을(를) 넘겨줄\n수는 없겠지요",
    "7:2386:0": "을(를) 노리는가\n무슨 일이 있어도 지켜 내라!",
    "7:2387:0": "을(를) 지켜라\n순순히 넘겨주진 않겠다",
    "7:2388:0": "을(를) 순순히\n넘겨줄 수는 없다!",
    "7:2389:0": "을(를) 방어하라\n끝까지 지켜 내거라!",
    "7:2390:0": "을(를) 지키러\n가겠습니다!",
    "7:2391:0": "을(를) 지켜라!\n결코 넘겨주지 않겠다!",
    "7:2392:0": "을(를) 넘겨줄\n수는 없습니다!",
    "7:2393:0": "을(를) 적의 손에\n넘겨서는 안 된다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S453", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
