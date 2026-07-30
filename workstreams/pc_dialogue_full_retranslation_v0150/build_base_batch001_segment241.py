#!/usr/bin/env python3
"""Build Base authoring segment 241 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S241.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s241", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3876:1": "\n즉시 실행에 옮기",
    "6:3877:0": "을(를) 건설하",
    "6:3877:1": "\n훌륭히 일한 자에게는 상을 내리",
    "6:3877:2": "\n모두, 힘써 일하",
    "6:3878:0": "의 건설에 착수하",
    "6:3878:1": "\n우리 성하를 더욱 나은 곳으로",
    "6:3879:0": "우리 성하에",
    "6:3879:1": "을(를) 건설하",
    "6:3879:2": "\n허투루 짓지 말고 후세에 남을 만한 것으로",
    "6:3880:0": "이제 시간을 진행하면 시설 건설이 시작됩니다\n튜토리얼에서는 금전과 노력이 필요 없습니다\n결과도 바로 나옵니다",
    "6:3881:0": "성하 시설을 지을 칸을 선택하거나 성하 방침을 설정하십시오",
    "6:3882:0": "역직을 내려 준 데\n감사하고 있다",
    "6:3883:0": "선물을 준 데 감사하고 있다",
    "6:3884:0": "우리 가문의 기세를\n높이 평가하고 있다",
    "6:3885:0": "혼인 관계를 맺고 있어\n신뢰할 만하다",
    "6:3886:0": "맹우로서\n신뢰하고 있다",
    "6:3887:0": "주종 관계를 맺은 세력이라\n신뢰하고 있다",
    "6:3888:0": "우리 가문을\n신뢰하고 있다",
    "6:3889:0": "에게\n호감을 품고 있다",
    "6:3890:0": "와(과)는\n마음이 잘 맞는다",
}

STATIC_COORDINATES: set[str] = {
    "6:3880:0",
    "6:3881:0",
    "6:3882:0",
    "6:3883:0",
    "6:3884:0",
    "6:3885:0",
    "6:3886:0",
    "6:3887:0",
    "6:3888:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S241", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
