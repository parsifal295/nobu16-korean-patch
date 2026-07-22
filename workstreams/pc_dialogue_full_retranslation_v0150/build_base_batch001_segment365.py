#!/usr/bin/env python3
"""Build Base authoring segment 365 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S365.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s365", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:953:0": "에게 패하다니……\n나약하기 짝이 없구나,",
    "7:953:1": "\n그 정도밖에 안 되는 가문이었나",
    "7:954:0": "에게 패할 정도라면 믿을 수 없다\n아니, 차라리",
    "7:954:1": "을(를) 공략하는 편이\n우리 가문에는 이득인가……",
    "7:955:0": "에게 패했다니, 안됐구나…… 후후\n우리 가문은 그렇다 쳐도 세상은\n",
    "7:955:1": "을(를) 얕보게 되겠지",
    "7:956:0": "에게 졌다고……?\n무사는 이겨야 마땅한 법이거늘\n이토록 각오가 부족한 가문이었나",
    "7:957:0": "에게 패하고 말았습니까……\n",
    "7:957:1": "도 쇠락했군요\n이제 신경 쓸 상대는 아니겠지요",
    "7:958:0": "와(과) 억지로 교류할 필요는 없다\n",
    "7:958:1": "에게 패할 정도라면\n앞날도 뻔하다",
    "7:959:0": "이(가)",
    "7:959:1": "에게 패했다고요?\n허울뿐이었던 모양이군요\n그에 걸맞게 대하도록 하지요",
    "7:960:0": "에게 패했다니……\n",
    "7:960:1": "와(과)의 향후 관계를\n다시 생각할 좋은 기회일지도 모르겠군",
    "7:961:0": "위풍으로 우리 가문과 주변 세력의 관계가 호전",
    "7:962:0": "을(를) 멸했는가…… 좋다\n",
    "7:962:1": "이여, 더욱 강해져라\n그리고 이 노부나가와 천하를 놓고 겨루어라",
    "7:963:0": "오오!　",
    "7:963:1": "을(를) 이겼구나!\n",
}

STATIC_COORDINATES: set[str] = {"7:961:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S365", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
