#!/usr/bin/env python3
"""Build Base authoring segment 614 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S614.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s614", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1381:0": "움직일 수 없군…… 이런 수에\n걸려들다니……",
    "9:1382:0": "윽!\n이래서는 움직일 수 없다……",
    "9:1383:0": "발을 묶어\n시간을 벌 셈인가……!",
    "9:1384:0": "적이 조금\n늘어난 것쯤이야!",
    "9:1385:0": "적군에 병력이\n합류했는가……!",
    "9:1386:0": "사전 공작도\n빈틈없이 해 두었군……",
    "9:1387:0": "고작 향토 무사일 뿐\n문제는 없겠군요",
    "9:1388:0": "적의 수가\n늘어났는가",
    "9:1389:0": "이 고을 사람들을\n자기편으로 끌어들이다니……",
    "9:1390:0": "고을 사람들이\n적군에 가담한 모양입니다",
    "9:1391:0": "으으음……\n어찌 적의 편을 드는가……",
    "9:1392:0": "하필 여기서 적의 편에\n붙다니……",
    "9:1393:0": "놈들, 저쪽에\n힘을 보탰는가……",
    "9:1394:0": "적이 늘어나는 건\n골치 아프군요……",
    "9:1395:0": "하필 여기서 적의 편을\n들다니 뼈아프군……",
    "9:1396:0": "으엇!?\n물이 이쪽까지……!",
    "9:1397:0": "아뿔싸!\n휘말린다…… 으아악!",
    "9:1398:0": "삼켜지고 말았는가……",
    "9:1399:0": "말도 안 돼!\n휘말리다니……",
    "9:1400:0": "크으윽……!\n대체 뭘 하는 게냐……!",
    "9:1401:0": "이, 이―",
    "9:1401:1": "\n쯤 되는 자가……",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1401:0",
    "9:1401:1",
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
                "segment": "base_msggame_B001_S614",
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
