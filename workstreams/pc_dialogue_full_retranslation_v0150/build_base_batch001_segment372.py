#!/usr/bin/env python3
"""Build Base authoring segment 372 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S372.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s372", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1040:0": "놈\n내 손바닥 위에서 실컷 놀아나거라",
    "7:1041:0": "따위에게\n우리가 당할 리는 없다만",
    "7:1042:0": "따위는\n단숨에 쓸어 버려 주마",
    "7:1043:0": "은(는) 오합지졸\n늙은 이 몸에게도 상대하기 쉽구나",
    "7:1044:0": "놈\n연륜의 차이를 가르쳐 주마",
    "7:1045:0": "은(는) 사기도 낮아\n손쉽게 격퇴할 수 있을 듯하옵니다",
    "7:1046:0": "따위로 주군께서 직접\n나서실 필요도 없습니다",
    "7:1047:0": "은(는) 호기로운 것인가\n아니면 분수를 모르는 것인가……",
    "7:1048:0": "따위는\n내 칼의 녹으로 만들어 주마",
    "7:1049:0": "라면\n쉽게 밀어낼 수 있을 것입니다",
    "7:1050:0": "라면\n아군의 손실도 미미할 것입니다",
    "7:1051:0": "쯤이라면\n격퇴하기 쉽겠군요",
    "7:1052:0": "라면\n나라도 수월하게 이길 수 있겠지요",
    "7:1053:0": ", 이 노부나가와\n대등한 힘을 지녔는가\n빈틈을 보여서는 안 된다",
    "7:1054:0": "은(는) 좌시할 수 없는 적\n속히 쳐부수어\n후환을 없애자",
    "7:1055:0": "인가, 우리와 대등한\n상대이군\n맞아 싸우는 것도 한 방법이지만……",
    "7:1056:0": "은(는) 내버려 둘 수 없다\n여기서는 치고 나가\n적과 자웅을 가려야 한다",
    "7:1057:0": "은(는) 방심할 수 없는 상대\n신중히 움직이면서\n승기를 노리는 것이 상책입니다",
    "7:1058:0": "이(가) 상대라니 좋은 기회로다\n미카와 무사의 강인함을\n지금이야말로 천하에 보이리라",
    "7:1059:0": "라니 흥미롭구나\n우리 다케다 기마대의 힘을\n마음껏 보여 주마",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S372", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
