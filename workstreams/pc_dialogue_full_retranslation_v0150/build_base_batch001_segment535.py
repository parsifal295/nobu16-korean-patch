#!/usr/bin/env python3
"""Build Base authoring segment 535 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S535.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s535", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:838:0": "「",
    "8:838:1": "」을(를)\n최대 수준까지 끌어올렸소이다!",
    "8:839:0": "「",
    "8:839:1": "」이(가)\n최대 수준에 이르렀습니다!",
    "8:840:0": "「",
    "8:840:1": "」을(를)\n최대 수준까지 끌어올렸다!",
    "8:841:0": "「",
    "8:841:1": "」을(를)\n최대 수준까지 끌어올렸습니다",
    "8:842:0": "할 수 있는 일은\n모두 마쳤사옵니다",
    "8:843:0": "할 수 있는 일은 죄다\n해냈다고!",
    "8:844:0": "지금 할 수 있는 일은\n모두 마쳤소이다",
    "8:845:0": "할 수 있는 작업은 다 했다\n지금으로서는 여기까지다",
    "8:846:0": "가능한 조치는 모두 취했습니다\n이제는 정책에 달렸군요",
    "8:847:0": "해야 할 바는 다 해 두었으니\n이제는 정책에 달렸느니라",
    "8:848:0": "흠… 지금으로서는\n할 수 있는 일을 다 했나",
    "8:849:0": "이것이 지금으로서는\n할 수 있는 최대한이군요",
    "8:850:0": "당장 할 수 있는 일은\n다 마친 듯하구나",
    "8:851:0": "이로써 작업은\n일단락되었군요",
    "8:852:0": "좋아! 할 수 있는 만큼\n다 해냈다",
    "8:853:0": "할 수 있는 일은 모두\n마친 듯하군요",
}

STATIC_COORDINATES = {
    f"8:{record_id}:0"
    for record_id in range(842, 854)
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S535", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
