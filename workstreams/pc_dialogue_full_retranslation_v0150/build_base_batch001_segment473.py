#!/usr/bin/env python3
"""Build Base authoring segment 473 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S473.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s473", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2671:0": "전공 제일이라니 훌륭하도다,",
    "7:2671:1": "!\n내 자랑이로다",
    "7:2672:0": ", 전공 제일을 축하드립니다!\n아아……칭송할 말을 찾지 못하겠습니다",
    "7:2673:0": ", 역시 대단하시군요\n저도 뒤처지지 않도록 정진해야겠습니다",
    "7:2674:0": ", 이 녀석, 용케도 해냈구나\n전공 제일이라니,",
    "7:2674:1": "까지 자랑스럽구나",
    "7:2675:0": ", 훌륭하도다\n화려함과 실속을 모두 갖춘 활약이었다",
    "7:2676:0": ", 이 녀석, 기대를 가뿐히 뛰어넘었구나\n후후, 진심으로 기쁘구나……",
    "7:2677:0": "의 전공 제일은 예상대로군\n언제나처럼 훌륭한 활약이로다",
    "7:2678:0": ", 훌륭한 싸움이었다!\n그 활약이야말로 나의 자랑이로다",
    "7:2679:0": "전공 제일도 수긍할 만한 활약\n",
    "7:2679:1": "의 싸움은 강하면서도 우아하도다",
    "7:2680:0": ", 감탄이 절로 나오는 활약이로다\n내 젊은 시절이 떠오르는구나!",
    "7:2681:0": "전공 제일이라니 더없이 경사스럽구나!\n",
    "7:2681:1": ", 역시 내가 기대한 대로군",
    "7:2682:0": "님, 참으로 훌륭하십니다!\n저도 큰 용기를 얻었습니다!",
    "7:2683:0": "님께서 전공 제일을 차지하셨다니 기쁩니다\n",
    "7:2683:1": "도 뒤를 따라야겠습니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S473", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
