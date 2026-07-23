#!/usr/bin/env python3
"""Build Base authoring segment 630 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S630.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s630", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1718:0": "여기서\n끝냅시다!",
    "9:1719:0": "끝장낼 때는\n지금이오!",
    "9:1720:0": "벌써 퇴각하나?\n싸울 맛이 안 나는군!",
    "9:1721:0": ", 기다려라!\n끝까지 승부하라!",
    "9:1722:0": "이토록 쉽게\n등을 보이다니",
    "9:1723:0": "역시 물러나는군요\n추격합시다!",
    "9:1724:0": "기다려라!\n그 목을 두고 가라!",
    "9:1725:0": "재정비하면 성가시다\n가능한 한 많이 쓰러뜨려라!",
    "9:1726:0": "겁쟁이로구나\n이리 쉽게 퇴각하다니",
    "9:1727:0": "끝까지 미련을 버리지 못하는군\n이제 체념하라!",
    "9:1728:0": "의 뒤를\n쫓읍시다!",
    "9:1729:0": "지금이 호기다! 나아가라!",
    "9:1730:0": "몰아붙입시다!",
    "9:1731:0": "\n절대 놓치지 않겠다!",
    "9:1732:0": "의 추격대에게서\n벗어날 수 있을 것 같습니까?",
    "9:1733:0": "주군이 위험해!\n어서 구해야 해!",
    "9:1734:0": "주군을 해치게 두면\n무사의 면목이 서지 않는다!",
    "9:1735:0": "무얼 하고 있느냐!\n어서 주군을 지켜라!",
    "9:1736:0": "주군만은 무사히\n퇴각시켜야 합니다",
    "9:1737:0": "주군을 지켜라!",
    "9:1738:0": "주군의 퇴로를 지켜라!",
    "9:1739:0": "주군만은 절대로 해치게 두지 않겠습니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1721:0",
    "9:1728:0",
    "9:1731:0",
    "9:1732:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S630", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
