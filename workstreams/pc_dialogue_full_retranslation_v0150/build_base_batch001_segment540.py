#!/usr/bin/env python3
"""Build Base authoring segment 540 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S540.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s540", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:907:0": "을(를) 포함해 총",
    "8:907:1": "명의 통솔 능력이 성장",
    "8:908:0": "의 무용 능력이 성장",
    "8:909:0": "을(를) 포함해 총",
    "8:909:1": "명의 무용 능력이 성장",
    "8:910:0": "의 지략 능력이 성장",
    "8:911:0": "을(를) 포함해 총",
    "8:911:1": "명의 지략 능력이 성장",
    "8:912:0": "의 정무 능력이 성장",
    "8:913:0": "을(를) 포함해 총",
    "8:913:1": "명의 정무 능력이 성장",
    "8:914:0": "대관으로 뽑히다니 영광",
    "8:914:2": "의 본거지인 「",
    "8:914:3": "」에\n걸맞은 활약을 보이",
    "8:915:0": "대관으로 뽑히다니 영광",
    "8:915:2": "의 본거지인 「",
    "8:915:3": "」에\n걸맞은 활약을 보이",
    "8:916:0": "대관의 임무, 삼가 받들",
    "8:916:2": "의 신임에 보답하고자\n온 힘을 다할 각오",
    "8:917:0": "정책의 계절 결산으로 금전(",
    "8:917:1": ")을 획득",
    "8:918:0": "정책의 연말 결산으로 금전(",
    "8:918:1": ")을 획득",
    "8:919:0": "이(가) 「",
    "8:919:1": "」(으)로 승진",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S540", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
