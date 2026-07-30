#!/usr/bin/env python3
"""Build Base authoring segment 17 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S17.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s17", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:483:0": "내 앞길을 막는 자는 용서하지 않겠다!\n천하의 평온을 향해 나아가라!",
    "2:484:0": "서둘러 이 군을 복속시켜\n백성을 평온한 삶으로 이끌자.",
    "2:485:0": "전투에서 가장 중요한 것은 병사들의 활약……\n모두, 너희를 믿겠다.",
    "2:486:0": "한시라도 빨리 전투 채비를 갖춰라.\n때를 지배하는 자가 전국을 제패한다!",
    "2:487:0": "맹우에게 위기가 닥쳤다……\n지금이야말로 의를 위해 일어설 때다!",
    "2:488:0": "나의 힘을 똑똑히 보아라!",
    "2:489:0": "휘하에 든 장수들에게\n마음껏 활약할 자리를 ",
    "2:489:1": "주겠다!",
    "2:490:0": "입신출세야말로\n",
    "2:490:1": "의 삶의 보람",
    "2:491:0": "참고 견딜 때 비로소 강함이 드러나는 법.\n무사의 기개란 그런 것이다……",
    "2:492:0": "싸우지 않고 상대를 굴복시키는 것이 상책.\n이 또한 난세를 살아가는 방도다……",
    "2:493:0": "나의 힘을 똑똑히 보아라!",
    "2:494:0": "일문이 굳게 뭉쳐야\n영지가 안정되는 법",
    "2:495:0": "지금은 한시라도 빨리 일을 마치고\n다음 싸움에 대비할 때다……",
    "2:496:0": "어떤 일이 닥쳐도\n",
    "2:496:1": "을(를) 보좌하여\n완벽한 성과로 이끌",
    "2:497:0": "영민의 행복을 바라는 것이야말로\n영주가 갖추어야 할 소양이지……",
    "2:498:0": "물은 그릇의 모양을 따르는 법……\n성에 따라 공략법도 달리해야 한다.",
    "2:499:0": "나의 힘을 똑똑히 보아라!",
    "2:500:0": "보다 큰 적과 싸울 때……\n어쩐지 가슴이 뛰는군!",
    "2:501:0": "나의 힘을 똑똑히 보아라!",
    "2:502:0": "무가에도 풍류는 빠질 수 ",
    "2:502:1": "없지요.\n풍류를 아는 마음이야말로 교섭의 요체입니다.",
    "2:503:0": "무가라 해도 풍류를 빼놓을 수 없지.\n풍류를 아는 마음으로",
    "2:503:1": "의 교섭을\n보좌해 보이겠",
    "2:504:0": "가신이 주군을 고른다…… 그것이야말로\n전국의 난세를 살아가는 비결이지.",
    "2:505:0": "시코쿠를 제패할 자는\n바로 이 「",
    "2:505:1": "」밖에 없다!",
    "2:506:0": "나의 힘을 똑똑히 보아라!",
    "2:507:0": "나의 힘을 똑똑히 보아라!",
    "2:508:0": "나의 힘을 똑똑히 보아라!",
    "2:509:0": "나의 힘을 똑똑히 보아라!",
    "2:510:0": "나의 힘을 똑똑히 보아라!",
    "2:511:0": "나의 힘을 똑똑히 보아라!",
    "2:512:0": "출진!",
    "2:512:1": " 나의 병법을\n똑똑히 보여 드리겠습니다.",
    "2:513:0": "나의 힘을 똑똑히 보아라!",
    "2:514:0": "적과 아군은 시세에 따라 달라지는 법.\n다시 손잡을 날도 있겠지.",
    "2:515:0": "나의 힘을 똑똑히 보아라!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {484, 485, 489, 490, 494, 496, 500, 502, 503, 505, 512, 514}
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
                "segment": "base_msggame_B001_S17",
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
