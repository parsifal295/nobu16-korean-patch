#!/usr/bin/env python3
"""Build Base authoring segment 392 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S392.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s392", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1419:0": "\n피아의 전력이 팽팽한 지금\n병력을 집중 운용하면 빼앗을 수 있을 듯하옵니다",
    "7:1420:0": "지금 우리와 전력이 대등한 상대—",
    "7:1420:1": "\n「사람은 성」이라 하듯\n총력을 쏟아 함락해야 합니다",
    "7:1421:0": "의 함락은 가능합니다\n피아의 전력이 호각이니\n병력을 집결시키면 공략도 수월합니다",
    "7:1422:0": "은(는) 빼앗을 수 있을 듯하옵니다\n적의 병력이 아군과 대등하니\n병력을 집중하면 우위에서 싸울 수 있습니다",
    "7:1423:0": "은(는)…… 지금 빼앗을 수 있사옵니다\n피아의 전력이 대등하니\n병력을 집중 운용하면 되는 것입니다",
    "7:1424:0": "지금 「",
    "7:1424:1": "」의 병력은 아군과 백중지세\n그렇다면 주변에서 병력을 모아\n수로 밀어붙이면…… 이길 수 있겠군요",
    "7:1425:0": "은(는) 빼앗을 수 있사옵니다\n피아의 병력이 호각인 것만으로도 승기는 충분\n총력으로 공격하면 더욱 확실할 것입니다",
    "7:1426:0": "을(를) 공략해야 하오!\n병력은 호각…… 그러니 주변 병력을\n집결시키면 우위에서 싸울 수 있사옵니다",
    "7:1427:0": "을(를) 공략할 때는 지금……\n병력은 호각이지만\n총력을 결집하면 함락할 수 있을 듯하옵니다",
    "7:1428:0": "을(를) 해방하는 방안을 검토해 주시옵소서\n전력은 현재 백중지세…… 그렇다면 병력을\n집중해 이 균형을 깨뜨리는 것이옵니다",
    "7:1429:0": "을(를) 함락하자꾸나\n병력이 반반이라면 이길 자신이 있다\n주변에서 병력을 모으면 확실하지",
    "7:1430:0": "이라면 함락할 수 있다\n병력이 호각이라 여기는 적에게\n전 병력으로 들이받는 거다!",
    "7:1431:0": "의 병력은\n아군과 대등합니다\n주변의 병력을 모아 공격합시다",
    "7:1432:0": "은(는) 함락할 수 있습니다\n현재 호각인 적에게\n전 병력을 모아 맞서는 것입니다",
    "7:1433:0": "을(를) 공략할 것을 건의드리옵니다\n지금 아군과 호각인 적의 병력에\n주변 병력을 집결해 맞서심이 어떠하올지",
    "7:1434:0": "대등한 적이 지키는 곳—",
    "7:1434:1": "\n공략의 관건은 병력의 집중 운용일 듯하옵니다\n총력으로 우위를 점해 싸움을 이끄시옵소서",
    "7:1435:0": "은(는) 지금 우리와 호각\n따라서 공격할 승산은 반반\n병력을 집결시키면 그 이상입니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S392", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
