#!/usr/bin/env python3
"""Build Base authoring segment 388 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S388.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s388", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1340:0": "따위의 허약한 성에\n우리의 온 힘을 쏟아부으면 어찌 될지\n볼만하겠구나",
    "7:1341:0": "은(는) 노려볼 만한 곳이오나\n방심하면 도리어 허를 찔려\n패배를 맛볼지도 모르옵니다",
    "7:1342:0": "을(를) 함락하려면\n비사문천의 깃발 아래\n전군을 모아 공격하는 것이 좋으리라",
    "7:1343:0": "을(를) 함락하기는 쉬우나\n만일에 대비하여\n전군으로 임해야 할 줄 아옵니다",
    "7:1344:0": "은(는) 노려볼 만한 곳\n병력을 아끼지 말고\n격류처럼 몰아붙이자",
    "7:1345:0": "은(는) 우리에게 유리하군요\n그러나 현명하신 주군이시니\n소수 병력으로 공성전을 벌이시진 않겠지요",
    "7:1346:0": "은(는) 우리가 우세하오나\n언제 뒤집힐지 모르는 법\n전군으로 공격해 단숨에 결판을 내십시다",
    "7:1347:0": "은(는) 우리가 유리하니\n완승을 기하고자\n아군 전군으로 맞서시는 것이 어떠실지요",
    "7:1348:0": "을(를) 함락하기는 쉬운 일\n더욱이 전군을 결집시킨다면\n이제 사방에 적수가 없을 것이오",
    "7:1349:0": "이라면 문제없어\n우리의 온 힘을\n주군께 보여 드리지!",
    "7:1350:0": "을(를) 함락하고 싶다면\n쩨쩨하게 굴지 말고\n모두 달려들면 되는 거야!",
    "7:1351:0": "이라면 걱정할 것 없사옵니다\n우리가 전력을 다해\n반드시 함락해 보이겠사옵니다!",
    "7:1352:0": "은(는) 손쉬운 표적\n하지만 주군의 기대에 부응하려면\n전군으로 나서야 하지 않겠습니까……?",
    "7:1353:0": "을(를) 함락하기는 쉬운 일\n그러므로 아군의 최대 전력으로\n필승을 기해야 할 줄 아옵니다",
    "7:1354:0": "을(를) 상대로는 우리가 우세하도다\n우리 전군으로 공격해 함락하고\n천하에 이름을 떨치자",
    "7:1355:0": "은(는) 손쉬운 표적이오나\n여기서는 조급한 마음을 누르고\n전군을 모아 필승을 기하십시다",
    "7:1356:0": "은(는) 손쉬운 표적\n하지만 만일의 사태를 상정하여\n전군을 집결시켜 맞서자",
    "7:1357:0": "은(는) 노려볼 만한 곳이군요\n우리의 전력을 여러 다이묘에게\n선보일 좋은 기회이기도 하옵니다",
    "7:1358:0": "은(는) 손쉬울 것이오\n전군으로 공격해 들어가\n우리의 용맹한 모습을 보여 주자",
    "7:1359:0": "은(는) 좋은 사냥감\n그렇기에 전군으로 공격하여\n주군께서 손에 넣으시옵소서",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S388", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
