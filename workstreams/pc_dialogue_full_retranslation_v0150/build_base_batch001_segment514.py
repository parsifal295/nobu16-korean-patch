#!/usr/bin/env python3
"""Build Base authoring segment 514 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S514.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s514", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:435:0": "공주·",
    "8:435:1": "이(가) 사망",
    "8:436:0": "당주·",
    "8:436:1": "이(가) 사망",
    "8:437:0": "의 당주·",
    "8:437:1": "이(가) 사망",
    "8:438:0": "군단장·",
    "8:438:1": "이(가) 사망",
    "8:439:0": "가신·",
    "8:439:1": "이(가) 사망",
    "8:440:0": "성주·",
    "8:440:1": "이(가) 사망",
    "8:441:0": "이제부터 불문에 들겠사옵니다\n우리 가문의 번영을 기원하옵니다…",
    "8:442:0": "이제부터 속세를 떠나 부처님을 섬기며\n세상의 앞날을 지켜보고자 하옵니다",
    "8:443:0": "저는 머리를 깎고 출가하여 속세를 떠나고자 하옵니다\n부디 말리지 마시옵소서",
    "8:444:0": "이제부터 칼과 창을 버리고 불문에 들어\n전장에서 스러진 이들의 명복을 빌고자 하옵니다",
    "8:445:0": "이제부터 불문에 귀의하여\n속세를 떠나 살아가고자 하옵니다",
    "8:446:0": "저는 이만 출가하겠사옵니다\n우리 가문을 비구니 사찰에서 지켜보고자 하옵니다",
    "8:447:0": "이것이 제 마지막입니까…\n후회는 없사옵니다…",
    "8:448:0": "이제 더는 도움이 되지 못할 듯하옵니다\n참으로 송구하옵니다…",
    "8:449:0": "내 수명도 여기까지인 듯하군요…\n하지만… 아직도… 못다 한 일이…",
    "8:450:0": "내 목숨, 여기서 스러지는가\n나쁘지 않은 생애였소이다… 이만 작별이오",
    "8:451:0": "아직 한참 더 힘이 되고 싶었사오나\n제 목숨은 여기까지인 듯하옵니다…",
    "8:452:0": "저는 여기까지입니다… 혹여 「",
    "8:452:1": "」께서\n조금이나마 저를 아쉬워해 주신다면 기쁘겠사옵니다",
}

STATIC_COORDINATES = {f"8:{record_id}:0" for record_id in range(441, 452)}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S514", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
