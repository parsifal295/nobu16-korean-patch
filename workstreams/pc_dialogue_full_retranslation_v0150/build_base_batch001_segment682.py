#!/usr/bin/env python3
"""Build Base authoring segment 682 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S682.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s682", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:2733:0": "전세를 만회해야 합니다!\n요충지를 빼앗으러 가겠습니다",
    "9:2734:0": "온 용기를 끌어모아라!\n지금이야말로 요충지를 빼앗을 때다",
    "9:2735:0": "이제 요충지를 빼앗는 것 말고는\n승산이 없사옵니다!",
    "9:2736:0": "요충지를 빼앗는다!\n전세를 뒤집어 보자!",
    "9:2737:0": "뭐냐, 저 소수 병력은?\n노릴 수밖에 없겠군!",
    "9:2738:0": "하나씩 전과를 쌓는다\n우선 저 소수 병력부터다!",
    "9:2739:0": "칠 수 있는 적부터 친다\n저 소수 병력을 노린다!",
    "9:2740:0": "저 소수 병력을 추격하세요\n놓쳐서는 안 됩니다!",
    "9:2741:0": "소수 병력부터 공격한다!\n한 명도 놓치지 마라!",
    "9:2742:0": "적의 수를 줄여 둘까\n저 소수 병력을 격파하라!",
    "9:2743:0": "노릴 만한 건 저 소수 병력인가\n진군을 시작한다!",
    "9:2744:0": "먹음직스러운 사냥감이로군\n저 소수 병력을 잡아먹자",
    "9:2745:0": "소수 병력부터 공격합니다\n결코 놓치지 마십시오!",
    "9:2746:0": "노려 달라는 듯하군\n저 소수 병력을 친다!",
    "9:2747:0": "소수 병력부터 치겠습니다\n봐줄 필요는 없습니다",
    "9:2748:0": "저 소수 병력을 노린다!\n공을 놓치지 마라!",
    "9:2749:0": "사내들아, 서둘러라!\n요충지를 지켜라!",
    "9:2750:0": "요충지로 급히 가라!\n방비를 굳혀라",
    "9:2751:0": "방어하러 간다\n요충지는 내주지 않겠다!",
    "9:2752:0": "병력이 필요하겠군요\n요충지로 향하겠습니다",
    "9:2753:0": "요충지는 내주지 않겠다!\n우리가 수비에 나선다!",
    "9:2754:0": "요충지가 걱정이다\n방비를 굳히자",
}

DYNAMIC_RUNTIME_COORDINATES: set[str] = set()
STATIC_COORDINATES = set(TRANSLATIONS)


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
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_"
                    "context_where_available"
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
                "segment": "base_msggame_B001_S682",
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
