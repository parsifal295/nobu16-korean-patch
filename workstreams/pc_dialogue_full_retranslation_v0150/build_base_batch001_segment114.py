#!/usr/bin/env python3
"""Build Base authoring segment 114 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S114.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s114", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2070:0": "에게 내려 둔\n",
    "6:2070:1": "개 지침이 중단돼 버렸어!\n새 지침을 내려 달라고!",
    "6:2071:0": "의 「",
    "6:2071:1": "」 등",
    "6:2071:2": "개 지침이\n더는 이어지지 않아 중지를 전하였소\n새 지침을 내려 주시길 바라오",
    "6:2072:0": "유감스럽지만",
    "6:2072:1": "의",
    "6:2072:2": "개 지침\n「",
    "6:2072:3": "」 등을 중단하였소\n새 지침을 정해 주시오",
    "6:2073:0": "의 지침 「",
    "6:2073:1": "」 등\n",
    "6:2073:2": "개 지침을 계속하기 어려워졌으니\n다시 지침을 내려 주시겠습니까",
    "6:2074:0": "의 「",
    "6:2074:1": "」을(를) 포함한\n",
    "6:2074:2": "개 지침은 더는 이어 갈 수 없소\n지침을 다시 검토해 주시오!",
    "6:2075:0": "부득이",
    "6:2075:1": "의 지침\n「",
    "6:2075:2": "」 등",
    "6:2075:3": "개를 중단하였습니다\n다음 지침은 어찌하시겠습니까",
    "6:2076:0": "「",
    "6:2076:1": "」 등",
    "6:2076:2": "개를 지시한 Gd1.GdName \n에서는 계속할 수 없다고 하옵니다…\n다음 지침을 검토해 주시옵소서",
    "6:2077:0": "의 지침 「",
    "6:2077:1": "」 등\n",
    "6:2077:2": "개가 계속될 수 없게 된 모양이구먼…\n새 지침을 내려 주지 않겠는가",
    "6:2078:0": "의 지침 「",
    "6:2078:1": "」 등\n",
    "6:2078:2": "개를 더는 계속할 수 없게 되었습니다\n다시 지침을 내려 주시겠습니까",
    "6:2079:0": "의 「",
    "6:2079:1": "」 등\n",
    "6:2079:2": "개 지침은 더는 이어 갈 수 없사옵니다…\n새 지침을 내려 주시옵소서",
    "6:2080:0": "의 「",
    "6:2080:1": "」 같은\n",
    "6:2080:2": "개 지침을 계속할 수 없게 된 듯합니다…\n새 지침을 검토해 주시겠습니까?",
    "6:2081:0": "의 「",
    "6:2081:1": "」 등\n",
    "6:2081:2": "개 지침을 더는 계속할 수 없게 되었습니다\n다시 지침을 내리시는 건 어떻겠습니까",
    "6:2082:0": "에서 일어난 잇키가 진압됨",
    "6:2083:0": " 함락에 성공했군…",
    "6:2083:2": "의 원군에 감사하오",
    "6:2084:0": " 함락에 성공했군…",
    "6:2084:2": "의 원군에 감사하오",
    "6:2085:0": " 함락에 성공했군…",
    "6:2085:2": "의 원군에 감사하오",
    "6:2086:0": " 함락에 성공했군…",
    "6:2086:2": "의 원군에 감사하오",
    "6:2087:0": " 함락에 성공했군…",
    "6:2087:2": "의 원군에 감사하오",
    "6:2088:0": " 함락에 성공했군…",
    "6:2088:2": "의 원군에 감사하오",
    "6:2089:0": " 함락에 성공했군…",
    "6:2089:2": "의 원군에 감사하오",
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
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
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
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
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
                "segment": "base_msggame_B001_S114",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
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
