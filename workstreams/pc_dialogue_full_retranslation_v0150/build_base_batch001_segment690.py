#!/usr/bin/env python3
"""Build Base authoring segment 690 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S690.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s690", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:2910:0": "병력 차를 생각하면…\n여기서는 방어 태세를 굳혀야 한다",
    "9:2911:0": "병력을 상당히 잃었군…\n수비에 전념하라",
    "9:2912:0": "병력이 이렇게 줄어서야…\n퇴각로 수비에 나설까",
    "9:2913:0": "병력 차가 크게 벌어졌습니다…\n수세로 돌아섭시다",
    "9:2914:0": "병력을 많이 잃었나…\n방비를 굳혀야겠군",
    "9:2915:0": "병력이 줄었군요\n후방을 굳힙시다",
    "9:2916:0": "병력을 상당히 잃었군…\n수비에 전념하라",
    "9:2917:0": "적은 얼마 안 된다!\n단숨에 쳐부숴라!",
    "9:2918:0": "병력 수에서는 우리가 우세하다\n총력으로 쳐부숴라!",
    "9:2919:0": "병력 수의 우위를 살린다\n전원, 돌격하라!",
    "9:2920:0": "적군은 병력이 적습니다\n공격만으로 이길 수 있습니다",
    "9:2921:0": "적은 얼마 되지 않는다!\n철저히 쳐부숴라!",
    "9:2922:0": "병력 수에서 유리하다!\n그저 밀어붙여라!",
    "9:2923:0": "우리 병력이 우세하다\n짓눌러 주마!",
    "9:2924:0": "병력 수는 우리가 압도적으로 많다!\n단숨에 집어삼켜라",
    "9:2925:0": "병력이라면 우리가 밀리지 않습니다\n공격에 전념하십시오",
    "9:2926:0": "적군은 소수 병력이다!\n전군, 돌격하라!",
    "9:2927:0": "병력 수에서는 우리가 우세합니다\n단숨에 쳐부수겠습니다!",
    "9:2928:0": "적은 소수 병력에 불과하다!\n단숨에 몰아쳐라!",
    "9:2929:0": "승부는 끝났다!\n녀석들아, 돌격이다!",
    "9:2930:0": "우리 병력이 앞선다\n지금이다, 쳐부숴라!",
    "9:2931:0": "적은 이제 얼마 남지 않았다\n전군, 공격하라!",
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
                "segment": "base_msggame_B001_S690",
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
