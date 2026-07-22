#!/usr/bin/env python3
"""Build Base authoring segment 99 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S99.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s99", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1598:0": "우선 경사스러운 일이오나,",
    "6:1598:1": (
        "을(를)\n"
        "산하에 들인 것으로 끝은 아니겠지요.\n"
        "그 가문을 써서 무엇을 하실 생각입니까"
    ),
    "6:1599:0": "우리 가문에 무릎을 꿇은",
    "6:1599:1": (
        "은(는)\n"
        "앞으로 우리의 검이 되겠지만,\n"
        "우리도 그들의 방패가 되어야 합니다"
    ),
    "6:1600:0": (
        "이(가) 산하에 들었다는 것은\n"
        "그들은 우리 자식, 우리는 그들의 부모와 같다는 뜻.\n"
        "자식과 부모가 서로를 위해 힘쓰는 것이 도리입니다"
    ),
    "6:1601:0": (
        "이(가) 우리 가문에 종속했습니다.\n"
        "우리의 수족처럼 부릴 수 있겠지만,\n"
        "수족을 지키는 것도 머리의 소임이지요"
    ),
    "6:1602:0": "우리 가문에 종속한",
    "6:1602:1": (
        "이지만,\n"
        "전쟁에 도움이 되는 것은 분명하되, 자칫하면\n"
        "전쟁의 불씨가 될 수도 있습니다"
    ),
    "6:1603:0": (
        "의 휘하에 드는 건 분하지만,\n"
        "우리가 약한 탓이란 거겠지.\n"
        "그렇다면 놈들보다 강해지는 수밖에 없어"
    ),
    "6:1604:0": (
        "을(를) 따르며 그놈들한테 턱짓으로\n"
        "부림당하는 건 참을 수 없지만 말이야.\n"
        "나쁜 점만 있는 건 아니겠지?"
    ),
    "6:1605:0": "내 힘이 모자라, 원통하게도",
    "6:1605:1": (
        "에게\n"
        "무릎을 꿇게 되었지만,\n"
        "지금은 힘을 기르고 벼리는 수밖에 없습니다"
    ),
    "6:1606:0": (
        "에게 종속했으니\n"
        "전쟁이 나면 우리의 뒷배가 되겠지만,\n"
        "저들의 전쟁에도 끌려 나가게 될 것입니다"
    ),
    "6:1607:0": "우리는 지금 약자의 처지이니,",
    "6:1607:1": "에게\n신종하여 시간을 버는 동안\n힘을 길러야 할 것입니다",
    "6:1608:0": "한번 따르기로 한 이상,",
    "6:1608:1": (
        "에게는\n"
        "예절과 신의를 보이며 충성을 다해야 합니다.\n"
        "단교하면 악평이 퍼질 것입니다"
    ),
    "6:1609:0": (
        "에게 종속했다고 해서\n"
        "위축될 필요는 없습니다.\n"
        "그 가문을 창과 방패로 삼아 우리 힘을 키우는 데 쓰십시오"
    ),
    "6:1610:0": "종속은 일방적으로 따르는 관계가 아닙니다.\n",
    "6:1610:1": "와(과) 운명을 함께할 각오를 하되,\n우리도 스스로 서야 합니다",
    "6:1611:0": "다른 가문의 아래에 서는 건 성미에 맞지 않지만,\n",
    "6:1611:1": "와(과) 우리 가문은 힘의 차이가\n너무 크니, 어쩔 수 없는 일입니다",
    "6:1612:0": "에게",
    "6:1612:1": (
        "께서 머리를 숙이게 된 것은\n"
        "우리의 힘이 부족했기 때문입니다.\n"
        "이 쓰라림을 잊지 않고 정진하겠습니다"
    ),
    "6:1613:0": "신종의 굴욕은 언젠가",
    "6:1613:1": "에게\n배로 갚기로 하고, 지금은 그들을\n이용할 방도를 생각하시지요",
    "6:1614:0": "머리 한 번 숙이는 것만으로",
    "6:1614:1": (
        "을(를) 우리 가문의\n"
        "방패로 삼으시다니 묘안이십니다. 우리 힘을\n"
        "감출 좋은 눈속임으로 써 보시지요"
    ),
    "6:1615:0": "약한 자가 먹히는 난세이니, 지금\n",
    "6:1615:1": "에게 종속하는 것은 어쩔 수 없습니다.\n하지만 여기서 끝은 아닙니다",
    "6:1616:0": "에게 종속한 뒤 우리 가문이\n쇠락할지, 아니면 도약할지는\n",
    "6:1616:1": "께 달렸습니다",
    "6:1617:0": "강한 자를 따르는 건 난세의 이치이고, 이는\n분명합니다. 하지만",
    "6:1617:1": "도 언젠가는\n성자필쇠, 그때를 대비해야 합니다",
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
                "segment": "base_msggame_B001_S99",
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
