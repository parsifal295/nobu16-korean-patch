#!/usr/bin/env python3
"""Build Base authoring segment 483 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S483.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s483", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2796:0": "을(를) 공격할 준비가 갖춰",
    "7:2796:1": "\n이제부터 우리 군단이\n",
    "7:2796:2": "을(를) 쳐부수고 돌아오",
    "7:2797:0": "아군과 힘을 합쳐,",
    "7:2797:1": "(으)로 쳐들어가겠습니다\n승전보를",
    "7:2797:2": "기대하",
    "7:2798:0": "아군의",
    "7:2798:1": "공격에 가세하",
    "7:2798:2": "\n우리 군단은",
    "7:2798:3": "(으)로 쳐들어가\n적군을 분산시키려 합니다",
    "7:2799:0": "의 방비가 허술해졌다고 하옵니다\n이 기회에 우리 군단이 공격해 빼앗고 오겠",
    "7:2800:0": "은(는) 싸움에 능하기로 이름난 장수\n그",
    "7:2800:1": "이(가) 우리 가문의 위협이 되기 전에\n우리 군단이 처단하고 오겠",
    "7:2801:0": "증오스러운",
    "7:2801:1": "이(가) 이웃 나라에 있다는 사실을\n더는 참을 수 없",
    "7:2801:2": "\n우리 군단이 토벌하고 오",
    "7:2802:0": "은(는)",
    "7:2802:1": "에게는 불구대천의 원수\n그자를 더는 살려 둘 수 없",
    "7:2802:2": "\n우리 군단이 황천으로 보내고 오",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S483", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
