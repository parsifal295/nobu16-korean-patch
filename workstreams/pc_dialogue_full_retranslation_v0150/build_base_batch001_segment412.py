#!/usr/bin/env python3
"""Build Base authoring segment 412 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S412.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s412", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1702:0": "병량이 빠듯한가……\n단기간에 승부가 나면 좋으련만",
    "7:1703:0": "싸움에는 병량이 필요한 법\n먼저 더 사 두는 편이\n좋겠구나",
    "7:1704:0": "병량을 확인해 보시오\n이 정도 양으로는 이길 싸움도\n이기지 못하게 될 것이오",
    "7:1705:0": "병량을 구입하는 것이 어떻겠소?\n장기전이 되면 위험하오",
    "7:1706:0": "으음, 병량이 부족한 듯하군\n이래서는 병사들이 제대로 싸울 수 없겠군",
    "7:1707:0": "병량을 확인했습니다만\n부족할 우려가 있습니다\n구입을 검토하심이 좋을 듯합니다",
    "7:1708:0": "이 병량으로는 마음이 놓이지 않습니다\n서둘러 성을 함락합시다",
    "7:1709:0": "성을 함락하려면 시간이 걸린다\n현재 병량으로 충분한가?",
    "7:1710:0": "이봐, 괜찮겠나……\n병량이 떨어지면\n싸울 수 없다고",
    "7:1711:0": "병량 없이는 싸울 수 없습니다\n장기전에 대비해\n병량을 사 두도록 합시다",
    "7:1712:0": "출진하시는 겁니까?\n하지만 병량이 염려되는데……\n더 사 두는 것이 어떻겠습니까",
    "7:1713:0": "병량이 빠듯하군\n이럴 때는 더 사 두어야 하겠군",
    "7:1714:0": "싸움이 길어지면 비용도 늘어납니다\n이 병량으로는 충분하다고는\n할 수 없겠지요",
    "7:1715:0": "병량은 싸움의 기본\n병량 없이는 싸울 수 없사옵니다\n우선 구입하시옵소서",
    "7:1716:0": "이래서는 어려울 듯하옵니다……\n병량을 조달한 뒤\n싸움에 임해야 할 것입니다",
    "7:1717:0": "공성에는 병량이 필요하다\n이래서는 싸울 수 없다",
    "7:1718:0": "명하신다면 전력을 다해 싸우겠으나\n아무래도 이 병량으로는\n전과를 올릴 수 있을지……",
    "7:1719:0": "공성에는 병량이 필수불가결\n여기서는 더 사 두어야 할 듯하옵니다",
    "7:1720:0": "우선 상인을 불러 주시옵소서\n지금 해야 할 일은\n병량을 구입하는 것입니다",
    "7:1721:0": "병량이 부족해 보이옵니다\n조달을 서두르시는 편이\n좋을 듯하옵니다",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S412", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
