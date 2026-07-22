#!/usr/bin/env python3
"""Build Base authoring segment 443 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S443.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s443", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2200:0": "아직 부대가 남아 있다\n힘으로 밀어붙여 무너뜨리면 된다!",
    "7:2201:0": "후원군도 있다\n두려워하지 말고 공격하라",
    "7:2202:0": "다른 부대도 대기하고 있다\n어서 공격하자고!",
    "7:2203:0": "후원군도 대기하고 있다\n강공으로 함락해야 한다!",
    "7:2204:0": "힘으로 밀어붙이는 편이\n후원군을 활용하기 좋겠군",
    "7:2205:0": "후원군까지 고려한다면\n힘으로 밀어붙이는 편이 효과적이겠군요",
    "7:2206:0": "후원군도 대기하고 있다\n피해를 두려워 말고 힘으로 밀어붙여라",
    "7:2207:0": "후원군을 활용하려면\n힘으로 밀어붙이는 편이 낫다!",
    "7:2208:0": "아직 부대가 남아 있다\n여기서는 강공해야 한다!",
    "7:2209:0": "힘으로 밀어붙이는 편이\n후방 부대도 활용하기 좋겠구나",
    "7:2210:0": "포위는 그만두죠\n후원군도 있잖아요!",
    "7:2211:0": "우리가 쓰러져도 후원군이 있다\n성을 강공하라!",
    "7:2212:0": "후방 병력도 대기하고 있습니다\n강공하는 편이 좋겠습니다",
    "7:2213:0": "후원군도 대기하고 있다\n피해를 두려워 말고 힘으로 밀어붙여라",
    "7:2214:0": "손대지 마라\n적의 전력이 소모되기를 기다린다",
    "7:2215:0": "흠, 무리하게 공격하지 말고\n기다려 보기로 할까",
    "7:2216:0": "지금은 그저 기다려라\n포위한 채 상황을 살펴라",
    "7:2217:0": "힘으로 밀어붙이는 것은 하책\n포위가 낫겠군",
    "7:2218:0": "병력 손실은 피하고\n포위에 전념하라",
    "7:2219:0": "힘으로 밀어붙여도 통하지 않는다\n느긋하게 기다리도록 하지",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S443", "decision_count": len(rows),
                             "retranslated": len(rows), "dynamic_runtime_review_pending": 0,
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
