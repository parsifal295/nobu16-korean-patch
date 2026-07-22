#!/usr/bin/env python3
"""Build Base authoring segment 98 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S98.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s98", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1577:0": (
        "놈, 단교하다니\n"
        "용서할 수 없는 짓이다. 반드시 그 대가를\n"
        "치르게 해야 하겠구나"
    ),
    "6:1578:0": (
        "이(가) 우리 가문과 단교했습니다.\n"
        "이 배신의 대가는 전쟁을 벌여서라도\n"
        "치르게 해야 합니다"
    ),
    "6:1579:0": (
        "이(가) 종속했다는 건\n"
        "그놈들이 우리 부하가 됐단 소리지.\n"
        "실컷 부려먹자고"
    ),
    "6:1580:0": "종속했다는 건",
    "6:1580:1": (
        "이(가)\n"
        "공격받으면 도와줘야 한다는 거지?\n"
        "짐만 안 되면 좋겠는데 말이야"
    ),
    "6:1581:0": "우리의 무용 앞에",
    "6:1581:1": (
        "이(가)\n"
        "무릎을 꿇었다고 합니다.\n"
        "이제 함께 나아갈 사이가 된 것입니까"
    ),
    "6:1582:0": "우리에게 종속한",
    "6:1582:1": (
        "은(는)\n"
        "뜻대로 움직일 수 있겠지만,\n"
        "배려하지 않으면 원한을 살 수 있습니다"
    ),
    "6:1583:0": (
        "이(가) 우리 가문에 종속했으니\n"
        "우리는 한 몸이 되어 함께 싸우고\n"
        "함께 나아가는 동포가 된 것이군요"
    ),
    "6:1584:0": "우리 가문에 종속했다고 해서",
    "6:1584:1": "은(는)\n저처럼",
    "6:1584:2": "의 가신은 아닙니다.\n대우에 신경 써야 하겠지요",
    "6:1585:0": (
        "의 종속으로 우리 세력이\n"
        "커진 것이나 다름없지만, 적도 늘었다고\n"
        "생각해야 합니다. 조심해야 합니다"
    ),
    "6:1586:0": (
        "이(가) 우리에게 굴복했다 해도\n"
        "멸망한 것은 아닙니다. 단교를\n"
        "생각지 못하도록 단단히 고삐를 쥐어야 합니다"
    ),
    "6:1587:0": "말재주만으로",
    "6:1587:1": (
        "을(를) 굴복시키시다니,\n"
        "과연 대단하십니다.\n"
        "저 같은 무인은 좀처럼 해내지 못할 일입니다"
    ),
    "6:1588:0": "흠,",
    "6:1588:1": (
        "이(가) 우리 가문에 종속했다고.\n"
        "그렇다면 그들과 말고삐를 나란히 하고\n"
        "무공을 겨루겠군. 벌써 팔이 근질거리는구려"
    ),
    "6:1589:0": (
        "의 종속, 참으로 경사스러운 일입니다.\n"
        "그들의 힘을 마음껏 활용하여\n"
        "앞으로 판세를 헤쳐 나가고 싶군요"
    ),
    "6:1590:0": "후후, 이제부터는",
    "6:1590:1": (
        "을(를)\n"
        "살리고 죽이는 것 모두 우리 가문의\n"
        "마음먹기에 달렸군요"
    ),
    "6:1591:0": (
        "이(가) 우리에게 항복한 이상\n"
        "우리는 일심동체이니, 뜻과\n"
        "지향하는 바도 하나로 모아야 합니다"
    ),
    "6:1592:0": "우리에게 종속하다니,",
    "6:1592:1": (
        "의 자들도\n"
        "보는 눈이 있군요. 그 기대에는\n"
        "우리도 부응해야 하겠습니다"
    ),
    "6:1593:0": "설마",
    "6:1593:1": (
        "이(가) 우리 가문에 복종할 줄은\n"
        "젊었을 때는 생각지도 못했지.\n"
        "오래 살고 볼 일이로구나"
    ),
    "6:1594:0": (
        "은(는) 이제 우리의\n"
        "수족처럼 움직이겠지만, 뒤로는\n"
        "발톱과 이빨을 갈고 있을지도 모릅니다"
    ),
    "6:1595:0": "종속한 이상,",
    "6:1595:1": (
        "은(는)\n"
        "이제 우리가 뒷받침하여 더욱\n"
        "강해지게 해야겠지요"
    ),
    "6:1596:0": (
        "이(가) 우리 가문에 종속했지만\n"
        "그들은 우리의 힘을 이용하려는 것\n"
        "뿐일지도 모릅니다. 조심하십시오"
    ),
    "6:1597:0": "종속시킨",
    "6:1597:1": (
        "은(는) 쉽사리\n"
        "버릴 수 없습니다. 산하에 들인 이상\n"
        "서로 맡은 바를 다해야 합니다"
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
                "segment": "base_msggame_B001_S98",
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
