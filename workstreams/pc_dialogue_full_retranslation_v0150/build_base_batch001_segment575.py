#!/usr/bin/env python3
"""Build Base authoring segment 575 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S575.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s575", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:540:0": "밀어붙여라! 무사의 기개를\n똑똑히 보여 주어라!",
    "9:541:0": "조금만 더 버텨라……\n밀어붙여라!",
    "9:542:0": "밀어붙이세요…… 다만\n방심하지는 마세요",
    "9:543:0": "이대로 밀어내\n버려라!",
    "9:544:0": "여기서는 밀어붙이는 것이\n상책일까……?",
    "9:545:0": "완전히 밀어붙이기까지\n이제 조금 남았군……",
    "9:546:0": "이제 얼마 남지 않았다!\n적을 밀어내자!",
    "9:547:0": "조금만 더!\n밀어붙여!",
    "9:548:0": "돌격하라!\n이대로 끝까지 밀어붙여라!",
    "9:549:0": "이대로 끝까지\n밀어붙이세요!",
    "9:550:0": "이제 조금 남았다!\n끝까지 밀어붙여라!",
    "9:551:0": "밀리지 마!\n정신 바짝 차려!",
    "9:552:0": "이대로 밀려날 수는\n없다……!",
    "9:553:0": "벼랑 끝이다\n굳건히 버텨라……!",
    "9:554:0": "생각해 내라……\n적을 밀어낼 계책을……!",
    "9:555:0": "큭…… 무엇을 하느냐!\n밀어내라!",
    "9:556:0": "적의 기세가 거세다……\n위험하군……!",
    "9:557:0": "이…… 이 무슨 기세인가……",
    "9:558:0": "안 된다!\n우리가 밀리고 있다!",
    "9:559:0": "무시무시한 기세야……\n이대로라면……",
    "9:560:0": "버텨라!\n적에게 밀려나지 마라……!",
    "9:561:0": "이대로라면\n밀려나고 만다……",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S575", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
