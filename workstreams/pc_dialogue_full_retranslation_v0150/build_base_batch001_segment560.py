#!/usr/bin/env python3
"""Build Base authoring segment 560 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S560.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s560", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:1176:0": "아소 신사는 예부터 화구의 이변을\n천하의 흉조로 여긴 신앙의 중심이오니\n재흥하면 반드시 우리에게 도움이 될 것입니다",
    "8:1177:0": "나카야마 신사의 가가미쓰쿠리노카미는\n대장일과 금속 세공을 관장하는 신이오니\n재흥하면 은광 채굴도 순조로워질 것입니다",
    "8:1178:0": "에나 신사는 기소 요시나카 공이 태도를 봉납한 곳이며\n섭사에는 금속 세공의 신 아메노마히토쓰노미코토를 모시니\n재흥하면 금광 채굴도 순조로워질 것입니다",
    "8:1179:0": "이세 신궁에서 아마테라스와 도요우케의 분령을 모신\n야마노우에 대신궁의 가호가 있다면\n우리의 위광도 더욱 널리 퍼지리라",
    "8:1180:0": "예로부터 수많은 무가의 숭경을 받아 온\n가시마 신궁도 전란으로 고통받는 듯하군\n우리가 기진하여 돕자",
    "8:1181:0": "교역의 이익을 더욱 늘리고자\n하역에 알맞은 교역항을\n이 땅에 건설하고자 하",
    "8:1182:0": "금 광맥을 발견했다는\n백성의 보고가 있",
    "8:1182:1": "\n채굴에 나서 보는 건 어떻",
    "8:1183:0": "새로운 은 광상이 발견되",
    "8:1183:1": "\n대규모 공사를 벌여\n채굴 체제를 정비하고자 하",
    "8:1184:0": "말 산지로 이름난 곳에 마목장을 두고 싶습니다…\n좋은 말을 많이 갖출 수 있다면\n기병의 질로 다른 가문을 압도할 수 있",
    "8:1185:0": "유능한 장인들을 모아 대장간 마을을 세우고\n철포 제작을 맡기면 어떻겠습니까?\n전시에 큰 도움이 되",
    "8:1186:0": "민심을 달래기 위해\n유랑 승려의 건의를 받아들여\n새 절을 세워 보는 건 어떻",
    "8:1187:0": "남만 수도사의 요청에 응하여\n남만사를 이 땅에 세우고\n민심을 달래고자 하",
    "8:1188:0": "천질이 좋은 온천이 있는 듯하니\n효율적으로 활용할 수 있도록\n온천향을 조성하고자 하",
    "8:1188:1": "의",
    "8:1188:2": "이(가)",
    "8:1189:0": "손대지 않은 넓은 땅을 단숨에 개간하여\n대농촌으로 바꾸고자 하",
    "8:1189:1": "\n이에 공사비 지원을 청하고자 합니다…",
    "8:1190:0": "손대지 않은 넓은 땅을 단숨에 개간하여\n대시장을 건설하고자 하",
    "8:1190:1": "\n이에 공사비 지원을 청하고자 합니다…",
}

STATIC_COORDINATES: set[str] = {
    "8:1176:0",
    "8:1177:0",
    "8:1178:0",
    "8:1179:0",
    "8:1180:0",
}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S560", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
