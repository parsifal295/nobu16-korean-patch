#!/usr/bin/env python3
"""Build Base authoring segment 524 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S524.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s524", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:617:0": "이런 대접이라니…\n가신단에서 업신여김만 받겠구나…",
    "8:618:0": "이보다 영지가 더 줄어들면\n살림은 갈수록 어려워지겠구나…",
    "8:619:0": "이해할 수 없습니다…\n늘려 주시는 것이 아니라 줄이신다는 말씀입니까?",
    "8:620:0": "더 잘 해낼 수 있으리라 여겼건만\n이 늙은이로는 안 되었던가…",
    "8:621:0": "내 무용이…\n중히 여겨지는 시대가 아니란 말인가",
    "8:622:0": "이토록 업신여김을 받으니\n서글퍼지는구려",
    "8:623:0": "지행에 대한 내 불만을\n풀어 주기는커녕 회수하겠다고…?",
    "8:624:0": "께서는 「",
    "8:624:1": "」 나름의 생각이 있으시겠지요\n이곳은 내놓겠습니다",
    "8:625:0": "여기에 더해 지행까지 회수…입니까\n웃을 수밖에 없군요…",
    "8:626:0": "의 지행은 너무 적지 않은가…?",
    "8:627:0": "허어… 지행을 회수하신다고…?\n더 내리신다는 말씀을 잘못 들은 겐가?",
    "8:628:0": "이보다 더 줄어들면\n앞으로 어떻게 살아가야 할까요",
    "8:629:0": "기존 지행고로도 불만이었는데\n거기서 더 회수하시다니…",
    "8:630:0": "제게는 맡길 수 없다는 뜻입니까…\n나름대로 힘쓰고 있습니다만…",
    "8:631:0": "배짱 한번 좋군\n가뜩이나 적은 지행을 더 줄이려 들다니",
    "8:632:0": "본의는 아니오나\n",
    "8:632:1": "의 명령이라면 따를 수밖에 없지요",
    "8:633:0": "지행을 회수하신다…는 말씀입니까…\n무능한 이 몸을 원망할 따름입니다…",
    "8:634:0": "그렇지 않아도 적은 지행이…",
    "8:635:0": "가신들의 불만을 돌아보지 않는 주군을 만난 것이\n이 몸의 불운인가…",
    "8:636:0": "나에 대한 평가는 이 정도가 고작인가…",
    "8:637:0": "어…?\n지금까지는 잘 대해 줬잖아",
    "8:638:0": "어쩔 수 없사옵니다\n",
    "8:638:1": "의 능력이 부족한 탓이겠지요",
}

STATIC_COORDINATES = {
    f"8:{record_id}:0"
    for start, end in ((617, 623), (625, 625), (627, 631), (633, 637))
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S524", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
