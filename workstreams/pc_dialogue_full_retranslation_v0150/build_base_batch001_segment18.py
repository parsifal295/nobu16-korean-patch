#!/usr/bin/env python3
"""Build Base authoring segment 18 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S18.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s18", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:516:0": "의 무용을 여기서 보이리라!\n자, 모두 기운을 내시오!",
    "2:517:0": "나의 힘을 똑똑히 보아라!",
    "2:518:0": "나의 힘을 똑똑히 보아라!",
    "2:519:0": "포위군이 마음대로 하게 두지 ",
    "2:519:1": "않겠다!\n우리도 ",
    "2:519:2": "반격하겠다!",
    "2:520:0": "나의 힘을 똑똑히 보아라!",
    "2:521:0": "성을 지키지 못한 것은 불찰!\n이리된 이상 적병에게 일격을 돌려주리라!",
    "2:522:0": "나의 힘을 똑똑히 보아라!",
    "2:523:0": "적의 모략은 미리 막는다.\n그것이 「",
    "2:523:1": "」의 방식이다……",
    "2:524:0": "나의 위광 앞에 무릎 꿇어라!",
    "2:525:0": "잔재주 따위 「",
    "2:525:1": "」에게는 통하지 않",
    "2:525:2": "!",
    "2:526:0": "의 농사 지식을\n이 땅에서 마음껏 펼치겠",
    "2:527:0": "대의 철포가 꿰뚫지 못할 것은 없다!",
    "2:528:0": "나의 동지들이여!\n가증스러운 적들을 몰아내자!",
    "2:529:0": "에게",
    "2:529:1": "\n진귀한 물건으로 신뢰를 쌓",
    "2:530:0": "가 수행하",
    "2:530:1": "\n진귀한 물건으로 신뢰를 쌓",
    "2:531:0": "의 힘이 되어 주도록\n다시 생각해 주지 않겠나?",
    "2:532:0": "원군을 보내 주다니 고맙소!\n",
    "2:532:1": "에게 힘을 보태 주시오!",
    "2:533:0": "에게는 스와의 가호가 있다!\n함께 천하를 노리",
    "2:534:0": "이 난세에 「",
    "2:534:1": "」은(는)\n타 가문과 함께 나아가야",
    "2:535:0": "맹우에게 칼을 겨눈 자들이여!\n우리가 모조리 쳐부숴 주마!",
    "2:536:0": "문무를 겸비한 내 재능을\n이 땅에서 펼쳐 보이겠다.",
    "2:537:0": "은(는),",
    "2:537:1": "의\n지략을 떠받치는 기둥이 되",
    "2:538:0": "이 땅을 풍요롭게 만들기 위해\n백성에게 힘을 다하겠다.",
    "2:539:0": "이(가) 적성을 함락해 보이겠",
    "2:540:0": "이 귀신",
    "2:540:1": "\n이 정도 열세쯤은 아무것도 아니다!",
    "2:541:0": "울부짖어라, 돈보키리!\n이 열세 속에서 나의 무용을 보이리라!",
    "2:542:0": "적은 이름난 맹장,",
    "2:542:1": "\n상대로서 부족함은",
    "2:542:2": "없다!",
    "2:543:0": "적은 이름난 맹장,",
    "2:543:1": "\n지략을 다해 승기를 잡겠",
    "2:544:0": "의 충성을 결코 잊지 않",
    "2:544:1": "……\n부디 편히 잠들기를.",
    "2:545:0": "뇌신이여……\n이 열세를 뒤집을 가호를 내리소서!",
    "2:546:0": "이 정도는 불리한 축에도 들지 않는다.\n여기는 「",
    "2:546:1": "」이(가) 십자창으로 만회하리라!",
    "2:547:0": "적이 병력으로는 우세한가!\n하, 창의 마타자가 진면목을 보일 때로군!",
    "2:548:0": "잡병들아, 길을 비켜라!\n이 귀신",
    "2:548:1": ", 전장을 누비리라!",
    "2:549:0": "병사의 많고 적음은 사소한 일.\n계책이 많으면 이기고 적으면 질 뿐이다.",
    "2:550:0": "열세인가……\n내 계책으로 무너뜨려 보이겠",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1])
    in {516, 519, 523, 525, 526, 527, 529, 530, 531, 532, 533, 534, 536, 537, 538, 539, 540, 542, 543, 544, 546, 548, 550}
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
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
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
                "segment": "base_msggame_B001_S18",
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
