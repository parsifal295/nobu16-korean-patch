#!/usr/bin/env python3
"""Build Base authoring segment 95 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S95.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s95", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1517:0": "중개자가 없어,",
    "6:1517:1": "와(과)의 친선을 중지",
    "6:1518:0": " 와(과)의 친선 담당:",
    "6:1518:1": "\n거리가 너무 멀어 친선을 계속할 수 없게 됨",
    "6:1519:0": " 와(과)의 친선 담당:",
    "6:1519:1": "\n비용이 부족해 친선을 계속할 수 없게 됨",
    "6:1520:0": " 와(과)의 친선 담당:",
    "6:1520:1": "\n중개자가 없어",
    "6:1520:2": " 친선을 계속할 수 없게 됨",
    "6:1521:0": "의 신용이",
    "6:1521:1": "에 도달",
    "6:1522:0": "와(과)",
    "6:1522:1": "의 동맹이 종료",
    "6:1523:0": "와(과)",
    "6:1523:1": "의 정전이 종료",
    "6:1524:0": "의 원군 요청이 2개월 미만 남음",
    "6:1525:0": "비용이 부족하여 조정 헌금을 중지",
    "6:1526:0": "중개자가 없어 조정 헌금을 중지",
    "6:1527:0": "조정 헌금을 마치고 관직 추천 대기 중",
    "6:1528:0": (
        "와(과) 단교했으니, 그놈들이\n"
        "우리가 건방지다며 길길이 날뛰어 이쪽으로 병사를\n"
        "보내올지도 몰라"
    ),
    "6:1529:0": "우리가",
    "6:1529:1": (
        "을(를) 버린 거야.\n"
        "우리를 공격해 온다면 당연히 전쟁이\n"
        "벌어진다는 거지. 헤헤, 기대되는군"
    ),
    "6:1530:0": "이로써",
    "6:1530:1": (
        "와(과) 단교했습니다.\n"
        "우리를 내버려 두면 상대도 가문의 위신이\n"
        "서지 않을 테지요"
    ),
    "6:1531:0": (
        "을(를) 배신한 셈이 되었으니\n"
        "여러 나라가 우리를 보는 눈도 엄격해질 것입니다.\n"
        "당분간은 바깥 정세를 살펴야 하겠습니다"
    ),
    "6:1532:0": "이런 식으로",
    "6:1532:1": (
        "와(과)\n"
        "단교했다면, 여러 나라도 우리를\n"
        "신뢰할 수 없다며 엄중히 보겠지요"
    ),
    "6:1533:0": "부득이한 일이었다 해도, 단교한 이상\n",
    "6:1533:1": "도 체면이 서지 않을 테니,\n우리를 공격해 올지도 모릅니다",
    "6:1534:0": "단교했으니,",
    "6:1534:1": (
        "은(는)\n"
        "물론 여러 나라도 우리를 공격할지 모릅니다.\n"
        "전쟁 채비를 해 두는 것이 좋겠습니다"
    ),
    "6:1535:0": (
        "와(과) 단교했다면\n"
        "전쟁이 벌어질 수 있사옵니다.\n"
        "우리도 지금이 고비이옵니다"
    ),
    "6:1536:0": (
        "와(과) 단교했다면, 이제\n"
        "전쟁이 벌어지겠구려.\n"
        "후후후, 벌써부터 팔이 근질거리는군"
    ),
}

DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS)


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S95",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
