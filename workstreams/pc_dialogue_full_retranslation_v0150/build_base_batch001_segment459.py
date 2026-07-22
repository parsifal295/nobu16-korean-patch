#!/usr/bin/env python3
"""Build Base authoring segment 459 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S459.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s459", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2445:0": "을(를) 공격하신다면\n직진 외에도 다른 방법이 있",
    "7:2445:2": "의 방안도",
    "7:2445:3": "검토",
    "7:2446:0": "의\n",
    "7:2446:1": "방향에서 공격하는 것은",
    "7:2446:2": "\n우회해야 하지만 공성에는 유리해지",
    "7:2447:0": "공격로에 비해\n부대 수가 지나치게 많은 방면이",
    "7:2447:1": "\n우회해야 하지만 진로 변경은",
    "7:2448:0": "전 부대가 곧장",
    "7:2448:1": "(으)로\n향하도록 지시",
    "7:2448:2": "인가?",
    "7:2449:0": "어쩔 수 없군. 잘 있거라",
    "7:2450:0": "목숨이 이곳에서 다하다니",
    "7:2451:0": "이 몸도 여기까지인가……",
    "7:2452:0": "꿈속의 또 꿈이로구나……",
    "7:2453:0": "미카와 무사의 최후를 똑똑히 보아라!",
    "7:2454:0": "모두 뜬세상의 꿈이었던가……",
    "7:2455:0": "훌륭하다. 내 목을 가져가라",
    "7:2456:0": "원한도 후회도 없다",
    "7:2457:0": "전장에서 죽으니 더할 나위 없구나",
}

STATIC_COORDINATES = {f"7:{record_id}:0" for record_id in range(2449, 2458)}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S459", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
