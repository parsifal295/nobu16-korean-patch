#!/usr/bin/env python3
"""Build Base authoring segment 272 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S272.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s272", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4180:2": "\n모두, 힘써 일하",
    "6:4181:0": "적성 조략의 방침을 각 성주에게 전했더니\n다음 성에서 구체안이 나왔",
    "6:4181:1": "\n어느 성주의 계책을 실행할지,",
    "6:4181:2": " 지시해 주",
    "6:4182:0": "영내 제책의 방침을 각 성주에게 전했더니\n다음 성에서 구체안이 나왔",
    "6:4182:1": "\n어느 성을 강화할지,",
    "6:4182:2": "지시해 주",
    "6:4183:0": "실행할 주명의 내용을 선택해 주십시오",
    "6:4184:0": "대상 성에 내린 명령을 취소합니다\n괜찮으시겠습니까?",
    "6:4185:0": "아군 성을 선택해\n원하는 내정을 지시할 수 있",
    "6:4186:0": "적성에 대한 조략을\n검토하도록 지시하",
    "6:4187:0": "강한 불만을 품은 무장에게\n우리 가문으로 돌아서도록 권유하",
    "6:4188:0": "유사시에 원군을 요청할 수 있도록\n국인중을 회유하",
    "6:4189:0": "국인중을 우리 가문의 산하에\n편입하도록 지시하",
    "6:4190:0": "적 영지의 백성을 선동해\n잇키를 일으켜 움직임을 봉쇄하",
    "6:4191:0": "적성에 파괴 공작을 명해\n성의 내구와 병력에 피해를 입히",
    "6:4192:0": "가보를 마련해\n외교 자세를 개선하",
    "6:4193:0": "적성에 불을 지르게 해\n병력과 병량에 피해를 입히",
    "6:4194:0": "적성 장수의 충성심을 흔들기 위해\n당주의 악소문을 퍼뜨리",
    "6:4195:0": "석고를 늘리기 위해\n농촌을 장악하",
}

STATIC_COORDINATES: set[str] = {"6:4183:0", "6:4184:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S272", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
