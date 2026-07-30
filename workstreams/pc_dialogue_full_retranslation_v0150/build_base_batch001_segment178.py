#!/usr/bin/env python3
"""Build Base authoring segment 178 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S178.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s178", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3134:0": "이로써 전쟁은 그만두기로…\n부디 잘 부탁드리오",
    "6:3135:0": "이로써 전쟁은 끝일세…\n약조를 어기지 말게",
    "6:3136:0": "이로써 전쟁은 잠시 끝이군요\n다행이에요…",
    "6:3137:0": "이로써 전쟁은 잠시 끝이오\n부디 승복해 주시오",
    "6:3138:0": "이로써 전쟁은 잠시 그만두는 것으로…\n부디 약조를 어기지 마시오",
    "6:3139:0": "수락해 주어 감사하오\n서로 병사들을 쉬게 합시다",
    "6:3140:0": "이로써 전쟁은 잠시 끝이야\n…후우, 살았다",
    "6:3141:0": "이로써 전쟁은 끝입니다\n잊지 마시길 바랍니다",
    "6:3142:0": "이로써 전쟁은 끝이다\n약조를 어기지 않도록 부탁한다",
    "6:3143:0": "이로써 전쟁은 끝난 것이지요?\n백성들도 안도하겠군요",
    "6:3144:0": "오, 받아들이겠느냐!\n이로써 전쟁은 잠시 끝이로다",
    "6:3145:0": "이 또한 가문을 지키기 위해서다\n너무 모질게 대하진 말아 달라고",
    "6:3146:0": "이 또한 가문을 지키기 위함…\n아무쪼록 잘 부탁드리오",
    "6:3147:0": "가문을 지키기 위한 결단이다\n부끄러워할 까닭이 어디 있겠는가…",
    "6:3148:0": "이 또한 가문을 지키기 위함입니다…\n부디 잘 부탁드립니다",
    "6:3149:0": "이 또한 가문을 지키기 위함이오…\n부디 잘 부탁드리오",
    "6:3150:0": "…가문만 지킬 수 있다면 어떻게든 될 터\n부디 잘 보살펴 주시오",
    "6:3151:0": "이 또한 가문을 지키기 위함…\n부디 부탁드리오",
    "6:3152:0": "이 또한 가문을 지키기 위함이로다…\n부디 잘 부탁하네…",
    "6:3153:0": "이 또한 가문을 지키기 위함입니다…\n부디 잘 부탁드립니다…",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S178", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
