#!/usr/bin/env python3
"""Build Base authoring segment 563 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S563.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s563", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:328:0": "제 지략과 모두의 무용으로\n승리를 거머쥐는 것입니다!",
    "9:329:0": "이번 싸움은 힘을 합쳐\n헤쳐 나갑시다",
    "9:330:0": "자, 단숨에 몰아붙여\n짓뭉개 버려라!",
    "9:331:0": "쳐라!\n적군은 두려워할 것 없다!",
    "9:332:0": "이런 싸움에서야말로\n무문의 이름을 떨치리라!",
    "9:333:0": "승패는 싸우기 전에\n이미 정해지는 법이니라!",
    "9:334:0": "싸움의 기운은 길조로다…\n나아가 승리를 거머쥐어라!",
    "9:335:0": "겁내지 말고 나아가라!\n내게 필승의 계책이 있노라!",
    "9:336:0": "대의는 우리에게 있다!\n두려워 말고 나아가라!",
    "9:337:0": "진군하라… 목숨을 아끼지 말고\n명예를 아껴라!",
    "9:338:0": "우리 가문의 흥망은\n이번 싸움에 달렸도다!",
    "9:339:0": "풀을 베듯\n적들을 모조리 베어 넘겨라!",
    "9:340:0": "가거라! 오랜 세월 갈고닦은\n무예를 보일 때로다!",
    "9:341:0": "목숨을 걸어야\n비로소 살길도 열리는 법… 가거라!",
    "9:342:0": "적은 오합지졸일 뿐입니다\n모조리 쳐부수고 오세요!",
    "9:343:0": "적과 조우합니다\n전군, 교전에 대비하세요!",
    "9:344:0": "이리된 이상\n싸울 수밖에 없겠군요",
    "9:345:0": "앞을 가로막는 자에게\n자비는 필요 없다… 베어라!",
    "9:346:0": "바라는 것은 총대장의 목!\n나머지는 내버려 두어라!",
    "9:347:0": "싸움이다! 병사들아!\n짐승이 되어 적을 찢어발겨라!",
    "9:348:0": "이제부터 적과 맞섭니다\n모두 분발하세요!",
    "9:349:0": "이 싸움에서 이기는 것만\n생각하세요",
    "9:350:0": "자비를 버리세요\n그러지 않으면 죽습니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S563", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
