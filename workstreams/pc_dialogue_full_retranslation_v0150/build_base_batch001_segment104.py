#!/usr/bin/env python3
"""Build Base authoring segment 104 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S104.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s104", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1701:0": "칙명 강화는 한 번 행하면\n다음 위계에 오를 때까지 다시 쓸 수 없습니다… 아니,\n알고 계시다는 것은 잘 압니다",
    "6:1702:0": "칙명 강화는 강력하지만 제약도 엄격합니다.\n지금 쓰면 다음 위계에 오른 뒤에야 다시 쓸 수 있지요…\n아니, 공자 앞에서 문자를 쓴 격이군요",
    "6:1703:0": "흠, 칙명 강화라…\n지금 써야 할지 깊이 생각하십시오.\n한번 쓰면 다음 위계에 오른 뒤에야 다시 쓸 수 있으니",
    "6:1704:0": "칙명 강화를 한 번 행하면\n다음 위계에 오를 때까지 다시 쓸 수 없습니다",
    "6:1705:0": "칙명 강화를 행하면\n다음 위계에 오를 때까지 다시 쓸 수 없다.\n그래도 괜찮으신가?",
    "6:1706:0": "칙명 강화를 사용하면\n다음 위계에 오를 때까지 다시 쓸 수 없습니다.\n잊지 마십시오",
    "6:1707:0": "칙명 강화를 한 번 행하면\n다음 위계에 오를 때까지 다시 쓸 수 없습니다.\n괜찮으시겠습니까?",
    "6:1708:0": "일방적으로 단교하겠다는 거지… 평판이 나빠질걸?\n앞으로 여러모로 일이 어려워지겠지만,\n그래도 할 건가?",
    "6:1709:0": "아니, 잠시 기다리십시오!\n신의는 무가가 서는 근본입니다!\n단교로 우리 가문에 악명이 퍼지면 어찌하시렵니까!",
    "6:1710:0": "일방적으로 맹약을 깨면\n나쁜 소문이 퍼질 것은 필연…\n다시 한번 깊이 생각하십시오",
    "6:1711:0": "이익 없는 맹약이라 해도 파기하면\n그에 걸맞은 악명이 따를 것입니다.\n주의하십시오",
    "6:1712:0": "단교하면 악명을 피할 수 없습니다.\n여러모로 곤란해질 것입니다만,\n어찌하시겠습니까?",
    "6:1713:0": "이익 없는 맹약은 일방적으로 끊어도 마땅하오나,\n세상 사람들은 우리 가문의 악명을 퍼뜨릴 것입니다.\n그것이 훗날 족쇄가 될지도 모릅니다…",
    "6:1714:0": "대의가 주군께 있음은 지당하오나,\n입 사나운 세상 사람들은 흠을 잡을 것입니다.\n악명이 앞날에 걸림돌이 될 터인데…",
    "6:1715:0": "일방적으로 단교하면 세상이 비난하겠지요.\n하지만 악명을 뒤집어쓰고서라도 해야 할 일은 있는 법.\n이번에는 어찌하시겠습니까?",
    "6:1716:0": "일방적인 동맹 파기는 불의로 여겨져\n세간에 악명이 퍼지고 맙니다.\n깊이 검토해 주십시오",
    "6:1717:0": "불필요한 동맹이라도 단교하면\n악명이 퍼지게 됩니다.\n주의하십시오",
    "6:1718:0": "동맹을 파기하면 나쁜 소문이 돕니다.\n명예와 눈앞의 이익 중 어느 쪽을 택할지,\n깊이 생각해 보십시오",
    "6:1719:0": "일방적인 단교는 악명의 근원입니다.\n권할 수는 없습니다만,\n그래도 맹약을 파기하시겠습니까?",
    "6:1720:0": "우리 가문의 부대가",
    "6:1720:1": "의 영내에 있으므로,\n지금 단교하면 악명이 크게 높아집니다.\n정말 계속하시겠습니까?",
    "6:1721:0": "겉으로나마 따랐는데 배신하면 악명이 퍼질걸.\n다른 곳과의 관계도 어떻게 될지 모르고…\n아무튼 신중히 생각해야 할 일이야",
    "6:1722:0": "한번 비호를 청한 상대를 버리다니 불의입니다!\n천하에 악명이 퍼질 것입니다!\n무사의 긍지가 이를 옳다고 하십니까?",
    "6:1723:0": "주군을 바꾸면 악명이 퍼집니다.\n은혜를 원수로 갚는 것이나 다름없으니…\n각오는 되어 있으십니까?",
    "6:1724:0": "주군을 바꾸면 악명이 퍼지고\n외교에도 나쁜 영향을 미칠 것입니다…\n어찌하시겠습니까?",
    "6:1725:0": "주군을 바꾸면 악명이 퍼져\n여러모로 곤란해집니다.\n각오하셔야 합니다",
    "6:1726:0": "시세에 따라 따랐을 뿐이니,\n시세에 따라 버린들 무슨 문제가 있겠소.\n다만 악명이 퍼지는 것은 뼈아프겠구려",
    "6:1727:0": "주군을 바꾸면 우리 가문의 악명이 퍼져\n외교에도 나쁜 영향을 미칠 것입니다.\n유념해 주십시오",
    "6:1728:0": "주군을 바꾸면 악명이 퍼져 고생할 것이다.\n하지만 내가 살아오며 배운 것은\n누구도 영원히 변하지 않을 수는 없다는 것이지",
    "6:1729:0": "그 가문을 저버리면 악명이 퍼집니다.\n외교에도 영향을 미치니,\n주의하십시오",
    "6:1730:0": "그 일은 악명의 근원이 될 것입니다.\n외교에도 나쁜 영향을 미치니,\n상황을 깊이 고려하십시오",
    "6:1731:0": "주군을 바꾸는 일을 누구도 좋게 보지는 않을 것입니다.\n세간의 미움을 받더라도 밀고 나갈\n각오가 필요합니다",
    "6:1732:0": "아니, 한 말씀 아뢰겠습니다.\n종속하던 가문을 배신하면 악명이 퍼져\n다른 가문과의 외교에도 지장을 줍니다",
    "6:1733:0": "혼인할 무장이나 공주를 선택하십시오",
    "6:1734:0": "혼인할 무장과 공주가 선택되지 않았습니다",
    "6:1735:0": "와(과)\n단교시킬 세력을 선택하십시오",
    "6:1736:0": "이 세력과",
    "6:1736:1": "의\n단교를 지시합니다",
    "6:1737:0": "와(과)\n정전시킬 세력을 선택하십시오",
    "6:1738:0": "이 세력과",
    "6:1738:1": "의\n정전을 지시합니다",
    "6:1739:0": "의 표적이 될\n세력을 선택하십시오",
    "6:1740:0": "이 세력을",
    "6:1740:1": "의 표적으로 지정합니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "6:1720:0",
    "6:1720:1",
    "6:1735:0",
    "6:1736:0",
    "6:1736:1",
    "6:1737:0",
    "6:1738:0",
    "6:1738:1",
    "6:1739:0",
    "6:1740:0",
    "6:1740:1",
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
                "segment": "base_msggame_B001_S104",
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
