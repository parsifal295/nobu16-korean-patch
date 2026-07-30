#!/usr/bin/env python3
"""Build Base authoring segment 285 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S285.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s285", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4341:1": "은(는) 우리 가문에\n더욱 유익한 정책이 되",
    "6:4342:0": "다른 가문보다 앞서기 위해\n서둘러 「",
    "6:4342:1": "」의 개량에 착수하",
    "6:4343:0": ", 「",
    "6:4343:1": "」을(를) 개정해\n더 나은 정책으로 만들",
    "6:4344:0": "이번 개선을 반영하면\n",
    "6:4344:1": "은(는) 우리 가문에\n더욱 유익한 정책이 되",
    "6:4345:0": "알겠",
    "6:4345:1": "\n다른 가문보다 앞서기 위해\n서둘러 「",
    "6:4345:2": "」의 개량에 착수하",
    "6:4346:0": "와(과)의 동맹이 만료됩니다\n연장을 요청할 수도 있을 듯합니다\n동맹을 연장하시겠습니까?",
    "6:4347:0": "그럼 「",
    "6:4347:1": "」와(과)의 동맹을\n더 이어 나가도록 하지요",
    "6:4348:0": "적대 행위로 「",
    "6:4348:1": "」와(과)의 친선을 중단",
    "6:4349:0": "적대 행위로 「",
    "6:4349:1": "」와(과)의 신용이 실추",
    "6:4350:0": "이번 철에는 판매할 가보를\n준비하지 못했습니다",
    "6:4351:0": "이번 철에 준비한 가보는\n모두 팔렸습니다",
    "6:4352:0": "동맹을 맺은 우리 가문을 경계하여\n",
}

STATIC_COORDINATES: set[str] = {"6:4350:0", "6:4351:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S285", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
