#!/usr/bin/env python3
"""Build Base authoring segment 76 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S76.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s76", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1181:0": "철포를 매각할 수 없습니다",
    "6:1182:0": "이번 철에는 상인이 가보를 들여오지 않았습니다",
    "6:1183:0": "이번 철에 입고된 가보는 모두 팔렸습니다",
    "6:1184:0": "매각할 수 있는 가보가 없습니다",
    "6:1185:0": "더 이상 금전을 보유할 수 없습니다",
    "6:1186:0": "구매할 금전이 부족합니다",
    "6:1187:0": "매각할 만큼 병량이 없습니다",
    "6:1188:0": "으로(로) 개발합니다\n",
    "6:1188:1": "※개발 완료까지",
    "6:1188:2": "일이 걸립니다",
    "6:1189:0": "변경을 취소합니다\n정말 취소하시겠습니까?",
    "6:1190:0": "설정을 변경할 지침을 선택하십시오",
    "6:1191:0": "설정을 확정하고 군단 방침 화면으로 이동합니다",
    "6:1192:0": "변경을 취소합니다\n정말 취소하시겠습니까?",
    "6:1193:0": "지침을 변경하면 진행 중인 건의를 철회하고\n새 지침에 따른 제안을 가신에게 요청합니다\n계속하시겠습니까?",
    "6:1194:0": "알겠습니다\n모두에게 새 목표를 전하고 오겠습니다",
    "6:1195:0": "적대 세력의 성만 목표로 삼을 수 있습니다",
    "6:1196:0": "너무 멀어서 목표로 삼을 수 없습니다",
    "6:1197:0": "너무 멀어서 목표로 삼을 수 없습니다",
    "6:1198:0": "아군 세력은 목표로 삼을 수 없습니다",
    "6:1199:0": "우선",
    "6:1199:1": "을(를) 목표로 삼지요\n당장이라도 공격할 수 있습니다",
    "6:1200:0": "우선",
    "6:1200:1": "을(를) 목표로 삼지요\n당장이라도 공격할 수 있습니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "6:1188:0",
    "6:1188:1",
    "6:1188:2",
    "6:1199:0",
    "6:1199:1",
    "6:1200:0",
    "6:1200:1",
}


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
                "segment": "base_msggame_B001_S76",
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
