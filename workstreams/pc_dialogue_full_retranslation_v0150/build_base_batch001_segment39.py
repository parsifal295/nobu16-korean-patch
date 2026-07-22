#!/usr/bin/env python3
"""Build Base authoring segment 39 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S39.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s39", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:472:0": "이제부터…\n재미있어지겠군!",
    "6:473:0": "새 당주님께도\n변함없는 충의를",
    "6:474:0": "새로운 시대가 오는군",
    "6:475:0": "새 당주님을\n받쳐 드려야겠군",
    "6:476:0": "중대한 결단을 내리셨군…\n그 심중을 헤아리오",
    "6:477:0": "우리 가문을 둘러싼 정세에는\n어떤 변화가…",
    "6:478:0": "…역시 은거할 시기는\n지금이었군요",
    "6:479:0": "선대께서는\n훌륭히 물러나셨구나",
    "6:480:0": "이 시기에\n은거하시다니",
    "6:481:0": "가문도 새 마음으로\n더욱 번성하리라",
    "6:482:0": "과감한 결단을…\n이것이 어떤 결과를 낳을지",
    "6:483:0": "새 당주님께\n인사 올리옵니다",
    "6:484:0": "축하를 드려야\n하겠군요!",
    "6:485:0": "선대께서도…\n참으로 애쓰셨소",
    "6:486:0": "쓸쓸해지겠군요…",
    "6:487:0": "당주가 바뀌었으니\n심기일전해야겠구나",
    "6:488:0": "세상은 무상하다…\n그런 뜻이겠지요",
    "6:489:0": "앞으로 우리 가문은\n어찌 되는 것일까",
    "6:490:0": "그저 온 힘을 다할 뿐…",
    "6:491:0": "이번 당주 대에\n난세가 평정되기를",
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
                "segment": "base_msggame_B001_S39",
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
