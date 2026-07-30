#!/usr/bin/env python3
"""Build Base authoring segment 637 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S637.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s637", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1861:0": "주군!\n무사하시옵니까!?",
    "9:1862:0": "안심하십시오\n",
    "9:1862:1": "이(가) 만회하겠습니다!",
    "9:1863:0": "심려하지 마시고\n맡겨 주시옵소서",
    "9:1864:0": "주군께서 패하시다니……\n이제 끝이다……",
    "9:1865:0": "한발 늦었는가……",
    "9:1866:0": "끄으윽……",
    "9:1867:0": "내 무력함이 원망스럽구나……",
    "9:1868:0": "구하지 못해 면목이 없소……",
    "9:1869:0": "끄으윽……",
    "9:1870:0": "끄으윽……",
    "9:1871:0": "끄으윽……",
    "9:1872:0": "끄으윽……",
    "9:1873:0": "구하지 못하다니……",
    "9:1874:0": "미안하오, 구하지 못했소……",
    "9:1875:0": "한 걸음이 모자랐습니다……",
    "9:1876:0": "용서해 주시오……",
    "9:1877:0": "빌어먹을!\n감히 이런 짓을 하다니!",
    "9:1878:0": "이놈……!",
    "9:1879:0": "……!\n구해 내지 못했는가!",
    "9:1880:0": "마저……\n방심할 수 없겠군요……",
    "9:1881:0": "의 몫까지\n싸울 뿐이다",
    "9:1882:0": "개의치 마라\n한탄한들 이길 수 없다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1862:0",
    "9:1862:1",
    "9:1879:0",
    "9:1880:0",
    "9:1881:0",
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
                "segment": "base_msggame_B001_S637",
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
