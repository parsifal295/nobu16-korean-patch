#!/usr/bin/env python3
"""Build Base authoring segment 552 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S552.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s552", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:1010:0": "내 지혜로 성을 다스리고\n적을 타도할 방도를 세워\n우리 가문 패업의 초석이 되",
    "8:1011:0": "그 성, 분명히 맡",
    "8:1011:1": "\n내 본분인 지략을 발휘할 수 있도록\n통치에 힘쓸 생각",
    "8:1012:0": "적과의 경계에서 먼 이 땅에서는\n내정에 중점을 두는 편이 상책일 듯\n장기적인 영토 발전을 목표로 삼",
    "8:1013:0": "\n내 본분인 정무 수완을\n이 성이라면 마음껏 발휘할 수 있을 듯",
    "8:1014:0": "정무가 필요한 성을 맡게 되다니\n실로 뜻밖의 기쁨",
    "8:1014:1": "\n제가 거둘 좋은 성과를 기대하",
    "8:1015:0": "그 성, 분명히 맡",
    "8:1015:1": "\n내 장기인 정무로\n우리 가문의 주요 생산 거점으로 만들",
    "8:1016:0": "적의 표적이 되기 쉬운 곳임을 생각하면\n느긋하게 내정을 정비할 여유는 있",
    "8:1016:1": "지 않을 터\n자, 어떤 방침으로 임하",
    "8:1016:2": "는가…",
    "8:1017:0": "알겠",
    "8:1017:1": "\n성주인",
    "8:1017:2": "이(가) 이 땅도 다스리",
    "8:1018:0": "콜록, 콜록…\n몸을 돌보지 않은 탓인 듯하",
    "8:1018:1": "…",
    "8:1019:0": "으윽, 병에 걸린 듯하",
    "8:1019:1": "…\n반드시 낫",
    "8:1019:2": "으니, 잠시",
    "8:1019:3": "시간을…",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S552", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
