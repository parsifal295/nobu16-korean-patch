#!/usr/bin/env python3
"""Build Base authoring segment 353 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S353.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s353", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:819:0": "이(가) 이토록 쇠퇴하다니……\n이대로 계속 섬겨도 앞날은 없다",
    "7:819:1": "\n충성을 다하는 것도 여기까지라",
    "7:820:0": "쇠퇴한 세력 「",
    "7:820:1": "」에 가망이 없다고 보고\n출분한 자가 있는 듯",
    "7:820:2": "\n등용할 좋은 기회일지도 모르",
    "7:821:0": "와(과) 싸우는 일이라면\n협력하기는 어렵겠소",
    "7:822:0": "의 평판을 듣자 하니,\n우리 병력을 맡길 만한 상대는 아니옵니다",
    "7:823:0": "현재 출진 중이라,\n더는 다른 가문에 원군을 보낼 수 없사옵니다",
    "7:824:0": "우리 병사들은 요양 중이라\n아직 원군을 보낼 형편이 아니옵니다",
    "7:825:0": "에는 이제 막 원군을 보낸 참이라\n더 이상의 협력은 어렵습니다",
    "7:826:0": "이(가) 병력 「",
    "7:826:1": "」을(를) 이끌고\n우리 영지를 노리고 있",
    "7:827:0": "예전부터 우리와 다투어 온 「",
    "7:827:1": "」의\n",
    "7:827:2": "놈이, 마침내 병력 「",
    "7:827:3": "」을(를) 이끌고\n우리 영지를 향해 출진해",
    "7:828:0": "이(가) 진군을 시작했다",
    "7:829:0": "의 요청에 따라\n",
    "7:830:0": "이(가) 병력 「",
    "7:830:1": "」을(를) 이끌고\n우리 영지를 향해 출진해 오",
}

STATIC_COORDINATES: set[str] = {"7:823:0", "7:824:0"}


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
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S353", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
