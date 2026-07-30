#!/usr/bin/env python3
"""Build Base authoring segment 364 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S364.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s364", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:943:0": "에게 패했다니……\n",
    "7:943:1": "의 힘을\n조금 지나치게 높이 평가했나……",
    "7:944:0": "에게 뒤처지다니……\n",
    "7:944:1": "은(는) 내 호적수가 될 수 없는가\n참으로 유감이로다",
    "7:945:0": "힘없는 의는 없는 것이나 다름없다\n",
    "7:945:1": "에게 패한 이상\n",
    "7:945:2": "와(과)는 조금 거리를 두겠다",
    "7:946:0": "에게 패한 것이 불운 탓인지 실력 탓인지\n어느 쪽이든",
    "7:946:1": "은(는) 쇠락을 피하지 못하리라\n앞으로 관계를 달리해야겠군",
    "7:947:0": "호오…… 그 싸움은 「",
    "7:947:1": "」이(가) 이겼는가\n그렇다면 「",
    "7:947:2": "」을(를) 공략하는 방안도\n염두에 두어야겠구나",
    "7:948:0": "은(는) 패했는가……\n의리에는 어긋나지만 이것이 난세의 도리\n우리 가문도 약자를 대하는 방식을 바꿔야겠군",
    "7:949:0": "에게 져 버렸다고!?\n",
    "7:949:1": "따위는 피라미잖아!\n엮여 봤자 시간 낭비라고!",
    "7:950:0": "은(는) 패했다고 하는군\n무를 숭상하는 이 세상에서 패배는 낙인\n우리 가문을 비롯한 다른 가문의 멸시는 피하지 못하리라",
    "7:951:0": "따위에게 패하다니……\n",
    "7:951:1": "의 쇠락은 온 천하에 알려졌군\n앞으로 대하는 방식도 바꿔야겠군",
    "7:952:0": "에게 패한 것입니까……\n",
    "7:952:1": "은(는) 이미 기울어 가는지도 모릅니다\n더는 깊이 교류할 필요도 없겠지요",
}

STATIC_COORDINATES: set[str] = set()


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S364", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
