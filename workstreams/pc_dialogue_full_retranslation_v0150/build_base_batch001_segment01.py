#!/usr/bin/env python3
"""Build the first source-free v0.15.0 Base dialogue decision segment.

The module contains only project-authored Korean.  It obtains the guarded
source/current hashes from the pinned private review queue and writes the
source-bearing decision envelope below ``tmp/``.  No game resource is written.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S01.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


# Every line is newly adjudicated from pristine PC JP plus same-record PC
# SC/TC context.  Prior Korean is not a semantic source.
TRANSLATIONS: dict[str, str] = {
    "2:80:0": "성인식을 마친 공주가 있군.\n앞날도 생각해 보아야겠어……",
    "2:81:0": "성인식을 마친 공주가 있는 모양입니다.\n앞날도 생각해 보아야겠군요……",
    "2:82:0": "성인식을 마친 공주가 있사옵니다.\n공주의 앞날도 헤아려 주시옵소서……",
    "2:83:0": "성인식을 마친 공주가 있사옵니다.\n공주의 앞날도 헤아려 주시옵소서……",
    "2:84:0": "이름과 읽는 법을 입력해 주십시오",
    "2:85:0": "이름에 사용할 수 없는 문자가 포함되어 있습니다",
    "2:86:0": "내용을 확인한 뒤 결정을 눌러 주십시오",
    "2:87:0": "무장과 공주 중 하나를 선택한 뒤 결정을 눌러 주십시오",
    "2:88:0": "부인·",
    "2:88:1": "이 무장으로 원복했습니다",
    "2:89:0": "따님·",
    "2:89:1": "이 무장으로 원복했습니다",
    "2:90:0": "부인·",
    "2:90:1": "이 성인식을 마치고 성인이 되었습니다",
    "2:91:0": "따님·",
    "2:91:1": "이 성인식을 마치고 성인이 되었습니다",
    "2:92:0": "가신의 딸·",
    "2:92:1": "이 성인이 되었습니다",
    "2:93:0": (
        "저도 원복… 아니, 성인식을 마쳤사오니\n"
        "이제 어엿한 장수로서 처신할 수 있사옵니다.\n"
        "무가에 시집온 몸으로서 훌륭한 공을 세우겠사옵니다"
    ),
    "2:94:0": (
        "이제 저도 마음껏 일할 수 있는 몸이 되었사오니\n"
        "반드시 주군께서 흡족해하시도록\n"
        "몸이 부서지도록 날마다 힘쓰겠사옵니다"
    ),
}

DYNAMIC_RUNTIME_COORDINATES = {
    "2:88:0", "2:88:1", "2:89:0", "2:89:1", "2:90:0",
    "2:90:1", "2:91:0", "2:91:1", "2:92:0", "2:92:1",
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
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
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
                "scope_classification": (
                    "runtime_fragment_pending"
                    if coordinate in DYNAMIC_RUNTIME_COORDINATES
                    else "retranslated"
                ),
                "layout_review": "unchanged_from_current",
                "runtime_review": (
                    "pending" if coordinate in DYNAMIC_RUNTIME_COORDINATES else "not_required"
                ),
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context",
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
                "segment": "base_msggame_B001_S01",
                "decision_count": len(rows),
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
