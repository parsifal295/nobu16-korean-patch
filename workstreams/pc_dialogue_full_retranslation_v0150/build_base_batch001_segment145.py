#!/usr/bin/env python3
"""Build Base authoring segment 145 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S145.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s145", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2694:0": "서로의 속셈이야 어떻든,",
    "6:2694:1": "와(과)의\n관계는 오래 이어 가고 싶구나",
    "6:2695:0": "우리 가문과,",
    "6:2695:1": "와(과)의 관계는 반석처럼 굳건하다\n언제까지나 이대로이고 싶구나",
    "6:2696:0": "은(는) 우리 가문의 으뜸가는 맹우다.\n이 관계를 해치지 않도록 조심해야겠어",
    "6:2697:0": "와(과)의 사이가 순조롭다니 잘된 일이로다\n언제까지 이어질지는 모르겠지만",
    "6:2698:0": "은(는) 우리의 방패이자 창과도 같다\n이 관계를 오래 이어 가고 싶구나",
    "6:2699:0": "와(과)의 친선을 이어 가고 싶구나\n설령 언젠가 단교하게 되더라도 말이다",
    "6:2700:0": "와(과)의 관계는 이 난세에도\n우의와 경의를 지켜 가고 싶구나",
    "6:2701:0": "와(과)는 이 전국 난세에서 드물게\n우의를 계속 지켜 가고 싶구나",
    "6:2702:0": "후후, 좋구나,",
    "6:2702:1": "와(과)의\n관계는 참으로 더할 나위 없구나",
    "6:2703:0": "와(과) 좋은 관계를 맺고 있군요\n하지만 이 난세에서는 방심은 금물입니다",
    "6:2704:0": "좋군요,",
    "6:2704:1": "와(과)는\n이런 관계를 계속 이어 가고 싶습니다",
    "6:2705:0": "우리 가문에는,",
    "6:2705:1": "와(과)의 관계가 중요하옵니다\n이대로 좋은 관계를 이어 가야 하옵니다",
    "6:2706:0": "와(과)의 우호를 이어 가는 것이 긴요하다\n결코 소홀히 해서는 안 되겠군",
    "6:2707:0": "와(과)는 지금의 좋은 관계를\n부디 오래도록 이어 가고 싶군요",
    "6:2708:0": "우리 가문에는,",
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S145", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
