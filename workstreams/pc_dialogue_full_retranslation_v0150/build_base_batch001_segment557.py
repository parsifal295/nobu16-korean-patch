#!/usr/bin/env python3
"""Build Base authoring segment 557 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S557.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s557", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:1090:0": "전보다 가신 등용이\n순조롭게 이루어지게 되었습니다\n이 또한 릿샤쿠지의 영험일지도 모릅니다",
    "8:1091:0": "아쓰타 신궁의 가호 덕분에\n가신들의 무예 솜씨가\n한층 날카로워진 듯합니다",
    "8:1092:0": "스와 대사에 기부한 덕인지\n영내의 말이 늘어난 듯합니다\n마목장 건설도 순조롭게 진행됩니다",
    "8:1093:0": "오모노누시 덕분에 해난이 줄고\n각지의 해운이 번성하여\n항구 건설도 순조로워졌습니다",
    "8:1094:0": "긴푸센지가 재흥하자\n승려들도 활기가 넘치고\n각지에서 사찰 건립의 기운이 높아졌습니다",
    "8:1095:0": "사찰과 신사의 장서에서 넓은 농지에 적용할\n새로운 모내기법의 실마리를 얻어\n대농촌의 석고가 늘었습니다",
    "8:1096:0": "가신들도 미카와 무사를 본받아\n우리 가문의 결속이 더욱 굳어졌다",
    "8:1097:0": "신사 안쪽에 자라는 식물을\n휴대 병량에 섞었더니 더 든든해져\n작게 만들어 더 많이 지닐 수 있게 됐다",
    "8:1098:0": "아시카가 학교의 다양한 장서 덕분에\n가신들의 성장이 눈에 띄게 되었다",
    "8:1099:0": "만간지에 기부한 덕에\n우리 가문의 위광이 널리 퍼지고\n병사들의 결속도 더욱 굳어졌습니다",
    "8:1100:0": "센겐 신사 제신의 가호로\n우리 영지의 풍작은 보장될 것입니다",
    "8:1101:0": "게히 신궁이 굳건히 자리한 한\n우리 가문의 영토는 반석과 같을 것입니다",
    "8:1102:0": "아소 신사가 재흥한 덕에\n어떠한 재해도 미리 내다보고\n대처할 수 있음이 틀림없습니다",
    "8:1103:0": "나카야마 신사에 광부들의 신앙이 모이고\n사고도 줄어든 덕분에\n각지의 은광 채굴이 활발합니다",
    "8:1104:0": "에나 신사에 광부들의 신앙이 모이고\n사고도 줄어든 덕분에\n각지의 금광 채굴이 활발합니다",
    "8:1105:0": "혼다와케노미코토를 받들어\n전투에서 승리하는 날에는\n가문의 위풍이 더욱 널리 퍼질 것입니다",
    "8:1106:0": "가시마 신궁의 가호가 있다면\n그 누구도\n쉽사리 영내에 침입하지 못합니다",
    "8:1107:0": "이곳은 교역에 알맞은 입지이건만\n항구가 비좁은 것이 아쉽군요\n설비가 조금만 더 갖춰졌다면…",
    "8:1108:0": "지방 무사들이 돈벌이를 두고 다투니\n무섭구먼… 금산은 영주님께서\n다스려 주셔야 마음이 놓인다오",
    "8:1109:0": "새 광상이 발견됐다더군\n은이 싸게 풀리면 헐값에 사들여\n나는 틀림없이 큰돈을 벌겠구먼!",
    "8:1110:0": "좋은 물, 좋은 풀, 좋은 공기!\n이것이야말로 준마가 자랄 터전\n말을 늘리려면 이 땅이 제격이겠군요",
    "8:1111:0": "사들이기만 해서는 철포를 갖출 수 없네…\n철포 제작은 지극히 어렵다 들었으나\n저 땅의 장인이라면 혹시",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S557", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
