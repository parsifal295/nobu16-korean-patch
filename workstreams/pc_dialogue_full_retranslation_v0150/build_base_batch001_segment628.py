#!/usr/bin/env python3
"""Build Base authoring segment 628 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S628.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s628", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1677:0": "알겠소\n돌아가는 길을 조심하시오",
    "9:1678:0": "무사해서 다행이오……\n나머지는 맡기시오",
    "9:1679:0": "분전하느라 고생했다\n나머지는 맡겨라",
    "9:1680:0": "나머지는\n제게 맡겨 주십시오!",
    "9:1681:0": "물러나 다오\n나머지는―",
    "9:1681:1": "에게 맡겨라!",
    "9:1682:0": "자―",
    "9:1682:1": "의\n차례로군요",
    "9:1683:0": "후우…… 어쨌든\n제때 도착해서 다행이다",
    "9:1684:0": "네놈은―",
    "9:1684:1": "의 먹잇감이다!",
    "9:1685:0": "네놈은 베겠다!\n나의 긍지를 걸고!",
    "9:1686:0": "시답잖은 헛소리를……\n자, 간다!",
    "9:1687:0": "이(가) 상대라면\n전력을 다해 맞서지요",
    "9:1688:0": "나의 원한을\n여기서 풀겠다!",
    "9:1689:0": "인가……\n잘됐군……",
    "9:1690:0": "……",
    "9:1690:1": "\n나서지 마라, 사라져라!",
    "9:1691:0": "여기서 만난 게\n네 운이 다한 날이니라!",
    "9:1692:0": "이건\n질 수 없겠군요……!",
    "9:1693:0": "마침 잘됐다!\n실컷 울게 해 주마",
    "9:1694:0": "입니까\n전력을 아낄 필요는 없겠군요",
    "9:1695:0": "(이)라고!?\n반드시 베겠다!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1681:0",
    "9:1681:1",
    "9:1682:0",
    "9:1682:1",
    "9:1684:0",
    "9:1684:1",
    "9:1687:0",
    "9:1689:0",
    "9:1690:0",
    "9:1690:1",
    "9:1694:0",
    "9:1695:0",
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
                "segment": "base_msggame_B001_S628",
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
