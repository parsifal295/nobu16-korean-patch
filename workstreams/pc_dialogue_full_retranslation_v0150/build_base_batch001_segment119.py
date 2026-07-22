#!/usr/bin/env python3
"""Build Base authoring segment 119 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S119.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s119", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2170:0": "이 내용으로 교섭을 제안합니다. 진행하시겠습니까?\n성공하면 이 내용으로 교섭이 확정되고\n실패하면 상대가 노하여 교섭이 난항을 겪을 것입니다",
    "6:2171:0": "정말 외교 화면에서 나가시겠습니까?",
    "6:2172:0": "정말 교섭을 거부하시겠습니까?",
    "6:2173:0": "좋은 교섭이었소!",
    "6:2174:0": "이 세력과 외교를 진행합니다",
    "6:2175:0": "교섭할 세력을 선택하십시오",
    "6:2176:0": "아직 성을 공략 중인 녀석들이 있는 건가.\n어쩔 수 없지. 끝나면 이쪽으로\n돌아오라고 전해 둬라",
    "6:2177:0": "병사를 돌려보내기로 한 날인데도 아직 공성 중인가.\n지금 진을 거두면 의리를 저버리게 되니\n조금 더 병사를 빌려줄 수밖에 없겠군",
    "6:2178:0": "약정한 날은 지났지만 원병은 아직\n성을 공략 중인가. 어쩔 수 없군.\n공성이 끝난 뒤에 철수시키도록 하지",
    "6:2179:0": "장병을 돌려받아야 하지만\n성을 공략 중이라면\n계속 빌려줄 수밖에 없겠군",
    "6:2180:0": "흠, 공성 도중에 병사를 물리면\n겁쟁이라는 비난을 듣겠군.\n끝날 때까지 병사를 두도록 할까",
    "6:2181:0": "공성 중에 병사를 거두는 것도 재미있겠지만\n이번에는 녀석들에게\n빚을 하나 지워 두기로 할까",
    "6:2182:0": "기일은 지났지만 원병은 아직\n공성 중인가.\n어쩔 수 없군. 조금 더 빌려주도록 하지",
    "6:2183:0": "진을 거두어 공성 병력이 모자라면\n우리 쪽이 원망을 살 수도 있겠군.\n공성이 끝날 때까지 기다릴 수밖에 없겠어",
    "6:2184:0": "공성 중인 병사를 돌려보내라 해 봐야\n상대도 곤란할 따름이겠지요.\n끝나는 대로 돌아오게 하지요",
    "6:2185:0": "공성 중에 진을 거두면\n우리 가문의 무위에도 흠이 되니 공략이 끝날 때까지\n병사를 빌려주도록 하겠다",
    "6:2186:0": "성을 공략 중인데 병사를 물리면\n상대도 곤란하겠지요.\n끝나는 대로 병사를 돌아오게 하지요",
    "6:2187:0": "빌려준 장병이 돌아올 날은 지났지만\n아직 공성 중인 이들도 있는 모양이군.\n공성이 끝날 때까지 철수를 기다리도록 할까",
    "6:2188:0": "잘 와 줬군!\n만나서 반갑다고",
    "6:2189:0": "이 먼 길을 오다니 고맙네.\n느긋이 이야기하고 싶지만 우선 용건부터인가",
    "6:2190:0": "이런, 이런!\n먼 길을 와 주어 감사하오",
    "6:2191:0": "잘 오셨습니다!",
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
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
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
                "segment": "base_msggame_B001_S119",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
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
