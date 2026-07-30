#!/usr/bin/env python3
"""Build Base authoring segment 539 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S539.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s539", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:889:0": "어느덧 제",
    "8:889:1": "년입니까…\n이곳은 제2의 고향입니다",
    "8:890:0": "의 군 특성 「",
    "8:890:1": "」의 레벨이 최대치에 도달",
    "8:891:0": "의 「",
    "8:891:1": "」 지행 기간:",
    "8:891:2": "년, 충성 +",
    "8:892:0": "요지를 맡겨 주시다니\n더욱 힘이 나옵니다",
    "8:893:0": "요지를 받았으니\n정신 바짝 차려야겠구먼!",
    "8:894:0": "요지를 맡겨 주시다니!\n더욱 힘써야겠구나!",
    "8:895:0": "중요한 땅을 하사받다니\n주군의 신뢰에 보답하겠소",
    "8:896:0": "이 땅은 우리 가문의 요지\n마음을 다잡고 임해야겠군…",
    "8:897:0": "요지를 지행으로 받았나…\n흥, 벌써부터 몸이 근질거리는군!",
    "8:898:0": "중요한 땅을 맡게 되었나\n주군께서도 내 진가를 알아보시는군",
    "8:899:0": "후후, 이리 중요한 땅을\n맡겨 주셨군요",
    "8:900:0": "이곳은 중요한 땅이로군\n맡게 되다니 영광이로다",
    "8:901:0": "설마 이곳을 맡겨\n주실 줄이야!",
    "8:902:0": "중요한 땅을 맡았으니\n기대에 부응해야겠군!",
    "8:903:0": "이곳을 맡겨 주시다니\n주군께 감사드립니다",
    "8:904:0": "을(를) 포함해 총",
    "8:904:1": "명이 지행 기간에 따라 훈공 획득",
    "8:905:0": "을(를) 포함해 총",
    "8:905:1": "개 군의 군 특성이 최대 레벨에 도달",
    "8:906:0": "의 통솔 능력이 성장",
}

STATIC_COORDINATES = {f"8:{record_id}:0" for record_id in range(892, 904)}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S539", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
