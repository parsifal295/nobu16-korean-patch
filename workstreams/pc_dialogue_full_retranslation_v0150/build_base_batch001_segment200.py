#!/usr/bin/env python3
"""Build Base authoring segment 200 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S200.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s200", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3442:0": "훈공 1위라니!\n이를 힘으로 삼아\n다음에도 힘차게 임하겠습니다!",
    "6:3443:0": "가장 큰 성과를 올렸군\n허나 목표는 아직 한참 위에 있다\n더욱 정진해야겠어",
    "6:3444:0": "분에 넘치는 영광이옵니다\n이에 만족하지 않고\n더 높은 곳을 향해 나아가겠사옵니다",
    "6:3445:0": "감사할 따름이오!\n이 기세로",
    "6:3445:1": "의 신임을\n더욱 얻어 가고 싶구려",
    "6:3446:0": "내 활약을 인정해 줘서 고맙다!\n앞으로는 더욱\n깜짝 놀라게 해 줄 테니 두고 보라고!",
    "6:3447:0": "훈공 1위,",
    "6:3447:1": "이(가) 삼가 받았소이다!\n한 방면을 맡은 장수에 걸맞은 활약을\n해냈다는 뜻이겠지요",
    "6:3448:0": "훈공 1위는 기쁘다만\n이 지위는 아직 내 능력에 못 미치는군\n더욱 힘써야겠다",
    "6:3449:0": "으로(로)서 모두의 본보기가 될 수 있었습니다\n꾸준히 힘써 온 결실이군요\n앞으로도 정진해 나가겠습니다",
    "6:3450:0": "호오, 훈공 1위라…\n",
    "6:3450:1": "이(가) 되면 할 수 있는 일도 많으니\n활약하는 것도 당연하지",
    "6:3451:0": "훈공 1위…? 필시 착오이겠지요\n",
    "6:3451:1": "이(가) 바친 계책 따위는\n이미",
    "6:3451:2": "의 마음속에 있던 것뿐이었으니…",
    "6:3452:0": "훈공 1위라니, 감사한 일이오\n정무와 전쟁 어느 쪽에서도 이익만 좇지 않고\n풍류를 잊지 않은 덕이겠소이까",
    "6:3453:0": "흠, 이 훈공 1위를 거머쥔 것은\n",
    "6:3453:1": "의 휘하에 있는 모두의 공이로다\n그리고 그들을 거느린 내 역량 덕이기도 하지",
    "6:3454:0": ", 아직 한참 더 일할 수 있습니다!\n더 많은 일을 맡겨 주십시오!",
    "6:3455:0": "중견으로 인정받게 된 셈인가\n허나 목표는 더욱 높은 곳\n한층 더 나아가도록 하자",
}

STATIC_COORDINATES: set[str] = {
    "6:3442:0",
    "6:3443:0",
    "6:3444:0",
    "6:3446:0",
    "6:3448:0",
    "6:3452:0",
    "6:3455:0",
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
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S200", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
