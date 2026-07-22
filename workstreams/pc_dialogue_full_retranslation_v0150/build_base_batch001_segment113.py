#!/usr/bin/env python3
"""Build Base authoring segment 113 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S113.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s113", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2051:0": "대상 세력에 다이묘가 보유한 관직을 요구합니다",
    "6:2052:0": "대상 세력에 다른 세력과 단교하도록 요청합니다",
    "6:2053:0": "이(가) 지급받은 지행 수에 불만  충성-",
    "6:2054:0": "이(가) 지급받은 지행 수에 만족  충성+",
    "6:2055:0": "의 지침 「",
    "6:2055:1": "」은(는) 지속 불가",
    "6:2056:0": "에게 지시해 둔\n「",
    "6:2056:1": "」이(가) 중단돼 버렸어!\n새 지침을 내려 달라고!",
    "6:2057:0": "의 「",
    "6:2057:1": "」이(가)\n더는 진행되지 않아 중지를 전하였소\n새 지침을 내려 주시길 바라오",
    "6:2058:0": "유감스럽지만",
    "6:2058:1": "의 지침\n「",
    "6:2058:2": "」을(를) 중단하였소\n새 지침을 정해 주시오",
    "6:2059:0": "의 지침 「",
    "6:2059:1": "」은(는)\n계속하기 어려워졌으니\n다시 지침을 내려 주시겠습니까",
    "6:2060:0": "의 「",
    "6:2060:1": "」은(는)\n더는 이어 갈 수 없소\n지침을 다시 검토해 주시오!",
    "6:2061:0": "부득이",
    "6:2061:1": "의 지침\n「",
    "6:2061:2": "」을(를) 중단하였습니다\n다음 지침은 어찌하시겠습니까",
    "6:2062:0": "「",
    "6:2062:1": "」을(를) 지시한 Gd1.GdName \n에서는 계속할 수 없다고 하옵니다…\n다음 지침을 검토해 주시옵소서",
    "6:2063:0": "의 지침 「",
    "6:2063:1": "」이(가)\n계속될 수 없게 된 모양이구먼…\n새 지침을 내려 주지 않겠는가",
    "6:2064:0": "의 지침 「",
    "6:2064:1": "」은(는)\n더는 계속할 수 없게 되었습니다\n다시 지침을 내려 주시겠습니까",
    "6:2065:0": "의 「",
    "6:2065:1": "」은(는)\n더는 이어 갈 수 없사옵니다…\n새 지침을 내려 주시옵소서",
    "6:2066:0": "의 「",
    "6:2066:1": "」은(는)\n더는 계속할 수 없게 된 듯합니다…\n새 지침을 검토해 주시겠습니까?",
    "6:2067:0": "의 지침 「",
    "6:2067:1": "」은(는)\n더는 계속할 수 없게 되었습니다\n다시 지침을 내리시는 건 어떻겠습니까",
    "6:2068:0": "의 지침 「",
    "6:2068:1": "」이(가)\n더는 계속될 수 없게 되",
    "6:2068:2": "\n다시 지침을 내리는 건 어떠할지",
    "6:2068:3": "인가",
    "6:2069:0": "의 「",
    "6:2069:1": "」 등",
    "6:2069:2": "개 지침은 지속 불가",
}

DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS) - {"6:2051:0", "6:2052:0"}


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
                "segment": "base_msggame_B001_S113",
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
