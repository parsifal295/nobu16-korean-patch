#!/usr/bin/env python3
"""Build Base authoring segment 518 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S518.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s518", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
COUNTY_TRAIT_GA = "의 군 특성이 「"
COUNTY_TRAIT_NO = "의 군 특성 「"
COUNTY_TRAIT_WO = "의 군 특성을 「"
TRANSLATIONS = {
    "8:509:0": "의 「",
    "8:509:1": "」 능력이 성장(",
    "8:509:2": "→",
    "8:509:3": ")",
    "8:510:0": COUNTY_TRAIT_GA,
    "8:510:1": "」로 진화",
    "8:511:0": COUNTY_TRAIT_GA,
    "8:511:1": "」로 퇴화",
    "8:512:0": COUNTY_TRAIT_NO,
    "8:512:1": "」의 LV가",
    "8:512:2": "까지 저하",
    "8:513:0": COUNTY_TRAIT_WO,
    "8:513:1": "」로 개발하기 시작",
    "8:514:0": COUNTY_TRAIT_WO,
    "8:514:1": "」로 개발 완료",
    "8:515:0": COUNTY_TRAIT_NO,
    "8:515:1": "」이(가) LV",
    "8:515:2": "까지 성장",
    "8:516:0": "이것뿐인가…\n좀 더 맡겨 줘도 좋을 텐데",
    "8:517:0": "지행을 더 가증해 주면\n더 잘 일할 텐데 말이야?",
    "8:518:0": "으음, 생각보다 적구나…\n영지 경영에는 자신이 있건만",
    "8:519:0": "혁혁한 무훈을 세우려면\n지행이 조금 더 필요하다만…",
    "8:520:0": "이것이 「",
    "8:520:1": "」의 평가인가…\n지행을 좀 더 나누어 줄 수는 없는가",
    "8:521:0": "불만은 없소… 없소만\n이 정도 지행에 만족할 그릇으로 보이는 것도\n다소 체면이 서지 않는군…",
}

STATIC_COORDINATES = {
    "8:516:0",
    "8:517:0",
    "8:518:0",
    "8:519:0",
    "8:521:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S518", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
