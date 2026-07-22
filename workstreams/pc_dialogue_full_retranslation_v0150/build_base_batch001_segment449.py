#!/usr/bin/env python3
"""Build Base authoring segment 449 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S449.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s449", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2316:0": "성 주변에 부대를 배치하라\n한 걸음씩 착실히 나아가자",
    "7:2317:0": "성을 치기 전에 기반을 다져라\n주변 지역을 제압하라!",
    "7:2318:0": "공격로를 확보하고\n공성에 나서겠다",
    "7:2319:0": "주변을 확보하라\n성은 그다음에 치면 된다",
    "7:2320:0": "발판을 확보하라\n주변 영토를 빼앗는 게다",
    "7:2321:0": "공성에 앞서\n주변에 부대를 배치해야 하오",
    "7:2322:0": "공성이다! 우선은\n주변부터 에워싸자",
    "7:2323:0": "진군을 개시하라!\n주변을 장악하라!",
    "7:2324:0": "먼저 성을 고립시킨다\n주변을 확보하라!",
    "7:2325:0": "주변 지역을 확보하여\n발판을 다지겠습니다",
    "7:2326:0": "공성이다!\n성 주변으로 향하라!",
    "7:2327:0": "공격에 앞서 주변을\n장악해 두어야겠군",
    "7:2328:0": "공성전을 벌인다\n먼저 발판을 확보하라",
    "7:2329:0": "우선 성을 고립시켜 무방비하게 만든다!\n주변을 확보하라!",
    "7:2330:0": "성 공략에 앞서\n주변에서 대기하겠습니다",
    "7:2331:0": "진군하라!\n먼저 주변의 군으로 향하라",
    "7:2332:0": "공성에 앞서\n발판을 확보하겠습니다",
    "7:2333:0": "성을 고립시켜라!\n먼저 주변의 군으로 향하라",
    "7:2334:0": "포위가 완성될 때까지\n",
    "7:2334:1": "에서 대기한다",
}

STATIC_COORDINATES = {f"7:{record_id}:0" for record_id in range(2316, 2334)}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S449", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
