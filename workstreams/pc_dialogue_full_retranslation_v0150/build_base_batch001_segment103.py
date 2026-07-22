#!/usr/bin/env python3
"""Build Base authoring segment 103 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S103.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s103", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1678:0": "정책 변경을 확정합니다",
    "6:1679:0": "변경된 항목이 없습니다",
    "6:1680:0": "중개를 부탁한 세력과의 외교 자세가\n일시적으로 낮아지거나 더 오르지 않습니다\n계속하시겠습니까?",
    "6:1681:0": "와(과)의 교섭이 성립하면\n다른 가문이 보낸 원군은 활동을 중지합니다\n정말 계속하시겠습니까?",
    "6:1682:0": "와(과)의 외교 관계를 파기하면\n주변 세력의 불신과 가신의 충성 저하를 부를\n수 있습니다. 정말 계속하시겠습니까?",
    "6:1683:0": "에게 종속하는 건가?\n다른 곳과 맺은 관계는 전부 사라진다고.\n괜찮겠어?",
    "6:1684:0": "에게 종속하면\n다른 가문과의 외교 관계를 모두 잃습니다.\n깊이 생각한 뒤 결정하십시오",
    "6:1685:0": "에게 종속하면\n다른 가문과의 관계는 모두 해소된다…\n그래도 괜찮겠는가?",
    "6:1686:0": "에게 종속하면\n다른 세력과의 관계가 모두 해소됩니다.\n신중히 결단하십시오",
    "6:1687:0": "에게 종속하면\n다른 가문과 맺은 모든 약정을 잃습니다.\n괜찮으시겠습니까?",
    "6:1688:0": "종속하면 다른 가문과의 외교 관계가 해소됩니다.\n",
    "6:1688:1": "의 뜻에 이의는 없으나,\n그 점만은 유념해 주십시오",
    "6:1689:0": "종속하면 다른 가문과 외교할 수 없습니다.\n지금까지 맺은 관계도 모두 잃습니다.\n깊이 생각해 주십시오",
    "6:1690:0": "에게 종속하면\n다른 가문과의 관계는 모두 사라집니다.\n정녕 괜찮으시겠습니까?",
    "6:1691:0": "에게 종속하면\n다른 가문과의 외교 관계가 사라집니다.\n괜찮으시겠습니까…?",
    "6:1692:0": "에게 종속하면\n다른 세력과의 관계가 모두 사라지는군…",
    "6:1693:0": "에게 종속하면\n모든 외교 관계가 해소됩니다",
    "6:1694:0": "에게 종속하면,\n다른 가문과의 외교 관계가 모두 사라집니다.\n깊이 생각해 주십시오",
    "6:1695:0": "에게 종속하면\n다른 외교 관계는 모두 해소되고",
    "6:1695:1": "\n정말 그래도 괜찮겠",
    "6:1695:2": "습니까?",
    "6:1696:0": "칙명 강화는 워낙 큰일이라서 말이지.\n한번 쓰면 조정에서 다음 위계에 오를 때까지 못 써.\n…그렇다는데?",
    "6:1697:0": "칙명 강화를 한 번 행하면\n다음 위계에 오를 때까지 다시 쓸 수 없습니다.\n괜찮으시겠습니까?",
    "6:1698:0": "칙명 강화를 행하면\n다음 위계에 오를 때까지 다시 쓸 수 없습니다.\n부디 잊지 마십시오",
    "6:1699:0": "칙명 강화를 행하면\n다음 위계에 오를 때까지 다시 쓸 수 없습니다.\n유념해 주십시오",
    "6:1700:0": "칙명 강화를 지금 쓰시겠습니까?\n다시 쓸 수 있는 것은 위계가 오른 뒤입니다.\n그 점을 깊이 생각하십시오",
}

DYNAMIC_RUNTIME_COORDINATES = {
    *(f"6:{record_id}:0" for record_id in range(1681, 1688)),
    "6:1688:0",
    "6:1688:1",
    *(f"6:{record_id}:0" for record_id in range(1690, 1695)),
    "6:1695:0",
    "6:1695:1",
    "6:1695:2",
}


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
                "segment": "base_msggame_B001_S103",
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
