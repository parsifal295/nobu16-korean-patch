#!/usr/bin/env python3
"""Build Base authoring segment 533 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S533.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s533", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:801:0": "난초에는 꽃이 있고 국화에는 향기가 있으니\n가을꽃도 좋은 법이로다",
    "8:802:0": "가을에는 맛있는 것이 많구나\n살아 있어 다행이로다",
    "8:803:0": "지내기 좋은 계절이\n되었군요!",
    "8:804:0": "단풍의 계절이구나\n넋을 잃고 바라보게 되는군…",
    "8:805:0": "어째서인지 묘하게\n마음이 쓸쓸해지는 계절…",
    "8:806:0": "춥구나…\n뼛속까지 얼어붙을 듯하구나",
    "8:807:0": "죽이라도 한 사발 퍼먹고\n몸을 덥히자고!",
    "8:808:0": "겨울의 차디찬 공기에\n몸가짐이 절로 다잡히는군",
    "8:809:0": "겨울은 뼛속까지 시리는구나…\n온천 요양을 떠나고 싶구나",
    "8:810:0": "서리가 내렸군요…\n밭은 괜찮을까요",
    "8:811:0": "겨울에는 눈이 있고\n좋은 계절이 되었구나",
    "8:812:0": "겨울은 고요하지\n…싫지는 않다",
    "8:813:0": "추위가 닥쳐야 늦게 시드는 송백의\n절개를 알게 된다는 말이군…",
    "8:814:0": "쌀쌀하구나…\n옛 상처가 쑤시는군",
    "8:815:0": "손이 곱아\n새빨갛게 되었습니다…",
    "8:816:0": "얼어붙을 듯한 공기가\n또 참을 수 없이 좋구나!",
    "8:817:0": "겨울에는 외출을 포기하고\n방에 틀어박혀 있는 게 제일이지요",
    "8:818:0": "백성을 등한시한\n벌을 받은 것이로다…",
    "8:819:0": "망쳐 버렸군…\n주군을 뵐 낯이 없어",
    "8:820:0": "아아, 이럴 수가…!\n무가의 수치로다…",
    "8:821:0": "백성을 다스리지 못하다니\n이 무슨 불찰인가…!",
    "8:822:0": "주군께도 백성에게도\n낯을 들 수 없사옵니다…",
    "8:823:0": "으음… 이 몸의 미숙함이\n부끄러울 따름이로다",
    "8:824:0": "주군께서 맡기신 땅을…\n이 모두 이 몸의 식견이 모자란 탓인가…",
    "8:825:0": "이런 사태에 이른 것은\n제 부덕의 소치이옵니다",
}

STATIC_COORDINATES = set(TRANSLATIONS)


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S533", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
