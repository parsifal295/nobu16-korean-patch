#!/usr/bin/env python3
"""Build Base authoring segment 154 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S154.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s154", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2821:1": "와(과)의 맹약은 해소한다",
    "6:2822:0": "알겠습니다\n",
    "6:2822:1": "와(과)의 맹약은 끊도록 하지요",
    "6:2823:0": "어쩔 수 없군…\n",
    "6:2823:1": "와(과)의 맹약은 끊도록 하겠소",
    "6:2824:0": "오오,",
    "6:2824:1": "와(과)는 단교하는 거군!\n고맙다!",
    "6:2825:0": "결단해 주어 고맙소\n귀공의 성의를 기억해 두겠소",
    "6:2826:0": "와(과)의 맹약을 끊은 판단은\n현명하도다",
    "6:2827:0": "와(과)의 맹약을 끊겠다는 결심\n결코 잊지 않겠소이다",
    "6:2828:0": "와(과)의 동맹을 끊겠다는 각오\n깊이 감사히 여기노라",
    "6:2829:0": "와(과) 단교해 주겠는가\n깊이 감사하오",
    "6:2830:0": "보다 우리 가문을 택해 주다니\n고마운 일이로다",
    "6:2831:0": "와(과) 단교해 주겠는가!\n이야말로 참으로 영단이로다",
    "6:2832:0": "와(과)의 동맹을 백지로 돌리시겠다니…\n현명한 선택이라 생각하옵니다",
    "6:2833:0": "와(과)의 맹약을 끊어 주겠는가\n감사하노라!",
    "6:2834:0": "와(과)의 단교에\n깊이 감사드리옵니다",
    "6:2835:0": "와(과)의 맹약을 끊는다니\n깊이 감사히 여기노라",
    "6:2836:0": "어쩔 수 없지\n",
    "6:2836:1": "와(과)는 단교할 수밖에 없겠군",
}

STATIC_COORDINATES = {"6:2825:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S154", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
