#!/usr/bin/env python3
"""Build Base authoring segment 132 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S132.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s132", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2460:0": "무사는 체면을 중히 여기는데\n그 체면을 상하게 하고 말았군…",
    "6:2461:0": "상대의 뜻을 헤아리지 못했나…\n태도가 완고해지고 말았군",
    "6:2462:0": "심기를 상하게 했나요…\n교섭하기 어려워졌군요",
    "6:2463:0": "화를 내는군…\n악수였어",
    "6:2464:0": "실책이었군\n심기가 뒤틀리고 말았어…",
    "6:2465:0": "너무 강하게 나갔나…\n이렇게까지 화나게 할 줄이야…",
    "6:2466:0": "이런!\n화나게 하고 말았군",
    "6:2467:0": "상대를 화나게 했을 뿐이군요…\n실책이었습니다…",
    "6:2468:0": "상대의 기분을 읽지 못했나…\n유감이군…",
    "6:2469:0": "과감한 수를 두었다가\n역효과가 나고 말았군요…",
    "6:2470:0": "실패한 것도 모자라\n화나게 하고 말다니…",
    "6:2471:0": "공략은 성공했소\n우선 감사드리오",
    "6:2472:0": "공략은 성공했소\n우선 감사드리오",
    "6:2473:0": "공략은 성공했소\n우선 감사드리오",
    "6:2474:0": "공략은 성공했소\n우선 감사드리오",
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
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
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
                "segment": "base_msggame_B001_S132",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
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
