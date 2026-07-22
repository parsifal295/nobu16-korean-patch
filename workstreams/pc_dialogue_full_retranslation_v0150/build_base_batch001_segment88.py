#!/usr/bin/env python3
"""Build Base authoring segment 88 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S88.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s88", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1381:0": "현재 군단을 신설할 수 없습니다",
    "6:1382:0": "군단을 맡길 성주가 부재중이거나 교전 중입니다",
    "6:1383:0": "편성할 수 있는 군단이 없습니다",
    "6:1384:0": "해산할 수 있는 군단이 없습니다",
    "6:1385:0": "을(를) 해산합니다\n정말 해산하시겠습니까?",
    "6:1386:0": "적대 행위를 제한하지 않음",
    "6:1387:0": "조략은 제한하지 않으며 군사 행동은 금지",
    "6:1388:0": "방어를 제외한 모든 적대 행위 금지",
    "6:1389:0": "모든 판단을 군단장에게 맡깁니다",
    "6:1390:0": "선택한 성을 공격합니다",
    "6:1391:0": "선택한 세력을 공격합니다",
    "6:1392:0": "이 군단에서는 모든 건의가 발생합니다",
    "6:1393:0": "이 군단에서는 물자에 관한 건의만 발생합니다",
    "6:1394:0": "이 군단에서는 무장에 관한 건의만 발생합니다",
    "6:1395:0": "이 군단에서는 건의가 전혀 발생하지 않습니다",
    "6:1396:0": "공략한 영토는 이 군단이 지배합니다",
    "6:1397:0": "공략한 영토는 다이묘 군단이 지배합니다",
    "6:1398:0": "공략한 영토가 인접하면 이 군단이 지배합니다",
    "6:1399:0": "군단장을 변경할 수 없습니다",
    "6:1400:0": "군단장을 변경합니다",
}

DYNAMIC_RUNTIME_COORDINATES = {"6:1385:0"}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S88",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
