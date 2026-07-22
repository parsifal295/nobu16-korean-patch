#!/usr/bin/env python3
"""Build Base authoring segment 399 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S399.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s399", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1553:0": "을(를) 공격하시려거든\n아군에 맞먹는 적과 싸우기보다\n먼저 주변부터 함락하는 것이 긴요하옵니다",
    "7:1554:0": "의 적은 얕볼 수 없사옵니다\n그러나 주변의 군부터 제압해\n적의 발판을 무너뜨리면 승산이 있사옵니다",
    "7:1555:0": "이라면 함락할 수 있습니다\n주변의 군부터 공격해\n성을 약체화시키면 되는 것입니다",
    "7:1556:0": "은(는) 공략할 수 있을 듯하옵니다\n우리와 맞먹는 수비군을 상대하기보다\n주변의 군부터 장악하는 것입니다",
    "7:1557:0": "을(를) 지키는 자는\n아군에 맞먹는 강적…… 우선은\n지리적 이점을 선점할 방도를 생각하시옵소서",
    "7:1558:0": "의 공략은 가능하옵니다\n주변의 군을 제압해 고립시킨다면\n그 성은 이미 손안에 든 것이나 다름없사옵니다",
    "7:1559:0": "의 적은 얕볼 수 없사옵니다\n……하나 주군께서 바라시면 공략할 수 있사오니\n주변을 제압해 약체화시키면 되옵니다",
    "7:1560:0": "을(를) 공격해야 할 듯하옵니다\n먼저 주변의 군부터 제압해\n지리적 이점을 얻는다면 이길 수 있사옵니다",
    "7:1561:0": "은(는) 함락할 수 있을 것이오\n우리와 백중세인 적과 맞서기보다\n주변을 공격해 약체화를 노리는 것이오",
    "7:1562:0": "의 공략에 관해서입니다만\n성하의 군을 제압해 성을 고립시키고\n약화시킨 뒤 함락하는 것이 좋을 듯하옵니다",
    "7:1563:0": "을(를) 공격하시려거든\n주변의 군부터 함락하시는 것이 좋사옵니다\n「급할수록 돌아가라」는 말도 있사옵니다",
    "7:1564:0": "은(는) 함락할 수 있으리라\n우리와 맞먹는 적이 지키고 있으나\n지리적 이점을 차지하면 이길 수 있을 것이오",
    "7:1565:0": "을(를) 공격해야 할 듯하옵니다\n정면으로 치면 승산은 반반이오나\n주변을 함락하면 우위에서 싸울 수 있습니다",
    "7:1566:0": "은(는) 공략할 수 있습니다\n성하의 군부터 제압한 뒤\n성을 약체화시키도록 합시다",
    "7:1567:0": "을(를) 공격하시려거든\n계책이 있사옵니다…… 먼저 군을 제압해\n성의 고립을 노리시옵소서",
    "7:1568:0": "을(를) 공격해야 하옵니다\n우리와 대등한 적이 지키고 있으나\n지리적 이점을 차지하면 이길 수 있사옵니다!",
    "7:1569:0": "을(를) 손에 넣으시려거든\n주변의 군부터 공략하시옵소서\n성을 약체화하면 적은 피해로 이길 수 있사옵니다",
    "7:1570:0": "을(를) 공격하시려거든\n우리와 맞먹는 적을 상대하기보다\n인근의 군부터 노리는 것이 상책이옵니다",
    "7:1571:0": "은(는) 우리와 대등한\n병력이 지키는 난공의 요충지…… 그러나\n지리적 이점을 차지하면 승기가 있을 듯하옵니다",
    "7:1572:0": "을(를) 공격해야 하오\n성하의 군을 함락해 기반을 무너뜨리면\n기필코 성을 함락할 수 있을 것이오",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S399", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
