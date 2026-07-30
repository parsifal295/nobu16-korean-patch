#!/usr/bin/env python3
"""Build Base authoring segment 532 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S532.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s532", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
GOOD_SEASON = "좋은 계절이 되었구나"
TRANSLATIONS = {
    "8:778:0": "봄잠에 날이 샌 줄도 몰랐구나\n새근…",
    "8:779:0": "화창하고 포근한 봄날\n점점 졸려 옵니…",
    "8:780:0": "봄은 좋구나\n절로 몸을 움직이고 싶어진다",
    "8:781:0": "새싹이 움트는 봄\n들로 산으로 거닐어 보시는 건 어떠신지요?",
    "8:782:0": "논의 벼가 푸르게\n무럭무럭 자라고 있사옵니다",
    "8:783:0": "여름 하면 수박이지!\n달고 시원해서 좋잖아!",
    "8:784:0": "덥다고?\n수련이 부족하구나",
    "8:785:0": "마음속 잡념을 떨쳐 버리면\n여름 더위도 또한 서늘하지…",
    "8:786:0": "무더운 날에는\n방에서 책을 읽는 것이 제일입니다",
    "8:787:0": f"여름에는 서늘한 바람이 있고\n{GOOD_SEASON}",
    "8:788:0": "장마철엔 비가 내리고 늦여름엔\n날이 개야 풍년이라지만…",
    "8:789:0": "여름이면 농사일이 한창이니\n그야말로 농번기에는 한가한 이가 없구나",
    "8:790:0": "더위가 꽤나 힘겹구나\n물이라도 마실까",
    "8:791:0": "이렇게 더워서야\n의욕이 나지 않는군요…",
    "8:792:0": "따갑게 내리쬐는 햇살\n싫지는 않다",
    "8:793:0": "커다란 구름이군요…\n소나기가 한차례 오려나요",
    "8:794:0": "벗과 달을 보며 마시는 술은\n참으로 맛있겠지요",
    "8:795:0": "밤이 주렁주렁 열렸군!\n밤밥을 지어 먹을까!",
    "8:796:0": "상쾌하구나…\n바람 소리가 실로 가을이로다",
    "8:797:0": "가을 저물녘과 종소리…\n어딘가 쓸쓸한 정취가 있구나",
    "8:798:0": "가을바람 사이로\n사슴 울음소리가 들리네요",
    "8:799:0": f"가을에는 달이 있고\n{GOOD_SEASON}",
    "8:800:0": "드디어 결실의 계절이로구나\n우리 가문의 곳간도 넉넉해지겠지",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S532", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
