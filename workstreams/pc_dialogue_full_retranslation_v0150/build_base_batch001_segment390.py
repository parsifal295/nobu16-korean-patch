#!/usr/bin/env python3
"""Build Base authoring segment 390 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S390.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s390", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1380:0": "로 쳐들어간다\n바람처럼 빠르게 몰아쳐라!",
    "7:1381:0": "의 수비는 바위와도 같으니\n한발 앞서 움직여 계책을 세우는 것이 좋을 듯하오",
    "7:1382:0": "을(를) 함락하려면\n신속하고 과감하게 공격해야 하리라",
    "7:1383:0": "보다 앞서 움직인다면\n취할 수 있는 계책도 늘어날 것입니다",
    "7:1384:0": "의 수비는 견고하니\n샛길을 지나 허를 찌를 수밖에 없겠군",
    "7:1385:0": "에 도전하려면\n먼저 움직여 정보를 얻어야 하겠소",
    "7:1386:0": "와(과)의 승산은 반반\n기선을 제압하는 것이 승리의 길인가",
    "7:1387:0": "을(를) 함락하려면\n우리도 서둘러 움직여야 하옵니다",
    "7:1388:0": "을(를) 함락할 승산은 반반\n뒤늦게 움직이면 일을 그르칠 것이옵니다",
    "7:1389:0": "에 도전한다면\n적보다 먼저 움직여 두자고",
    "7:1390:0": "은(는) 만만한 상대가 아니야\n지름길로 단숨에 끝내 주마!",
    "7:1391:0": "의 수비는 견고하군요\n먼저 움직이면 유리해질 것이옵니다",
    "7:1392:0": "의 정면 돌파는 어렵다\n기선을 제압해 유리하게 움직여야 한다",
    "7:1393:0": "은(는) 견고하다 하옵니다\n부디 뒤늦게 움직이는 일이 없도록",
    "7:1394:0": "을(를) 공격하려면\n선수를 쳐 적의 기세를 꺾어야 하오",
    "7:1395:0": "은(는) 정면 승부를 벌이기보다\n한발 앞서 기책으로 맞서는 것이 상책일 듯하옵니다",
    "7:1396:0": "은(는) 함락하기 어려운 성\n선수를 잡지 않으면 고전은 피할 수 없소",
    "7:1397:0": "을(를) 함락하려거든\n적보다 빨리 움직여 포위하시는 것이 좋소",
    "7:1398:0": "에는 정예병이 포진했다 들었소\n선수를 쳐 싸움을 유리하게 이끌어야 하오",
    "7:1399:0": "이(가) 계책을 쓰기 전에\n재빨리 공격해 들어가는 것이 필승의 길이옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S390", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
