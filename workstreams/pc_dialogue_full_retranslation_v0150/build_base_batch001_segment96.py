#!/usr/bin/env python3
"""Build Base authoring segment 96 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S96.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s96", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1537:0": "우리 가문이",
    "6:1537:1": (
        "와(과) 단교한 이상\n"
        "여러 나라도 우리를 가만두지 않을 것입니다.\n"
        "만전을 기해 대비해야 합니다"
    ),
    "6:1538:0": "여기서 단교를 택한 것은 묘수이오나\n",
    "6:1538:1": (
        "도 우리가 뜻대로 하도록 두고 보지는 않으려\n"
        "움직일 것입니다. 지금은 전쟁에 대비해야 합니다"
    ),
    "6:1539:0": "역시",
    "6:1539:1": "님,",
    "6:1539:2": (
        "와(과) 단교하여\n"
        "악평이 높아지더라도 뜻한 길을 가시다니,\n"
        "이래야 우리 가문의 주군이시지요"
    ),
    "6:1540:0": "일이 이렇게 된 이상\n",
    "6:1540:1": (
        "와(과)는 교섭할 수도 없습니다.\n"
        "아시겠지만, 일전을 치를 각오를 하십시오"
    ),
    "6:1541:0": "단교하면",
    "6:1541:1": (
        "의 감정은\n"
        "최악이라 해도 지나치지 않습니다.\n"
        "전쟁이 벌어져도 이상하지 않습니다"
    ),
    "6:1542:0": "이 난세에는 어쩔 수 없는 일이오나\n단교한다면",
    "6:1542:1": "은(는)\n우리를 용서하지 않겠지요",
    "6:1543:0": "단교한다면",
    "6:1543:1": (
        "이(가)\n"
        "전쟁을 걸어올지도 모릅니다.\n"
        "군량과 군마는 충분히 갖추셨는지요"
    ),
    "6:1544:0": (
        "와(과) 단교했으니\n"
        "전쟁이 벌어질 것으로 보아야 합니다.\n"
        "대비해 두어야겠지요"
    ),
    "6:1545:0": (
        "단교하면 이제 교섭은\n"
        "성립할 수 없으니, 전쟁 채비를\n"
        "염두에 두어야 합니다"
    ),
    "6:1546:0": "단교는 신의를 저버리는 일이오나\n",
    "6:1546:1": "따위와 함께 갈 수 없다는\n뜻은 충분히 납득하였사옵니다",
    "6:1547:0": (
        "와(과) 단교한 이상\n"
        "이를 도약의 발판으로 삼지 못하면\n"
        "여러 나라에 짓눌리고 말 것입니다"
    ),
    "6:1548:0": "이런 세상이니 어쩔 수 없다 생각하오나\n",
    "6:1548:1": (
        "와(과)의 단교는, 잘못 대응하면\n"
        "여러 다이묘의 신뢰를 잃게 될 것입니다"
    ),
    "6:1549:0": (
        "께서도 충분히 생각하셨으리라\n"
        "믿습니다만, 단교를 거듭하면\n"
        "악평이 높아질 수 있으니 조심하십시오"
    ),
    "6:1550:0": (
        "와(과) 단교하면\n"
        "외교가 어려워질 것입니다.\n"
        "병마를 정비해야 할 것입니다"
    ),
    "6:1551:0": (
        "와(과)의 단교라니, 이 난세에는\n"
        "신의 따위 필요 없다는 말씀이시군요.\n"
        "훌륭한 결단이오나 전쟁에 대비해야 합니다"
    ),
    "6:1552:0": "우리 가문이",
    "6:1552:1": (
        "와(과) 단교한 이상\n"
        "여러 나라도 우리를 가만두지 않을 터…\n"
        "만전을 기해 대비해야 한다"
    ),
    "6:1553:0": (
        "와(과) 단교한 이상\n"
        "앞으로 외교가 어려워질 것은 필연…\n"
        "병마를 정비해야 한다"
    ),
    "6:1554:0": "역시",
    "6:1554:1": "님,",
    "6:1554:2": (
        "와(과) 단교하여\n"
        "악평이 높아지더라도 뜻한 길을 가시다니…\n"
        "이래야 우리 가문의 주군이시지요"
    ),
    "6:1555:0": (
        "의 놈들, 우리를 배신하고도\n"
        "무사할 수 있으리라 여겼다면\n"
        "큰 착각임을 똑똑히 깨닫게 해 주마"
    ),
    "6:1556:0": (
        ", 이렇게 체면을 짓밟히고\n"
        "잠자코 있을 수는 없잖아!\n"
        "전쟁이다,"
    ),
    "6:1556:1": "에게 전쟁을 걸자고!",
}

DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS) - {"6:1545:0"}


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
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
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
                "segment": "base_msggame_B001_S96",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
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
