#!/usr/bin/env python3
"""Build Base authoring segment 411 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S411.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s411", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1688:0": "고작—",
    "7:1688:2": "을(를)\n함락시켜 보이겠습니다",
    "7:1689:0": "은(는) 약해져 있습니다\n지침을 철회해 주십시오\n",
    "7:1689:1": "은(는) 차지하는 것입니다",
    "7:1690:0": "두려워할 필요는 없습니다\n",
    "7:1690:1": "의 성—",
    "7:1690:2": "을(를)\n공격해 빼앗읍시다",
    "7:1691:0": "은(는) 두려워할 것 없소\n지침을 철회해 주시오\n",
    "7:1691:1": "을(를) 차지합시다",
    "7:1692:0": "은(는) 대단한 적이\n아닙니다\n",
    "7:1692:1": "을(를) 공격할 적기는 지금입니다",
    "7:1693:0": "공성은 하루아침에 끝나지 않는 법\n병량을 더 사 두는 편이\n좋겠구나",
    "7:1694:0": "병량 부족은 불 보듯 뻔하다\n이대로 싸움에 나선다면\n군세를 유지할 수 없을 터",
    "7:1695:0": "병량이 부족하군요\n우선 병량부터\n구입하는 것이 어떻겠습니까",
    "7:1696:0": "배가 고프면 싸울 수 없는 법\n병량이 부족해서는 싸울 수 없사옵니다",
    "7:1697:0": "비축한 병량이 염려되옵니다\n싸움을 시작하기 전에\n부디 구입을 검토해 주시옵소서",
    "7:1698:0": "서두르시는 마음은 이해하오나\n병량 없이는 애초에\n싸움이 되지 않사옵니다",
    "7:1699:0": "공성에는 시간이 걸리는 법\n병량을 확보할 필요가\n있겠사옵니다",
    "7:1700:0": "병량이 염려되옵니다만\n온갖 수를 다 쓴다면 어쩌면……",
    "7:1701:0": "성을 공격하기에는 병량이 부족하오\n병량을 조달하는 것이 어떻겠소?",
}

STATIC_COORDINATES: set[str] = {
    "7:1693:0", "7:1694:0", "7:1695:0", "7:1696:0", "7:1697:0",
    "7:1698:0", "7:1699:0", "7:1700:0", "7:1701:0",
}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S411", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
