#!/usr/bin/env python3
"""Build Base authoring segment 581 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S581.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s581", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:667:0": "더 이상의 교전은……\n물러나겠습니다!",
    "9:668:0": "전의가 오르지 않는군……\n물러나겠다",
    "9:669:0": "이래서는 싸울 수 없겠군요\n물러납시다……",
    "9:670:0": "이렇게까지 몰렸으니\n……큭, 물러나라",
    "9:671:0": "이봐, 괜찮은 거냐?",
    "9:672:0": "불찰이다!\n주군의 부대가 무너졌는가……!",
    "9:673:0": "이럴 수가……무사히 전장을\n빠져나갈 수 있을까……?",
    "9:674:0": "눈앞에서 주군의 부대가\n무너지게 두다니……!",
    "9:675:0": "주군의 부대가 무너졌다고!?\n이놈들……!",
    "9:676:0": "주군의 부대가 무너지다니……\n좋지 않군",
    "9:677:0": "주군의 부대가 무너지다니\n가신으로서 수치로다……",
    "9:678:0": "주군의 부대가!? 에잇!\n당하고 말았구나!",
    "9:679:0": "주군께서……!?\n이제 어찌 되는 거지?",
    "9:680:0": "적에게 정신을\n너무 빼앗겼던가……",
    "9:681:0": "그럴 수가……!\n주군께서는 무사하실까요",
    "9:682:0": "부디 피하소서!",
    "9:683:0": "여기서는\n물러설 수밖에 없나……",
    "9:684:0": "물러나야 한다니……\n참으로 면목이 없구나",
    "9:685:0": "후퇴하겠다……\n내 힘으로는 감당 못 할 적이었다",
    "9:686:0": "지금이 물러날 때……\n물러나겠습니다!",
    "9:687:0": "유감이지만,\n물러날 수밖에 없겠군……",
    "9:688:0": "병사들이 버티지 못했나……\n물러나겠다",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S581", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
