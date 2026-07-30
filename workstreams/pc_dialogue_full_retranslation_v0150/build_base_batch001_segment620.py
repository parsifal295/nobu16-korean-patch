#!/usr/bin/env python3
"""Build Base authoring segment 620 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S620.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s620", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1508:0": "으음―",
    "9:1508:1": "에게\n신세를 지게 되었나……",
    "9:1509:0": "도\n너무 무르구나……",
    "9:1510:0": "원호를 받은 건 사실이니……\n감사는 드리겠습니다",
    "9:1511:0": "흥―",
    "9:1511:1": "의\n도움 따위 필요 없다!",
    "9:1512:0": "……?\n내게 신경을 써 주다니……",
    "9:1513:0": "의 원호를\n받게 되다니……",
    "9:1514:0": "에게서 원호를 받다니?\n굴욕적이군요……",
    "9:1515:0": "원호라고?\n쓸데없는 짓을……",
    "9:1516:0": "의 도움인가!\n고맙군!",
    "9:1517:0": "!\n가세해 주어 고맙소!",
    "9:1518:0": "의 원호인가\n흥, 제법 세심하군",
    "9:1519:0": "원호 사격,\n감사드립니다",
    "9:1520:0": "!\n원호해 주어 고맙소",
    "9:1521:0": "원호 사격인가……\n고맙다고는 해 두지",
    "9:1522:0": "감사드립니다\n큰 도움이 되었습니다",
    "9:1523:0": "인가!\n오오, 살았구나!",
    "9:1524:0": "!\n지원에 감사드립니다!",
    "9:1525:0": "원호인가, 고맙군!",
    "9:1526:0": "원호 사격, 큰 도움이 됩니다",
    "9:1527:0": "!\n지원해 주어 고맙소!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1508:0",
    "9:1508:1",
    "9:1509:0",
    "9:1511:0",
    "9:1511:1",
    "9:1512:0",
    "9:1513:0",
    "9:1514:0",
    "9:1516:0",
    "9:1517:0",
    "9:1518:0",
    "9:1520:0",
    "9:1523:0",
    "9:1524:0",
    "9:1527:0",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S620", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
