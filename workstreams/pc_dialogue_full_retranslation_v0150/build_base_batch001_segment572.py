#!/usr/bin/env python3
"""Build Base authoring segment 572 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S572.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s572", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:477:0": ", 무슨 낯짝으로\n기어들어 온 거냐!",
    "9:478:0": "!\n반드시 처단해 주마!",
    "9:479:0": "을(를) 놓치면\n대대로 수치가 되리라",
    "9:480:0": "만큼은\n절대 놓치지 않겠습니다",
    "9:481:0": "!\n쓰러뜨릴 자는―",
    "9:481:1": "이다!",
    "9:482:0": "을(를) 쓰러뜨릴 호기\n……라는 것인가",
    "9:483:0": "……귀에 거슬리는 이름이\n적진에 있는 듯하군요",
    "9:484:0": "오늘을 네 기일로\n만들어 주마!",
    "9:485:0": "만큼은\n반드시 쓰러뜨리겠습니다!",
    "9:486:0": "잘 만났다, 이제 네 운도 끝이다\n",
    "9:486:1": ", 각오하라!",
    "9:487:0": "은(는) 여기서\n쓰러뜨려야 합니다",
    "9:488:0": ", 놓치지 않겠다\n절대로 놓치지 않으마!",
    "9:489:0": "나타났구나\n혼쭐을 내 주마!",
    "9:490:0": "!\n상대로 부족함이 없구나",
    "9:491:1": "와(과) 승부하라",
    "9:492:0": "서두르지 말고 차분히\n대처합시다",
    "9:493:0": "내 앞에 나타나다니\n운도 없는 자로군",
    "9:494:0": "빈틈을 노려……찔러라",
    "9:495:0": "일거에 쓸어버리리라!",
    "9:496:0": "자, 정정당당히 승부다!",
}

STATIC_COORDINATES: set[str] = {
    "9:483:0",
    "9:484:0",
    "9:489:0",
    "9:492:0",
    "9:493:0",
    "9:494:0",
    "9:495:0",
    "9:496:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S572", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
