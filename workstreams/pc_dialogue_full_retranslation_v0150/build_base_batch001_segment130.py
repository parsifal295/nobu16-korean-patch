#!/usr/bin/env python3
"""Build Base authoring segment 130 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S130.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s130", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2420:0": "끝이 나지 않는군…\n오늘은 돌아가 주시오",
    "6:2421:0": "오늘은 이만 하지요\n머리가 아파 오는군요",
    "6:2422:0": "…말도 안 되는군\n썩 꺼져라!",
    "6:2423:0": "…이제 됐다\n우리 가문을 화나게 하러 왔다면 성공했군",
    "6:2424:0": "후… 진심으로 실망했다\n교섭은 여기까지로 하지",
    "6:2425:0": "이토록 타협점을 찾지 못하다니…\n앞으로의 관계도 다시 생각해야 하나…",
    "6:2426:0": "오늘은 돌아가 주시오\n다음에는 결실 있는 이야기를 합시다",
    "6:2427:0": "이야기해도 소용없는 듯하군\n돌아가 주시오",
    "6:2428:0": "이야기가 성사될 것 같지 않습니다\n오늘은 이만 마치지요",
    "6:2429:0": "오늘은 돌아가 주시오\n조금 쉬어야겠소",
    "6:2430:0": "안 돼, 안 돼! 온 보람이 없잖아!\n잘 있어라! 돌아가 홧김에 잠이나 자야지!",
    "6:2431:0": "이건 아무래도…! 물러나자\n어리석은 짓으로 우리 가문의 긍지를 상하게 했군…",
    "6:2432:0": "교섭 결렬이군…",
    "6:2432:1": "님을 믿고 찾아왔건만\n그 믿음에 보답하지 않으셨군",
    "6:2433:0": "그런 대가는 준비할 수 없습니다\n설마 했던 교섭 결렬이라니… 실망스럽군요…",
    "6:2434:0": "이… 이런 대가는 들을 생각이 없다는 것과 같소!\n…실례했소. 흥분했군. 이만 가겠소",
    "6:2435:0": "훌륭한 대가로군요. 교섭 결렬입니다… 뭐\n궁한 처지를 파고든 처사는 아니시겠지요",
    "6:2436:0": "응할 수 없군요… 교섭 결렬입니다\n참으로 어려울 때의 벗은 얻기 힘든 법",
    "6:2437:0": "그건 받아들일 수 없네. 교섭은 결렬일세…\n잘 가게… 당분간 얼굴을 보고 싶지 않군",
    "6:2438:0": "도저히 받아들일 수 없는 일입니다\n…실례하겠습니다",
    "6:2439:0": "시간을 낭비한 듯하군\n…실례하오!",
}

DYNAMIC_COORDINATES = {"6:2432:0", "6:2432:1"}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        dynamic = coordinate in DYNAMIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S130",
                "decision_count": len(rows),
                "retranslated": len(rows) - len(DYNAMIC_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_COORDINATES),
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
