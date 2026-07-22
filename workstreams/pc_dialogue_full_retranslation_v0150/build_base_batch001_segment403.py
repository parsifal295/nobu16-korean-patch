#!/usr/bin/env python3
"""Build Base authoring segment 403 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S403.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s403", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1616:0": "와(과)의 우호……\n",
    "7:1616:1": "이(가) 가져다줄 이익……\n으음……",
    "7:1617:0": "은(는) 차지하고 싶은데……\n",
    "7:1617:1": "와(과)의 관계를\n재고할 때인가",
    "7:1618:0": "와(과)는 여기까지다\n",
    "7:1618:1": "을(를) 차지할 가치는\n충분히 있다",
    "7:1619:0": "은(는) 노리기 알맞구나\n",
    "7:1619:1": "와(과)의 우호도 있사오나\n단교도 검토해 주시길 바라옵니다",
    "7:1620:0": "의 성—",
    "7:1620:1": "\n관계를 끊더라도\n우리 것으로 삼고 싶구려",
    "7:1621:0": "은(는) 수비가 허술하옵니다\n",
    "7:1621:1": "와(과)의 우호는\n끊어야 할 듯하옵니다",
    "7:1622:0": "은(는) 이제—",
    "7:1622:1": "에게\n더는 필요 없는 것이니\n우리 소유로 삼아야 한다",
    "7:1623:0": "은(는) 포기하기 아까운 곳\n",
    "7:1623:1": "와(과)의 우호 중 어느 쪽을 택할지\n저울질해 보시는 것이 어떠하옵니까?",
    "7:1624:0": "의 성—",
    "7:1624:1": "\n손에 넣는다면\n우리 가문도 평안할 터인데……",
    "7:1625:0": "은(는) 노릴 만한 곳\n",
    "7:1625:1": "와(과)의 우호가 필요한지\n다시 생각해 봐야 할 듯하옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S403", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
