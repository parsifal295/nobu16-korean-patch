#!/usr/bin/env python3
"""Build Base authoring segment 525 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S525.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s525", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:639:0": "이만한 지행이 있다면\n무훈도 세울 수 있으리라 기뻐했거늘…",
    "8:640:0": "으으음, 분하지만 어쩔 수 없겠구나",
    "8:641:0": "내 위엄에도\n흠집이 나고 말겠구나…",
    "8:642:0": "다른 이를 적임이라 여기신다면\n어쩔 수 없는 일이지…!",
    "8:643:0": "은(는) 제대로 다스리고 있었을 터인데…\n어찌하여…",
    "8:644:0": "본의는 아니지만…\n",
    "8:644:1": "의 능력이 부족했던 탓이겠지…",
    "8:645:0": "호오…\n어쩐지 돌아가는 형세가 달라진 듯한데…?",
    "8:646:0": "지금은 견뎌야 하겠지\n언젠가 주군께 인정받고 말겠다",
    "8:647:0": "재능을 마음껏 펼치기에는\n이제 지행이 부족해졌구나…",
    "8:648:0": "으음… 이보다 더 줄어들면…\n하지만 지금 형편에는 어쩔 수 없겠군…",
    "8:649:0": "군신의 화목이란\n좀처럼 이어지지 않는 모양이옵니다",
    "8:650:0": "오오, 「",
    "8:650:1": "」의 지행이 줄어드는구나…",
    "8:651:0": "이제는 쓸모가 없다고 여기신 것인가…",
    "8:652:0": "때로는 이런 일도 있는 법이지요…",
    "8:653:0": "이래서는… 제대로 활약하지도\n못하게 되고 말겠군…",
    "8:654:0": "나, 나한테 불만이라도 있는 거냐!?",
    "8:655:0": "그 지행지로 만족하고 있었거늘…",
    "8:656:0": "더 잘 다스려 주실 분이\n계시다면야…",
    "8:657:0": "또다시… 지행이 부족한 형편이\n되고 말았습니다…",
}

STATIC_COORDINATES = {
    f"8:{record_id}:0"
    for start, end in ((639, 642), (645, 649), (651, 657))
    for record_id in range(start, end + 1)
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S525", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
