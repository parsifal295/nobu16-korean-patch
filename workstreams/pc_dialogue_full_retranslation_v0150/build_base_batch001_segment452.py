#!/usr/bin/env python3
"""Build Base authoring segment 452 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S452.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s452", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2356:0": "을(를) 우리 것으로\n삼을 절호의 기회다!",
    "7:2357:0": "을(를) 차지해도\n손해 볼 일은 없겠지",
    "7:2358:0": "은(는)\n우리에게야말로 어울린다",
    "7:2359:0": "을(를) 제압하자\n여러 다이묘를 견제하는 것이다",
    "7:2360:0": "은(는)\n우리 것으로 삼겠다!",
    "7:2361:0": "(으)로 진군하여\n우리 영토로 삼으리라!",
    "7:2362:0": "을(를) 공격한다!\n빼앗을 수 있는 건 모조리 빼앗아라",
    "7:2363:0": "을(를)\n빼앗겠다!",
    "7:2364:0": "을(를) 탈취한다\n이 또한 난세의 이치다",
    "7:2365:0": "선수를 치면 남을 제압할 수 있습니다\n",
    "7:2365:1": "을(를) 빼앗겠습니다",
    "7:2366:0": "을(를) 빼앗아라\n우리 영지로 삼는다!",
    "7:2367:0": "은(는)…… 우리 쪽이\n더 잘 활용할 수 있겠군",
    "7:2368:0": "을(를) 제압한다\n진군하라!",
    "7:2369:0": "을(를)\n차지해 둘까나",
    "7:2370:0": "을(를) 제압하러\n갑시다",
    "7:2371:0": "남보다 앞서 공을 세우는 것이 전장의 꽃\n",
    "7:2371:1": "을(를) 공격하겠다",
    "7:2372:0": "은(는)\n차지하겠습니다!",
    "7:2373:0": "은(는)\n우리 가문의 것으로 삼겠다!",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S452", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
