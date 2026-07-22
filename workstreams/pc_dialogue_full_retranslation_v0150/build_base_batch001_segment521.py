#!/usr/bin/env python3
"""Build Base authoring segment 521 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S521.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s521", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:564:0": "오오, 지행을 가증해 주다니\n제법 뭘 아는군!",
    "8:565:0": "중히 대접받고 있다는 게 실감 나는군!",
    "8:566:0": "께서 나를\n다시 평가해 주셨는가!",
    "8:567:0": "오오, 지행이 이만큼이나 된다면…!\n전장에서의 활약을 기대해 주시오!",
    "8:568:0": "이만한 영지를 받는다면\n아무런 불만도 없사옵니다",
    "8:569:0": "흠, 이 정도 지행고라면\n가신단 모두가 나를 중히 여기겠지",
    "8:570:0": "가증에 걸맞은 활약으로 보답하겠습니다",
    "8:571:0": "역시 이 정도는\n내게 맡겨 주셔야지요",
    "8:572:0": "여태 참아 온 보람이 있었구나",
    "8:573:0": "이 지행에 걸맞은 무용을 보여 드리리다",
    "8:574:0": "이제야 평가가 내 실력을 따라잡은 모양이군",
    "8:575:0": "이만한 지행을 받았으니\n내 재주를 마음껏 펼쳐 보이리다",
    "8:576:0": "주군께서는 나를 잊지 않으셨구나",
    "8:577:0": "어진 새는 나무를 가려 앉는다고 하옵니다만\n좋은 주군을 만나 뵙게 되었사옵니다",
    "8:578:0": "역시 「",
    "8:578:1": "」!\n",
    "8:578:2": "을(를) 눈여겨봐 주셨던 것이군!",
    "8:579:0": "황송한 배려이옵니다\n더욱 충의를 다하겠사옵니다",
    "8:580:0": "지행을 가증해 주시다니!\n저를 잊으신 줄 알았어요",
    "8:581:0": "이 지행으로\n더욱 가문에 보탬이 되겠습니다!",
}

STATIC_COORDINATES = {
    "8:564:0",
    "8:565:0",
    *(f"8:{record_id}:0" for record_id in range(567, 578)),
    *(f"8:{record_id}:0" for record_id in range(579, 582)),
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S521", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
