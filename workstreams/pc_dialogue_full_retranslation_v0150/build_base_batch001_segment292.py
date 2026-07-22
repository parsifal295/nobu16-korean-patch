#!/usr/bin/env python3
"""Build Base authoring segment 292 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S292.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s292", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4400:0": "을(를) 배속해",
    "6:4400:1": "\n적의 어떠한 조략도\n막아 보이겠",
    "6:4401:0": "방비가 필요한 땅이니\n",
    "6:4401:1": "에게 맡기려는 것은 당연한 일…\n하지만 솔직히 내키지는 않",
    "6:4402:0": "이 「",
    "6:4402:1": "」은(는), 부디 「",
    "6:4402:2": "」에게 맡겨 주십시오\n적지와 맞닿은 땅이야말로\n제 수완을 보일 곳입니다",
    "6:4403:0": "전선의 땅",
    "6:4403:1": ", 팔이 근질거리",
    "6:4403:3": "을(를) 배속하신다면\n부대의 방비 강화에 이바지할 수 있습니다",
    "6:4404:0": "과연, 제 창 솜씨를",
    "6:4404:1": " 원하시는 것이군요",
    "6:4404:2": "\n하지만… 인선은 다시 검토해 주시길 바랍니다",
    "6:4405:0": "에 배속되다니, 바라던 바입니다!\n부디, 「",
    "6:4405:1": "」을(를) 임명하여\n무공을 세우게 해",
    "6:4406:0": "전선 배속은 바라던 바\n전장에서야말로 내 재주를\n발휘할 수 있을 터",
    "6:4407:0": "적성 포위라면 분명 자신 있습니다\n하지만 마음은 내키지 않",
    "6:4408:0": "에는, 부디 「",
    "6:4408:1": "」을(를)\n포위전으로 성을 공격한다면\n반드시 도움이 되겠",
}

STATIC_COORDINATES: set[str] = set()


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S292", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
