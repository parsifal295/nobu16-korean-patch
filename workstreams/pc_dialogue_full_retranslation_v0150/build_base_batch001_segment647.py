#!/usr/bin/env python3
"""Build Base authoring segment 647 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S647.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s647", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2065:0": "좋은 수로다…… 그러면\n적의 약점을 파고들자",
    "9:2066:0": "훌륭한 전법이로다\n자, 그 열매를 함께 거두자",
    "9:2067:0": "적은 약해졌다\n단숨에 쓸어버려라!",
    "9:2068:0": "큰 도움이 됩니다!\n단숨에 공격합시다!",
    "9:2069:0": "좋아!\n공세로 나선다!",
    "9:2070:0": "이대로라면 이길 수 있습니다\n감사합니다",
    "9:2071:0": "이 틈을 타\n공격해 들어가라!",
    "9:2072:0": "무작정 힘으로만 밀어붙인 게\n아니었다 이거냐……!",
    "9:2073:0": "크윽…… 히, 힘이……!",
    "9:2074:0": "적이지만\n영리한 수법이군……",
    "9:2075:0": "과연……\n생각이 깊군요",
    "9:2076:0": "이놈!\n제법 교묘한 수를……!",
    "9:2077:0": "이, 이것은……\n",
    "9:2077:1": "의 소행인가……",
    "9:2078:0": "이래서는……!\n비겁하구나!",
    "9:2079:0": "으으으……\n갑자기 늙은 기분이로다",
    "9:2080:0": "적도\n제법 성가시게 하는군요",
    "9:2081:0": "이, 이까짓\n일로……!",
    "9:2082:0": "설마\n이런 수로 나올 줄이야……",
    "9:2083:0": "실력을…… 발휘할 수가 없다……!",
    "9:2084:0": "전력이 상당히 깎였군……",
    "9:2085:0": "크으윽……!\n이 무슨 위력이냐!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2077:0",
    "9:2077:1",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S647", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
