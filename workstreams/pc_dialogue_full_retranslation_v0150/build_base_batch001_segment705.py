#!/usr/bin/env python3
"""Build Base authoring segment 705 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S705.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s705", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3233:0": "의 부대가 괴멸하다니…!?\n",
    "9:3233:1": ", 달아날 틈도 없군…",
    "9:3234:0": "물러날 틈조차 주지 않는 일격…\n",
    "9:3234:1": ", 두려운 적이로다…",
    "9:3235:0": "이 무슨 일격인가…\n",
    "9:3235:1": ", 얕볼 수 없는 상대군…",
    "9:3236:0": "으음, 물러날 틈도 주지 않는가…\n",
    "9:3236:1": ", 제법 뛰어난 장수로군…",
    "9:3237:0": "이렇게 쉽게 지다니…\n",
    "9:3237:1": "의 힘을 얕보았군요…",
    "9:3238:0": "일격에 무너지다니…\n",
    "9:3238:1": ", 생각보다 강하군",
    "9:3239:0": "철수조차 허용하지 않는 일격…\n이것이",
    "9:3239:1": "의 힘입니까…",
    "9:3240:0": "물러날 틈도 없이 괴멸하다니…\n",
    "9:3240:1": ", 어찌 이리 강한가",
    "9:3241:0": "놈들, 퇴각로를 노리고 있군!\n누군가 보내는 게 좋겠어",
    "9:3242:0": "퇴각로를 노리는 적군이 있습니다!\n즉시 대처해야 할 듯합니다!",
    "9:3243:0": "놈들은 퇴로를 끊을 셈이군\n퇴각로를 지킬 부대가 필요하오",
    "9:3244:0": "적의 목표는 퇴각로인 듯하군요\n방어에도 병력을 돌려야겠습니다",
    "9:3245:0": "적이 퇴각로로 향하고 있습니다!\n병력을 나누어 대비해야 할 듯합니다",
    "9:3246:0": "퇴각로를 노리다니 적도 제법이군요\n미리 대책을 세워야겠습니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    f"9:{record_id}:{literal_id}"
    for record_id in range(3233, 3241)
    for literal_id in range(2)
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
                "segment": "base_msggame_B001_S705",
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
