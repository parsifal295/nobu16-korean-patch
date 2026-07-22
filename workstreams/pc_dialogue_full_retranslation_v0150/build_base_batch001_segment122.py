#!/usr/bin/env python3
"""Build Base authoring segment 122 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S122.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s122", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2236:0": "…와 있었던 거냐",
    "6:2237:0": "같은 자와 자리를 함께하다니\n고통스럽기만 하군… 빨리 끝내지",
    "6:2238:0": "님인가… 뭐, 좋다",
    "6:2239:0": "아아…",
    "6:2239:1": "님이셨군요",
    "6:2240:0": "…무슨 일이지?\n나눌 이야기는 없다고 생각하는데?",
    "6:2241:0": "이익이 된다면 과거의 경위는 상관없지\n아예 개의치 않는 그 배짱이 재미있군",
    "6:2242:0": "이런, 이런,",
    "6:2242:1": "님\n이리도 거리낌 없이 찾아올 줄은 몰랐소",
    "6:2243:0": "매몰차게 쫓아내지는 않겠지만 이곳은 본디\n",
    "6:2243:1": "이(가) 발을 들여도 될 땅이 아니다",
    "6:2244:0": "님, 오셨군요…",
    "6:2245:0": "분명…",
    "6:2245:1": "님이었지. 와 있었나",
    "6:2246:0": "어머…",
    "6:2246:1": "님이신가요…",
    "6:2247:0": "이런,",
    "6:2247:1": "님이 나타나다니…",
    "6:2248:0": ", 뭐 하러 왔느냐!",
    "6:2249:0": "여기에 나타난 배짱은 높이 사주마\n그것이",
    "6:2249:1": "을(를) 지금 베지 않는 이유다",
    "6:2250:0": "…이야기가 끝났으면 어서 꺼져라",
    "6:2251:0": "님, 적이나 다름없는 우리 가문에\n무엇을 바라십니까?",
    "6:2252:0": "…무슨 일로 왔느냐",
    "6:2253:0": "철포대가",
    "6:2253:1": "의 얼굴을 노려도 소용없겠군\n두꺼운 낯가죽에 튕겨 나갈 테니",
    "6:2254:0": "이런, 이런. 보기 드문 손님이군… 잊었나?\n우리 가문과 그대 가문의 사이가 어땠는지",
    "6:2255:0": "뭐,",
    "6:2255:1": "? 꾀병을 핑계로 돌려보내라\n…이런, 벌써 들어와 앉았구먼",
}

STATIC_COORDINATES = {"6:2240:0", "6:2241:0", "6:2250:0", "6:2252:0", "6:2254:0"}


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
        static = coordinate in STATIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required" if static else "pending",
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
                "segment": "base_msggame_B001_S122",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
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
