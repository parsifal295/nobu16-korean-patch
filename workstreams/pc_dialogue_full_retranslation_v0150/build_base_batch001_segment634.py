#!/usr/bin/env python3
"""Build Base authoring segment 634 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S634.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s634", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
DUPLICATE_SUPPORT_FAILURE = "우리의 지원이 부족했던 탓에……!"
TRANSLATIONS = {
    "9:1797:0": "전사는 무사의 명예……\n장렬한 최후로다",
    "9:1798:0": "……",
    "9:1798:1": "의 전사를\n어떻게 승리로 이어 갈 것인가",
    "9:1799:0": "편히 잠드시오\n뒷일은 맡았소",
    "9:1800:0": "크으윽!\n죽게 두고 말다니……!",
    "9:1801:0": "의\n한을 풀겠습니다!",
    "9:1802:0": "―이놈!\n결코 용서하지 않겠다!",
    "9:1803:0": "의\n원한을 풀어 드리겠습니다",
    "9:1804:0": "만은\n내 손으로 베겠다!",
    "9:1805:0": "늦고 말았나…… 미안하다……!",
    "9:1806:0": DUPLICATE_SUPPORT_FAILURE,
    "9:1807:0": "아무리 후회해도 모자라겠구나……",
    "9:1808:0": "이(가) 좀 더 일찍 알아챘더라면……",
    "9:1809:0": DUPLICATE_SUPPORT_FAILURE,
    "9:1810:0": DUPLICATE_SUPPORT_FAILURE,
    "9:1811:0": DUPLICATE_SUPPORT_FAILURE,
    "9:1812:0": DUPLICATE_SUPPORT_FAILURE,
    "9:1813:0": "큭, 늦고 말았습니까……",
    "9:1814:0": "구하지 못하다니 원통하군……",
    "9:1815:0": "에게 힘이 조금만 더 있었더라면……",
    "9:1816:0": "송구하옵니다……",
    "9:1817:0": "의 힘으로 구출해 주고\n싶다만……",
    "9:1818:0": "이를 저버려서는\n겁쟁이라 비웃음을 사리라……",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1798:0",
    "9:1798:1",
    "9:1801:0",
    "9:1802:0",
    "9:1803:0",
    "9:1804:0",
    "9:1808:0",
    "9:1815:0",
    "9:1817:0",
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
                "segment": "base_msggame_B001_S634",
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
