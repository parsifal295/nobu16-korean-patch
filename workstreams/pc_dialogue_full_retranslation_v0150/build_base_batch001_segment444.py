#!/usr/bin/env python3
"""Build Base authoring segment 444 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S444.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s444", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2220:0": "적의 성을 포위하라!\n무리하게 밀어붙이는 것은 금물이다!",
    "7:2221:0": "힘으로 밀어붙이기보다\n포위하는 것이 상책이다",
    "7:2222:0": "무리하게 공격하지 마라\n느긋하게 포위하자고",
    "7:2223:0": "공격할 필요는 없다\n적의 성을 완전히 포위하라!",
    "7:2224:0": "공격할 필요도 없다\n에워싸라!",
    "7:2225:0": "성을 포위하고\n상황을 지켜보겠습니다",
    "7:2226:0": "적의 성을 포위하라!\n절대로 공격하지 마라!",
    "7:2227:0": "무리하게 강공할 필요는\n없을 듯하군",
    "7:2228:0": "피해를 입을 필요는 없다\n차분히 포위하라",
    "7:2229:0": "서두르면 지는 게야\n성을 포위하라!",
    "7:2230:0": "무리는 금물입니다\n성을 포위해 주십시오",
    "7:2231:0": "피해를 입을 필요는 없다\n성을 포위하라!",
    "7:2232:0": "성을 포위하겠습니다\n차분히 공략합시다",
    "7:2233:0": "힘으로 밀어붙일 필요는 없다\n포위하자",
    "7:2234:0": "은(는) 내 영지다\n탈환해야겠군",
    "7:2235:0": "은(는) 본래\n우리 가문의 것이다!",
    "7:2236:0": "은(는) 우리의 군이다\n탈환하도록 하지",
    "7:2237:0": "을(를) 탈환해\n훗날 전쟁에 활용하도록 하지",
    "7:2238:0": "을(를)\n탈환해 오겠다",
    "7:2239:0": "은(는) 탈환해\n두도록 하지",
}

STATIC_COORDINATES = {f"7:{record_id}:0" for record_id in range(2220, 2234)}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S444", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
