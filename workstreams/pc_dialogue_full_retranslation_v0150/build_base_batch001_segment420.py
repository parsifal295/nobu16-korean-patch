#!/usr/bin/env python3
"""Build Base authoring segment 420 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S420.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s420", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1850:0": "의 방어 완료\n이제 귀환한다",
    "7:1851:0": "의 방어는\n이제 충분하겠군요",
    "7:1852:0": "은(는) 반석과도 같다\n이만 철수하도록 하지",
    "7:1853:0": "의 제압을 마쳤다\n야망에 한 걸음 더 가까워졌군",
    "7:1854:0": "을(를) 제압했다!\n모두, 잘했다!",
    "7:1855:0": "을(를) 점령했노라\n서두르지 말고 착실히 나아가자",
    "7:1856:0": "은(는) 수중에 있다\n침략하기를 불같이",
    "7:1857:0": "을(를) 제압했다\n진을 거두고 성으로 들어가라",
    "7:1858:0": "의 선무는\n무사히 끝났구나",
    "7:1859:0": "을(를) 빼앗았다\n자, 군을 거두자꾸나",
    "7:1860:0": "을(를) 제압했다\n목표를 달성했는가",
    "7:1861:0": "은(는)\n",
    "7:1861:1": "들의 것이로군!",
    "7:1862:0": "을(를) 평정했다\n모두, 철수하라!",
    "7:1863:0": "의 제압 완료\n나의 무명을 떨쳤도다",
    "7:1864:0": ", 점령했습니다\n자, 병사를 물릴까요",
    "7:1865:0": "을(를) 빼앗았노라\n좋은 싸움이었도다",
    "7:1866:0": "을(를) 장악했다\n일이 순조롭게 풀렸군",
    "7:1867:0": "을(를) 제압했다\n목적을 달성했군",
    "7:1868:0": "의 제압 완료\n이제 돌아가도록 하지",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S420", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
