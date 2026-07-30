#!/usr/bin/env python3
"""Build Base authoring segment 666 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S666.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s666", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2419:0": "자, 이 몸이 왔노라!\n이제 모든 일을 내게 맡겨라!",
    "9:2420:0": "덕분에 살았군!\n그럼 뒤를 부탁한다!",
    "9:2421:0": "구원에 감사한다!\n이제 후퇴하겠다",
    "9:2422:0": "참으로 고맙소……\n이제 후퇴하겠소",
    "9:2423:0": "덕분에 살았습니다\n부디 조심하십시오",
    "9:2424:0": "우리는 일단 물러나겠다……\n무운을 빈다!",
    "9:2425:0": "참으로 고맙소……\n이제 후퇴하겠소",
    "9:2426:0": "뒷일은 부탁하오……\n모두, 후퇴하라!",
    "9:2427:0": "하늘이 내린 구원이로구나!\n이 은혜는 잊지 않겠소!",
    "9:2428:0": "덕분에 살았습니다……\n뒷일은 부탁드립니다!",
    "9:2429:0": "구원에 감사한다\n우리는 이만 물러나겠다",
    "9:2430:0": "이제 물러나겠습니다\n이 은혜는 언젠가 꼭……",
    "9:2431:0": "고맙소\n이만 물러나겠소",
    "9:2432:0": "다음은―",
    "9:2432:1": "이(가) 상대다!\n어디 한번 덤벼 봐라!",
    "9:2433:0": "제법 하는 모양이군\n",
    "9:2433:1": "이(가) 상대해 주마!",
    "9:2434:0": "멋대로 날뛰게 두지 않겠다\n다음은―",
    "9:2434:1": "이(가) 상대다!",
    "9:2435:0": "이번에는―",
    "9:2435:1": "와(과)\n한 수 겨루어 주시지요",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2432:0",
    "9:2432:1",
    "9:2433:0",
    "9:2433:1",
    "9:2434:0",
    "9:2434:1",
    "9:2435:0",
    "9:2435:1",
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
                "segment": "base_msggame_B001_S666",
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
