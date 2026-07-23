#!/usr/bin/env python3
"""Build Base authoring segment 612 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S612.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s612", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1337:0": "설마 다리를 끊는\n수를 쓰다니……",
    "9:1338:0": "다리를 끊다니\n대담하군……",
    "9:1339:0": "여기서 다리를\n끊는 겁니까……",
    "9:1340:0": "다리를 쓸 수 없다니……\n에잇!",
    "9:1341:0": "이래서는…… 지나갈 수 없다……",
    "9:1342:0": "다리가…… 불타 무너진다……!",
    "9:1343:0": "비겁한 수작을……!",
    "9:1344:0": "다리를 끊어 버리다니!",
    "9:1345:0": "쳇, 다리가!",
    "9:1346:0": "과감한 짓을 하는군……",
    "9:1347:0": "다리가……\n이럴 수가……",
    "9:1348:0": "놈들, 대체 얼마나\n간이 큰 거야!",
    "9:1349:0": "이 무슨 기세인가!",
    "9:1350:0": "분하지만\n훌륭한 비탈 돌격이로다",
    "9:1351:0": "절벽을 뛰어 내려오다니……\n적도 필사적이군요",
    "9:1352:0": "크윽!\n힘에서 밀리다니!",
    "9:1353:0": "말도 안 돼, 공포심마저\n타 버린 것인가!",
    "9:1354:0": "절벽에서 무리하게 밀어붙이다니……\n도리조차 물러설 수밖에 없군",
    "9:1355:0": "기세에\n밀려나다니!",
    "9:1356:0": "이 비탈을\n내려오다니!",
    "9:1357:0": "당했다……\n설마 내려올 줄이야",
    "9:1358:0": "급습!?\n무슨 배짱이람……",
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
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S612", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
