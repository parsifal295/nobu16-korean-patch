#!/usr/bin/env python3
"""Build Base authoring segment 253 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S253.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s253", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4020:0": "공략",
    "6:4020:1": "\n우리 가문의 병력이 뒤처져 있",
    "6:4021:0": "공략 목표로 삼을 성을 선택해",
    "6:4022:0": "노릴 곳은",
    "6:4022:1": "!\n적을 압도하여 천하포무의 초석으로 삼으리라!",
    "6:4023:0": "운은 하늘에 있고, 갑옷은 가슴에 있으며\n공은 발에 있다…\n",
    "6:4023:1": "을(를) 공략할 채비를 갖춰라",
    "6:4024:0": "만사 서두르지 말지어다\n",
    "6:4024:1": "을(를) 공략하기에 앞서\n각자 만전의 군비를 갖추어라",
    "6:4025:0": "계책이 많으면 이기고, 적으면 진다\n",
    "6:4025:1": "을(를) 공략하기에 앞서\n충분히 계책을 마련해 두자",
    "6:4026:0": "자, 대비하라. 당당한 진군으로\n",
    "6:4026:1": "의 간담을 서늘하게 하리라",
    "6:4027:0": "자, 모두들! 독안룡의 출전 준비다!\n",
    "6:4027:1": "따위는 단숨에 삼켜 주마",
    "6:4028:0": "반석 같은 대비야말로 승전의 근본\n자, 각자",
    "6:4028:1": "을(를) 공략할 채비를 갖춰라",
    "6:4029:0": "다음 사냥감은",
    "6:4029:1": "이다!\n체스토, 채비를 서둘러라!",
    "6:4030:0": "갑주를 챙겨라, 창을 들어라!\n",
}

STATIC_COORDINATES: set[str] = set()


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S253", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
