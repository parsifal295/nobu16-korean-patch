#!/usr/bin/env python3
"""Build Base batch 001 segment 03 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S03.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s03", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:117:0": "내가 당주라… 알겠어,",
    "2:117:1": (
        "보다 못지않은\n"
        "훌륭하고 대단한 다이묘가 되겠어!\n"
        "그러니 잘 지켜봐 줘!"
    ),
    "2:118:0": "선대를 대신해\n이",
    "2:118:1": "이 우리 가문을 지켜 내겠소",
    "2:119:0": "모두 알겠사옵니다,",
    "2:119:1": "보다 못지않도록\n제 무용으로 반드시",
    "2:119:2": "의 이름을\n천하에 떨쳐 보이",
    "2:120:0": "뒷일은 맡겨 주시오\n이",
    "2:120:1": "이 우리 가문을 패자로 만들겠소",
    "2:121:0": (
        "의 이름이 주는 책임은 무겁지만 자랑스럽기도 하니\n"
        "절로 마음가짐이 바로 서는군"
    ),
    "2:121:1": "\n부디 뒷일은",
    "2:122:0": "맡겨 주십시오\n우리 가문을 끝까지 지켜 내겠습니다",
    "2:123:0": "부디 안심하십시오,",
    "2:123:1": "이 지켜 온\n",
    "2:123:2": (
        "가문을 제 지혜와 용맹으로 이어 가고…\n"
        "아니, 더욱 번영시키겠다고"
    ),
    "2:123:3": "약속드리",
    "2:124:0": "의 뒤를 이어\n이 가문을 일으켜 세우겠소",
    "2:125:0": (
        "님, 지금까지 가주로서 소임을 다하시느라\n"
        "참으로 고생 많으셨습니다"
    ),
    "2:125:1": "\n뒷일은",
    "2:125:2": "에게",
    "2:126:0": "안심하십시오\n제 재주로 가문을 번영으로 이끌겠습니다",
    "2:127:0": "안심하십시오",
    "2:127:1": ", 이",
    "2:127:2": "이\n당주",
    "2:127:3": "가 된 이상, 어떤 수를\n써서라도 가문을 번영시키겠",
    "2:128:0": "의 뒤를 이어\n",
    "2:128:1": "이 가문을 끝까지 지켜 내겠소",
    "2:129:0": "우리 가문의 앞날을 맡게 되다니\n더없는 기쁨인 동시에,",
    "2:129:1": "막중한 소임에\n마음이 절로 다잡히는군",
    "2:130:0": "이 늙은이에게 맡겨 주시오\n더욱 번영시킬 것을 약속드리겠소",
    "2:131:0": (
        "이런, 살날이 얼마 남지 않은 몸으로 무거운 짐을\n"
        "지게 될 줄이야… 하지만\n"
    ),
    "2:131:1": "의",
    "2:131:2": "기대에는 반드시 부응하겠소",
}


STATIC_RUNTIME_NOT_REQUIRED = {
    "2:122:0",
    "2:126:0",
    "2:130:0",
}


DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS) - STATIC_RUNTIME_NOT_REQUIRED


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
                "basis": "pristine_pc_jp_with_same_record_pc_en_sc_tc_context_where_available",
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
                "segment": "base_msggame_B001_S03",
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
