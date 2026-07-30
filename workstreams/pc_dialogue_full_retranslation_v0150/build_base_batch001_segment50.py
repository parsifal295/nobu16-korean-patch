#!/usr/bin/env python3
"""Build Base authoring segment 50 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S50.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s50", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:677:0": "후후… 이 정도 일은\n바쁘다고 할 수도 없지",
    "6:678:0": "남보다 배로 하지 않으면\n두각을 나타낼 수 없다",
    "6:679:0": "이야… 어제는\n한 시진이나 잤습니다",
    "6:680:0": "후우… 격무 또한\n기대의 표시인가",
    "6:681:0": "이거 참, 칼 손질조차\n못 하고 있을 정도라네",
    "6:682:0": "한가해지면\n검술 수련이나 할까",
    "6:683:0": "유능한 자에게는\n일이 몰리는 법이지",
    "6:684:0": "남이 못 한다면\n직접 할 수밖에 없지",
    "6:685:0": "하하… 요즘은 렌가 모임에 갈\n시간도 나지 않아서요",
    "6:686:0": "다도가 그립다고\n생각할 겨를조차 없소이다",
    "6:687:0": "요즘은 쇼기 벗들에게도\n도리를 다하지 못하는구먼",
    "6:688:0": "만사에 경험이 필요한 법이니\n바쁜 것도 어쩔 수 없지",
    "6:689:0": "후후… 너무 일했더니\n조금 야위었나",
    "6:690:0": "아아… 어깨가 뻐근해\n누가 좀 주물러 줘!",
    "6:691:0": "격무라고?\n이 정도로 웃기지 마라",
    "6:692:0": "뭐, 평범한 자로는\n버티지 못할 일의 양인가",
    "6:693:0": "으윽…\n바빠서… 토할 것 같아",
    "6:694:0": "바쁘다는… 감각이\n마비되어 갑니다…",
    "6:695:0": "아아!\n정말 바쁘구나!",
    "6:696:0": "한가하시면 조금은\n도와주시지 않겠습니까",
}

DYNAMIC_RUNTIME_COORDINATES: set[str] = set()


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
                "segment": "base_msggame_B001_S50",
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
