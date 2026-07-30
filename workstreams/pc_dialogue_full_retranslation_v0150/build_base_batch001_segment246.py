#!/usr/bin/env python3
"""Build Base authoring segment 246 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S246.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s246", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3940:2": "\n승낙하시겠습니까?",
    "6:3941:0": "거절하면",
    "6:3941:1": "의 신용이 떨어질 뿐만 아니라\n다른 가문들의 불신도 사게 됩니다만\n괜찮으시겠습니까?",
    "6:3942:0": "요청을 수락한 동안에는",
    "6:3942:1": "을(를) 우리 가문이 함락하더라도\n",
    "6:3942:2": "의 지배하에 들",
    "6:3942:3": "\n부디 각별히 주의해 주",
    "6:3943:0": "전 영주",
    "6:3943:1": "이(가) 옛 영지",
    "6:3943:2": "에 복귀했습니다",
    "6:3944:0": ", 조정에서",
    "6:3944:1": "사자가 찾아오셨",
    "6:3944:2": "\n꼭",
    "6:3944:3": "을(를)\n뵙고 싶다고 하",
    "6:3945:0": "님,\n귀공의 처신에는 우리도 감복했소\n앞으로도 우호를 이어 가고자 찾아왔소",
    "6:3946:0": "요즘 그대가 여러모로 돈을 바쳐 주고 있다만\n다시",
    "6:3946:1": "만큼 바친다면 관위를 내려도 좋다고\n천황께서 말씀하셨다. 어떠한가?",
    "6:3947:0": "요즘은 세상이 흉흉하여 이래저래 돈이 드는구먼…\n",
    "6:3947:1": "만큼 금전으로 성의를 보인다면\n조정에서 편의를 봐줄까 하는데…",
    "6:3948:0": "으음…그러한가\n아쉽지만 어쩔 수 없군\n다음에는 좋은 답을 들려주게",
}

STATIC_COORDINATES: set[str] = {
    "6:3948:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S246", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
