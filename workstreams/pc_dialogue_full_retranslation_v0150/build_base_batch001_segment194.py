#!/usr/bin/env python3
"""Build Base authoring segment 194 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S194.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s194", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3388:0": "뭐라고…!?\n…언젠가 후회하게 될 것이다",
    "6:3389:0": "후계자가 군단장이므로\n군단을 해산하고 다이묘 직할로 전환합니다\n계속하시겠습니까?",
    "6:3390:0": "혈족이 아닌 무장이 후계자로 선택되었습니다\n혈족 무장의 충성이 낮아집니다\n계속하시겠습니까?",
    "6:3391:0": ", 뒷일은 내게",
    "6:3391:1": "!\n이 손으로",
    "6:3391:2": "을(를) 반드시 일으켜 세우고\n훌륭한 당주가 되어 보이겠",
    "6:3391:3": "!",
    "6:3392:0": "내가 당주라…알겠어,",
    "6:3392:1": "에게 지지 않는\n훌륭하고 대단한 다이묘가 되어 보이겠다!\n똑똑히 지켜봐 줘!",
    "6:3393:0": "알겠사옵",
    "6:3393:1": ", 뒷일은",
    "6:3393:2": ".\n반드시",
    "6:3393:3": "의 기대에 부응하여\n",
    "6:3393:4": "을(를) 끝까지 지켜 내 보이겠",
    "6:3394:0": "잘 알겠사옵니다,",
    "6:3394:1": "에게 지지 않도록\n내 무용으로 반드시",
    "6:3394:2": "의 이름을\n천하에 떨쳐 보이겠",
    "6:3395:0": "이 판단이 틀리지 않았음을\n이 한 생을 걸고",
    "6:3395:1": "을(를)\n일으켜 세워 증명",
    "6:3396:0": "의 이름은 무겁지만 자랑스럽기도 하여\n절로 자세가 바로 서는 기분",
}

STATIC_COORDINATES = {"6:3388:0", "6:3389:0", "6:3390:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S194", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
