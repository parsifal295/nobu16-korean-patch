#!/usr/bin/env python3
"""Build Base authoring segment 558 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S558.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s558", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:1112:0": "백성은 오랜 전란에 지쳐 있네…\n부처님의 가르침을 널리 펴서\n조금이나마 그 마음을 구하고 싶건만",
    "8:1113:0": "좋은 땅, 찾았습니다\n더 많은 사람에게 가르침 전하려면\n기도드릴 곳, 있으면 좋겠습니다",
    "8:1114:0": "요양하러 온천에 가고 싶건만\n사람이 들어갈 상태가 아니라더군…\n누가 좀 정비해 주지 않으려나",
    "8:1115:0": "저 넓은 땅에 벼를 심으면\n참으로 많이 거둘 수 있을 텐데\n개간해 줄 사람은 없으려나",
    "8:1116:0": "사람이 많이 오가는 이곳에\n시장이 서면 큰돈을 벌 게 틀림없어!\n다만, 저 넓은 땅을 어떻게 정비할지…",
    "8:1117:0": "전쟁으로 마을이 이 꼴이 됐어…\n제대로 살 수도 없는데\n우리끼리 뭘 어쩌란 말이야…",
    "8:1118:0": "전쟁통에 도적떼에게 상품을\n빼앗기고 말았어… 이대로면\n관가에 바칠 것도 없다고…",
    "8:1119:0": "도적떼가 출몰한다는 모양인데\n우리만으로는 도저히 감당할 수 없어\n이대로면 백성들이 불안해할 텐데…",
    "8:1121:0": "강물이 넘쳐 집이 떠내려가 버렸어\n논도 밭도 모조리 망가졌고…\n이제 어떻게 살아가야 할지…",
    "8:1122:0": "산사태가 나서 길이 막혔어\n물건을 제대로 들여오지 못하면\n장사는 끝장이라고…",
    "8:1123:0": "제방이 무너져 강물이 넘치고 있습니다\n주변 마을에도 피해가…\n서둘러 복구하고 싶습니다만…",
    "8:1125:0": "마을이 이 지경이 됐는데도\n무사 나리들은 도와주지 않는 건가…\n성 수리도 중요하겠지만…",
    "8:1126:0": "잔해가 길을 막고 있는 건가…\n장사도 제대로 할 수 없고\n대체 복구는 어떻게 되고 있는 거야",
    "8:1127:0": "성벽 수리에 동원된 탓에\n백성의 불만이 쌓이고 있다…\n한시라도 빨리 끝내야 한다…",
    "8:1129:0": "집도 밭도 모조리 타 버렸어\n내일부터 어떻게 살란 말이야…\n하다못해 먹을 것만이라도 있으면…",
    "8:1130:0": "마을 시장이 불타 버렸어…\n물건이 있어도 팔 곳이 없으면\n우리더러 어찌 장사하란 말이야…",
    "8:1131:0": "밭이 불타 수확이 부족하다…\n이대로 세금을 바치게 하면\n굶주린 백성의 불만이 폭발할 듯하다…",
    "8:1133:0": "올해는 흉작이라 먹을 것도 이젠…\n배고프다…",
    "8:1134:0": "쌀 부족에 성난 백성들이 모여\n불온한 일을 꾸미는 모양입니다\n유혈 사태로 번지지 않으면 좋겠습니다만",
    "8:1135:0": "올해는 벼 작황이 나빠\n모두가 굶주리고 있다…\n어떻게든 도울 방도가 없을까…",
    "8:1137:0": "강물이 넘쳐 집이 떠내려가 버렸어\n논도 밭도 모조리 망가졌고…\n이제 어떻게 살아가야 할지…",
    "8:1138:0": "산사태가 나서 길이 막혔어\n물건을 제대로 들여오지 못하면\n장사는 끝장이라고…",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S558", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
