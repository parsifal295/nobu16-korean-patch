#!/usr/bin/env python3
"""Build Base authoring segment 522 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S522.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s522", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:582:0": "이제야 내 재능을 알아본 것인가",
    "8:583:0": "이만한 지행이 있다면\n마음껏 싸움에 나설 수 있겠군!",
    "8:584:0": "어머, 지행 가증인가요\n참아 온 보람이 있었네요",
    "8:585:0": "하아…\n만족하였사옵니다…",
    "8:586:0": "을(를) 이리 높이 평가해 주시다니!\n이만하면 충분하옵니다",
    "8:587:0": "이토록 많은 지행을…!\n",
    "8:587:1": "의 신뢰에 반드시 부응해 보이겠사옵니다!",
    "8:588:0": "이곳에서 지낸 지도 어느덧 제",
    "8:588:1": "년이 되었군\n또 놀러 오고 싶구먼",
    "8:589:0": "년이나 다스린 땅과도\n이제 작별인가…",
    "8:590:0": "년이나 다스린 땅을 떠나게 되는가\n참 쓸쓸하구나…",
    "8:591:0": "년 동안\n내 휘하에서 힘써 준 병사들이여\n그동안 고마웠다",
    "8:592:0": "년이나 지내면 애착도 생기지만\n어쩔 수 없겠지",
    "8:593:0": "년인가…\n아니, 감상에 젖다니 어리석었군\n모두 건강히 지내거라",
    "8:594:0": "돌이켜 보니 이 땅에 머문 지도 어언 제",
    "8:594:1": "년을 넘겼구나\n세월은 참 빠르게 흐르는군요",
    "8:595:0": "년 동안 다스린 백성들…\n제가 없어도 괜찮을까요…?",
    "8:596:0": "주군의 명령이라지만\n",
    "8:596:1": "년이나 다스린 땅을 떠나려니 쓸쓸하군",
    "8:597:0": "년 동안 내가 수련했던 그 산… 그 들판을\n결코 잊지 않으리…",
}

STATIC_COORDINATES = {f"8:{record_id}:0" for record_id in range(582, 586)}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S522", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
