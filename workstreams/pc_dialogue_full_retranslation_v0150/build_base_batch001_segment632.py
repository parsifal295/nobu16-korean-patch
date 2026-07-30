#!/usr/bin/env python3
"""Build Base authoring segment 632 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S632.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s632", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1761:0": "주군을 지키지 못하고서\n무예가 무슨 소용인가……!",
    "9:1762:0": "가문이 흔들리겠군……",
    "9:1763:0": "주군을 속절없이\n잃고 말다니……",
    "9:1764:0": "원통하도다……\n원통하기 그지없도다……!",
    "9:1765:0": "아무것도……\n하지 못했다니……",
    "9:1766:0": "이 무슨 꼴인가……\n한심하구나……",
    "9:1767:0": "아무것도 하지 못해…… 원통합니다",
    "9:1768:0": "이럴 리가……",
    "9:1769:0": "인정 못 해……!\n",
    "9:1769:1": "은(는) 살아 있어",
    "9:1770:0": "훌륭한 최후로다……\n일족으로서 자랑스럽구나",
    "9:1771:0": "의 죽음을\n헛되게 하지 않으리……",
    "9:1772:0": "이(가) 죽었다니요?\n믿을 수 없습니다……",
    "9:1773:0": "이(가) 세상을 떠났는가……",
    "9:1774:0": "말도 안 돼……\n",
    "9:1774:1": "이(가)……!",
    "9:1775:0": "이(가)……?\n어찌 이리 허망한가……",
    "9:1776:0": "……!\n나를 두고 떠나지 마라!",
    "9:1777:0": "그럴 수가……!?\n",
    "9:1777:1": "이(가)……",
    "9:1778:0": "이(가)!?\n거짓말이다…… 인정 못 한다……",
    "9:1779:0": "설마―",
    "9:1779:1": "이(가)\n세상을 떠나다니……",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1769:0",
    "9:1769:1",
    "9:1771:0",
    "9:1772:0",
    "9:1773:0",
    "9:1774:0",
    "9:1774:1",
    "9:1775:0",
    "9:1776:0",
    "9:1777:0",
    "9:1777:1",
    "9:1778:0",
    "9:1779:0",
    "9:1779:1",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
        static = coordinate in STATIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required" if static else "pending",
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available"
                ),
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
                "segment": "base_msggame_B001_S632",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
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
