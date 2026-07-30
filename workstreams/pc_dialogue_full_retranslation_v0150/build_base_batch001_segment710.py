#!/usr/bin/env python3
"""Build Base authoring segment 710 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S710.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s710", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3313:0": "요충지를 노리는 적군이 있사옵니다\n수비 부대가 필요할 듯하옵니다",
    "9:3314:0": "의 준비가 끝난 모양이군\n한번 써 보지 않겠나?",
    "9:3315:0": "지금이야말로 쓸 것은…",
    "9:3315:1": "입니다\n준비는 모두 갖추어졌사옵니다",
    "9:3316:0": "의 준비가 끝났사옵니다\n지금이야말로 쓸 때이옵니다",
    "9:3317:0": "을(를) 써야 할 때인 듯하옵니다\n이 호기를 살립시다",
    "9:3318:0": "지금이야말로 쓸 것은…",
    "9:3318:1": "이오\n준비는 만반으로 갖추어졌소",
    "9:3319:0": "을(를) 써야 할 때인 듯하옵니다\n이 호기를 살립시다",
    "9:3320:0": "을(를) 활용하기 좋은 상황이옵니다\n쓰지 않을 이유가 없사옵니다",
    "9:3321:0": "지금 활용할 수 있는 것은…",
    "9:3321:1": "이옵니다\n이 호기를 놓쳐서는 아니 되옵니다",
    "9:3322:0": "을(를) 쓸 수 있을 듯합니다\n이 호기를 살립시다",
    "9:3323:0": "의 준비가 끝났습니다\n지금이야말로 쓸 때입니다",
    "9:3324:0": "을(를) 활용할 수 있는 상황입니다\n준비는 되어 있습니다",
    "9:3325:0": "지금이야말로 쓸 것은…",
    "9:3325:1": "이오\n준비는 만반으로 갖추어졌소",
    "9:3326:0": "놈들이 쓰려는 것은…",
    "9:3326:1": "인 모양이군\n가까이 갈 때는 조심해야겠어",
    "9:3327:0": "적이 쓰려는 것은…",
    "9:3327:1": "인 듯하옵니다\n경계가 필요할 듯하옵니다",
}

STATIC_COORDINATES = {"9:3313:0"}
DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS) - STATIC_COORDINATES


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
                "segment": "base_msggame_B001_S710",
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
