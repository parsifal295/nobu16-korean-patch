#!/usr/bin/env python3
"""Build Base authoring segment 555 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S555.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s555", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:1043:0": "전쟁으로 황폐해진 마을의\n복구를 지원하",
    "8:1043:1": "\n백성들도 무척 감사하고 있",
    "8:1044:0": "전쟁에 휘말린 상인들을 위해\n살아갈 터전을 마련하",
    "8:1044:1": "\n상인들도 감사하고 있",
    "8:1045:0": "전쟁에 휘말린 마을로 가서\n도적을 토벌하고 오",
    "8:1045:1": "\n이로써 백성들도 안심하고 살 수 있",
    "8:1047:0": "피해를 입은 백성들을 위해\n살 집을 새로 마련하",
    "8:1047:1": "\n예전의 활기를 되찾은 듯",
    "8:1048:0": "토사를 치우고 가도를 정비하",
    "8:1048:1": "\n사람들의 왕래가 늘고\n장사도 활기를 띠",
    "8:1049:0": "피해를 입은 마을을 복구하고\n제방도 수리하",
    "8:1049:1": "\n더 이상의 피해는 생기지 않을 것",
    "8:1051:0": "파괴된 취락을\n재건하",
    "8:1051:1": "\n백성들도 예전처럼 지낼 수 있을 것",
    "8:1052:0": "잔해를 치우고 가도를\n정비하",
    "8:1052:1": "\n이로써 사람들의 왕래도 늘어나",
    "8:1053:0": "성벽을 수리하",
    "8:1053:1": "\n백성들이 노역에서 풀려나\n불만도 줄어든 듯",
    "8:1055:0": "식량을 제공하고\n습격으로 불탄 마을을 지원하",
    "8:1055:1": "\n백성들도 감사하고",
    "8:1056:0": "시장을 재건하",
    "8:1056:1": "\n사람들이 많이 모여들고\n장사도 활기를 띠고 있",
    "8:1057:0": "굶주린 백성의 불만을 달래려고\n식량을 베풀",
    "8:1057:1": "\n백성의 불만도 누그러지고 있",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S555", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
