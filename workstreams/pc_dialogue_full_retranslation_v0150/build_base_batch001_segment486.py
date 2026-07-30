#!/usr/bin/env python3
"""Build Base authoring segment 486 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S486.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s486", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:151:0": "철포 생산량이 늘었다! 이제 마음껏 쏠 수 있겠군!",
    "8:152:0": "철포 생산량이 늘었습니다. 훈련도 더 해야겠습니다",
    "8:153:0": "철포 생산량이 늘었습니다. 나머지는 맡겨 주십시오",
    "8:154:0": "철포 생산량이 늘었습니다",
    "8:155:0": "철포 생산량이 늘었습니다. 일이 한결 수월해지겠소!",
    "8:156:0": "낭보입니다. 철포 생산량이 늘었습니다",
    "8:157:0": "철포 생산량이 늘어납니다. 취급에는 주의해야겠군요",
    "8:158:0": "철포가 늘어나니 우리 가문은 더욱 번창하겠구나",
    "8:159:0": "철포 조달량이 이전보다 더 늘어날 듯합니다",
    "8:160:0": "철포 생산량이 늘었습니다. 훈련을 해야겠군요",
    "8:161:0": "철포가 늘어납니다. 취급에 주의합시다",
    "8:162:0": "철포 조달량이 이전보다 늘어날 듯합니다",
    "8:163:0": "의 영지가\n풍요로워졌습니다",
    "8:164:0": "후후, 또 한 걸음\n앞으로 나아갔습니다",
    "8:165:0": "보시옵소서. 제 영지는\n이토록 발전했사옵니다",
    "8:166:0": "제 영지가 발전한 모습은\n어떠십니까",
    "8:167:0": "제 영지가\n발전하였사옵니다!",
    "8:168:0": "참으로 풍요롭게\n변해 가는구나",
    "8:169:0": "좋아, 좋아! 내 영지도\n풍요로워지고 있구나",
    "8:170:0": "맡겨 주신 영지를\n훌륭히 발전시켰사옵니다",
}

STATIC_COORDINATES: set[str] = {
    *(f"8:{record_id}:0" for record_id in range(151, 163)),
    *(f"8:{record_id}:0" for record_id in range(164, 171)),
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S486", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
