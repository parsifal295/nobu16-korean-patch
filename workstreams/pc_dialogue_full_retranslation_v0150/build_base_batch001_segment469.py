#!/usr/bin/env python3
"""Build Base authoring segment 469 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S469.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s469", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2610:0": "따위에게 뒤처졌는가\n이 꼴로는,",
    "7:2610:1": "의 야망도 한낱 꿈이로다",
    "7:2611:0": "이(가) 전공 제일이라……\n어쩔 수 없군",
    "7:2612:0": "이(가) 전공 제일이라고!?\n그자에게만큼은 지고 싶지 않았건만……",
    "7:2613:0": "보다 공이 뒤지다니……\n뭘, 이제부터 치고 올라가 주마!",
    "7:2614:0": "이(가) 전공 제일이라……\n한 걸음씩 정진해 언젠가 반드시 앞지르리라",
    "7:2615:0": "의 아래에 서게 되다니……\n아니, 지금은 참고 견딜 때다",
    "7:2616:0": "와는 뜻이 맞지 않으나 실력은 확실하다\n이번 전공 제일도 수긍할 만하군",
    "7:2617:0": "……오늘은 전공으로 졌는가……\n뭐, 마지막에 이기면 그만이다",
    "7:2618:0": "에게 전공 제일을 내주다니……\n투지가 절로 끓어오르는군",
    "7:2619:0": "마음에 자만이 없어야 남의 장점을 안다\n전공 제일을 놓치고,",
    "7:2619:1": "의 용맹을 알았도다",
    "7:2620:0": "이(가) 전공 제일이라……\n허허, 훌륭하다고 인정해야겠군",
    "7:2621:0": "에게 공을 내주었는가\n뭐, 됐다. 전공 제일 따위 바라지 않는다",
    "7:2622:0": "이(가) 전공 제일이라고!?\n다음번에는",
    "7:2622:1": "이(가) 이긴다! 똑똑히 보아라!",
    "7:2623:0": "의 아래에 서게 되다니……!\n다음 싸움에서는 구름을 움켜쥐고 전공 제일로 오르리라!",
    "7:2624:0": "이(가) 전공 제일……?\n아니, 태평성대에 가까워진 일이다…… 기뻐해야지……",
    "7:2625:0": "에게 공이 미치지 못했다……?\n아니…… 아군의 영예를 기뻐해야 한다",
    "7:2626:0": "이(가) 가장 큰 공을 세웠다고!?\n그 자식…… 인정 못 해!",
}

STATIC_COORDINATES: set[str] = set()


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S469", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
