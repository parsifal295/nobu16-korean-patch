#!/usr/bin/env python3
"""Build Base batch 001 segment 06 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S06.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s06", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:163:0": "지배 중인 성의 성하에 조정의 권위를 보여 주는 시설이 없음",
    "2:164:0": "지배 중인 성의 성하에 조정의 권위를 보여 주는 시설이 있음",
    "2:165:0": "당주가 관직에 취임하지 않음",
    "2:166:0": "당주가 조정에서 맡은 관직:",
    "2:166:1": "임",
    "2:167:0": "조정과 연고가 있는 가문:",
    "2:167:1": "의 당주임",
    "2:168:0": "지배 중인 성의 성하에 종교·문화 등의 가치를 지닌 시설이 없음",
    "2:169:0": "지배 중인 성의 성하에 종교·문화 등의 권위를 드러내는 시설이 있음",
    "2:170:0": "일향종을 통솔하는 세력:",
    "2:170:1": "의 종주임",
    "2:171:0": "권위 있는 가문:",
    "2:171:1": "의 당주임",
    "2:172:0": "막부의 정당성을 드러내는 정책을 채택하지 않음",
    "2:173:0": "막부의 정당성을 드러내는 정책을 채택하고 있음",
    "2:174:0": "조정의 위광을 드러내는 정책을 채택하지 않음",
    "2:175:0": "조정의 위광을 드러내는 정책을 채택하고 있음",
    "2:176:0": "종교·문화 등으로 천하에 존재감을 드러내는 정책을 채택하지 않음",
    "2:177:0": "종교·문화 등으로 천하에 존재감을 드러내는 정책을 채택하고 있음",
    "2:178:0": "지배 중인 군에 종교·문화 등의 가치를 지닌 취락이 없음",
    "2:179:0": "지배 중인 군에 종교·문화 등의 권위를 드러내는 취락이 있음",
    "2:180:0": "우리 가문이 다스리는 성:",
    "2:180:1": "개",
}


STATIC_RUNTIME_NOT_REQUIRED = {
    "2:163:0",
    "2:164:0",
    "2:165:0",
    "2:168:0",
    "2:169:0",
    "2:172:0",
    "2:173:0",
    "2:174:0",
    "2:175:0",
    "2:176:0",
    "2:177:0",
    "2:178:0",
    "2:179:0",
}


DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS) - STATIC_RUNTIME_NOT_REQUIRED


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
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": (
                    "runtime_fragment_pending"
                    if coordinate in DYNAMIC_RUNTIME_COORDINATES
                    else "retranslated"
                ),
                "layout_review": "unchanged_from_current",
                "runtime_review": (
                    "pending" if coordinate in DYNAMIC_RUNTIME_COORDINATES else "not_required"
                ),
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context",
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
                "segment": "base_msggame_B001_S06",
                "decision_count": len(rows),
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
