#!/usr/bin/env python3
"""Build Base authoring segment 704 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S704.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s704", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3217:0": "님, 내가 가세하겠소!\n적에게 당하게 둘 수야 없지!",
    "9:3218:0": "의 원호에 나서라\n결코 적이 접근하게 두지 마라!",
    "9:3219:0": "의 철수를 지원한다\n우군을 끝까지 지켜 내라!",
    "9:3220:0": "의 원호를 맡겠습니다\n적이 접근하게 두어서는 안 됩니다",
    "9:3221:0": "님!\n결코 저버리지 않겠소!",
    "9:3222:0": "님의 호위를 맡자\n적의 표적이 되시면 버티기 어려우실 터",
    "9:3223:0": "의 곁을 지키겠다\n후퇴할 때까지 지원한다",
    "9:3224:0": "님의 철수는\n",
    "9:3224:1": "에게 원호를 맡기시오!",
    "9:3225:0": "의 원호를 맡겠습니다\n끝까지 지켜 내겠습니다!",
    "9:3226:0": "에게는 원호가 필요하다\n",
    "9:3226:1": ", 호위를 맡겠나이다",
    "9:3227:0": "의 지원에 나서겠습니다\n적은 제게 맡겨 주십시오",
    "9:3228:0": "의 철수를 원호한다\n결코 쓰러지게 두지 마라!",
    "9:3229:0": "이토록 쉽게 당하다니…!\n",
    "9:3229:1": "… 괴물인가!?",
    "9:3230:0": "철수할 틈조차 주지 않다니…\n",
    "9:3230:1": "의 힘은 진짜인 듯하군",
    "9:3231:0": "이 무슨 뼈아픈 타격인가…\n",
    "9:3231:1": "에게 당하고 말았구나…",
    "9:3232:0": "우리 부대가 이토록 허무하게 무너지다니…\n",
    "9:3232:1": ", 만만치 않은 상대군요",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:3217:0",
    "9:3218:0",
    "9:3219:0",
    "9:3220:0",
    "9:3221:0",
    "9:3222:0",
    "9:3223:0",
    "9:3224:0",
    "9:3224:1",
    "9:3225:0",
    "9:3226:0",
    "9:3226:1",
    "9:3227:0",
    "9:3228:0",
    "9:3229:0",
    "9:3229:1",
    "9:3230:0",
    "9:3230:1",
    "9:3231:0",
    "9:3231:1",
    "9:3232:0",
    "9:3232:1",
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
                "segment": "base_msggame_B001_S704",
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
