#!/usr/bin/env python3
"""Build Base authoring segment 36 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S36.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s36", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:427:0": "신상필벌은 무문을\n떠받치는 근본",
    "6:428:0": "너무 눈에 띄는 짓은\n하지 말아야겠군…",
    "6:429:0": "그자는\n충성을 다하겠지요",
    "6:430:0": "역시 가보를\n회수하셨습니까",
    "6:431:0": "참으로 부러운 일이로다",
    "6:432:0": "분에 넘치는 일품 따위를\n지니고 있으니 그렇지",
    "6:433:0": "인덕이며 지휘 솜씨며\n과연 훌륭하십니다",
    "6:434:0": "아무 생각 없이 귀물을\n썩히고 있으니 그렇지",
    "6:435:0": "포상에는 사람을 보는 눈이\n드러나는 법이지요",
    "6:436:0": "주군의 손을 거치면\n가치가 높아지는 법",
    "6:437:0": "참으로\n영광스러운 일이로다",
    "6:438:0": "인생만사 새옹지마\n이런 일도 있는 법",
    "6:439:0": "훌륭히 공을 세우면\n",
    "6:439:1": "도 언젠가는…",
    "6:440:0": "…이 또한\n주종의 운명이라면야",
    "6:441:0": "이러한 영예를\n언젠가는",
    "6:441:1": "도…",
    "6:442:0": "그 귀물을 받으려면\n더욱 힘써야겠구나",
    "6:443:0": "참으로 경사로다",
    "6:444:0": "가엾기도 하지…",
    "6:445:0": "이 얼마나 큰 영예인가…\n",
    "6:445:1": "도 분발해야지",
    "6:446:0": "가보를 지닌다는 것도\n좋기만 한 일은 아니군…",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {439, 441, 445}
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
                "segment": "base_msggame_B001_S36",
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
