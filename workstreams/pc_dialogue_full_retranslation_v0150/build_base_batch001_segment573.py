#!/usr/bin/env python3
"""Build Base authoring segment 573 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S573.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s573", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:497:0": "!\n각오하십시오!",
    "9:498:0": "!\n",
    "9:498:1": "이(가) 상대해 주마!",
    "9:499:0": "\n승부를 청합니다!",
    "9:500:0": "상대할 자는―",
    "9:500:1": "이다!",
    "9:501:0": "들이받아 주마!",
    "9:502:0": "의 싸움을\n보여 주마!",
    "9:503:0": "접전이 무엇인지\n가르쳐 주마!",
    "9:504:0": "신중히……대열이 흐트러지지\n않도록 나아갑시다",
    "9:505:0": "덤벼라!\n쳐부숴 주마!",
    "9:506:0": "난전인가……좋다",
    "9:507:0": "난전으로 몰고 가라!",
    "9:508:0": "자, 바짝 달라붙어\n놓치지 마라!",
    "9:509:0": "적을 포착했습니다!\n공격 개시!",
    "9:510:0": "덤벼라!\n본때를 보여 주마!",
    "9:511:0": "적과 접촉했습니다\n공격을 개시합니다",
    "9:512:0": "의 싸움을\n똑똑히 보아라!",
    "9:513:0": "가진 것을 모두\n쏟아부어라!",
    "9:514:0": "쏴라!\n확실히 처치하라!",
    "9:515:0": "화살과 탄환의 비를 퍼부어라!",
    "9:516:0": "잘 겨누고……지금입니다!",
    "9:517:0": "쏴라!",
    "9:518:0": "빗맞히지 마라……쏴라!",
}

STATIC_COORDINATES: set[str] = {
    "9:501:0",
    "9:503:0",
    "9:504:0",
    "9:505:0",
    "9:506:0",
    "9:507:0",
    "9:508:0",
    "9:509:0",
    "9:510:0",
    "9:511:0",
    "9:513:0",
    "9:514:0",
    "9:515:0",
    "9:516:0",
    "9:517:0",
    "9:518:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S573", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
