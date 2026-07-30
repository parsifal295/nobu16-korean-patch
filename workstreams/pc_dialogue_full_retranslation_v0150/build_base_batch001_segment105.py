#!/usr/bin/env python3
"""Build Base authoring segment 105 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S105.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s105", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1741:0": "원군의 목표가 될 성을 선택하십시오",
    "6:1742:0": "이 세력을\n",
    "6:1742:1": "의 원군 목표로 지정합니다",
    "6:1743:0": "제안할 가보를 선택하십시오",
    "6:1744:0": "제안할 관직을 선택하십시오",
    "6:1745:0": "단교할 세력을 선택하십시오",
    "6:1746:0": "교섭의 대가로 이 세력과 단교합니다",
    "6:1747:0": "군이나 성을 주고받으면\n자동으로 6개월간 정전이 체결됩니다.\n계속하시겠습니까?",
    "6:1748:0": "원군이나 중개 교섭에 필요한 신용입니다",
    "6:1749:0": "동맹 교섭에 필요한 신용입니다",
    "6:1750:0": "혼인 동맹 교섭에 필요한 신용입니다",
    "6:1751:0": "혼인 동맹이나 역직 교섭에 필요한 신용입니다",
    "6:1752:0": "동맹이나 종속 관계가 아니면 원군이나 중개를 요청할 수 없습니다",
    "6:1753:0": "동맹 관계가 아니면 혼인 동맹을 제안할 수 없습니다",
    "6:1754:0": "쇼군 가문 외의 먼 세력과는 외교할 수 없습니다",
    "6:1755:0": "우리 가문은 다른 가문에 종속되어 있어 종주 가문 외에는 외교할 수 없습니다",
    "6:1756:0": "상대가 다른 세력에 신종하고 있어 외교할 수 없습니다",
    "6:1757:0": "상대는 우리 가문의 친선을 거부하고 있습니다",
    "6:1758:0": "친선에 필요한 금전이 부족합니다",
    "6:1759:0": "중개자를 맡을 수 있는 무장이 없습니다",
    "6:1760:0": "우리 가문은 다른 가문에 종속되어 있어 종주 가문 외에는 외교할 수 없습니다",
    "6:1761:0": "상대가 다른 세력에 신종하고 있어 외교할 수 없습니다",
    "6:1762:0": "상대는 우리 가문과 교섭할 뜻이 없습니다",
    "6:1763:0": "교섭할 수 있는 항목이 없습니다",
    "6:1764:0": "막부 세력에는 역직을 줄 수 없습니다",
    "6:1765:0": "다른 가문에 종속된 세력에는 역직을 줄 수 없습니다",
    "6:1766:0": "상대는 우리 가문과의 교섭을 거부하고 있습니다",
    "6:1767:0": "외교 자세가 더는 개선되지 않습니다",
    "6:1768:0": "이 세력에 줄 수 있는 역직이 없습니다",
    "6:1769:0": "교전 중이거나 교전한 지 얼마 되지 않았습니다",
    "6:1770:0": "공물의 효과는 앞으로",
    "6:1770:1": "개월간 지속됩니다",
    "6:1771:0": "개월간 동맹 체결을 제안합니다",
    "6:1772:0": "성 공략을 위한 원군을 요청합니다",
    "6:1773:0": "지정 세력과",
    "6:1773:1": "개월간 정전 중개를 의뢰합니다",
    "6:1774:0": "혼인 동맹 체결을 제안합니다",
    "6:1775:0": "외교 관계를 파기합니다",
    "6:1776:0": "우리 가문에 종속하도록 권고합니다",
    "6:1777:0": "상대에게 신종을 청합니다",
    "6:1778:0": "막부에 역직 수여를 요청합니다",
    "6:1779:0": "우리 세력이나 종속 세력의 성을 방어해 달라고 요청합니다",
    "6:1780:0": "어느 세력도 우리 가문과 친선할 뜻이 없습니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "6:1742:0",
    "6:1742:1",
    "6:1770:0",
    "6:1770:1",
    "6:1771:0",
    "6:1773:0",
    "6:1773:1",
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
                "segment": "base_msggame_B001_S105",
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
