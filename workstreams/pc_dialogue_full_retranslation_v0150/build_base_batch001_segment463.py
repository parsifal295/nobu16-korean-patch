#!/usr/bin/env python3
"""Build Base authoring segment 463 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S463.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s463", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2518:0": "끝내 수급이 되었는가",
    "7:2519:0": "적장을 베어 쓰러뜨렸노라!",
    "7:2520:0": "최후를 장식했구나",
    "7:2521:0": "적장을 베어 쓰러뜨렸습니다",
    "7:2522:0": "적장의 수급을 취했습니다",
    "7:2523:0": "적장을 베어 쓰러뜨렸소이다!",
    "7:2524:0": "적장을 베었노라. 값진 수급이로다!",
    "7:2525:0": "적장을 베어 쓰러뜨렸사옵니다",
    "7:2526:0": "스러지는 모습, 실로 훌륭하옵니다",
    "7:2527:0": "적장을 베어 쓰러뜨렸노라!",
    "7:2528:0": "베어 쓰러뜨렸다!",
    "7:2529:0": "의",
    "7:2529:1": "이 전사",
    "7:2530:0": "이번 싸움의 전공 제일은 이 노부나가다\n내가 휘두른 창이야말로\n새 시대를 열어 갈 창끝이 되리라",
    "7:2531:0": "일번창,",
    "7:2531:1": "이(가) 해냈습니다!\n적진에 뛰어드는 것은 조금 두렵지만\n주군을 생각하면 백 명의 힘이 솟지요!",
    "7:2532:0": "일번창,",
    "7:2532:1": "이(가) 해냈다\n미카와 무사의 흔들림 없는 힘을\n똑똑히 보여 주었노라",
    "7:2533:0": "일번창은 바로 이",
    "7:2533:1": "다\n다케다 기마대의 용맹을\n똑똑히 깨달았으리라",
}

STATIC_COORDINATES: set[str] = {
    *(f"7:{record_id}:0" for record_id in range(2518, 2529)),
    "7:2530:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S463", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
