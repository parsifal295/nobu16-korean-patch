#!/usr/bin/env python3
"""Build Base authoring segment 172 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S172.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s172", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3064:3": "님의 뜻에 달린 듯하옵니다",
    "6:3065:0": "와(과)는 특별한 관계가 아니게 되어\n",
    "6:3065:1": "개월 후에는 동맹도 효력을 잃사옵니다.\n앞으로 어찌 대할지는 마음먹기에 달렸사옵니다",
    "6:3066:0": "은(는) 이제 완전히 남이 되었으니\n동맹도",
    "6:3066:1": "개월 후면 끝나옵니다.\n서로의 관계를 다시 생각해 볼 때인 듯하옵니다",
    "6:3067:0": "와(과)의 인연이 끊어져, 동맹도 앞으로\n",
    "6:3067:1": "개월만 남게 되었사옵니다.\n그 뒤에도 함께 나아갈 수 있으면 좋으련만…",
    "6:3068:0": "인척 관계가 끝났으므로\n",
    "6:3068:1": "와(과)의 동맹은 앞으로",
    "6:3068:2": "개월만 남았사오며\n그 뒤에는 적이 될지도 모르옵니다",
    "6:3069:0": "이(가) 떠나 버렸으니\n",
    "6:3069:1": "와(과)의 동맹도 앞으로",
    "6:3069:2": "개월 뒤면\n끝나 버린다고. 조심하라고",
    "6:3070:0": "이(가) 우리 가문을 떠났으므로\n",
    "6:3070:1": "와(과) 이어 온 동맹도\n",
    "6:3070:2": "개월 후까지만 이어지게 되었사옵니다",
    "6:3071:0": "이(가) 우리 가문을 떠나, 혼인을 맺었던\n",
    "6:3071:1": "와(과)의 동맹도\n",
    "6:3071:2": "개월 뒤면 끝나게 되었사옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S172", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
