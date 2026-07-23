#!/usr/bin/env python3
"""Build Base authoring segment 618 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S618.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s618", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1467:0": "봐줄 생각은 없어\n각오해 두는 게 좋을걸?",
    "9:1468:0": "한가하게 있을 수는\n없겠군!",
    "9:1469:0": "가자!\n질 수는 없다!",
    "9:1470:0": "병사들도 기세가 올랐군……\n가자!",
    "9:1471:0": "우리도 공을\n세우도록 하지요",
    "9:1472:0": "우리도 뒤따라 참전하자!",
    "9:1473:0": "우리도 뒤질 수는 없겠군",
    "9:1474:0": "질 수는 없겠군요",
    "9:1475:0": "자, 우리도 뒤따르는 게다!",
    "9:1476:0": "도 가세해야겠군",
    "9:1477:0": "우리도 뒤따라야겠군",
    "9:1478:0": "손 놓고 있을 수는\n없겠군요",
    "9:1479:0": "공도 세우지 못하고 돌아가면\n무사의 수치다!",
    "9:1480:0": "도 한바탕 날뛰고 싶다……!",
    "9:1481:0": "어서 나가\n싸우고 싶구나……",
    "9:1482:0": "어째서\n참전 허가가 나지 않는가……",
    "9:1483:0": "은(는) 장식물이\n아니옵니다만……",
    "9:1484:0": "함성을 들으니\n몸이 근질거리는구나!",
    "9:1485:0": "으음…… 공을 모두\n빼앗기고 말겠군……",
    "9:1486:0": "도\n전선에 나가고 싶건만……",
    "9:1487:0": "에잇!\n아직 출격할 수 없는가!",
    "9:1488:0": "도 참전하고 싶다……",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1476:0",
    "9:1480:0",
    "9:1483:0",
    "9:1486:0",
    "9:1488:0",
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
                "segment": "base_msggame_B001_S618",
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
