#!/usr/bin/env python3
"""Build Base authoring segment 712 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S712.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s712", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3339:0": "님께서 전사하셨다고!?\n",
    "9:3339:1": "에게 조금만 더 힘이 있었다면…",
    "9:3340:0": "님께서 전사하셨다니…\n전쟁이라 해도 견디기 힘들군…",
    "9:3341:0": "님께서 전사하셨다고!?\n반드시 원수를 갚겠습니다…",
    "9:3342:0": "님께서 전사하셨다고!?\n이놈들, 용서하지 않겠다!",
    "9:3343:0": "님께서 전사하셨나…\n얼마나 분하셨을까…",
    "9:3344:0": "님께서 전사하셨다니…\n도저히 믿을 수 없군…",
    "9:3345:0": "님께서 전사하셨다니…\n아까운 분을 잃었구나…",
    "9:3346:0": "님께서 전사하셨다고!?\n그럴 수가…",
    "9:3347:0": "님께서 전사하셨다고!?\n실로 훌륭한 싸움이었소…",
    "9:3348:0": "님께서 전사하셨다니…\n이제 다시 뵐 수 없다니…",
    "9:3349:0": "님께서 전사하셨다고!?\n믿을 수 없다…",
    "9:3350:0": "님께서 붙잡히셨다고!?\n이럴 수가…",
    "9:3351:0": "님께서 사로잡히셨나?\n구해 드리고 싶지만…",
    "9:3352:0": "님께서 붙잡히셨나…\n무사하셔야 할 텐데…",
    "9:3353:0": "님께서 붙잡히셨다니…\n전력 저하는 피할 수 없겠군요…",
    "9:3354:0": "님께서 붙잡히셨나…\n끝까지 싸워 내셨군",
    "9:3355:0": "님께서 붙잡히셨나\n부디 무사히 돌아와 주시기를…",
    "9:3356:0": "님께서 붙잡히셨다…\n살아 계시면 희망은 있다…",
    "9:3357:0": "님께서 붙잡히셨다고!?\n구출해 드리고 싶지만…",
    "9:3358:0": "님께서 적의 손에 붙잡히셨다고!?\n어떻게든 해야 해!",
    "9:3359:0": "님께서 사로잡히셨다고?\n아무것도 하지 못하다니 면목이 없군",
    "9:3360:0": "님께서 사로잡히시다니…\n무사하시면 좋겠습니다만",
}

STATIC_COORDINATES: set[str] = set()
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
                "segment": "base_msggame_B001_S712",
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
