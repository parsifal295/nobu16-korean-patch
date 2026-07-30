#!/usr/bin/env python3
"""Build Base authoring segment 97 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S97.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s97", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1557:0": (
        "놈, 단교하다니!\n"
        "우리 가문을 우롱한 처사입니다. 이럴 때는\n"
        "그 무리를 응징해야 합니다"
    ),
    "6:1558:0": "단교라니, 우리 가문을 얕보았구나.\n",
    "6:1558:1": (
        "에게는 전쟁에서 내 무용을 떨쳐\n"
        "우리 가문의 위세를 똑똑히 보여 주겠습니다"
    ),
    "6:1559:0": (
        "의 놈들, 감히 단교하다니\n"
        "언어도단이자 용서할 수 없는 짓입니다.\n"
        "응분의 대가를 치르게 해야 합니다"
    ),
    "6:1560:0": (
        "이(가) 단교를 선언했다고 합니다.\n"
        "이를 내버려 두면 다른 가문에도\n"
        "얕보일 수 있습니다"
    ),
    "6:1561:0": (
        "이(가) 우리 가문과 단교했다고 합니다.\n"
        "실로 중대한 사태이니, 서둘러\n"
        "토벌해야 할 것입니다"
    ),
    "6:1562:0": "합종연횡이 난세의 이치라 하나, 이번\n",
    "6:1562:1": "의 배신은 신의를 저버린\n행위이니, 반드시 주벌해야 합니다",
    "6:1563:0": (
        "놈이 단교했다니!\n"
        "우리 가문의 이름에 먹칠한 대가를\n"
        "치르게 해야 분이 풀리겠습니다"
    ),
    "6:1564:0": "이렇게 된 이상",
    "6:1564:1": (
        "의 무리\n"
        "뿐만 아니라, 우리를 배신하면 어떤\n"
        "꼴이 되는지 여러 나라에 보여 줘야 하오!"
    ),
    "6:1565:0": "이때 단교하다니",
    "6:1565:1": (
        "도 어리석구나.\n"
        "이제 우리 가문이 그놈들을 어떻게 다루든\n"
        "누구도 불평하지 못할 것이다"
    ),
    "6:1566:0": (
        "이(가) 우리 가문의 산하를 떠나다니,\n"
        "과연 살아남을 수 있으려나… 다만\n"
        "망하기 전에 대가는 치르게 해야지"
    ),
    "6:1567:0": "우리 가문에서",
    "6:1567:1": (
        "이(가) 떠난다니, 참으로\n"
        "얕보인 모양입니다.\n"
        "우리의 힘을 보여 줘야 하겠습니다"
    ),
    "6:1568:0": "흠, 우리 가문이",
    "6:1568:1": (
        "따위에게\n"
        "얕보일 까닭은 없습니다.\n"
        "군사를 내서라도 짓눌러야 합니다"
    ),
    "6:1569:0": "이놈,",
    "6:1569:1": "! 우리를\n배신한 대가는 톡톡히\n치르게 해야겠구나",
    "6:1570:0": (
        "따위가 우리 가문에 반기를 들다니.\n"
        "이를 용서하면 위신이 서지 않으니\n"
        "군사를 내서라도 제압해야 합니다"
    ),
    "6:1571:0": "우리 가문이 내민 손을 뿌리치다니,\n",
    "6:1571:1": "의 소행은 용서할 수 없습니다.\n어떻게든 대가를 치르게 합시다",
    "6:1572:0": "우리 가문의 산하에 있던",
    "6:1572:1": (
        "이(가)\n"
        "단교 같은 짓을 저지르다니.\n"
        "내버려 두면 후환이 될 것입니다"
    ),
    "6:1573:0": (
        "이(가) 반기를 들다니 가소롭군.\n"
        "이런 불의를 엄히 다스리지 않으면\n"
        "주변 여러 나라도 잠자코 있지 않을 것이다"
    ),
    "6:1574:0": "단교한 배신자에게는\n벌을 내려야 도리가 설 것입니다.\n",
    "6:1574:1": "따위는 공격해 점령해야 합니다",
    "6:1575:0": "참으로 유감스럽게도",
    "6:1575:1": (
        "이(가)\n"
        "우리 가문의 산하에서 이탈했습니다.\n"
        "우리가 미덥지 못했던 것일까요…"
    ),
    "6:1576:0": "이(가) 단교했다는 것은,",
    "6:1576:1": (
        "께서\n"
        "얕보였다는 뜻입니다.\n"
        "이것만은 용서할 수 없겠군요…"
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
                "segment": "base_msggame_B001_S97",
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
