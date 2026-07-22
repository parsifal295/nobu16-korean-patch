#!/usr/bin/env python3
"""Build Base authoring segment 493 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S493.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s493", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
BOUNTY_GROUP = (
    "을(를) 비롯해 풍작을 맞은\n",
    "개 군에서\n병량 수입이 증가",
    "\n백성들도 기뻐하고",
)
TRANSLATIONS = {
    "8:251:0": "병량 고갈",
    "8:252:0": "우리 군단의 병량이 바닥났습니다\n이대로 행군을 계속하면\n병사들이 낙오하고 말 것입니다",
    "8:253:0": ", 기뻐해",
    "8:253:1": "\n올해는 풍작",
    "8:253:2": "\n쌀이 곳간에 다 들어가지 않",
    "8:254:0": "놀랍게도 올해는 풍작",
    "8:254:1": "!\n이 또한",
    "8:254:2": "의 위광 덕분이니\n참으로 기쁜 일",
    "8:255:0": "아무래도 올해는 풍작",
    "8:255:1": "\n탐스러운 벼 이삭을 앞에 두고\n백성들도 기뻐하고",
    "8:256:0": "올해는 풍작",
    "8:256:1": "\n이 정도면 당분간\n병량 걱정은 끝",
    "8:257:0": ", 봐",
    "8:257:1": "\n풍작을 맞은 전답은 황금빛 들판과 같은\n모습",
    **{
        f"8:{record_id}:{literal_id}": translation
        for record_id in range(258, 260)
        for literal_id, translation in enumerate(BOUNTY_GROUP)
    },
}

STATIC_COORDINATES = {"8:251:0", "8:252:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S493", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
