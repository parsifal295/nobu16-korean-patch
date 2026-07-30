#!/usr/bin/env python3
"""Build Base authoring segment 404 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S404.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s404", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1626:0": "의 성—",
    "7:1626:1": "\n반드시 차지해 두고 싶사옵니다\n우호보다 실리를 취해야 할 듯하옵니다",
    "7:1627:0": "노린다면—",
    "7:1627:2": "와(과)의 우호는\n이제 시세에 맞지 않을 듯하옵니다",
    "7:1628:0": "의 성—",
    "7:1628:1": "\n관계를 끊더라도\n우리 것으로 삼아야 할 것입니다",
    "7:1629:0": "은(는) 수비가 취약해 보이는군\n",
    "7:1629:1": "와(과)의 관계를\n바꾸어도 되지 않겠는가",
    "7:1630:0": "와(과)도 여기까지다!\n",
    "7:1630:1": "을(를)\n빼앗아 버리자고",
    "7:1631:0": "은(는) 노리기 알맞을 듯하옵니다\n",
    "7:1631:1": "와(과)의 우호 관계를\n재고해도 좋을 것입니다",
    "7:1632:0": "와(과)의 우호는\n이제 불필요하지 않사옵니까\n",
    "7:1632:1": "을(를) 빼앗아야 하옵니다",
    "7:1633:0": "은(는) 함락할 수 있을 듯하나\n",
    "7:1633:1": "와(과)는 우호 관계이니\n어찌해야 할까……?",
    "7:1634:0": "을(를) 빼앗는 수밖에 없사옵니다\n",
    "7:1634:1": "와(과)의 인연을\n끊어 주시옵소서",
    "7:1635:0": "의 방비는 허술하옵니다\n공격하려면 지금이오나\n",
    "7:1635:1": "와(과)의 관계를 재고하시옵소서",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S404", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
