#!/usr/bin/env python3
"""Build Base authoring segment 187 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S187.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s187", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3279:0": "용맹으로 이름난 귀 가문이라면\n",
    "6:3279:1": "의 공략쯤은 일도 아니겠지",
    "6:3280:0": "을(를) 공략하는 일,\n실패 없도록 부탁드리오",
    "6:3281:0": "의 공략을\n잘 부탁하네",
    "6:3282:0": "의 공략,\n기대하고 있소이다",
    "6:3283:0": "을(를) 공략해 주겠는가\n참으로 든든하구나",
    "6:3284:0": "의 공략,\n좋은 소식을 기다리겠네",
    "6:3285:0": "따위는\n가볍게 해치워 주십시오",
    "6:3286:0": "의 공략,\n꼭 성공해 주게!",
    "6:3287:0": "은(는) 맡겼습니다\n기대하겠습니다",
    "6:3288:0": "귀 가문의 병력이라면\n",
    "6:3288:1": "따위는 손쉽게 함락할 터…\n길보를 기다리고 있겠소이다",
    "6:3289:0": "은(는) 소중한 땅이다\n부탁한다, 끝까지 지켜 다오",
    "6:3290:0": "은(는) 내줄 수 없는 곳이오\n부디 끝까지 지켜 주길 바라오",
    "6:3291:0": "은(는) 우리에게 생명줄과도 같은 성\n부디 끝까지 지켜 주게",
    "6:3292:0": "의 방어를\n부디 잘 부탁드립니다",
    "6:3293:0": "은(는) 요지다\n반드시 끝까지 지켜 다오",
    "6:3294:0": "은(는) 우리에게 없어서는 안 될 땅\n부디 끝까지 지켜 주길 바란다",
    "6:3295:0": "은(는) 잃을 수 없소\n반드시 지켜 주시오",
    "6:3296:0": "은(는) 요지요\n부디 끝까지 지켜 주시오",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S187", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
