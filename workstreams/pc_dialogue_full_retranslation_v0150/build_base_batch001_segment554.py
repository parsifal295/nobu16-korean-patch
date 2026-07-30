#!/usr/bin/env python3
"""Build Base authoring segment 554 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S554.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s554", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:1032:0": "을(를) 건설하",
    "8:1032:1": "\n영내는 더욱 발전할 것",
    "8:1033:0": "교역항이 완성되",
    "8:1033:1": "\n곧바로 각지에서 배가 모여들어\n크게 붐비",
    "8:1034:0": "금산 마을을 건설하",
    "8:1034:1": "\n새로운 수입원을 얻은 덕분에\n우리 가문의 재정도 넉넉해지",
    "8:1035:0": "은산 마을을 건설하",
    "8:1035:1": "\n우리 가문의 새 수입원이 되어\n영내는 더욱 발전할 것",
    "8:1036:0": "마목장을 건설하",
    "8:1036:1": "\n이로써 많은 준마가 자라나\n기병도 한층 정예해질 것",
    "8:1037:0": "대장간 마을을 건설하",
    "8:1037:1": "\n철포를 충분히 갖출 수 있게 되어\n전장에서도 마음껏 활용할 수 있을 듯",
    "8:1038:0": "절을 건설하",
    "8:1038:1": "\n백성들이 마음을 기댈 곳이 되어\n승려들도 기쁨을 감추지 못하는 듯 보이",
    "8:1039:0": "남만사를 건설하",
    "8:1039:1": "\n포교가 진전됨에 따라\n새로운 문화가 뿌리내릴지도……",
    "8:1040:0": "온천향을 건설하",
    "8:1040:1": "\n아무래도 부상 치료에 효험이 있어\n병사들의 요양에도 도움이 될 것",
    "8:1041:0": "대농촌을 건설하",
    "8:1041:1": "\n광활한 농지를 본 백성들도 의욕이 넘치니\n수확량은 물론 병사 수도 기대할 수 있을 듯",
    "8:1042:0": "대시장을 건설하",
    "8:1042:1": "\n벌써 장사가 활발해진 모습이니\n큰 수입을 기대할 수 있",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S554", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
