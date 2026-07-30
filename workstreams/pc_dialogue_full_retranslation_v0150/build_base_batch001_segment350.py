#!/usr/bin/env python3
"""Build Base authoring segment 350 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S350.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s350", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:791:2": "!",
    "7:792:0": "(어찌 내 영지를 지켜 주지 못했",
    "7:792:1": "단 말인가……\n 우리 가문의 힘도 알 만하군……",
    "7:792:2": ")",
    "7:793:0": "(내 성 하나 지켜 내지 못하다니……\n 이래서는 주군을 뵐 면목이 없사옵니다……)",
    "7:794:0": "의 통치 범위 밖이므로\n",
    "7:794:1": "은(는) 다이묘 군단 소속이 됩니다",
    "7:795:0": "은(는) 본거지에서 멀리 떨어져 있어",
    "7:795:1": "\n휘하 군단에 통치를 맡기는 것이 좋겠습니다",
    "7:796:0": "의 성이 사라졌으므로\n",
    "7:796:1": "은(는) 해체되었습니다",
    "7:797:0": "의 본거지를\n새로 정해 주십시오",
    "7:798:0": "의 본거지를\n새로 정해 주십시오",
    "7:799:0": "본거지 이전으로 지휘 범위 밖이 된 「",
    "7:799:1": "」은(는)\n다이묘 군단 소속이 됩니다",
    "7:800:0": "본거지 이전으로\n통치 범위 밖이 된 「",
    "7:800:1": "」에서 얻는\n금전 수입이 크게 감소합니다",
    "7:801:0": "본거지 이전으로\n통치 범위 밖이 된 「",
    "7:801:1": "」 외",
    "7:801:2": "곳의 성이\n다이묘 군단 소속이 됩니다",
}

STATIC_COORDINATES: set[str] = {"7:793:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S350", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
