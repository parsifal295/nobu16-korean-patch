#!/usr/bin/env python3
"""Build Base authoring segment 207 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S207.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s207", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3516:1": "\n우리 같은 자들이 중추가 되어 힘쓰지 않으면\n우리 가문의 번영은",
    "6:3516:2": "것이니",
    "6:3517:0": "에 이름을 올린다는 것은\n일거수일투족마다 우리 가문을 짊어진다는 것\n품격 없는 행동은 할 수 없",
    "6:3517:1": "까닭에",
    "6:3518:0": "이(가) 훈공 1위라니, 감사하",
    "6:3518:1": "\n낭중지추라 하듯, 낮은 자리에 있으면서도\n",
    "6:3518:2": "의 눈에 든 것이야말로 뜻밖의 기쁨",
    "6:3519:0": "훈공 1위라니!\n이를 힘으로 삼아\n다음에도 힘껏 분발하",
    "6:3519:1": "!",
    "6:3520:0": ", 아직 더 일할 수 있",
    "6:3520:1": "!\n더 많은 일을 맡겨 주십시오!",
    "6:3521:0": "가장 큰 성과를 거두",
    "6:3521:1": "구나\n",
    "6:3521:2": ", 목표는 아직도 더 높은 곳\n더욱 힘쓰",
    "6:3521:3": "겠소",
    "6:3522:0": "이제야 한 사람 몫을 한다고 말할 수 있",
    "6:3522:1": "는가\n꽃이 피었으니, 다음에는 열매를 맺",
    "6:3523:0": "과분한 영광",
    "6:3523:1": "군요\n이에 만족하지 않고,\n더욱 높은 곳을 향하",
    "6:3524:0": "이렇게,",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S207", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
