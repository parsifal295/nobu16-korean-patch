#!/usr/bin/env python3
"""Build Base authoring segment 205 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S205.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s205", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3499:0": "도 마침내",
    "6:3499:1": "에…!\n이 은혜는 평생을 바쳐 갚",
    "6:3500:0": "이렇게 공적을 인정받",
    "6:3500:1": "으니\n충절을 다한 보람도 있",
    "6:3500:2": "\n우리 가문을 더욱 번영시킬 각오",
    "6:3501:0": "이(가) 된다는 것은\n이토록 각별한 기쁨인 것",
    "6:3502:0": "가신 모두가 더욱 충성을 다하여\n우리 가문을 일으켜 세워야겠군…",
    "6:3503:0": "공이 큰 자, 작은 자…\n논공행상은 제 공적을 돌아보는\n좋은 계기가 되는 것",
    "6:3504:0": "신상필벌은 나라의 근본\n열심히 일한 자에게는 마땅한 보상이 있어야\n당연한 일이라 생각하",
    "6:3505:0": "훈공 1위",
    "6:3505:1": "!\n이 기세로 정상까지\n오르고야 말",
    "6:3505:2": "다!",
    "6:3506:0": "공을 인정받",
    "6:3506:1": "는가,\n참으로 고마울 따름",
    "6:3506:2": "!\n앞으로 더욱 놀라게 해 보이",
    "6:3506:3": "!",
    "6:3507:0": "이(가) 훈공 1위라…\n아랫사람들도 지켜보고 있",
    "6:3507:1": "\n더욱 힘쓰",
    "6:3507:2": "!",
    "6:3508:0": "훈공 1위, 감사히 받",
}

STATIC_COORDINATES: set[str] = {
    "6:3502:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S205", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
