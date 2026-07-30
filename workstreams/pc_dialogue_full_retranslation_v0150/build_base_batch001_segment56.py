#!/usr/bin/env python3
"""Build Base authoring segment 56 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S56.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s56", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:797:0": "오래 머무를 자리는\n아닌 듯하군",
    "6:798:0": "…무슨 일인가?\n돌아가고 싶다만",
    "6:799:0": "이 가문의 물은\n내게 맞지 않는 모양이군요…",
    "6:800:0": "…후우, 이 자리조차\n고통스럽게 느껴지는구나",
    "6:801:0": "인내도 한계로다…",
    "6:802:0": "울분을 풀 길이 없구나…",
    "6:803:0": "이 불만…\n어찌 풀어야 하나",
    "6:804:0": "지금은 따르고 있지만\n언젠가는…",
    "6:805:0": "좋은 새는 깃들 나무를 고른다\n하옵니다…",
    "6:806:0": "가신의 불만도\n알아차리지 못하시는가",
    "6:807:0": "언젠가는 누군가의\n인내심도 한계에 이르리라",
    "6:808:0": "뼈를 묻어야 할 땅은\n이곳이 아니란 말인가…",
    "6:809:0": "가신의 불만에도\n신경 쓰지 않으시는군요…",
    "6:810:0": "이토록 가신의 불만을\n방치하시다니",
    "6:811:0": "…마음에 들지 않는군\n이 가문의 모든 것이",
    "6:812:0": "…쳇\n아직 뭔가 있는 건가",
    "6:813:0": "출사하는 일이\n…괴롭다",
    "6:814:0": "쌓이고 쌓인 시름이\n…터질 것만 같사옵니다",
    "6:815:0": "더 나은 주군을…\n이런, 실례",
    "6:816:0": "…무슨 일이오?\n어서 돌려보내 주시오",
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
                "segment": "base_msggame_B001_S56",
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
