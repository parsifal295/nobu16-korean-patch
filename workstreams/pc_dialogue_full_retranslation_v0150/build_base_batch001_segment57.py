#!/usr/bin/env python3
"""Build Base authoring segment 57 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S57.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s57", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:817:0": "흥,",
    "6:817:1": "…\n마음에 안 드는군",
    "6:818:0": "와 동석인가…\n짜증 나는군",
    "6:819:0": "따위와\n어깨를 나란히 하다니",
    "6:820:0": "…",
    "6:820:1": "와도\n협력해야만…",
    "6:821:0": "와 동석인가…\n모두 가문을 위해서다",
    "6:822:0": "을(를) 인정하지 못할 만큼\n속 좁은 사람은 아니다",
    "6:823:0": "이(가) 벌인 실책의\n뒤처리는 사양입니다",
    "6:824:0": "우리 가문에",
    "6:824:1": "따위\n필요 없다고 생각하오만…",
    "6:825:0": "따위는\n안중에도 없다",
    "6:826:1": "인가…\n호오는 접어 두어야겠지",
    "6:827:0": "…\n무슨 일을 저지르지는 않을지…",
    "6:828:0": "이(가)",
    "6:828:1": "을(를)\n참소하는 건 아닌지…",
    "6:829:0": "을(를) 피하는 것도\n무례라는 것인가…",
    "6:830:0": "의 책략이라는 것을\n가르쳐 달라고 청하고 싶군…",
    "6:831:0": "…\n잘난 척하는 얼굴을",
    "6:832:0": "하아…",
    "6:832:1": "와\n한자리에 앉다니",
    "6:833:0": "…",
    "6:833:1": "와도\n협력해야 하는데…",
    "6:834:0": "의 얼굴 따위…\n솔직히 보고 싶지도 않다",
    "6:835:0": "…\n쳇, 불쾌하군",
    "6:836:0": "와의 원한을\n삼킬 수밖에 없는가",
}

DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS)


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
                "segment": "base_msggame_B001_S57",
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
