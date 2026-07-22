#!/usr/bin/env python3
"""Build Base authoring segment 107 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S107.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s107", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1821:0": "우리 세력이나 종속 세력과 인접하지 않았습니다",
    "6:1822:0": "상대는 우리 가문에 종속되기를 거부하고 있습니다",
    "6:1823:0": "상대가 아직 강대하여 종속시킬 수 없습니다",
    "6:1824:0": "상대에 비해 우리 가문의 위신과 병력이 부족합니다",
    "6:1825:0": "교전 중이거나 교전한 지 얼마 되지 않은 세력과는 종속·신종 관계를 맺을 수 없습니다",
    "6:1826:0": "막부는 다른 가문의 산하에 들어갈 수 없습니다",
    "6:1827:0": "이미 상대와 주종 관계를 맺고 있습니다",
    "6:1828:0": "우리 가문은 다른 가문에 종속되어 있어 다른 세력에 신종할 수 없습니다",
    "6:1829:0": "독립 상태가 아닌 세력에는 신종할 수 없습니다",
    "6:1830:0": "다른 가문에 종속된 세력에는 신종할 수 없습니다",
    "6:1831:0": "우리 세력이나 종속 세력과 인접하지 않았습니다",
    "6:1832:0": "상대는 우리 가문의 신종 요청을 거부하고 있습니다",
    "6:1833:0": "상대는 우리 가문에 아직 여력이 있다고 보아 신종 의사를 믿지 않습니다",
    "6:1834:0": "우리 가문의 규모로는 신종하겠다고 해도\n믿어 주지 않습니다",
    "6:1835:0": "우리 가문이 막부를 열었습니다",
    "6:1836:0": "막부 세력에만 역직을 요청할 수 있습니다",
    "6:1837:0": "우리 가문은 막부 외의 세력에 신종하고 있습니다",
    "6:1838:0": "상대는 우리 가문과의 교섭을 거부하고 있습니다",
    "6:1839:0": "우리 가문이 취임할 수 있는 역직이 없습니다",
    "6:1840:0": "신용이 부족합니다",
    "6:1841:0": "교전 중이거나 교전한 지 얼마 되지 않아 거부하고 있습니다",
    "6:1842:0": "충분히 방어할 수 있는 상황이 아닙니다",
    "6:1843:0": "관직이 없어 조정과 접촉할 연줄이 없습니다",
    "6:1844:0": "취임할 수 있는 관직이 없습니다",
    "6:1845:0": "중개자를 맡을 수 있는 무장이 없습니다",
    "6:1846:0": "취임할 수 있는 관직에 자리가 나는 대로 임관할 예정입니다",
    "6:1847:0": "헌상할 금전이 부족합니다",
    "6:1848:0": "아시카가 가문만 실행할 수 있습니다",
    "6:1849:0": "다른 세력에 줄 수 있는 관직이 없습니다",
    "6:1850:0": "역직을 줄 수 있는 세력이 없습니다",
    "6:1851:0": "외교할 수 있는 세력이 없습니다",
    "6:1852:0": "다른 세력과 외교합니다",
    "6:1853:0": "이 세력과 외교합니다",
    "6:1854:0": "단교 상태인 세력입니다",
    "6:1855:0": "쇼군 가문 외의 먼 세력과는 외교할 수 없습니다",
    "6:1856:0": "우리 가문에 노골적인 적의를 드러내고 있습니다",
    "6:1857:0": "우리 가문에는 제안할 수 있는 교섭 재료가 없습니다",
    "6:1858:0": "이 세력과는 외교할 수 없습니다",
    "6:1859:0": "다른 가문에 종속된 세력과는 교섭할 수 없습니다",
    "6:1860:0": "그 세력과는 방금 외교했습니다.",
    "6:1860:1": "일 뒤에 다시 외교할 수 있습니다",
}

DYNAMIC_RUNTIME_COORDINATES = {"6:1860:0", "6:1860:1"}


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
                "segment": "base_msggame_B001_S107",
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
