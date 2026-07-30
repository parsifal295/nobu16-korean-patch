#!/usr/bin/env python3
"""Build Base authoring segment 669 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S669.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s669", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:2477:0": "병사들이 지쳐 보입니다……\n지금은 물러납시다",
    "9:2478:0": "계속 싸울 수는 없다……\n물러난다!",
    "9:2479:0": "무리는 금물입니다\n부대를 물리겠습니다",
    "9:2480:0": "더는 버티지 못한다……\n우리는 후퇴한다!",
    "9:2481:0": "을(를) 협격하는 데 성공",
    "9:2482:0": "이건 잡았다!\n협격이다!",
    "9:2483:0": "협격하라!\n단숨에 짓뭉갠다!",
    "9:2484:0": "즉시 에워싸라!\n한 명도 놓치지 마라!",
    "9:2485:0": "자비는 필요 없습니다\n양쪽에서 쳐부수겠습니다",
    "9:2486:0": "공격하라!\n양쪽에서 섬멸하리라!",
    "9:2487:0": "협격이 이루어졌다!\n이제 쳐부수기만 하면 된다!",
    "9:2488:0": "측면에서 꿰뚫어 버린다!\n자비는 필요 없다!",
    "9:2489:0": "참으로 빈틈투성이로구나\n협격해 주마!",
    "9:2490:0": "협격하겠습니다!\n단숨에 몰아칩시다!",
    "9:2491:0": "잡았다!\n에워싸서 쳐부순다!",
    "9:2492:0": "지금입니다!\n양쪽에서 무너뜨리십시오!",
    "9:2493:0": "공격하라!\n양쪽에서 섬멸하리라!",
    "9:2494:0": "을(를)\n따르라!",
    "9:2495:0": "와(과)\n호흡을 맞춘다!",
    "9:2496:0": "와(과)\n호흡을 맞춰라!",
    "9:2497:0": "을(를)\n따르도록 합시다!",
    "9:2498:0": "와(과)\n호흡을 맞춰라!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2481:0",
    "9:2494:0",
    "9:2495:0",
    "9:2496:0",
    "9:2497:0",
    "9:2498:0",
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
    print(ENGINE.json.dumps({"status":"ok", "segment":"base_msggame_B001_S669", "decision_count":len(rows),
                             "retranslated":len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending":len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed":False, "output":str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
