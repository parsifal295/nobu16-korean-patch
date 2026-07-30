#!/usr/bin/env python3
"""Build Base authoring segment 369 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S369.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s369", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:994:0": "에게 패하다니\n",
    "7:994:1": "와(과)의 관계도\n여기까지인가……?",
    "7:995:0": "위풍으로 주변 국인중의 우리 가문에 대한 종속도 상승",
    "7:996:0": "에게 이겼단 말이지!\n역시 「",
    "7:996:1": "」을(를)\n따라갈 수밖에 없겠군!",
    "7:997:0": "을(를) 꺾었는가\n",
    "7:997:1": "……\n그 산하에 들어도 부끄럽지 않을 무위로다",
    "7:998:0": "에게 승리를 거두었다고\n",
    "7:998:1": "을(를) 의지한 것은\n역시 옳은 판단이었군",
    "7:999:0": "에게 이기다니……\n역시 「",
    "7:999:1": "」에게 의지하는 것이야말로\n우리가 살아남을 길이겠지요",
    "7:1000:0": "에게 이겼는가\n",
    "7:1000:1": "의 무위라면\n의지할 만하군",
    "7:1001:0": "에게 승리하다니\n",
    "7:1001:1": "의 기세라면\n우선은 믿을 만하겠군",
    "7:1002:0": "을(를) 굴복시키다니\n",
    "7:1002:1": "의 앞날은 창창하군……\n더욱 긴밀히 관계를 맺어야겠구려",
    "7:1003:0": "에게 이겼다고\n갑자기 빌붙으려는 건 아니다\n늘 의지할 곳은 「",
    "7:1003:1": "」이라 생각해 왔을 뿐이다",
    "7:1004:0": "에게 이겨 버리다니!\n역시 「",
}

STATIC_COORDINATES: set[str] = {"7:995:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S369", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
