#!/usr/bin/env python3
"""Build Base authoring segment 151 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S151.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s151", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2774:0": "뚜렷한 적이 없는 지금\n나라를 부유하게 하고 아군을 만들어야겠군",
    "6:2775:0": "지금은 나라를 부유하게 할 때. 영내뿐 아니라\n외교로도 아군과 이득을 얻어야겠지요",
    "6:2776:0": "우리 가문을 번영시키려면 지금이 중요합니다\n외교도 소홀히 할 수 없지요",
    "6:2777:0": "적이라 여길 자가 없다면\n나라를 부유하게 해야 한다.\n외교도 정치의 한 축을 맡고 있으니",
    "6:2778:0": "우리 가문이 제 길을 간다 해도\n바깥과 전혀 관계하지 않을 수는 없겠지",
    "6:2779:0": "뚜렷한 적이 없는 지금은 영내를 돌봐야…\n아, 바깥과 교류하는 것도 잊어서는 안 되지요",
    "6:2780:0": "적이라 정한 자가 없다면 외교로\n아군을 만들고 이득을 얻어야 할 것입니다",
    "6:2781:0": "우리는 우리의 길을 갈 뿐이다. 하지만\n영내만 바라보고 있을 수는 없다",
    "6:2782:0": "그 일만 할 수는 없으니 외교에도\n지금부터 힘써 두어야겠군",
    "6:2783:0": "우리 가문에 종속한",
    "6:2783:1": "입니다만\n가신으로 받아들이는 것이 어떻겠습니까?",
    "6:2784:0": "저,",
    "6:2784:1": "은(는) 앞으로 주군의 가신으로서\n대대로 섬겨 온 분들께 뒤지지 않도록 힘쓸 각오입니다!\n잘 부탁드리옵니다",
    "6:2785:0": "알겠습니다\n이 이야기는 일단 거두도록 하지요",
    "6:2786:0": "이(가) 우리 가문의 산하로",
    "6:2787:0": "이(가),",
    "6:2787:1": "의 산하로",
    "6:2788:0": "빌린 장병을 돌려드릴 날이 지났지만\n아직 공성이 계속되고 있소\n이번 공성이 끝날 때까지 기다려 주지 않겠소?",
    "6:2789:0": "빌린 장병을 돌려드릴 날이 지났지만\n아직 공성이 계속되고 있소\n이번 공성이 끝날 때까지 기다려 주지 않겠소?",
    "6:2790:0": "빌린 장병을 돌려드릴 날이 지났지만\n아직 공성이 계속되고 있소\n이번 공성이 끝날 때까지 기다려 주지 않겠소?",
}

DYNAMIC_COORDINATES = {
    "6:2783:0", "6:2783:1", "6:2784:0", "6:2784:1", "6:2786:0", "6:2787:0", "6:2787:1",
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        dynamic = coordinate in DYNAMIC_COORDINATES
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved",
                     "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                     "layout_review": "unchanged_from_current", "runtime_review": "pending" if dynamic else "not_required",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S151", "decision_count": len(rows),
                             "retranslated": len(rows) - len(DYNAMIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
