#!/usr/bin/env python3
"""Build Base authoring segment 439 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S439.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s439", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2120:0": "병량이 부족한가……\n그렇다면 강공할 뿐이다",
    "7:2121:0": "병량이 불안하군\n어서 함락해 다오",
    "7:2122:0": "병량이 위태롭군……\n단숨에 짓밟아 주자고",
    "7:2123:0": "병량이 위태롭군\n어서 함락해 다오",
    "7:2124:0": "병량이 빠듯한가……\n서둘러 끝장을 내야겠군",
    "7:2125:0": "병량이 걱정되는군요……\n여기서는 속공이 최선입니다",
    "7:2126:0": "병량이 부족하다면\n어서 함락해 주마",
    "7:2127:0": "병량이 조금 부족한가\n서둘러 끝내자",
    "7:2128:0": "비축한 병량이 적다\n어서 함락해야겠군",
    "7:2129:0": "병량이 불안하구나\n느긋하게 굴 수는 없겠군",
    "7:2130:0": "병량이 얼마 남지 않았다……\n신속히 함락시키겠습니다!",
    "7:2131:0": "병량이 불안하다……\n시간을 끌 수는 없다!",
    "7:2132:0": "병량이 넉넉하지 않습니다\n어서 함락합시다",
    "7:2133:0": "병량이 불안하군\n서둘러 함락해야 한다",
    "7:2134:0": "서둘러 함락시켜라\n후원군이 오면 성가시다",
    "7:2135:0": "후원군이 도착하기 전에\n함락해 버리는 게다",
    "7:2136:0": "적이 원군을 보냈는가\n성 공략을 서두르게 하자",
    "7:2137:0": "후원군을 보냈다면\n느긋하게 공격할 수 없겠군",
    "7:2138:0": "후원군이 도착하기 전에\n함락하면 됩니다",
    "7:2139:0": "후원군을 보냈구나\n침공을 서두르게 하라",
}

STATIC_COORDINATES = set(TRANSLATIONS)


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
                     "semantic_review": "approved", "scope_classification": "retranslated",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S439", "decision_count": len(rows),
                             "retranslated": len(rows), "dynamic_runtime_review_pending": 0,
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
