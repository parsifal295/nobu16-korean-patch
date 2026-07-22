#!/usr/bin/env python3
"""Build Base authoring segment 396 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S396.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s396", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1493:0": "을(를) 빼앗자꾸나\n아군과 맞먹는 병력이 지키는 성이니\n다른 가문의 원군과 함께 공격하는 것이 좋으리라",
    "7:1494:0": "은(는) 우리와 대등한 병력이 지키고 있다\n우리 힘만으로는 벅찰 터\n다른 가문의 원군을 불러 공격하자꾸나",
    "7:1495:0": "을(를) 공격하시려면\n다른 가문에 원군을 청하십시다\n쓸 수 있는 것은 써야 하옵니다!",
    "7:1496:0": "의 적은\n단독으로 공격하기엔 조금 벅찰 듯하니\n다른 가문의 원군을 청하심이 어떻겠습니까?",
    "7:1497:0": "의 적은 우리와 대등합니다\n여기서는 신중을 기해\n다른 가문에도 원군을 청해야 할 듯합니다",
    "7:1498:0": "의 수비는 얕볼 수 없습니다\n다른 가문의 원군과 보조를 맞춰\n함께 공격하심이 어떻겠습니까",
    "7:1499:0": "을(를) 공략하시려거든\n성을 공격하는 일은 지키는 것보다 어려우니\n다른 가문의 원군도 청해 두심이 어떠하옵니까",
    "7:1500:0": "의 수비를 생각하면\n단독 공격으로는 불안이 남습니다\n원군을 부르심이 어떠하겠습니까",
    "7:1501:0": "을(를) 공략하는 일이옵니다만\n아군의 공격과 적의 수비는 백중세이니\n원군과 함께 공격하심이 어떠하겠습니까",
    "7:1502:0": "은(는) 함락할 수 있을 것이옵니다\n다만 우리 힘만으로는 미덥지 못하니\n다른 가문에서 원군을 불러야 할 듯하옵니다",
    "7:1503:0": "은(는) 탈취할 수 있사옵니다\n다만 성을 지키는 적과 우리는 호각이니\n원군을 청하시는 것이 좋겠사옵니다",
    "7:1504:0": "은(는) 수비가 제법 견고합니다\n우리 힘만으로는 다소 벅찰 듯하니\n원군과 협력해 공격하시옵소서",
    "7:1505:0": "을(를) 지키는 적은\n아군과 대등한 전력을 지녔사옵니다\n다른 가문의 원군과 함께 공격하시옵소서",
    "7:1506:0": "을(를) 탈취해야 하오\n하지만 상당한 병력이 지키는 성이니\n원군을 부르시는 편이 좋을 듯하오",
    "7:1507:0": "은(는) 함락할 수 있을 것이옵니다\n하지만 공성전은 신중해야 하는 법\n원군과 함께 공격하시옵소서",
    "7:1508:0": "은(는) 공략할 수 있습니다\n다만 성의 병력이 우리와 대등하니\n다른 가문의 원군이 필요할 것입니다",
    "7:1509:0": "이라면 빼앗을 수 있겠군\n수비 병력이 아군과 비슷하니\n원군을 부르는 것이 전제지만……",
    "7:1510:0": "을(를) 손에 넣는 거다\n우리만으로는 어렵겠지만\n원군이 있다면 해낼 수 있을 거야",
    "7:1511:0": "을(를) 공격합시다\n적잖은 병력이 주둔해 있사오나\n다른 가문의 원군이 있다면 이길 수 있사옵니다",
    "7:1512:0": "을(를) 공략하리라!\n우리와 대등한 적병도\n원군이 있다면 쉽게 무찌를 수 있을 것이옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S396", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
