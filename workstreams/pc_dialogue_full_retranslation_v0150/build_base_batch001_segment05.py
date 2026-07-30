#!/usr/bin/env python3
"""Build Base batch 001 segment 05 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S05.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s05", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:147:0": "공략 대상:",
    "2:147:1": "세력이 멸망하여 공략 방침을 해제했습니다",
    "2:148:0": "공략 대상:",
    "2:148:1": "세력과 동맹을 맺어 공략 방침을 해제했습니다",
    "2:149:0": "공략 대상:",
    "2:149:1": "세력으로 향하는 진군로가 사라져 공략 방침을 해제했습니다",
    "2:150:0": "공략 대상:",
    "2:150:1": "세력과 정전하여 공략 방침을 해제했습니다",
    "2:151:0": "공략 대상:",
    "2:151:1": "을 함락했습니다",
    "2:152:0": "의 소속 세력이 바뀌어 공략 대상에서 해제되었습니다",
    "2:153:0": "의 소속 세력이 아군이 되어 공략 대상에서 해제되었습니다",
    "2:154:0": "방면의 진군로가 사라져 공략 대상에서 해제되었습니다",
    "2:155:0": "의 소속 세력과 정전하여 공략 대상에서 해제되었습니다",
    "2:156:0": "지배 중인 성의 성하에 막부의 권위를 보여 주는 시설이 없음",
    "2:157:0": "지배 중인 성의 성하에 막부의 권위를 보여 주는 시설이 있음",
    "2:158:0": "당주가 정이대장군으로서 무사들의 수장임",
    "2:159:0": "당주가 막부의 관직에 취임하지 않음",
    "2:160:0": "당주가 막부에서 맡은 관직:",
    "2:160:1": "임",
    "2:161:0": "막부를 연 시조의 계통을 잇는 가문:",
    "2:161:1": "의 당주임",
    "2:162:0": "막부와 연고가 있는 가문:",
    "2:162:1": "의 당주임",
}


STATIC_RUNTIME_NOT_REQUIRED = {
    "2:156:0",
    "2:157:0",
    "2:158:0",
    "2:159:0",
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
                "segment": "base_msggame_B001_S05",
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
