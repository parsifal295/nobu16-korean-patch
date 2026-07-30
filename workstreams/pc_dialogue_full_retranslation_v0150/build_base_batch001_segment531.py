#!/usr/bin/env python3
"""Build Base authoring segment 531 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S531.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s531", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:758:0": "이대로는 태풍에\n휘쓸려 날아가고 말 것이오…",
    "8:759:0": "큰일이군, 이 제방으로는\n태풍을 버티지 못하겠어…",
    "8:760:0": "의 현 상태로는…\n수해 피해가 크겠군",
    "8:761:0": "의 치수로는\n태풍에 맞설 수 없겠구나…",
    "8:762:0": "수해 대비가\n되어 있지 않군요…",
    "8:763:0": "바람만 불어도 날아갈 듯한 치수라니\n…태풍아, 오지 마라!",
    "8:764:0": "위험하군… 「",
    "8:764:1": "」은(는)\n치수 수준이 지나치게 낮다",
    "8:765:0": "이런 치수 대책으로는…\n수해로 인한 피해를 면할 수 없겠군",
    "8:766:0": "이거야 태풍이 아니더라도\n",
    "8:766:1": "의 치수로는 버티기 어렵겠군…",
    "8:767:0": "아아, 태풍이 오면\n어찌 될지 걱정이네요…",
    "8:768:0": "지금 상태로는 태풍에\n대처할 수 없겠구나…",
    "8:769:0": "지금은 태풍이 오지 않기를\n기도할 수밖에…",
    "8:770:0": "날씨가 참 좋구나\n꽃놀이하기에 딱 좋은 날이로다",
    "8:771:0": "죽순을 산더미만큼 캤다!\n삶아 먹으면 정말 맛있다고!",
    "8:772:0": "봄꽃처럼 피어나\n꽃잎처럼 지고 싶구나",
    "8:773:0": "봄 들판에서 뛰노는 아이들…\n참으로 흐뭇한 광경이로다",
    "8:774:0": "아름다운 봄 풍경이군요…\n언제까지나 바라보고 싶습니다",
    "8:775:0": "봄에는 백화가 있고\n좋은 계절이 되었구나",
    "8:776:0": "봄은 농사의 시작이다\n할 일이 산더미처럼 많구나",
    "8:777:0": "「산이 웃는다」는 말이 참이로구나\n봄 산의 신록이 아름다워…",
}

STATIC_COORDINATES = {
    f"8:{record_id}:0"
    for start, end in ((758, 759), (762, 763), (765, 765), (767, 777))
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S531", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
