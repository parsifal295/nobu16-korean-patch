#!/usr/bin/env python3
"""Build Base authoring segment 120 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S120.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s120", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2192:0": "오오,",
    "6:2192:1": "님, 잘 오셨소\n이번 교섭으로 두 가문의 사이가 더욱 깊어지면 좋겠군",
    "6:2193:0": "후후…",
    "6:2193:1": "님, 잘 오셨소\n흥미로운 이야기라면 기꺼이 참여하겠소",
    "6:2194:0": "오오,",
    "6:2194:1": "님! 부디 편히 계시오\n이야기가 성사되면 차 자리를 마련해 두었소",
    "6:2195:0": "이(가) 오다니 반갑구먼\n일이 순조롭게 풀리면 좋겠어",
    "6:2196:0": "이런,",
    "6:2196:1": "님\n어서 오십시오!",
    "6:2197:0": "잘 오셨소! 환영하오",
    "6:2198:0": "어머, 꼭 뵙고 싶었답니다",
    "6:2199:0": "호오, 잘 오셨소!\n차라도 한잔 어떠신가?",
    "6:2200:0": "! 잘 지내는 모양이군!",
    "6:2201:0": "님, 잘 오셨소\n요즘 그쪽의 무위는 어떠하오?",
    "6:2202:0": "님, 별고 없으신 듯하오",
    "6:2203:0": "님의 활약은\n익히 들어 왔사옵니다",
    "6:2204:0": "오오,",
    "6:2204:1": "님이셨군\n그럼 이야기를 들어 보지",
    "6:2205:0": "이(가) 아닌가… 후후\n두 가문의 번영을 위해 이번에는 무슨 꿍꿍이인가?",
    "6:2206:0": "기다리고 있었소,",
    "6:2206:1": "님\n부디 편히 계시오… 그래, 용건은 무엇이오?",
    "6:2207:0": "하하하,",
    "6:2207:1": "의 이야기는 통쾌하구먼\n자, 서론이 길었으니 본론으로 들어갈까",
    "6:2208:0": "님, 건강해 보이시니 다행입니다",
    "6:2209:0": "님, 강녕해 보이시는군",
    "6:2210:0": "님, 변함없으신 듯하군요",
    "6:2211:0": "님, 무탈하시니 다행이오",
    "6:2212:0": "이봐,",
    "6:2212:1": "\n무슨 할 말이라도 있나?",
    "6:2213:0": "이런,",
    "6:2213:1": "이군\n잘 오셨소",
    "6:2214:0": "님\n상의할 일이라면 들어 드리겠소",
    "6:2215:0": "우리 가문과 상의하다니\n현명한 판단이군요",
}

STATIC_COORDINATES = {"6:2197:0", "6:2198:0", "6:2199:0", "6:2215:0"}


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
                "segment": "base_msggame_B001_S120",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
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
