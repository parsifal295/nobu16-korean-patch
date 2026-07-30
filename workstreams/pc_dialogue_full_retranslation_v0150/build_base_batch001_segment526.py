#!/usr/bin/env python3
"""Build Base authoring segment 526 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S526.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s526", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:658:0": "내 영지가…\n",
    "8:658:1": "께서 노하신 겐가…",
    "8:659:0": "만족하며 힘쓰고 있었거늘 어찌하여…?\n설마…",
    "8:660:0": "줄어드는 건 분하지만\n이만큼이면 충분해",
    "8:661:0": "그 땅은 가져가 버리는 거냐\n그래, 알았다",
    "8:662:0": "그 땅은 다른 자에게?\n분부라면 돌려드리겠소",
    "8:663:0": "목숨 걸고 지켜 온 영지…\n부디 소중히 다루어 주시오",
    "8:664:0": "아쉽기는 합니다만\n그 영지는 내놓도록 하지요",
    "8:665:0": "께서 뜻하신 대로 따르겠사옵니다",
    "8:666:0": "어쩔 수 없군요\n돌려드리겠습니다",
    "8:667:0": "예, 그러시지요\n제 손으로 몰라볼 만큼 바꾸어 놓았답니다",
    "8:668:0": "이 정도는 별것 아니지\n",
    "8:668:1": "에게는 아직 지행이 있으니까",
    "8:669:0": "뜻하시는 대로",
    "8:670:0": "상관없사옵니다\n부디 뜻대로 쓰시옵소서",
    "8:671:0": "그리해야 할 때라고\n소인도 생각하고 있었사옵니다",
    "8:672:0": "그 땅은 회수하시는 겁니까\n아무래도 기대에 미치지 못한 모양이군요",
    "8:673:0": "이 또한 가문을 위한 일\n부디 거두어 주시옵소서",
    "8:674:0": "그 정도는 가져가 주시오\n",
    "8:674:1": "은(는) 평소 후히 대접받고 있으니 말이오",
    "8:675:0": "깊은 뜻이 있으신 일이겠지요\n분부 받들겠소",
    "8:676:0": "마침 제 손에 벅차던 참입니다\n다른 분께 맡겨 주십시오",
    "8:677:0": "소중히 다스려 온 땅입니다\n부디 앞으로도 잘 보살펴 주시옵소서",
}

STATIC_COORDINATES = {
    *(f"8:{record_id}:0" for record_id in range(659, 665)),
    *(f"8:{record_id}:0" for record_id in range(666, 668)),
    *(f"8:{record_id}:0" for record_id in range(669, 674)),
    *(f"8:{record_id}:0" for record_id in range(675, 678)),
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S526", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
