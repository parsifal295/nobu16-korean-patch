#!/usr/bin/env python3
"""Build Base authoring segment 684 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S684.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s684", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:2778:0": "전투란 서로 속내를 떠보는 수 싸움\n미묘한 낌새 하나도 놓치지 않는다",
    "9:2779:0": "상대의 허를 찌르는 것쯤\n쉬운 일이지",
    "9:2780:0": "싸움은 목숨을 주고받는 일\n신중하게 움직여야겠군",
    "9:2781:0": "적도 우리와 같은 사람입니다\n생각하면 답은 나옵니다",
    "9:2782:0": "적을 압도할 계책을\n생각해야겠군",
    "9:2783:0": "병사들의 목숨을 맡았으니\n신중히 움직입시다",
    "9:2784:0": "어떻게 움직일지\n고심해야 할 때로군",
    "9:2785:0": "을(를) 노려라!\n다른 놈들은 신경 쓰지 마라!",
    "9:2786:0": "노릴 것은―",
    "9:2786:1": "\n기필코 격파하리라!",
    "9:2787:0": "을(를) 격파하라!\n우리의 공으로 삼으리라",
    "9:2788:0": "을(를)\n격파하도록 하지요",
    "9:2789:0": "을(를) 노린다!\n결코 놓치지 마라!",
    "9:2790:0": "을(를) 노린다\n한 부대씩 무너뜨리자",
    "9:2791:0": "을(를)\n격파하는 것이 상책이다",
    "9:2792:0": "의 수급을\n취할 자는 바로 이 몸이다!",
    "9:2793:0": "을(를)\n목표로 삼아 진군 개시!",
    "9:2794:0": "그저 달려라!\n",
    "9:2794:1": "을(를) 격파한다!",
    "9:2795:0": "을(를)\n처치하도록 하지요",
    "9:2796:0": "을(를) 노린다\n적장을 쓰러뜨려 공을 세우리라",
    "9:2797:0": "퇴각로를 봉쇄한다!\n놈들을 살아서 돌려보내지 마라!",
    "9:2798:0": "퇴각로를 장악하라!\n놈들을 독 안에 든 쥐로 만들어 주마",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2785:0",
    "9:2786:0",
    "9:2786:1",
    "9:2787:0",
    "9:2788:0",
    "9:2789:0",
    "9:2790:0",
    "9:2791:0",
    "9:2792:0",
    "9:2793:0",
    "9:2794:0",
    "9:2794:1",
    "9:2795:0",
    "9:2796:0",
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
                "segment": "base_msggame_B001_S684",
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
