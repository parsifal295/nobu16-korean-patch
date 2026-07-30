#!/usr/bin/env python3
"""Build Base authoring segment 19 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S19.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s19", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:551:0": "열세야말로\n내 책모가 진가를 발휘할 무대다!",
    "2:552:0": "적은 「",
    "2:552:1": "」!\n바로 여기서 쳐부숴 주겠",
    "2:552:2": "!",
    "2:553:0": "나무아미타불……\n지금이야말로 불적에게 벌을 내리리라!",
    "2:554:0": "나왔는가, 군신……\n내 지휘로 이 악연을 끊어 주마!",
    "2:555:0": "왔는가, 나의 숙적이여!\n자, 마음껏 자웅을 겨뤄 보자!",
    "2:556:0": "의",
    "2:556:1": "무운을\n삼가 빌어 드리겠",
    "2:557:0": "배웅해 주셔서 감사하",
    "2:557:1": ".\n좋은 소식을 기다려 주시오.",
    "2:558:0": "서방님의 무운을\n계속 빌고 있을게요.",
    "2:559:0": "맡겨 둬!\n",
    "2:559:1": "은(는) 더 크게 출세할 테니까!",
    "2:560:0": "사랑하는",
    "2:560:1": ", 잘 있거라",
    "2:560:2": "……",
    "2:561:0": ", 안심하",
    "2:561:1": "……\n우리 가문의 앞날은 이",
    "2:561:2": "이(가)\n끝까지 지켜보겠",
    "2:562:0": "사랑하는",
    "2:562:1": ", 잘 있거라",
    "2:562:2": "……",
    "2:563:0": "오합지졸 따위는 두려워할 것 없다.\n천운은 이 「",
    "2:563:1": "」의 손안에 있다!",
    "2:564:0": "이 정도 열세는",
    "2:564:1": "이(가) 뒤집어 보이겠다!\n이곳을 출세의 발판으로 삼을 테다!",
    "2:565:0": "평온한 세상을 이루기 위해서라면……\n이 주베에, 손을 더럽히는 것도 마다하지 않겠다.",
    "2:566:0": "살무사의 궤계……\n실컷 맛보고 가거라!",
    "2:567:0": "적은 다수다!\n미카와 무사의 기개를 보일 때는 지금이다!",
    "2:568:0": "적도 아군도 똑똑히 보아라!\n이 독안룡이 웅비하는 모습을!",
    "2:569:0": "우리 결사의 붉은 갑옷 군단……\n열세를 뒤집으리라!",
    "2:570:0": "병력 차 따위 지모로 뒤집는다.\n그것이 「",
    "2:570:1": "」의 싸움이지.",
    "2:571:0": "열세는 분명하다.\n이를 어떻게 버텨 낼 것인가……!",
    "2:572:0": "죽음을 각오하고 싸우면 살고,\n살고자 싸우면 반드시 죽는다……\n전군, 목숨을 내게 맡겨라!",
    "2:573:0": "수로 우리를 누를 수 있으리라 생각했느냐?\n",
    "2:573:1": "도 얕보였군.",
    "2:574:0": "이런이런, 대군을 끌고 오느라 수고했군.\n자…… 어떤 수를 써 볼까?",
    "2:575:0": "강대한 적을 맞으면 죽음을 각오하고 반드시 이겨야 한다!\n천하에 우리의 용맹을 보여라!",
    "2:576:0": "적이 병력으로 우세한가.\n한 수의 실수도 없이 신중한 계책으로 이기리라.",
    "2:577:0": "대적이라 한들 무엇이 두려우랴.\n오니와코의 창이 꿰뚫지 못할 것은 없다!",
    "2:578:0": "적귀의 군세에 숫자만 믿는 자는 필요 없다.\n자, 혈로를 뚫어라!",
    "2:579:0": "『돌아갈 수 없는 흉일』이라는 말이 참이었나.\n……물론 강적을 모조리 쓰러뜨리고\n출세해 다시 돌아갈 필요가 없다는 뜻이지!",
    "2:580:0": "모두, 당황하지 마라.\n내 눈에는 호랑이보다 강한 적으로 보이지 않는다.",
    "2:581:0": "싸움은 병력의 많고 적음으로 결정되지 않는다.\n병사들을 하나로 뭉쳐 대세를 뒤집으리라!",
    "2:582:0": "적은 마왕인가……\n이 한판으로 아버지를 뛰어넘어 보이겠다!",
    "2:583:0": "적을 천하의 얼간이라 얕보지 마라.\n우리는 우리 방식으로 이길 뿐이다.",
    "2:584:0": "얼간이인가, 걸물인가……\n직접 가려보는 것도 또 하나의 재미지.",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {552, 556, 557, 559, 560, 561, 562, 563, 564, 570, 573}
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
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context",
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
                "segment": "base_msggame_B001_S19",
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
