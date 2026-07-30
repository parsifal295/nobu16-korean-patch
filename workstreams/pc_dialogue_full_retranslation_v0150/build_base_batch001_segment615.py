#!/usr/bin/env python3
"""Build Base authoring segment 615 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S615.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s615", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1402:0": "아직―",
    "9:1402:1": "이(가) 여기에……\n으아아악!",
    "9:1403:0": "으아아악……!\n우리를 휘말리게 했구나……!",
    "9:1404:0": "아뿔싸!\n피해가 이쪽까지!?",
    "9:1405:0": "이럴 수가……\n휘말렸단 말인가……",
    "9:1406:0": "휘말리다니……",
    "9:1407:0": "그, 그럴 수가!\n",
    "9:1407:1": "마저……!",
    "9:1408:0": "홍수라고!?\n그런 말은 못 들었다!",
    "9:1409:0": "큭, 둑을 터뜨리다니\n이 무슨 폭거인가……!",
    "9:1410:0": "건곤일척의 대승부에\n나섰단 말인가……!",
    "9:1411:0": "적도 수단을 가릴\n처지가 아닌 모양이군……",
    "9:1412:0": "물살을 당해 낼 수 없다!\n으아악!",
    "9:1413:0": "수공이라고!?\n불찰이다!",
    "9:1414:0": "물…… 물이이이!",
    "9:1415:0": "크윽!\n수공이다!",
    "9:1416:0": "홍수!?\n모두, 침착해!",
    "9:1417:0": "이래서는\n자유롭게 움직일 수 없다……!",
    "9:1418:0": "이래서는\n적의 뜻대로입니다……",
    "9:1419:0": "으아악!\n주위가 온통 물바다다!",
    "9:1420:0": "해 주마!",
    "9:1421:0": "오오오!",
    "9:1422:0": "시작됐군……!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1402:0",
    "9:1402:1",
    "9:1407:0",
    "9:1407:1",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
                "segment": "base_msggame_B001_S615",
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
