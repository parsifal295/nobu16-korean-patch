#!/usr/bin/env python3
"""Build Base authoring segment 474 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S474.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s474", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2684:0": "훌륭하구나,",
    "7:2684:1": "!\n",
    "7:2684:2": "도 질 수는 없지!",
    "7:2685:0": "전공 제일이라니 훌륭하군\n",
    "7:2685:1": "하고 싸우면 뜨겁게 달아오를 수 있어 좋군",
    "7:2686:0": "역시,",
    "7:2686:1": "님은 다르십니다\n우리 가문의 자랑이십니다",
    "7:2687:0": "역시,",
    "7:2687:1": "님은 강하시군요\n",
    "7:2687:2": "도 안심하고 싸울 수 있습니다",
    "7:2688:0": "역시 대단하구나,",
    "7:2688:1": "!\n내 일처럼 기쁘구나!",
    "7:2689:0": "오오,",
    "7:2689:1": "이(가) 전공 제일인가!\n함께 우리 가문을 더욱 빛내세",
    "7:2690:0": "그에 비해,",
    "7:2690:1": "은(는) 그럭저럭이군\n아직 더 높은 곳을 노릴 수 있을 터다",
    "7:2691:0": "큭, 전공 제일에는 이르지 못했는가……!",
    "7:2692:0": "의 전과는 그럭저럭이다만\n조금 아쉽구나",
    "7:2693:0": "공을 세울 때도 최고를 노려야지!",
    "7:2694:0": "내 전과도 썩 좋았다고 할 만하군",
    "7:2695:0": "착실하게 공을 세운 모양이군",
    "7:2696:0": "다음에야말로 전공 제일을 노리자",
}

STATIC_COORDINATES: set[str] = {
    "7:2691:0",
    "7:2693:0",
    "7:2694:0",
    "7:2695:0",
    "7:2696:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S474", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
