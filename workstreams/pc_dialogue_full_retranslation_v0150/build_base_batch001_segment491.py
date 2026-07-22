#!/usr/bin/env python3
"""Build Base authoring segment 491 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S491.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s491", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:231:0": "(으)로 들어간다\n모두, 방심하지 마라",
    "8:232:0": "자, 「",
    "8:232:1": "」을(를)\n공략하겠습니다!",
    "8:233:0": "은(는)\n",
    "8:233:1": "이(가) 빼앗겠습니다",
    "8:234:0": "을(를) 우리 손에 넣읍시다!\n모두, 해냅시다!",
    "8:235:0": "자, 「",
    "8:235:1": "」은(는)\n우리 것이다!",
    "8:236:0": "을(를)\n제압하는 것은 우리다!",
    "8:237:0": "을(를) 차지한다!\n모두, 방심하지 마라!",
    "8:238:0": "우리 손으로\n",
    "8:238:1": "을(를) 빼앗는다!",
    "8:239:0": "바로 「",
    "8:239:1": "」이(가)\n",
    "8:239:2": "을(를) 제압한다!",
    "8:240:0": "자, 「",
    "8:240:1": "」을(를)\n차지해 볼까",
    "8:241:0": "을(를) 버리고\n",
    "8:241:1": "의 편에 서겠다!",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S491", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
