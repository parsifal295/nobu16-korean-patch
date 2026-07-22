#!/usr/bin/env python3
"""Build Base authoring segment 106 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S106.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s106", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1781:0": "친선에 필요한 금전이 부족합니다",
    "6:1782:0": "중개자를 맡을 수 있는 무장이 없습니다",
    "6:1783:0": "어느 세력도 우리 가문과 교섭할 뜻이 없습니다",
    "6:1784:0": "어느 세력과도 교섭할 수 있는 항목이 없습니다",
    "6:1785:0": "이미 장기 동맹을 맺고 있습니다",
    "6:1786:0": "우리 가문이 종속 중이므로 동맹을 맺을 수 없습니다",
    "6:1787:0": "상대가 종속 중이므로 동맹을 맺을 수 없습니다",
    "6:1788:0": "상대는 우리 가문과의 교섭을 거부하고 있습니다",
    "6:1789:0": "신용이 부족합니다",
    "6:1790:0": "교전 중이거나 교전한 지 얼마 되지 않은 세력과는 동맹을 맺을 수 없습니다",
    "6:1791:0": "다른 가문의 요청으로 파견한 원군이 상대와 교전하고 있습니다",
    "6:1792:0": "신종한 대상 외에는 원군을 요청할 수 없습니다",
    "6:1793:0": "상대가 우리 가문 외의 세력에 신종하고 있어 원군을 요청할 수 없습니다",
    "6:1794:0": "동맹 또는 종속 관계가 아니면 원군을 요청할 수 없습니다",
    "6:1795:0": "이미 상대에게 원군을 요청했습니다",
    "6:1796:0": "원군을 요청할 수 있는 성이 없습니다",
    "6:1797:0": "상대는 원군을 보낼 수 있는 상태가 아닙니다",
    "6:1798:0": "상대는 우리 가문과의 교섭을 거부하고 있습니다",
    "6:1799:0": "신용이 부족합니다",
    "6:1800:0": "신종한 대상 외에는 중개를 요청할 수 없습니다",
    "6:1801:0": "상대가 종속 중이므로 중개를 요청할 수 없습니다",
    "6:1802:0": "동맹 또는 종속 관계가 아니면 중개를 요청할 수 없습니다",
    "6:1803:0": "상대가 정전을 중개해 줄 수 있는 세력이 없습니다",
    "6:1804:0": "상대는 우리 가문과의 교섭을 거부하고 있습니다",
    "6:1805:0": "신용이 부족합니다",
    "6:1806:0": "이미 혼인 관계를 맺고 있습니다",
    "6:1807:0": "우리 가문이 종속 중이므로 혼인 동맹을 맺을 수 없습니다",
    "6:1808:0": "동맹 관계가 아니면 혼인 동맹을 맺을 수 없습니다",
    "6:1809:0": "상대가 종속 중이므로 혼인 동맹을 맺을 수 없습니다",
    "6:1810:0": "혼인할 수 있는 공주나 무장이 없습니다",
    "6:1811:0": "상대는 우리 가문과의 교섭을 거부하고 있습니다",
    "6:1812:0": "신용이 부족합니다",
    "6:1813:0": "상대와 파기할 만한 외교 관계가 없습니다",
    "6:1814:0": "원군 요청 기간 중이므로 파기할 수 없습니다",
    "6:1815:0": "상대 또는 상대에게 종속된 세력의 영내에\n우리 가문의 부대가 있거나 진입하려 하고 있습니다",
    "6:1816:0": "막부는 다른 가문의 산하에 들어갈 수 없습니다",
    "6:1817:0": "이미 상대와 주종 관계를 맺고 있습니다",
    "6:1818:0": "우리 가문이 신종 중이므로 다른 가문을 종속시킬 수 없습니다",
    "6:1819:0": "다른 가문과 동맹·종속·신종 관계를 맺은 세력은\n종속시킬 수 없습니다",
    "6:1820:0": "너무 멀리 있어 종속시킬 수 없습니다",
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
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
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
                "segment": "base_msggame_B001_S106",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
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
