#!/usr/bin/env python3
"""Build Base authoring segment 431 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S431.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s431", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1995:0": "이(가) 위험하다\n모두 서둘러 돌아가자!",
    "7:1996:0": "이(가) 위험하다\n함락만은 막아야 한다",
    "7:1997:0": "조호이산의 계책인가……\n",
    "7:1997:1": "(으)로 돌아가자!",
    "7:1998:0": "에 공성군이 붙었는가\n돌아가자!",
    "7:1999:0": "에\n적이 들러붙었는가",
    "7:2000:0": "에 적군이 왔다고?\n내가 처단해 주마!",
    "7:2001:0": "에 적군이 있다\n물론, 두고 볼 수 없다",
    "7:2002:0": "이(가) 위험해!\n돌아가라, 어서 돌아가!",
    "7:2003:0": "이(가) 포위됐다\n에잇, 내가 방심했군!",
    "7:2004:0": "에 적……?\n발칙하군…… 당장 친다",
    "7:2005:0": "에 적의 손길이……\n서둘러 돌아가겠사옵니다",
    "7:2006:0": "에 적이라고?\n무엄하도다!",
    "7:2007:0": "을(를) 노리는가……\n흥, 예상한 바다",
    "7:2008:0": "의 위기다!\n지금 즉시 귀환하라!",
    "7:2009:0": "에 적이라고?\n돌아가지 않으면 위험하겠군……",
    "7:2010:0": "이(가) 표적이 됐다고?\n즉시 돌아가겠습니다!",
    "7:2011:0": "을(를) 노리는가?\n즉시 귀환한다!",
    "7:2012:0": "이(가) 위험합니다\n곧 돌아갑시다",
    "7:2013:0": "이(가) 위험하다!\n서둘러 돌아가야 한다!",
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
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S431", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
