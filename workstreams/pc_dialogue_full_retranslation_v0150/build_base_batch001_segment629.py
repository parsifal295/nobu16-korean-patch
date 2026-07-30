#!/usr/bin/env python3
"""Build Base authoring segment 629 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S629.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s629", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1696:0": "격이 다르다는 걸\n가르쳐 주마!",
    "9:1697:0": "돌파할 뿐이다!\n가자!",
    "9:1698:0": "스스로 사지에\n뛰어들다니!",
    "9:1699:0": "호오\n솜씨를 한번 보지요",
    "9:1700:0": "방해된다! 비켜라!",
    "9:1701:0": "도 곧\n물러서게 될 것이다",
    "9:1702:0": "새 상대의 등장입니까",
    "9:1703:0": "이 몸이 나섰노라!\n쳐부숴 주마!",
    "9:1704:0": "누가 상대든 상관없다!",
    "9:1705:0": "기다리고 있었다!\n각오하라!",
    "9:1706:0": "누가 상대든\n마찬가지입니다!",
    "9:1707:0": "누구든\n쳐부술 뿐이다!",
    "9:1708:0": "단숨에 몰아붙여라!",
    "9:1709:0": "놓치지 마라!\n무훈을 마음껏 세울 때다!",
    "9:1710:0": "에게 도망칠 틈을 주지 마라\n끝장을 내라!",
    "9:1711:0": "수급을 취할 호기입니다",
    "9:1712:0": "호기다!\n추격하라!",
    "9:1713:0": "적이 물러난다……\n이 기회를 놓치지 마라!",
    "9:1714:0": "적을 놓치지 마라!\n소탕하라!",
    "9:1715:0": "추격이다!\n전공을 세울 때는 지금이다!",
    "9:1716:0": "마지막 일격을 가하는 겁니다!",
    "9:1717:0": "끝장낼 때는 지금이다!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1701:0",
    "9:1710:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S629", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
