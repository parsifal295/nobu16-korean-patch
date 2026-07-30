#!/usr/bin/env python3
"""Build Base authoring segment 13 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S13.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s13", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:302:0": "내게서 달아날 수 있으리라 생각했느냐?",
    "2:304:0": "무엄하다! 쇼군 앞이니라!",
    "2:306:0": "순순히 빼앗기지는 않겠다……",
    "2:308:0": "에게 부상을 입혀 주었노라!",
    "2:309:0": "대장을 보좌하는 것이 부장의 본분이다!",
    "2:313:0": "그런 공격은 「",
    "2:313:1": "야샤미노",
    "2:313:2": "」에게 통하지 않는다!",
    "2:314:0": "이 「",
    "2:314:1": "기요요시",
    "2:314:2": "」는 농사에 조예가 있습니다.\n마을을 더욱 풍요롭게 하겠습니다.",
    "2:315:0": "명수로 이름난 건축 솜씨를\n마음껏 발휘하겠다.",
    "2:316:0": "명수로 이름난",
    "2:316:1": "이(가)\n",
    "2:316:2": "을(를)",
    "2:316:3": "뒷받침하겠",
    "2:318:0": "사이가슈의 철포가 꿰뚫지 못할 것은 없다!",
    "2:319:0": "나의 동지들이여!\n",
    "2:319:1": "오토모",
    "2:319:2": "의 적을 쳐부수자!",
    "2:320:0": "이 「",
    "2:320:1": "란마루",
    "2:320:2": "」에게",
    "2:320:3": "\n진귀한 물건으로 신뢰를 쌓",
    "2:321:0": "란마루",
    "2:321:1": "가 수행하",
    "2:321:2": "\n진귀한 물건으로 신뢰를 쌓",
    "2:322:0": "에게는 그대가 필요하다.\n다시 한번",
    "2:322:1": "미요시",
    "2:322:2": "의 힘이 되어 주게.",
    "2:323:0": "원군을 보내 주다니 고맙소!\n",
    "2:323:1": "아사쿠라",
    "2:323:2": "와 함께 싸우세!",
    "2:324:0": "이 팥 자루로 알려야 해……",
    "2:325:0": "스와 대명신께 맹세코\n",
    "2:325:1": "이(가) 천하를 쟁취하리라!",
    "2:326:0": "이 성은 죽어도 내주지 않겠다!",
    "2:327:0": "신뢰를 얻는 것이 첫째다.\n타 가문과 맺은 인연이 「",
    "2:327:1": "사나다",
    "2:327:2": "」의 요체가 되리라.",
    "2:330:0": "우리 「",
    "2:330:1": "」의 의로써\n증오스러운 적을 물리치리라!",
    "2:331:0": "당대 제일이라 칭송받은 내 재주를\n이 땅에서 펼쳐 보이겠다.",
    "2:332:0": "를 온 힘을 다해 뒷받침하",
    "2:332:1": "\n 그것이 아내의 소임",
    "2:334:0": "내 지략으로 「",
    "2:334:1": "」을(를)\n천하의 주인으로",
    "2:335:0": "대일대만대길의 깃발 아래,\n이 땅을 풍요롭게 만들겠다.",
    "2:338:0": "지금이 공격할 때다!\n이 「",
    "2:338:1": "고토 마타베에 모토쓰구",
    "2:338:2": "」를 따르라!",
    "2:339:0": "의 이름에 부끄럽지 않은\n훌륭한 싸움을 보여 주마!",
    "2:340:0": "우리 가문의 가훈에 따라\n군율이 바로 선 군단으로 만들겠다.",
    "2:341:0": "성이 또 하나 우리 것이 되었군……\n",
    "2:341:1": "의 명성도 높아지겠어.",
    "2:342:0": "적은 돈으로 큰 이익을 얻어야 한다.\n돈은 모아야 가치가 있는 법이지.",
    "2:343:0": "이 땅의 병사들을 정예 철포대로\n훈련시키겠다.",
}

NON_DISPLAY_COORDINATES = {
    f"2:{record_id}:0"
    for record_id in {301, 303, 305, 307, 310, 311, 312, 317, 328, 329, 333, 336, 337}
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1])
    in {308, 313, 314, 315, 316, 319, 320, 321, 322, 323, 325, 327, 330, 331, 332, 334, 335, 338, 339, 340, 341, 343}
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    coordinates = sorted(
        set(TRANSLATIONS) | NON_DISPLAY_COORDINATES,
        key=lambda value: tuple(int(part) for part in value.split(":")),
    )
    for coordinate in coordinates:
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        non_display = coordinate in NON_DISPLAY_COORDINATES
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        row: dict[str, object] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "base_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256": target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
            "semantic_review": "approved",
            "scope_classification": (
                "confirmed_non_display"
                if non_display
                else "runtime_fragment_pending" if dynamic else "retranslated"
            ),
            "layout_review": "not_needed" if non_display else "unchanged_from_current",
            "runtime_review": "not_required" if non_display or not dynamic else "pending",
            "basis": (
                "explicit_unused_trait_dummy_slot_structural_evidence"
                if non_display
                else "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available"
            ),
            "historic_korean_used": False,
            "switch_korean_used": False,
        }
        if not non_display:
            row["translation"] = TRANSLATIONS[coordinate]
        rows.append(row)
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    expected_count = len(TRANSLATIONS) + len(NON_DISPLAY_COORDINATES)
    if len(validated) != expected_count:
        raise RuntimeError("validated decision count differs from the segment decision count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S13",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "confirmed_non_display": len(NON_DISPLAY_COORDINATES),
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
