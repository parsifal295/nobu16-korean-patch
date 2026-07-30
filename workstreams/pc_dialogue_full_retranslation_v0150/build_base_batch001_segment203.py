#!/usr/bin/env python3
"""Build Base authoring segment 203 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S203.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s203", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3479:0": "사람을 이끄는 자로서\n주어진 일을 해내고 있을 뿐이다\n얼마든지 더 맡겨도 좋다!",
    "6:3480:0": "어머나,",
    "6:3480:1": "이(가) 훈공 1위라도 괜찮은 걸까요\n여러분, 그래서는",
    "6:3480:2": "을(를)\n따라잡을 수 없답니다",
    "6:3481:0": "이(가)",
    "6:3481:1": "의 자리에 오른 것은\n",
    "6:3481:2": "의 뒷받침이 있었기 때문이오\n녹봉만 축낼 수는 없으니 말이오",
    "6:3482:0": "이제 명예 따위에는 연연하지 않는다만\n",
    "6:3482:1": "은(는) 가족이나 다름없지\n앞으로도",
    "6:3482:2": "을(를) 의지하라고!",
    "6:3483:0": "훈공 1위는 당연하지\n가신 필두라 할 만한 지위에 있는 몸이다\n남에게 내줘서는 무문의 수치로다!",
    "6:3484:0": "은(는) 말하자면 가신들의 얼굴…\n훈공 1위를 차지하지 못한다면\n",
    "6:3484:1": "의 패업을 받들기에는 역부족이겠지",
    "6:3485:0": "신하의 도를 닦는 길에는 끝이 없으니…\n우리 가문의 앞날을 지켜보는 것이야말로\n",
    "6:3485:1": "의 천명이옵니다",
    "6:3486:0": "훈공 1위인가…\n뭐, 거들먹거리기만 하는 것도 지겨워져서\n지위에 걸맞은 몫을 했을 뿐이다",
    "6:3487:0": "훈공 1위라니 주제넘은 일…\n",
    "6:3487:1": "의 마음을 헤아려 충의를 다했을 뿐\n치하받을 만한 일은 하지 않았사옵니다",
    "6:3488:0": "훈공 1위라니 쑥스럽구려\n이 정도는 늘 해 오던 일이옵니다\n",
    "6:3488:1": "도 잘 아실 터인데",
}

STATIC_COORDINATES: set[str] = {
    "6:3479:0",
    "6:3483:0",
    "6:3486:0",
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
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S203", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
