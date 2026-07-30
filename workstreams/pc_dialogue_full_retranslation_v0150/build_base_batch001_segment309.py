#!/usr/bin/env python3
"""Build Base authoring segment 309 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S309.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s309", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:178:0": "저 망루가 남아 있는 한,\n백성도 우리를 따르기 어려울 듯합니다",
    "7:179:0": "적의 망루 따위는\n해만 끼칠 뿐입니다",
    "7:180:0": "모처럼 있는 망루이니,\n손에 넣어 유용하게 씁시다",
    "7:181:0": "그 망루를 손에 넣어,\n백성의 마음을 얻는 것이 어떻겠습니까",
    "7:182:0": "그 땅의 망루를\n수중에 넣어야 합니다",
    "7:183:0": "이(가) 전장에\n나왔다 하니, 절호의 기회입니다",
    "7:184:0": "이(가) 전면에\n나섰다면 쓰러뜨려야 합니다",
    "7:185:0": "의 당주가 몸소\n전면에 나서다니, 절호의 기회입니다",
    "7:186:0": "지금이야말로 「",
    "7:186:1": "」이(가)\n수급을 올릴 때입니다!",
    "7:187:0": "의 당주가 모습을 드러냈으니,\n이 기회는 놓칠 수 없습니다!",
    "7:188:0": "놈, 몸소 오다니\n목을 내걸어 달라는 모양입니다",
    "7:189:0": "을(를) 사로잡아\n공성의 실마리로 삼읍시다",
    "7:190:0": "이(가) 출진했습니다.\n공성에 앞서 제압합시다",
    "7:191:0": "을(를) 쓰러뜨리면\n공성도 수월해질 것입니다",
    "7:192:0": "성주 「",
    "7:192:1": "」이(가)\n나왔으니 사로잡읍시다",
    "7:193:0": "은(는) 성주이니,\n먼저 제거하는 것이 좋겠습니다",
    "7:194:0": "적성 공략을 위해,",
    "7:194:2": "을(를) 사로잡읍시다",
}

STATIC_COORDINATES: set[str] = {"7:178:0", "7:179:0", "7:180:0", "7:181:0", "7:182:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S309", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
