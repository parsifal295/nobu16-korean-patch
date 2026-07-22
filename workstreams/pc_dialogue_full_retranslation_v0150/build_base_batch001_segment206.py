#!/usr/bin/env python3
"""Build Base authoring segment 206 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S206.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s206", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3508:1": "!\n",
    "6:3508:2": "의 말석에 이름을 올리고, 이름도 조금 알려진 몸\n신분에 부끄럽지 않도록 힘쓰",
    "6:3508:3": "!",
    "6:3509:0": "의",
    "6:3509:1": "이(가) 으뜸",
    "6:3509:2": "…\n쑥스럽지만 기쁜 일\n더욱",
    "6:3509:3": "의 힘이 되",
    "6:3510:0": "훈공 1위라니 경사로군\n아직 반쪽짜리",
    "6:3510:1": "만 한 걸음씩 힘써\n우리 가문에 공헌하",
    "6:3511:0": "이(가) 훈공 1위라니…\n미숙한 자에게 과분한 평가\n황공하기 그지없",
    "6:3512:0": "이(가) 으뜸이라니 기쁜 일",
    "6:3512:1": "\n앞으로도 이 영예에 자만하지 않고\n스스로를 엄히 다스릴 생각",
    "6:3513:0": "이(가) 훈공 1위라니…\n아랫사람은 죽도록 땀 흘려야만\n보탬이 되",
    "6:3513:1": "…그 일념으로",
    "6:3514:0": "이(가) 훈공 1위라 해서 놀라",
    "6:3514:1": "\n오히려 놀라운 것은 이처럼 아랫사람에게\n공을 세울 기회를 주신",
    "6:3514:2": "의 혜안이 아니겠습니까?",
    "6:3515:0": "훈공 1위라니 과분한 처사…\n재주 없는 몸을 이 지위에 앉혀",
    "6:3515:2": "에게 은혜를 갚고자 힘쓸 뿐이오",
    "6:3516:0": "이(가) 훈공 1위",
}

STATIC_COORDINATES: set[str] = set()


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S206", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
