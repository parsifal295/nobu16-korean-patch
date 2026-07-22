#!/usr/bin/env python3
"""Build Base authoring segment 94 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S94.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s94", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1497:0": "의 방어 원군 요청을 달성",
    "6:1498:0": "이(가) 방어 원군 요청을 달성",
    "6:1499:0": "의 원군 요청을 취소",
    "6:1500:0": "이(가) 원군 요청을 취소",
    "6:1501:0": "에 파견한 공략 원군이 궤멸",
    "6:1502:0": "의 공략 원군이 궤멸",
    "6:1503:0": "에 파견한 방어 원군이 궤멸",
    "6:1504:0": "의 방어 원군이 궤멸",
    "6:1505:0": "와(과)의 동맹이 2개월 미만 남음",
    "6:1506:0": "기한 만료로",
    "6:1506:1": "와(과)의 동맹이 종료",
    "6:1507:0": "에 대한 원군 요청이 2개월 미만 남음",
    "6:1508:0": "공성전 중이므로",
    "6:1508:1": "에 대한 원군 요청이 연장",
    "6:1509:0": "와(과)의 정전이 2개월 미만 남음",
    "6:1510:0": "기한 만료로",
    "6:1510:1": "와(과)의 정전이 종료",
    "6:1511:0": "와(과)의 우호도가 상승",
    "6:1512:0": "의 외교 자세가",
    "6:1512:1": "으로(로) 변경",
    "6:1513:0": "의 신용이 하락",
    "6:1514:0": "의 외교 자세가",
    "6:1514:1": "으로(로) 변경",
    "6:1515:0": "거리가 멀어져",
    "6:1515:1": "와(과)의 친선을 중지",
    "6:1516:0": "비용이 부족하여",
    "6:1516:1": "와(과)의 친선을 중지",
}

DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS)


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append({"schema":ENGINE.DECISION_SCHEMA,"resource":"base_msggame","coordinate":coordinate,"source_record_raw_sha256":target["source_record_raw_sha256"],"current_ko_utf16le_sha256":target["current_ko_utf16le_sha256"],"translation":translation,"semantic_review":"approved","scope_classification":"runtime_fragment_pending","layout_review":"unchanged_from_current","runtime_review":"pending","basis":"pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available","historic_korean_used":False,"switch_korean_used":False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status":"ok","segment":"base_msggame_B001_S94","decision_count":len(rows),"retranslated":0,"dynamic_runtime_review_pending":len(rows),"steam_write_performed":False,"output":str(OUTPUT)},ensure_ascii=True,separators=(",",":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
