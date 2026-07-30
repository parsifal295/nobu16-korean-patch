#!/usr/bin/env python3
"""Build Base authoring segment 100 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S100.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s100", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1618:0": "종속을 택한 심정이 참담하셨겠지만, 모든 것은\n이제부터입니다.",
    "6:1618:1": "을(를)\n잘 이용하여 판세를 헤쳐 나가십시오",
    "6:1619:0": (
        "에게 무릎을 꿇는 것은 치욕이지만,\n"
        "여러 나라를 적으로 돌리는 것보다는 낫습니다.\n"
        "산하에서 힘을 길러 앞날을 도모하십시오"
    ),
    "6:1620:0": (
        "에게 신종한 것이 아니라\n"
        "뒷배를 얻었다고 생각해야 합니다.\n"
        "전쟁이 나면 든든한 아군이 될 테니까요"
    ),
    "6:1621:0": (
        "에게 머리를 숙이는 굴욕만 견디면\n"
        "공격받을 때 원군을 기대할 수 있습니다.\n"
        "저들의 전쟁을 돕는 일도 우리 무명을 높인다고 생각하면…"
    ),
    "6:1622:0": "종속하면",
    "6:1622:1": (
        "이(가) 뜻하는 대로\n"
        "우리를 움직이겠지만, 지금은 참아 내며\n"
        "정사와 병마를 갈고닦아 위세를 높입시다"
    ),
    "6:1623:0": "종속하면 가문도 당분간은 평안할 것입니다.\n지금은",
    "6:1623:1": "의 아래에 서더라도\n",
    "6:1623:2": "님이라면, 언젠가 이 관계를 뒤집을 수 있습니다",
    "6:1624:0": "께서는",
    "6:1624:1": (
        "에게 종속하는 것을\n"
        "고뇌 끝에 결정하셨겠지만, 이것이\n"
        "두 가문을 위한 최선이기를 빕니다"
    ),
    "6:1625:0": (
        "에게 신종했으니 우리는\n"
        "그 가문의 수족처럼 움직여야 하지만,\n"
        "공격받을 때는 원군을 기대할 수 있습니다"
    ),
    "6:1626:0": (
        "에게 무릎을 꿇었으니\n"
        "우리는 그 산하에서 움직이게 됩니다.\n"
        "험난한 길이지만 지금은 견뎌야 합니다"
    ),
    "6:1627:0": "이야,",
    "6:1627:1": "와(과)",
    "6:1627:2": (
        "의\n"
        "혼례라니 참으로 경사로군.\n"
        "이제 두 가문은 한식구란 말이지!"
    ),
    "6:1628:0": "와(과)",
    "6:1628:1": (
        "의 결연,\n"
        "참으로 경사스러운 일입니다. 이로써 두 가문은\n"
        "굳은 유대로 맺어진 맹우가 되었군요"
    ),
    "6:1629:0": "와(과)",
    "6:1629:1": (
        "의 결연,\n"
        "참으로 경사스럽습니다. 우리 가문과도 연이 깊어져\n"
        "믿을 수 있는 집안이 되어 주겠지요"
    ),
    "6:1630:0": "와(과)",
    "6:1630:1": (
        "의 결연으로\n"
        "두 가문의 결속은 더없이 굳어졌고,\n"
        "우리 앞날도 밝아질 것입니다"
    ),
    "6:1631:0": "와(과)",
    "6:1631:1": (
        "의 혼인은\n"
        "우리 가문과 저 가문을 잇는 유대의 상징이지요.\n"
        "아니, 그 얘기는 나중에 하고 우선 잔치부터 열까요"
    ),
    "6:1632:0": "정략의 결과이긴 하지만,",
    "6:1632:1": "와(과)\n",
    "6:1632:2": "의 사이에 두 가문의\n앞날이 걸려 있습니다",
    "6:1633:0": "와(과)",
    "6:1633:1": (
        ", 두 사람의\n"
        "혼인은 두 가문의 유대를 굳건히 하여\n"
        "오래도록 이어지겠지요"
    ),
    "6:1634:0": "와(과)",
    "6:1634:1": (
        "의 혼례는\n"
        "두 가문의 결속을 여러 나라에 과시하기 위해서라도\n"
        "성대하게 치러야 합니다!"
    ),
    "6:1635:0": "와(과)",
    "6:1635:1": (
        "의 혼약이\n"
        "맺어졌으니, 두 가문은 이제\n"
        "한집안이자 맹우로서 함께 나아갈 것입니다"
    ),
    "6:1636:0": "어려운 얘기는 접어두고, 무엇보다 경사스러운 일입니다!\n",
    "6:1636:1": "와(과)",
    "6:1636:2": ", 이 두 사람을\n마음껏 축하하지 않겠습니까!",
    "6:1637:0": "와(과)",
    "6:1637:1": (
        "에게는\n"
        "정략을 잊고 행복하게 살기를 바랄 뿐입니다.\n"
        "두 가문이 다투는 일은 생각하고 싶지도 않습니다"
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
                "segment": "base_msggame_B001_S100",
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
