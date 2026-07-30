#!/usr/bin/env python3
"""Build Base authoring segment 653 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S653.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s653", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2185:0": "후후……",
    "9:2185:1": "\n간파했다",
    "9:2186:0": "제아무리",
    "9:2186:1": "라 해도\n",
    "9:2186:2": "에게는 통하지 않는다",
    "9:2187:0": "인가…… 하마터면\n걸려들 뻔했구나",
    "9:2188:0": "후후―",
    "9:2188:1": "\n이미 들켰습니다",
    "9:2189:0": "가소롭기 짝이 없구나!\n생각이 얕다―",
    "9:2190:0": "거짓말에는 소질이 없으시군요\n",
    "9:2191:0": "에\n휘둘리지는 않았군",
    "9:2192:0": "흘려들어라!\n이것은 놈들의 거짓말이다!",
    "9:2193:0": "간자는 베었다!\n위보계는 깨뜨렸다",
    "9:2194:0": "뻔히 보이는 거짓말이다……\n모두, 넘어가서는 안 된다!",
    "9:2195:0": "안타깝게도 누구 하나\n믿지 않았습니다",
    "9:2196:0": "배짱이 두둑하면\n속지 않는 법이다",
    "9:2197:0": "위보는 유효한 수다……\n성공한다면 말이지",
    "9:2198:0": "거짓 정보라니……\n꽤나 낡은 수법이군",
    "9:2199:0": "속아 넘어갈 리가\n없지 않느냐!",
    "9:2200:0": "적의 거짓 정보입니다!\n속지 마십시오!",
    "9:2201:0": "이런 계책으로\n",
    "9:2201:1": "을 속이려 들다니!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2185:0",
    "9:2185:1",
    "9:2186:0",
    "9:2186:1",
    "9:2186:2",
    "9:2187:0",
    "9:2188:0",
    "9:2188:1",
    "9:2189:0",
    "9:2190:0",
    "9:2191:0",
    "9:2201:0",
    "9:2201:1",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required" if static else "pending",
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available"
                ),
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S653",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
