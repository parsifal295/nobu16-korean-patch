#!/usr/bin/env python3
"""Build Base authoring segment 201 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S201.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s201", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3456:0": "이리하여,",
    "6:3456:1": "을(를) 섬길 수 있게 되어\n기쁘기 그지없습니다\n앞으로의 활약도 부디 기대해 주십시오",
    "6:3457:0": "우리 가문의 쟁쟁한 장수들 가운데서도\n남보다 갑절이나 애쓴 보람이 있었소\n이제 병사들의 동경을 한 몸에 받겠구려",
    "6:3458:0": "내가 일등이 돼 버렸군!\n주위엔 쟁쟁한 녀석들뿐인데 말이야!\n이젠 목에 힘 좀 주고 다닐 수 있겠는걸!",
    "6:3459:0": "훈공 1위, 감사히 받겠사옵니다!\n",
    "6:3459:1": "의 말석을 더럽히고 이름도 조금은 알려진 몸\n그 지위에 부끄럽지 않게 활약해야 하리라!",
    "6:3460:0": "으로(로)서 훈공 1위는 당연한 일\n허나 정상까지는 아직 멀었소\n올해를 한층 더 도약하는 해로 삼겠소",
    "6:3461:0": "가장 뛰어난 성과를 거두었군요\n아랫사람을 길러 내는 몸으로서\n훈공 1위를 계속 지켜야겠군요",
    "6:3462:0": "훈공 1위도 달갑기만 한 것은 아니로군\n무예로 공을 세워 인정받음은 기쁘다만\n남의 위에 서는 것은 번거롭구나",
    "6:3463:0": "훈공 1위라니 참으로 과분하옵니다…\n재주 없는 저를 이 자리에 앉혀 주셨기에\n",
    "6:3463:1": "께 은혜를 갚으려 힘쓰고 있을 뿐이옵니다…",
    "6:3464:0": "에 이름을 올린다는 것은\n일거수일투족에 우리 가문을 짊어진다는 뜻\n품격 없는 처신은 할 수 없사옵니다",
    "6:3465:0": "훈공 1위\n",
    "6:3465:1": "의",
    "6:3465:2": "이(가) 차지하지 않고 누가 차지하겠느냐!\n모두,",
    "6:3465:3": "을(를) 본보기로 우러러야 하느니라!",
    "6:3466:0": "으로(로)서 충분한 성과를 거두었습니다!\n이로써 후진들에게도 모범을 보였군요",
    "6:3467:0": "이제야 어엿한 무장이라 할 수 있겠구나\n꽃을 피웠으니, 다음에는 열매를 맺어 보자꾸나",
    "6:3468:0": "라면 당연한 일이지요\n이 정도로 만족할 생각은 없답니다",
    "6:3469:0": "우리 가문에서",
}

STATIC_COORDINATES: set[str] = {
    "6:3457:0",
    "6:3458:0",
    "6:3461:0",
    "6:3462:0",
    "6:3467:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S201", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
