#!/usr/bin/env python3
"""Build Base authoring segment 11 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S11.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s11", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:241:0": "공사는 본래 내 특기지……\n신속히 마쳐 보이겠",
    "2:242:0": "공사라면 자신 있",
    "2:242:2": "이(가)",
    "2:242:3": "의 손발이 되어\n신속히 마쳐 보이겠",
    "2:243:0": "재해 피해는 최소한으로 억누를 ",
    "2:243:1": "테니\n걱정하지 않아도 된다.",
    "2:244:0": "서둘러 성을 보수하여 적의\n공격에 ",
    "2:244:1": "대비하겠다!",
    "2:245:0": "좋은 물건을 손에 넣",
    "2:245:1": "\n모두에게 보여 주고 싶은 것",
    "2:246:0": "도로 정비에는 자신이 있으니\n",
    "2:246:1": "성과를 기대해 ",
    "2:246:2": "주십시오.",
    "2:247:0": "도로 정비에는 자신이",
    "2:247:2": "기대한 성과를 거둘 수 있도록\n",
    "2:247:3": "를 보좌하겠소",
    "2:248:0": "나의 힘을 똑똑히 보아라!",
    "2:249:0": "타 가문과의 교섭이라면\n",
    "2:249:1": "이 가장 자신 있는 분야",
    "2:250:0": "타 가문을 설득하는",
    "2:250:1": "임무라면\n",
    "2:250:2": "이(가) 가장 자신 있는 분야\n",
    "2:250:3": "의 교섭을 뒷받침",
    "2:251:0": "대의 기병이 위력을\n떨칠 때다!",
    "2:252:0": "대가 자랑하는 철포의 위력을\n뼈저리게 깨달아라",
    "2:252:1": "!",
    "2:253:0": "지금이야말로 기마 철포대의 위력을\n똑똑히 보여 ",
    "2:253:1": "주마!",
    "2:254:0": "내 앞길을 막는 자는 용서하지 않겠다!\n천하의 평온을 향해 나아가라!",
    "2:255:0": "천하포무를 펼친다!\n백성들이여,",
    "2:255:1": "노부나가",
    "2:255:2": "의 패업을 따르라!",
    "2:256:0": "사람은 성이요, 사람은 돌담이며, 사람은 해자다.\n인정은 아군이 되고 원한은 적이 된다……",
    "2:257:0": "한시라도 빨리 전투 채비를 갖춰라.\n가이의 호랑이가 출진한다!",
    "2:258:0": "맹우에게 위기가 닥쳤다……\n의를 위해 일어설 때는 지금이다!",
    "2:259:0": "모두, 용기를 북돋아라!\n에치고의 용의 기세를 보여 주리라!",
    "2:260:0": "내 휘하에 드는 장수는 복 받은 자다.\n마음껏 활약할 자리를 얻을 테니 말이다!",
    "2:261:0": "입신출세야말로\n내가 살아가는 보람이니라!",
    "2:262:0": "참고 견딜 때 비로소 강함이 드러나는 법.\n그것이 미카와 무사의 기개다……",
    "2:263:0": "싸우지 않고 상대를 굴복시키는 것이 상책.\n교활한 너구리라 부르고 싶으면 부르라……",
    "2:264:0": "나의 힘을 똑똑히 보아라!",
    "2:265:0": "화살 하나는 부러져도 셋을 합치면\n부러지지 않는다…… 결속이 가장 중요하다.",
    "2:266:0": "때는 지금이다…… 무슨 일이든 때를 놓치지 않아야\n완벽한 성과로 이어지는 법.",
    "2:267:0": "때는 지금이다…… 어떤 일이 닥쳐도\n",
    "2:267:1": "을(를) 보좌하여\n완벽한 성과로 이끌리라",
    "2:268:0": "녹수응온…… 영민의 행복을 기원하는 것은\n소운 공 이래 이어 온 우리 가풍이다.",
    "2:269:0": "물은 그릇의 모양을 따르는 법……\n성에 따라 공략법도 달리해야 한다.",
    "2:270:0": "약해, 너무 약해! 누구든 좋다, 이",
    "2:270:1": "에게\n생채기라도 내 보아라!",
    "2:271:0": "자기보다 큰 적을 집어삼키는 것이\n",
    "2:271:1": "다테",
    "2:271:2": "의 멋이라는 것이지!",
}


DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1])
    in {241, 242, 243, 244, 245, 246, 247, 249, 250, 251, 252, 253, 255, 267, 270, 271}
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
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": (
                    "runtime_fragment_pending"
                    if coordinate in DYNAMIC_RUNTIME_COORDINATES
                    else "retranslated"
                ),
                "layout_review": "unchanged_from_current",
                "runtime_review": (
                    "pending" if coordinate in DYNAMIC_RUNTIME_COORDINATES else "not_required"
                ),
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
                "segment": "base_msggame_B001_S11",
                "decision_count": len(rows),
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
