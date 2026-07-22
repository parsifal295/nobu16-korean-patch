#!/usr/bin/env python3
"""Build Base authoring segment 160 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S160.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s160", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2900:1": "의 농간인가",
    "6:2901:0": "이(가) 맹약을 파기한다고!?\n이놈,", "6:2901:1": "의 농간인가!",
    "6:2902:0": "이(가) 맹약을 깨다니\n", "6:2902:1": "은(는) 제법 수완이 좋은 자인 듯하다…",
    "6:2903:0": "이(가) 단교해 왔구나!\n", "6:2903:1": "의 농간이겠지…",
    "6:2904:0": "이(가) 맹약을 파기한다니…!?\n큭,", "6:2904:1": "이(가) 뒤에서 조종한 것이\n틀림없군요",
    "6:2905:0": "이(가) 동맹을 파기한다고!?\n큭,", "6:2905:1": "의 농간인가\n용서하지 않겠다!",
    "6:2906:0": "에서 단교 통보가…?\n", "6:2906:1": "에게 당하고 말았군요…",
    "6:2907:0": "이(가) 맹약을 파기했다고!?\n큭,", "6:2907:1": "의 농간인가!",
    "6:2908:0": "의 녀석이\n우리를 배신했겠다!",
    "6:2909:0": "이놈,", "6:2909:1": "!\n우리를 배신하는가!",
    "6:2910:0": "으윽…", "6:2910:1": "놈!\n우리를 배신했구나!",
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S160", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
