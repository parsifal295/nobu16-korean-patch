#!/usr/bin/env python3
"""Build Base authoring segment 357 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S357.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s357", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:847:0": "모신",
    "7:848:0": "도카이도 제일의 무사",
    "7:849:0": "독안룡",
    "7:850:0": "사가미의 사자",
    "7:851:0": "귀신 시마즈",
    "7:852:0": "귀신 시마즈",
    "7:853:0": "도사의 걸물",
    "7:854:0": "놈이 건방지구나\n",
    "7:854:1": "이(가) 직접 네 분수를 가르쳐 주마!",
    "7:855:0": "우쭐대지 마라, 「",
    "7:855:1": "」놈아!\n살무사의 안목이 흐려졌음을\n이 창으로 증명해 보이겠다!",
    "7:856:0": ", 그 소문이 사실인지 아닌지\n내 눈으로 가려내 주마",
    "7:857:0": "설마 이런 날이 오다니……\n구면이라 해도 봐줄 수는 없소",
    "7:858:0": "불적·",
    "7:858:1": "!\n불구대천의 원수이니, 이제 칼과 창으로 말할 뿐이다",
    "7:859:0": "어리석은 놈, 누구에게 칼을 겨누는 것이냐!\n벼락출세한 자의 오만을 더는 좌시할 수 없다!",
    "7:860:0": "·",
    "7:860:1": "……\n장수가 악귀나찰이라 해도, 싸우는 자는 사람이다……!",
    "7:861:0": "왔는가, 호적수여!\n자, 이제 자웅을 가리자!",
    "7:862:0": "그 무례한 야심, 가소롭도다\n교토에 어느 깃발이 설 것인지\n이 한 번의 싸움으로 밝혀 내리라",
}

STATIC_COORDINATES: set[str] = {
    "7:847:0", "7:848:0", "7:849:0", "7:850:0", "7:851:0", "7:852:0", "7:853:0",
    "7:857:0", "7:859:0", "7:861:0", "7:862:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S357", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
