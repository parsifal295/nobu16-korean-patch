#!/usr/bin/env python3
"""Build Base authoring segment 662 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S662.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s662", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2342:0": "각오하십시오!",
    "9:2343:0": "자, 간다!",
    "9:2344:0": "결판을 냅시다!",
    "9:2345:0": "해치워 주마!",
    "9:2346:0": "여기서 끝내겠습니다",
    "9:2347:0": "결정적인 한 수를!",
    "9:2348:0": "좋았어!\n한 방 먹여 줘라!",
    "9:2349:0": "훌륭한 무훈이로다!",
    "9:2350:0": "훌륭하도다!\n전황을 유리하게 이끌겠구나",
    "9:2351:0": "역시 대단하십니다\n승리에 기여하셨군요",
    "9:2352:0": "잘했다!\n승리에 한 걸음 더 다가섰다",
    "9:2353:0": "훌륭한 활약이로다……\n요지를 활용한다면…… 후후",
    "9:2354:0": "훌륭한 수완이오\n큰 공을 세우셨구려",
    "9:2355:0": "잘했도다!\n큰 공을 세웠구나!",
    "9:2356:0": "역시 대단하십니다!\n기대하고 있었습니다!",
    "9:2357:0": "해냈구나!\n이제 한결 수월해지겠어",
    "9:2358:0": "이제 유리하게\n싸울 수 있을 터",
    "9:2359:0": "믿음직스럽구려",
    "9:2360:0": "싸움도 공도\n남에게 지기는 싫으니까!",
    "9:2361:0": "퇴각로 파괴의 무훈!\n",
    "9:2361:1": "이(가) 차지했다",
    "9:2362:0": "소임을 다했을 뿐",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2361:0",
    "9:2361:1",
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
                "segment": "base_msggame_B001_S662",
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
