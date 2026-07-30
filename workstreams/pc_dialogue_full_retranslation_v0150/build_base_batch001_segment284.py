#!/usr/bin/env python3
"""Build Base authoring segment 284 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S284.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s284", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4328:1": "」을(를) 수행 중입니다\n혼인 동맹을 맺으면 중단됩니다\n정말 괜찮으시겠습니까?",
    "6:4329:0": "공격 측 아군 세력에는 방어를 의뢰할 수 없습니다",
    "6:4330:0": "방어를 의뢰할 수 있는 성이 없습니다",
    "6:4331:0": "교전 중인 세력이 아니면 정전할 수 없습니다",
    "6:4332:0": "으로(로)는 중재할 수 없을 만큼 강대한 세력입니다",
    "6:4333:0": "이(가) 교전 중인 세력과는 정전할 수 없습니다",
    "6:4334:0": "그럼 곧바로, 「",
    "6:4334:1": "」 발령을 위한\n준비에 착수하겠",
    "6:4335:0": "한시라도 빨리 「",
    "6:4335:1": "」을(를) 발령해\n다른 가문보다 앞지르",
    "6:4335:2": "인가?",
    "6:4336:0": "의 발령이 이루어지면\n우리 가문의 천하가 또 한 걸음 가까워질 터…",
    "6:4337:0": "알겠",
    "6:4337:2": "의 발령 준비에\n곧바로 착수하",
    "6:4338:0": "다른 가문보다 앞서기 위해\n한시라도 빨리 「",
    "6:4338:1": "」을(를) 발령해\n반드시 이루어 내",
    "6:4339:0": "의 발령은 훌륭한 방안인 듯하",
    "6:4339:1": "\n서둘러 준비를 갖추",
    "6:4340:0": "을(를) 개정해\n더 나은 정책으로 발령하",
    "6:4341:0": "이번 개선을 반영하면\n",
}

STATIC_COORDINATES: set[str] = {"6:4329:0", "6:4330:0", "6:4331:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S284", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
