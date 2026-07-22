#!/usr/bin/env python3
"""Build Base authoring segment 125 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S125.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s125", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2320:0": "더 얹지 않으면",
    "6:2320:1": "님의\n마음을 움직일 수 없겠지요…",
    "6:2321:0": "승낙을 받아 내기에는\n대가가 너무 초라한가…",
    "6:2322:0": "이걸로",
    "6:2322:1": "이(가) 승낙할지는\n부딪쳐 봐야 알겠군…",
    "6:2323:0": "이 정도면 무사의 면목도 서겠지\n…하지만 아직 확실하다고는 할 수 없다",
    "6:2324:0": "이걸로",
    "6:2324:1": "님이\n움직여 주면 좋으련만…",
    "6:2325:0": "교섭의 성패는\n",
    "6:2325:1": "님의 마음에 달렸군요…",
    "6:2326:0": "성공할 가망도 보이는군\n이대로 승부를 걸어 볼까…?",
    "6:2327:0": "이제 운을 하늘에 맡겨야 하나\n물론 더 많이 내놓을수록 가능성도 커지지만…",
    "6:2328:0": "상대의 기분에 달린 셈이군\n체면을 세워 줄수록 기분도 좋아지겠지만…",
    "6:2329:0": "아직은 운에 달렸어… 확실하게 하려면\n더 얹어야겠군…",
    "6:2330:0": "이걸로",
    "6:2330:1": "님이 승낙할지는\n운에 맡길 수밖에 없겠군요…",
    "6:2331:0": "이를 받아들일지는\n",
    "6:2331:1": "님의 기분에 달렸나…",
    "6:2332:0": "이걸로 승낙해 준다면\n더 바랄 것도 없습니다만…",
    "6:2333:0": "아직 부족하려나…\n아니, 운이 좋으면 받아 줄지도…",
    "6:2334:0": "이만큼 내놓으면\n그 녀석도 고개를 끄덕이겠지!",
    "6:2335:0": "이 정도면 상대도 받아들이겠지\n무사의 면목은 충분히 세웠을 터",
    "6:2336:0": "받아들이기에 충분한 대가로다\n",
    "6:2336:1": "님도 만면에 희색을 띠겠지",
    "6:2337:0": "대가는 충분하군요\n",
    "6:2337:1": "님도 납득하시겠지요",
    "6:2338:0": "…이만큼이나 건넸는데\n거절한다면 베어 버리겠다",
    "6:2339:0": "이 정도면 확실하다\n얻는 것보다 주는 것이 더 많은 듯하지만",
}

DYNAMIC_COORDINATES = {
    "6:2320:0",
    "6:2320:1",
    "6:2322:0",
    "6:2322:1",
    "6:2324:0",
    "6:2324:1",
    "6:2325:0",
    "6:2325:1",
    "6:2330:0",
    "6:2330:1",
    "6:2331:0",
    "6:2331:1",
    "6:2336:0",
    "6:2336:1",
    "6:2337:0",
    "6:2337:1",
}


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
                "segment": "base_msggame_B001_S125",
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
