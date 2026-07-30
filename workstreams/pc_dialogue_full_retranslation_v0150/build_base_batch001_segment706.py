#!/usr/bin/env python3
"""Build Base authoring segment 706 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S706.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s706", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3247:0": "퇴각로로 향하는 적군이 있사옵니다!\n대처할 부대가 필요하옵니다!",
    "9:3248:0": "적은 퇴각로를 칠 셈인 듯합니다!\n아군 부대에 수비를 맡겨야겠군요",
    "9:3249:0": "퇴각로가 노려지고 있습니다!\n즉시 대응하도록 하지요",
    "9:3250:0": "적은 퇴각로로 향하는 모양입니다\n우리도 요격해야 할 듯합니다",
    "9:3251:0": "적이 퇴각로로 향하고 있습니다\n수비를 맡겨야겠군요",
    "9:3252:0": "적이 퇴각로를 노리고 있습니다!\n막아 낼 부대가 필요하겠습니다",
    "9:3253:0": "다들 지칠 대로 지쳤어…\n한번 쉬었다 싸우고 싶은데…",
    "9:3254:0": "병사들이 너무 지쳤군…\n조금이라도 쉬게 해 주고 싶은데…",
    "9:3255:0": "병사들은 이미 녹초가 됐군…\n물러나 쉬게 하고 싶다만…",
    "9:3256:0": "병사들이 몹시 지쳐 있군요…\n잠시 쉬게 하고 싶습니다만…",
    "9:3257:0": "이대로는 모두의 체력이 버티지 못한다…\n틈을 보아 쉬게 해 주고 싶다만…",
    "9:3258:0": "병사들의 피로도 한계인가…\n쉬게 하지 않으면 제대로 싸우지 못하겠군…",
    "9:3259:0": "병사들의 움직임이 둔해졌군\n부대를 잠시 물리고 싶다만…",
    "9:3260:0": "아무래도 피로가 쌓였군…\n한번 병사들을 쉬게 하고 싶다만…",
    "9:3261:0": "병사들이 지쳐 있사옵니다…\n잠시 숨을 돌리게 하고 싶습니다만…",
    "9:3262:0": "병사들의 피로도 한계인가\n물러나 쉬게 하고 싶다만…",
    "9:3263:0": "이대로는 모두의 체력이 버티지 못하겠군요…\n쉬게 해 주고 싶습니다만…",
    "9:3264:0": "병사들이 너무 지쳤군…\n조금이라도 쉬게 해 주고 싶은데…",
    "9:3265:0": "적은 전의를 잃고 철수하는 듯하군…\n이 싸움,",
    "9:3265:1": "의 승리",
    "9:3265:2": "!",
    "9:3266:0": "전황은 명백한 열세",
    "9:3266:1": "\n여기서는 물러날 수밖에",
    "9:3266:2": "…",
}

DYNAMIC_RUNTIME_COORDINATES = {
    f"9:{record_id}:{literal_id}"
    for record_id in (3265, 3266)
    for literal_id in range(3)
}


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
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
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
                "segment": "base_msggame_B001_S706",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
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
