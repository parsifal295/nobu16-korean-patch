#!/usr/bin/env python3
"""Build Base authoring segment 159 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S159.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s159", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2885:0": "의 밑에서는 난세를 살아남을 수 없소\n의지할 곳은 귀 가문뿐입니다",
    "6:2886:0": "의 밑에서는 앞날이 불안하오…\n앞으로 신세를 지겠소이다",
    "6:2887:0": "은(는) 의지할 수 없사옵니다…\n앞으로 잘 부탁드리옵니다",
    "6:2888:0": "은(는) 믿을 만하지 않소…\n앞으로는 귀공을 의지하겠소",
    "6:2889:0": "은(는) 위에 모실 그릇이 아니었소\n귀 가문 아래에서야 우리 가문도 번영할 것이오",
    "6:2890:0": "은(는) 의지할 수 없소…\n아무쪼록 잘 부탁하오",
    "6:2891:0": "은(는) 믿을 수 없사옵니다…\n앞으로 잘 부탁드리옵니다",
    "6:2892:0": "에게는 정이 다 떨어졌습니다…\n이제부터는 귀 가문을 위해 일하겠습니다",
    "6:2893:0": "은(는) 시시한 자였어…\n앞으로 신세를 지겠다",
    "6:2894:0": "의 얼굴은 이제 보고 싶지 않습니다\n당신의 산하에 들어오게 되다니\n꿈만 같습니다",
    "6:2895:0": "은(는) 의지할 수 없사옵니다…\n그에 비하면 귀공은 참으로 믿음직스럽습니다",
    "6:2896:0": "이(가) 단교한다고!?\n칫,", "6:2896:1": "의 농간인가!",
    "6:2897:0": "이(가) 맹약을 파기한다고?\n설마,", "6:2897:1": "의 농간인가!",
    "6:2898:0": "이(가) 맹약을 끊다니\n", "6:2898:1": "의 농간인가… 용서할 수 없군",
    "6:2899:0": "이(가) 단교를 통고해 왔다고요?\n설마…", "6:2899:1": "의 농간이군요",
    "6:2900:0": "이(가) 단교한다고…?\n…",
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S159", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
