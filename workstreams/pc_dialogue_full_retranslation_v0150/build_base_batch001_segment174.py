#!/usr/bin/env python3
"""Build Base authoring segment 174 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S174.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s174", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3078:1": "이(가) 우리 가문을 떠나\n",
    "6:3078:2": "와(과)의 사이에도 금이 갔사옵니다\n유예는 앞으로",
    "6:3078:3": "개월뿐이옵니다",
    "6:3079:0": "이(가) 이어 주고 있던\n",
    "6:3079:1": "와(과)의 혼인 동맹도",
    "6:3079:2": "개월 후면\n끝나고 마는군요…",
    "6:3080:0": "이(가) 떠나,",
    "6:3080:1": "와(과)의\n혼인 동맹도 앞으로",
    "6:3080:2": "개월 후면 파기됩니다.\n부디 유의하시옵소서",
    "6:3081:0": "은(는) 충분한 힘을 길렀으니",
    "6:3081:1": "\n이제부터는 종속이 아닌 대등한 동맹을 맺어\n서로 도우",
    "6:3082:0": "귀군은 충분한 힘을 얻었으니",
    "6:3082:1": "\n이제부터는 종속이 아닌 대등한 동맹을 맺어\n서로 도우",
    "6:3083:0": "귀군은 충분한 힘을 얻었으니",
    "6:3083:1": "\n이제부터는 종속이 아닌 대등한 동맹을 맺어\n서로 도우",
    "6:3084:0": "귀군은 충분한 힘을 얻었으니",
    "6:3084:1": "\n이제부터는 종속이 아닌 대등한 동맹을 맺어\n서로 도우",
    "6:3085:0": "귀군은 충분한 힘을 얻었으니",
    "6:3085:1": "\n이제부터는 종속이 아닌 대등한 동맹을 맺어\n서로 도우",
    "6:3086:0": "귀군은 충분한 힘을 얻었으니",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S174", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
