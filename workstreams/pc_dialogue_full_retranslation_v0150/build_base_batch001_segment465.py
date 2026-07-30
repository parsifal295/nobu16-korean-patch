#!/usr/bin/env python3
"""Build Base authoring segment 465 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S465.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s465", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2545:0": "일번창은",
    "7:2545:1": "의 것이로다!\n연륜은 못 당하는 법\n모두 똑똑히 깨달았을 테지!",
    "7:2546:0": "일번창은",
    "7:2546:1": "입니다!\n하지만 이번 승리는\n모두가 분투해 준 덕분입니다",
    "7:2547:0": "이(가) 일번창이다!\n온 힘을 다해 싸웠다\n그뿐이다",
    "7:2548:0": "어머나,",
    "7:2548:1": "이(가) 일번창입니까?\n모두에게 힘이 될 수 있어\n무척 기쁩니다",
    "7:2549:0": "일번창은 소인이 차지했소이다!\n명예로운 나의 싸움 모습을\n모두가 알게 되리라",
    "7:2550:0": "노부나가야말로 이번 싸움의 전공 제일이로다!\n퇴로가 끊기고도 살아남을 적이 어디 있으랴\n아군을 승리로 이끌어 주었도다",
    "7:2551:0": "전공 제일은 내가 받겠노라!\n",
    "7:2551:1": "의 활약으로 적은 독 안에 든 쥐\n달아날 길도 없이 상대가 되지 못했겠지!",
    "7:2552:0": "적의 퇴로를 끊은 것이야말로\n승패를 가른 결정타였다\n실로 천금 같은 활약이로다",
    "7:2553:0": "퇴로를 막으면 적은 한곳으로 내몰린다\n이제 반격할 틈도 주지 않고 짓누를 뿐\n전공 제일도 당연한 일이로다",
    "7:2554:0": "흠…… 전공 제일인가\n그러고 보니 적의 퇴로를 끊었지……\n그 공이겠군",
    "7:2555:0": "적의 퇴로를 끊는 것은 싸움의 정석\n전공 제일이라니 분에 넘치는 영광이오\n감사히 받겠소이다",
    "7:2556:0": "이번 싸움에서 적의 퇴로를 끊어\n아군에게 승리를 안겨 준\n",
    "7:2556:1": "야말로 전공 제일이다!",
    "7:2557:0": "퇴로가 끊겼으니\n적도 어찌할 도리가 없었을 터\n우리의 승리는 필연이었다",
    "7:2558:0": "똑똑히 봐라, 전공 제일이다!\n퇴로를 막아 줬더니 적이 허둥대더군\n정말이지, 즐거운 싸움이었다고!",
    "7:2559:0": "적의 퇴로를 끊은 것이\n아군의 승리…… 나아가 무훈으로 이어지다니!\n전공 제일, 황송하옵니다!",
}

STATIC_COORDINATES: set[str] = {
    "7:2549:0", "7:2550:0", "7:2552:0", "7:2553:0", "7:2554:0", "7:2555:0",
    "7:2557:0", "7:2558:0", "7:2559:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S465", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
