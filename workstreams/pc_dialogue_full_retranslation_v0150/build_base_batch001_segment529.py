#!/usr/bin/env python3
"""Build Base authoring segment 529 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S529.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s529", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:718:0": "백성의 불만에 불을 지르는\n자가 나타나면 잇키가 일어나겠구먼…",
    "8:719:0": "백성들이 불안해하고 있습니다\n다른 가문의 선동을 받는다면…",
    "8:720:0": "잇키가 일어날 수도 있겠군\n조략을 경계해야 한다",
    "8:721:0": "다른 가문의 선동으로\n잇키가 일어날 수도 있습니다",
    "8:722:0": "위기는 벗어났습니다만\n방심은 금물이로군요",
    "8:723:0": "백성의 신뢰가 조금은\n돌아온 모양이긴 한데…",
    "8:724:0": "당장 잇키가 일어날 고비는\n넘긴 것인가…",
    "8:725:0": "잇키가 일어나지 않을 뿐이지…\n안정되었다고 하긴 어려워",
    "8:726:0": "잇키는 피했습니다만…\n아직 앞일을 장담할 수 없는 상황입니다",
    "8:727:0": "영민들의 눈에서\n살기가 조금 가셨사옵니다",
    "8:728:0": "잇키의 위기는 넘겼으나\n아직 안심하기에는 이르다",
    "8:729:0": "최악의 상황은 벗어났지만\n백성의 움직임을 주시해야겠군",
    "8:730:0": "마을 사람들의 노여움이… 조금은\n가라앉은 듯하구먼…",
    "8:731:0": "백성의 신뢰가 조금 회복되어…\n우선은 안심해도 되겠지요",
    "8:732:0": "잇키의 위기는 지나갔다\n그러나 계속 조심할 필요가 있다",
    "8:733:0": "위기는 넘겼습니다만\n아직 안심할 수 없습니다",
    "8:734:0": "백성들의 분노에 찬 탄원서가…\n잇키가 일어나는 것도 시간문제입니다",
    "8:735:0": "백성이 으르렁대고 있어…\n이거 난리가 나겠는데…",
    "8:736:0": "백성의 불만이 극에 달해\n그야말로 일촉즉발…",
    "8:737:0": "백성들의 움직임이 심상치 않다…\n잇키가 일어날 수도 있겠어",
}

STATIC_COORDINATES = set(TRANSLATIONS)


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S529", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
