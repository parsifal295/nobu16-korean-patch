#!/usr/bin/env python3
"""Build Base authoring segment 448 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S448.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s448", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2296:0": "이제 성을 공격해야 한다",
    "7:2297:0": "더는 기다릴 필요 없다\n당장 성을 공격하라",
    "7:2298:0": "기회를 놓치지 말고 공격하라",
    "7:2299:0": "더는 기다릴 수 없군\n공격하려면 지금이다",
    "7:2300:0": "기다리고 있을 수 없다\n우리는 성을 공격한다!",
    "7:2301:0": "이제 됐다\n공성을 개시하라!",
    "7:2302:0": "기다릴 것 없다\n성을 공격한다!",
    "7:2303:0": "이제 충분하다\n성을 공격하리라!",
    "7:2304:0": "기다릴 필요 없다\n공성에 들어간다!",
    "7:2305:0": "지금이 기회라 판단했습니다\n공성을 개시합니다",
    "7:2306:0": "더 기다려서는 안 된다\n공성을 개시하라!",
    "7:2307:0": "더 기다릴 생각이었지만\n공성의 기회는 놓칠 수 없다",
    "7:2308:0": "상황을 더 지켜보는 편이 이로울 수도 있으나\n공성을 개시한다",
    "7:2309:0": "더는 기다릴 것도 없다\n공성전에 들어가도록 하지",
    "7:2310:0": "이제 나설 때입니다\n성 공격을 시작하겠습니다!",
    "7:2311:0": "호기라 판단했다\n성을 공격할 때는 지금이다!",
    "7:2312:0": "지금이 기회라 판단했습니다\n공성을 개시하겠습니다",
    "7:2313:0": "기회를 놓쳐서는 안 된다\n공성에 나선다!",
    "7:2314:0": "주변을 빼앗아라\n성은 그다음이다",
    "7:2315:0": "성을 고립시켜 무방비하게 만드는 게다\n우선 주변부터 확보하라!",
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
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S448", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
