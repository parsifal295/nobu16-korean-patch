#!/usr/bin/env python3
"""Build Base authoring segment 517 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S517.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s517", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:490:0": "다시 태어날 수 있다 해도, 다음 생에도\n",
    "8:490:1": "의 곁에서 일하고 싶사옵니다…",
    "8:491:0": "제 지략과 무용이 「",
    "8:491:1": "」의 패업에 도움이\n되었사옵니까…",
    "8:492:0": "을(를) 모실 수 있었던 것은\n제 생애의 영예였사옵니다…",
    "8:493:0": "이제는 창조차 들 수 없는 몸, 허나 전장에서\n쓰러지지 못한 것이 유일한 한이옵니다…",
    "8:494:0": "이제는 지옥의 귀신과 싸울 작정이옵니다.\n",
    "8:494:1": ", 이만 작별이옵니다",
    "8:495:0": "계략을 꾸미고, 속이고, 기만하며 살아왔으나\n제 목숨이 다하는 것만은 참이옵니다…",
    "8:496:0": "훗, 크큭, 이 몸의 죽음마저 계략의\n하나로 삼아 주신다면 여한이 없사옵니다…",
    "8:497:0": "제 수명이 다했사옵니다. 이제부터는\n함께 걷지 못함을 부디 용서해 주시기를…",
    "8:498:0": "목숨을 다하고도 아직 정상은 보이지 않는가.\n",
    "8:498:1": ", 부디 천하를 거머쥐시옵소서…",
    "8:499:0": "이토록 오래 살았으니 여한 따위 없느냐 하면…\n산더미처럼 남았지만, 후인들에게 맡기도록 하지…",
    "8:500:0": "을(를) 모실 수 있었던 것은\n제 생애에서 가장 복된 일이었사옵니다",
    "8:501:0": "여기까지인 듯하옵니다… 먼저 가겠사옵니다\n이곳에는 되도록 늦게 오시기를 바라옵니다…",
    "8:502:0": "이제는 서는 것조차 여의치 않사옵니다…\n저승에서 우리 가문의 번영을 빌겠사옵니다",
    "8:503:0": "이토록 오래 살 줄이야\n전장에서 쓰러지지 못함은 아쉬우나 어쩔 수 없군",
    "8:504:0": "을(를) 위해 칼과 창을 휘둘러 왔사오나\n여기까지인 듯하옵니다… 원통하옵니다…",
    "8:505:0": "제 목숨도 여기까지인 듯하옵니다… 좀 더\n",
    "8:505:1": "의 힘이 되고 싶었사옵니다…",
    "8:506:0": "후후…",
    "8:506:1": "을(를) 모실 수 있어\n저는 행복했사옵니다…",
    "8:507:0": "은(는) 여기까지인가…\n참으로 원통하도다…",
    "8:508:0": ", 송구하옵니다…\n이제는 도움이 되지 못할 듯하옵니다…",
}

STATIC_COORDINATES = {
    "8:493:0",
    "8:495:0",
    "8:496:0",
    "8:497:0",
    "8:499:0",
    "8:501:0",
    "8:502:0",
    "8:503:0",
}


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
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S517", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
