#!/usr/bin/env python3
"""Build Base authoring segment 394 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S394.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s394", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1453:0": "은(는) 빼앗을 수 있으리라\n피아의 전력 차이는 거의 없으니\n성하의 군부터 제압해야 하겠지만 말이다",
    "7:1454:0": "을(를) 공격하려면\n성 주변의 군부터 빼앗아야 한다\n그리하여 성을 약체화시키는 것이야",
    "7:1455:0": "을(를) 공격하시려거든\n먼저 주변의 군부터 공략하시옵소서\n이것이 공성의 기본이옵니다",
    "7:1456:0": "을(를) 함락하지 않으시겠습니까\n수비가 제법 견고하오나\n성하의 군부터 제압하면 그만이옵니다!",
    "7:1457:0": "을(를) 공격해 보심이 어떠하올지\n수비 전력은 우리와 대등하오나\n주변의 군부터 함락한다면……",
    "7:1458:0": "의 공략은\n주변의 군부터 공략하시옵소서\n성을 고립시켜 무방비한 성으로 만드는 것입니다",
    "7:1459:0": "을(를) 함락하는 것은 어렵지 않소\n「장수를 쏘려거든 먼저 말을 쏘라」 하였듯\n주변의 군부터 공략하는 것이오",
    "7:1460:0": "을(를) 빼앗으려면\n주변의 군부터 차례로 공략합시다\n지리적 이점 없이는 이길 수 없사옵니다",
    "7:1461:0": "은(는) 빼앗을 수 있을 듯하옵니다\n먼저 주변의 군을 습격해\n약체화시키면 함락은 필연이옵니다",
    "7:1462:0": "을(를) 공격합시다\n「장수를 쏘려거든 먼저 말을 쏘라」는 말처럼\n주변의 군부터 하나씩 빼앗는 것입니다",
    "7:1463:0": "을(를) 공격하시려거든\n먼저 주변부터 제압하시옵소서\n지원을 잃으면 견고한 성도 무너지기 마련이오",
    "7:1464:0": "이라면 빼앗을 수 있을 것입니다\n주변부터 함락해 고립시키면\n성안의 결속도 무너져 절로 함락될 것이옵니다",
    "7:1465:0": "을(를) 공격해야 하옵니다\n수비병의 전력은 얕볼 수 없사오나\n주변부터 함락하면 공략할 수 있을 듯하옵니다",
    "7:1466:0": "을(를) 빼앗자꾸나\n까다로운 상대이니\n주변의 군을 쳐서 약체화하는 것이 어떻겠느냐",
    "7:1467:0": "을(를) 공격해야 하옵니다\n수비 전력은 얕볼 수 없사오나\n지리적 이점을 얻으면 이길 수 있사옵니다",
    "7:1468:0": "의 적은 얕볼 수 없사옵니다\n그러나 주변부터 점령해\n약체화시키면 공략할 수 있을 듯하옵니다",
    "7:1469:0": "을(를) 빼앗을 거라면\n주변의 군부터 습격하는 게 좋아\n성을 약체화시키는 거다",
    "7:1470:0": "의 수비는 성가시군\n주변부터 하나씩 무너뜨린 뒤\n성을 함락하는 수로 가자고",
    "7:1471:0": "을(를) 공략할 계책이 있사옵니다\n주변의 군을 제압해 고립시키면\n함락하는 것도 가능하옵니다",
    "7:1472:0": "을(를) 공격해야 하옵니다\n얕볼 수 없는 적이오나\n주변부터 함락하면 이길 수 있을 것이옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S394", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
