#!/usr/bin/env python3
"""Build Base authoring segment 29 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S29.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s29", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "4:50:0": "의 시설 건설 칸이 확장되었습니다",
    "6:277:0": "설정한 명령을 취소합니다\n계속하시겠습니까?",
    "6:278:0": "적이 노리고 있습니다",
    "6:279:0": "슬슬 질리는군…",
    "6:280:0": "가끔은\n느긋하게 쉬자고",
    "6:281:0": "어려운 논의로군…",
    "6:282:0": "이렇게 앉아 있는 것도\n썩 나쁘지 않군",
    "6:283:0": "안건이 무엇이려나",
    "6:284:0": "어려운 일일수록 시간을 들여\n도전해야 한다",
    "6:285:0": "나와 상관없는\n이야기뿐이군",
    "6:286:0": "충분히 검토하심이\n좋을 듯하옵니다",
    "6:287:0": "지루한 이야기뿐이로군",
    "6:288:0": "생각할 시간이 필요하군",
    "6:289:0": "어서 끝나지 않으려나",
    "6:290:0": "시간을 들여\n궁리해 보자",
    "6:291:0": "시간을 그리\n낭비할 수는 없다만",
    "6:292:0": "생각이 곧 정리될 듯하다",
    "6:293:0": "복잡한 이야기는\n영 질색이구나",
    "6:294:0": "서두를 필요도\n없겠지",
    "6:295:0": "글쎄, 무슨 말씀을\n나누고 계신 걸까요",
    "6:296:0": "쉬어 가며 합시다",
    "6:297:0": "사냥을 나가고 싶군…",
    "6:298:0": "차분히 계획을\n다듬을 수 있겠군",
    "6:299:0": "이야기가 계속되는군요…",
    "6:300:0": "다시 살필 시간도\n필요하겠네요",
    "6:301:0": "슬슬 숨 좀\n돌리고 싶구나…",
    "6:302:0": "때로는 오래 숙고할 필요도 있습니다",
    "6:303:0": "소집인가? 기다렸다고!",
    "6:304:0": "모두를 만날 생각에\n기대되는군",
    "6:305:0": "평정이라니…\n무슨 일일까",
    "6:306:0": "주군께서 건재하시니\n이보다 더한 경사는 없구나",
}

DYNAMIC_RUNTIME_COORDINATES = {"4:50:0"}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
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
                "segment": "base_msggame_B001_S29",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
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
