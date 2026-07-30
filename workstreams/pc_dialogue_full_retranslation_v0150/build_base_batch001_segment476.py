#!/usr/bin/env python3
"""Build Base authoring segment 476 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S476.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s476", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2717:0": "재미있는 싸움이었군……\n즐거웠다",
    "7:2718:0": "다음에는 진정한 힘을 보여 드리지요",
    "7:2719:0": "전공 제일은 양보했습니다만\n승리에 보탬이 될 만큼은 활약한 듯합니다",
    "7:2720:0": "장하도다, 장하도다!\n이것이",
    "7:2720:1": "의 싸움 방식이로다",
    "7:2721:0": "전장에서 쌓아 온 공이 다르다네",
    "7:2722:0": "조금 더 해낼 수 있을 줄 알았습니다만……\n아쉽군요……",
    "7:2723:0": "이번 결과에 자만하지 않고 정진하겠습니다",
    "7:2724:0": "이 정도는 당연한 일\n다음에는 더 큰 활약을 보여 주마",
    "7:2725:0": "제법 싸웠다고 생각했건만……\n고작 이 정도인가",
    "7:2726:0": "제법 잘 싸웠다고 생각합니다",
    "7:2727:0": "이토록 많은 공을 세웠다니……",
    "7:2728:0": "흠, 내 전공도 제법이로군",
    "7:2729:0": "애쓴 보람이 있었어!",
    "7:2730:0": "출진한 무장은 「자율 행동」을 하며,\n스스로 판단하여 행동을 바꾸기도 합니다\n(예)\n·적의 성을 포위하도록 진로를 바꾼다\n·비운 성이 노려지면 되돌아가 성을 지킨다 등",
    "7:2731:0": "부대를 자신의 명령대로 움직이게 하려면,\n자율 행동을 금지할 수도 있습니다\n설정은 언제든 변경할 수 있으므로,\n상황에 따라 알맞게 활용합시다",
    "7:2732:0": "자율 행동의 초기 설정을\n「허가」로 설정하시겠습니까?\n※언제든 게임 설정에서 변경할 수 있습니다",
    "7:2733:0": "이(가)",
    "7:2733:1": "을(를) 편입",
    "7:2734:0": "을(를) 간자로부터\n끝까지 지켜 내",
}

STATIC_COORDINATES: set[str] = {
    *(f"7:{record_id}:0" for record_id in range(2717, 2720)),
    *(f"7:{record_id}:0" for record_id in range(2721, 2733)),
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S476", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
