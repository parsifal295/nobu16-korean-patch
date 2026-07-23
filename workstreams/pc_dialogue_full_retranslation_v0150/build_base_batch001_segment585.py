#!/usr/bin/env python3
"""Build Base authoring segment 585 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S585.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s585", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:754:0": "주군께서 부상하셨다고!?",
    "9:755:0": "여기서는 물러날 수밖에 없어……",
    "9:756:0": "힘이 미치지 못했소……\n면목이 없소",
    "9:757:0": "설마―",
    "9:757:1": "이(가)\n패하고 말 줄이야……",
    "9:758:0": "큭…… 이번 퇴각도\n예상한 바……입니다……",
    "9:759:0": "으으음……\n허를 찔렸구나",
    "9:760:0": "큭, 설마\n이런 일이……",
    "9:761:0": "승패는 시운에 달린 법……",
    "9:762:0": "칫……\n실수했구먼",
    "9:763:0": "윽, 그만\n방심하고 말았습니다……",
    "9:764:0": "지금은 물러나라!\n이 빚은 언젠가……",
    "9:765:0": "기대에 부응하지 못해……\n송구합니다……",
    "9:766:0": "끄으으윽……\n이놈, 분하구나……",
    "9:767:0": "을(를)\n베어 쓰러뜨렸다!",
    "9:768:0": "\n베어 쓰러뜨렸노라!",
    "9:769:0": "의 수급을\n거두었소이다",
    "9:770:0": "\n베어 쓰러뜨렸습니다!",
    "9:771:0": "\n베어 쓰러뜨렸노라!",
    "9:772:0": "\n베어 쓰러뜨렸도다!",
    "9:773:0": "\n베어 쓰러뜨렸노라!",
    "9:774:0": "\n베어 쓰러뜨렸도다!",
}

STATIC_COORDINATES: set[str] = {
    "9:754:0",
    "9:755:0",
    "9:756:0",
    "9:758:0",
    "9:759:0",
    "9:760:0",
    "9:761:0",
    "9:762:0",
    "9:763:0",
    "9:764:0",
    "9:765:0",
    "9:766:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S585", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
