#!/usr/bin/env python3
"""Build Base authoring segment 576 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S576.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s576", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:562:0": "이렇게까지\n밀리고 말 줄이야……",
    "9:563:0": "좋았어!\n이대로 돌파해!",
    "9:564:0": "모두, 기세를 드높여라!\n지금이 기회다!",
    "9:565:0": "적이 물러나고 있다……\n방심 말고 계속 밀어붙여라!",
    "9:566:0": "공세를 늦추어서는\n안 됩니다!",
    "9:567:0": "적이 주춤했다!\n단숨에 밀어붙여라!",
    "9:568:0": "후후, 이걸로\n끝까지 밀어붙였군……!",
    "9:569:0": "지금이야말로 단숨에\n적을 밀어낼 때다!",
    "9:570:0": "정신을 다잡아라!\n밀어붙이는 게다!",
    "9:571:0": "적이 주춤했습니다!\n바로 지금입니다!",
    "9:572:0": "좋아! 이대로\n짓눌러 버려라!",
    "9:573:0": "적이 물러났습니다……\n이 기세로 공격하겠습니다",
    "9:574:0": "미…… 밀어냈는가!\n공세를 늦추지 마라!",
    "9:575:0": "어쩔 수 없지, 얼른\n밀어내자!",
    "9:576:0": "만만치 않은 적이다……\n서둘러 전열을 재정비해야 한다!",
    "9:577:0": "으음, 서둘러\n전열을 가다듬어야겠군……",
    "9:578:0": "큭…… 전열을 재정비하는 게\n최우선이군요",
    "9:579:0": "에잇, 전열을 재정비하라!",
    "9:580:0": "큭…… 전열을 가다듬으려\n물러났을 뿐이다……",
    "9:581:0": "설마―",
    "9:581:1": "마저\n밀려나고 말 줄이야……",
    "9:582:0": "이건 당해 낼 수 없군!",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS) - {"9:581:0", "9:581:1"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S576", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
