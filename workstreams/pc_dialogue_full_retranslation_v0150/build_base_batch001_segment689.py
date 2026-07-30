#!/usr/bin/env python3
"""Build Base authoring segment 689 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S689.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s689", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:2888:0": "여기서 느긋이\n기다리도록 하지",
    "9:2889:0": "상황이 변할 때까지\n기다리겠습니다",
    "9:2890:0": "대기하라\n당분간 움직이지 않는다",
    "9:2891:0": "당분간 상황을\n지켜보도록 하지요",
    "9:2892:0": "아직 기다릴 때다\n기회를 보아 움직인다",
    "9:2893:0": "병력이 부족한가…\n퇴각로를 지킬 수밖에 없어",
    "9:2894:0": "병력 수로는 승부가 안 된다…\n수비전이 되겠군",
    "9:2895:0": "병력이 부족하다…\n수비에 전념해야 한다",
    "9:2896:0": "병력 수로는 이길 수 없습니다…\n퇴각로를 수비하겠습니다",
    "9:2897:0": "적보다 병력이 적은가…\n퇴각로 수비에 나선다",
    "9:2898:0": "병력 차가 벌어졌군…\n후방에서 수비해야겠다",
    "9:2899:0": "병력 수에서 불리하다…\n퇴각로를 굳게 지켜라",
    "9:2900:0": "병력이 부족하군…\n퇴각로의 방비를 굳히자",
    "9:2901:0": "적보다 병력이 적군요…\n수비하는 편이 좋겠습니다",
    "9:2902:0": "병력 수에서 밀린다…\n수비에 전념하자",
    "9:2903:0": "병력이 열세군요…\n방비를 굳힙시다",
    "9:2904:0": "병력이 부족하군…\n퇴각로를 굳게 지킨다",
    "9:2905:0": "병력이 부족하군…\n여기서는 수비에 나선다!",
    "9:2906:0": "병력을 많이 잃었군…\n수비로 돌아설 수밖에 없어",
    "9:2907:0": "병력 소모가 심하다…\n방비를 굳혀라!",
    "9:2908:0": "병력 손실이 크다…\n수비에 전념하도록 합시다",
    "9:2909:0": "이렇게 병력이 적어서야…\n여기서는 방어로 돌아서지",
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
                "segment": "base_msggame_B001_S689",
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
