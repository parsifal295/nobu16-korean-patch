#!/usr/bin/env python3
"""Build Base authoring segment 184 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S184.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s184", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3242:0": "뭐라, 우리와 단교할 셈인가",
    "6:3243:0": "뭐라…우리와 단교하다니 어리석군",
    "6:3244:0": "말도 안 됩니다!\n우리와 단교하겠다는 겁니까!",
    "6:3245:0": "뭐라…우리와 단교할 셈인가",
    "6:3246:0": "어리석구나, 우리와 단교하겠다는 것이냐!",
    "6:3247:0": "호오, 우리와 단교하겠다고…\n언젠가 후회하게 될 것이다",
    "6:3248:0": "뭐라, 우리와 단교하겠다는 것인가!",
    "6:3249:0": "그럴 수가, 이렇게 갑자기 단교하다니…!",
    "6:3250:0": "말도 안 돼, 단교하겠다고!",
    "6:3251:0": "아아…이리도 매정하실 수가…",
    "6:3252:0": "뭐라, 우리와 단교하겠다는 것인가!",
    "6:3253:0": "좋아\n",
    "6:3253:1": "을(를) 함락시켜 주마!",
    "6:3254:0": "알겠소\n",
    "6:3254:1": "을(를) 반드시 함락시키겠소",
    "6:3255:0": "잘 알겠소\n",
    "6:3255:1": "을(를) 함락시켜 드리겠소",
    "6:3256:0": "알겠습니다\n",
    "6:3256:1": "을(를) 공략해 보이겠습니다",
    "6:3257:0": "알겠소\n",
}

STATIC_COORDINATES = {
    "6:3242:0", "6:3243:0", "6:3244:0", "6:3245:0", "6:3246:0", "6:3247:0",
    "6:3248:0", "6:3249:0", "6:3250:0", "6:3251:0", "6:3252:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S184", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
