#!/usr/bin/env python3
"""Build Base authoring segment 101 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S101.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s101", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1638:0": "와(과)",
    "6:1638:1": "의 결연이\n이루어졌으니, 두 가문 사이에는\n혼인으로 맺어진 굳은 동맹이 성립했습니다",
    "6:1639:0": "세력 전체의 금전·병량 세율을 변경할 수 있습니다",
    "6:1640:0": "세력 전체의 금전·병량 세율을 변경할 수 있습니다",
    "6:1641:0": "금전 세율을 변경합니다",
    "6:1642:0": "병량 세율을 변경합니다",
    "6:1643:0": "세력 전체의 각 부문 수준을 변경할 수 있습니다",
    "6:1644:0": "부문의 수준을 높입니다",
    "6:1645:0": "부문의 수준을 낮춥니다",
    "6:1646:0": "세율 변경을 확정합니다",
    "6:1647:0": "변경된 항목이 없습니다",
    "6:1648:0": "세율 변경을 확정하지 않았습니다\n변경 내용이 취소됩니다. 계속하시겠습니까?",
    "6:1649:0": "알겠습니다\n새 세율에 맞춰 준비하겠습니다",
    "6:1650:0": "금전 부족으로 모든 정책을 철회",
    "6:1651:0": "금전 부족으로 모든 정책을 철회",
    "6:1652:0": "금전 부족으로 정책을 유지할 수 없어\n모든 정책을 일단 중지했습니다\n서둘러 재검토해 주십시오",
    "6:1653:0": "돈이 모자라 정책을 유지할 수 없어서\n모든 정책을 일단 멈춰 뒀어!\n시행할 것만 추려야겠군",
    "6:1654:0": "금전 부족으로 정책을 유지할 수 없어\n모든 정책을 중지시켰습니다\n어서 재검토하시는 것이 좋겠습니다",
    "6:1655:0": "금전이 부족해 정책을 유지할 수 없으니\n일단 모든 정책을 중지해 두었소\n시행할 정책을 다시 살펴야겠구려",
    "6:1656:0": "금전 부족으로 정책이 무너지고 있습니다\n우선 정책을 중지해 두었습니다\n낭비를 줄이고 다시 검토합시다",
    "6:1657:0": "자금 사정이 어려워 정책을 이어 갈 수 없다\n지금은 정책을 중지할 수밖에 없군\n모두를 위해서도 서둘러 재검토해야겠다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "6:1638:0",
    "6:1638:1",
    "6:1644:0",
    "6:1645:0",
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
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
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
                "segment": "base_msggame_B001_S101",
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
