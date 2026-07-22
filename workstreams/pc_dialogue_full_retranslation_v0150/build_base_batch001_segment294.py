#!/usr/bin/env python3
"""Build Base authoring segment 294 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S294.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s294", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4417:2": "면해 주시길 바랍니다…",
    "6:4418:0": "전선이야말로 제 특성이 빛을 발할 곳입니다\n부디 그 땅을",
    "6:4418:1": "에게 맡겨 주십시오!\n결코 후회하지 않게 해 드리",
    "6:4419:0": "그 땅에서의 행군을 생각하신다면\n제 특성은 반드시\n유리하게 작용할 것",
    "6:4420:0": "제 특성은 바로 그 땅과 같은\n전선에서야말로 빛납니다…\n기대를 결코 저버리지",
    "6:4421:0": "…전선의 땅이니, 배속된다면\n조략을 펼치게 되",
    "6:4421:1": "\n하지만,",
    "6:4421:2": "…",
    "6:4422:0": "부디 이 땅을",
    "6:4422:1": "에게 맡겨 주십시오!\n제 뛰어난 조략으로\n반드시 성과를 내 보이",
    "6:4423:0": "적지에 접한 그 땅이라면\n제 조략 솜씨를 선보일 기회가\n있을지도 모르",
    "6:4424:0": "취락 장악 진척이 더딘 모양이군",
    "6:4424:1": "\n분명",
    "6:4424:2": "도 취락 장악에는 능하지만\n가능하면 다른 이를 택해 주십시오…",
    "6:4425:0": "취락 장악은 제 특기입니다\n부디 이 땅은",
    "6:4425:1": "에게 맡겨 주십시오!\n단숨에 진척시켜 보이",
    "6:4426:0": "아직 장악하지 못한 취락이 있군요…\n",
    "6:4426:1": "에게 맡겨 주신다면\n신속히 장악을 진행하",
    "6:4427:0": "성의 수입 기반은 군의 취락에서 나옵니다…\n장악 진척이 더딘 듯하지만\n",
    "6:4427:1": "에게 맡기시면 개선할 수 있",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S294", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
