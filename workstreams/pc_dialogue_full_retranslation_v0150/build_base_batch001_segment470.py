#!/usr/bin/env python3
"""Build Base authoring segment 470 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S470.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s470", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2627:0": "에게 공으로 밀려 버리다니……\n칫,",
    "7:2627:1": "도 이제 한물갔군!",
    "7:2628:0": "이(가) 전공 제일의 영예를 차지했는가……\n그자에게 무훈을 내주다니 분하군……",
    "7:2629:0": "의 활약에 미치지 못했는가……\n다른 누구도 아닌 그자에게……!",
    "7:2630:0": "이(가) 전공 제일인가\n분하기도 하고 기쁘기도 하구나",
    "7:2631:0": "이(가) 전공 제일이라……\n저런 자에게 활약에서 밀리다니 나도 미숙했군",
    "7:2632:0": "에게 전공 제일을 빼앗기다니\n제 활약이 그에 미치지 못했다는 뜻이군요",
    "7:2633:0": "에게 전공으로 뒤졌습니까\n……다음에는 그렇게 두지 않겠습니다",
    "7:2634:0": "에게 전공 제일을 빼앗겼는가\n아직 단련이 한참 부족하군……",
    "7:2635:0": "따위에게 전공 제일을 빼앗기다니\n부끄럽기 짝이 없구나……",
    "7:2636:0": "이(가) 이번 싸움의 핵심이었나\n마음에 들진 않지만…… 확실히 싸움에는 능하군",
    "7:2637:0": "이(가) 전공 제일이라니\n두고 보아라……",
    "7:2638:0": "이(가) 전공 제일이라니……\n이번만은 승리를 양보해 주도록 하지",
    "7:2639:0": "의 전공 제일, 참으로 장하도다\n다음에도 기껏 목숨이나 내던져 싸워 주었으면 좋겠군",
    "7:2640:0": "에게 뒤처지다니……\n나이는 먹고 싶지 않은 법이군……",
    "7:2641:0": "에게 전공 제일을 빼앗기다니……\n으으, 분하구나……",
    "7:2642:0": "에게 일등을 빼앗기다니……\n다음에는 절대로 지지 않겠습니다!",
    "7:2643:0": "이(가) 전공 제일? 아니야\n다음에는,",
    "7:2643:1": "이(가) 전공 제일이 되면 내가 진 게 아니야",
    "7:2644:0": "이(가) 전공 제일이라고?\n실컷 기뻐해 두어라. 다음에는 어림없다……",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S470", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
