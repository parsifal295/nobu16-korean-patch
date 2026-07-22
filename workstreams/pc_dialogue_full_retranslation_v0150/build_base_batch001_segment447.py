#!/usr/bin/env python3
"""Build Base authoring segment 447 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S447.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s447", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2277:0": "포위는 완성됐다\n성을 함락하면 모든 것이 끝난다",
    "7:2278:0": "주변은 이미 손안에 있다\n이제 성을 공격하라",
    "7:2279:0": "주변은 이미 장악했다\n자, 성을 몰아붙여라",
    "7:2280:0": "주변을 확보했는가\n만반의 준비를 갖춰 공성에 나서라!",
    "7:2281:0": "주변에 부대 배치를 마쳤다\n성 공략에 착수하라",
    "7:2282:0": "주변의 적은 제압했군\n좋아, 성을 박살 내라!",
    "7:2283:0": "주변 정리는 끝났군\n성을 공격하라!",
    "7:2284:0": "주변은 제압했다\n성 공략을 시작하라",
    "7:2285:0": "부대는 주변에 배치했다……\n자, 공성에 나서자!",
    "7:2286:0": "주변의 적은 격파했다……\n자, 성을 공격하라!",
    "7:2287:0": "이제 성은 고립되었다\n",
    "7:2287:1": "을(를) 공략하라",
    "7:2288:0": "주변 전력을 약화시켰다\n성 공략을 마무리하자",
    "7:2289:0": "주변은 함락되었다\n이제 공성에 나서는 게다",
    "7:2290:0": "포위는 완성됐군요\n공성에 나서겠습니다!",
    "7:2291:0": "포위는 이미 완성되었다\n남은 것은 성뿐이다!",
    "7:2292:0": "주변에 부대 배치를 마쳤다\n성 공략에 들어가겠습니다",
    "7:2293:0": "각 부대의 준비는 끝났다\n이제 성을 빼앗을 뿐이다!",
    "7:2294:0": "더는 기다릴 수 없다\n성을 함락시켜라",
    "7:2295:0": "서둘러\n공성에 나서는 게다!",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS) - {"7:2287:0", "7:2287:1"}


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
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S447", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
