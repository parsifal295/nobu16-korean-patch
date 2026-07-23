#!/usr/bin/env python3
"""Build Base authoring segment 631 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S631.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s631", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1740:0": "주군을 해치게 두지 마라!\n모두 나서라!",
    "9:1741:0": "어서……!\n어서 주군을 지켜야 한다",
    "9:1742:0": "누구라도 좋다\n당장 보내라!",
    "9:1743:0": "이런…… 어서 주군을\n구해야 한다……",
    "9:1744:0": "주군의 신변이……!\n구하러 가야 한다!",
    "9:1745:0": "!\n뒈지지 마라!",
    "9:1746:0": "무사의 자존심이 걸렸다!\n",
    "9:1746:1": "만은 해치게 두지 마라!",
    "9:1747:0": "도 역시 장수이니……\n무사히 퇴각하겠지",
    "9:1748:0": "어떻게든 무사히\n퇴각시켜야 한다……",
    "9:1749:0": "마저\n무너지다니……",
    "9:1750:0": "의 퇴로를 확보하고\n호위를 서둘러라……",
    "9:1751:0": "만 한\n장수가……!",
    "9:1752:0": "만은\n해치게 두지 마라!",
    "9:1753:0": "무사히 달아날 수만 있다면\n좋겠습니다만……",
    "9:1754:0": "\n무운을 빌겠다……",
    "9:1755:0": "\n부디 무사하기를!",
    "9:1756:0": "무사하시기를 빌겠소……",
    "9:1757:0": "동료들을 볼 면목이 없어……",
    "9:1758:0": "나의 긍지가……\n땅에 떨어졌는가……!",
    "9:1759:0": "이제는……\n탄식할 기력조차 없구나……",
    "9:1760:0": "아무것도 하지 못하다니……\n가신 자격이 없습니다……",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1745:0",
    "9:1746:0",
    "9:1746:1",
    "9:1747:0",
    "9:1749:0",
    "9:1750:0",
    "9:1751:0",
    "9:1752:0",
    "9:1754:0",
    "9:1755:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S631", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
