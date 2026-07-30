#!/usr/bin/env python3
"""Build Base authoring segment 405 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S405.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s405", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1636:0": "의 성—",
    "7:1636:1": "\n빼앗아 버리고 싶은\n곳이다만……",
    "7:1637:0": "은(는) 어떻겠습니까\n",
    "7:1637:1": "와(과)의 인연을 끊고\n쳐들어가는 것도 좋을 듯하옵니다",
    "7:1638:0": "단교도 어쩔 수 없으리라\n",
    "7:1638:1": "의 성—",
    "7:1638:2": "\n우리 가문의 것으로 삼아야 할 것입니다",
    "7:1639:0": "을(를) 빼앗기 위해\n",
    "7:1639:1": "와(과)의 관계를 끊는 것이\n어떻겠습니까",
    "7:1640:0": "다른 가문과 언제까지고 우호를 지킬 수는……\n",
    "7:1640:1": "의 성—",
    "7:1640:2": "\n빼앗고 싶다만……",
    "7:1641:0": "노릴 곳은—",
    "7:1641:2": "와(과)의 관계는\n여기서 청산해야 할 듯하옵니다",
    "7:1642:0": "의 성—",
    "7:1642:1": "을(를) 공격하려면\n지금이 적기일 것입니다\n이 또한 세상사의 이치라 여기시면 되옵니다",
    "7:1643:0": "은(는) 노려볼 만하옵니다\n",
    "7:1643:1": "와(과)의 우호를\n끝내시는 것이 어떻겠습니까?",
    "7:1644:0": "공격한다면—",
    "7:1644:2": "와(과)의 관계를\n끊을 기회일지도 모르옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S405", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
