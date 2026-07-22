#!/usr/bin/env python3
"""Build Base authoring segment 55 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S55.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s55", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:777:0": "견마지로도 마다하지 않고\n가문을 위해 힘쓰겠소",
    "6:778:0": "우리 모두 의기충천!\n어서 약진의 명을 내려 주십시오",
    "6:779:0": "우리 가문의 기세를 살려\n좋은 방책으로 전환해야 하오",
    "6:780:0": "우리 가문의 지금 규모라면\n이런 책략은 어떤가…",
    "6:781:0": "군신이 서로 화합하여\n가문이 번성하는구려",
    "6:782:0": "우리 가문은 떠오르는 해 같은 기세\n섬길 보람이 있사옵니다",
    "6:783:0": "이런 큰 가문을 섬기게 되다니\n내게 내린 복이로다",
    "6:784:0": "우리 가문과 번영을\n함께하고 싶소이다",
    "6:785:0": "우리 가문의 일거수일투족이\n천하를 뒤흔들 것입니다",
    "6:786:0": "우리 가문의 규모이기에\n할 수 있는 일이 있을 터",
    "6:787:0": "우리 가문의 힘으로\n천하를 평정하리라",
    "6:788:0": "천하를 움직이는 대전…\n생각만 해도 가슴이 뛰는구나",
    "6:789:0": "우리 가문의 기세 그대로\n천하가 평안해지기를",
    "6:790:0": "태평한 세상을 이루기 위해\n미력을 다하겠습니다",
    "6:791:0": "우리 가문의 규모라면\n천하통일도 꿈이 아니오",
    "6:792:0": "우리의 기세야말로\n천하를 다스릴 힘이다",
    "6:793:0": "쳇…\n못 해먹겠군",
    "6:794:0": "…이제 돌아가도 되나",
    "6:795:0": "불만은 쌓여만 가는군",
    "6:796:0": "…할 말은 없다",
}

DYNAMIC_RUNTIME_COORDINATES: set[str] = set()


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
                "segment": "base_msggame_B001_S55",
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
