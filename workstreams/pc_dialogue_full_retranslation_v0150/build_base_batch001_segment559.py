#!/usr/bin/env python3
"""Build Base authoring segment 559 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S559.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s559", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:1139:0": "제방이 무너져 강물이 넘치고 있습니다\n주변 마을에도 피해가…\n서둘러 복구하고 싶습니다만…",
    "8:1141:0": "영주님이 손을 대셨는지는 몰라도\n이웃 나라 놈들과 다툼이 벌어지고 있어\n싸움이 커지기 전에 달아나야겠군…",
    "8:1142:0": "이웃 나라와 분쟁이 벌어진 건가\n아무래도 일촉즉발의 분위기로군\n이래서야 장사할 때가 아니야…",
    "8:1143:0": "국경에 적병 놈들이 주둔하고 있군\n백성들에겐 미안하지만 대치해 보자고\n당분간 전선에 주둔하겠어",
    "8:1157:0": "주손지가 전란으로 황폐해졌습니다\n이대로 사라지게 두기는 참으로 아까우니\n수리해 보시는 것이 어떻겠습니까",
    "8:1158:0": "겐지와 인연이 깊은 고토쿠인도 전화로 쇠락했습니다\n이때 우리가 지원한다면\n동국에서의 지위를 굳힙시다",
    "8:1159:0": "전화로 도다이지의 승려들도 고통받는 듯합니다\n우리가 지원한다면\n신심 깊은 백성들의 호감을 살 것입니다",
    "8:1160:0": "예로부터 조정과 연이 깊은\n이세 신궁에 기부한다면\n우리의 위신이 더욱 높아질 것입니다",
    "8:1161:0": "스사노오노미코토를 경내 소가노야시로에 모신\n이즈모 대사가 부흥하면\n병사들도 싸울 때 크게 분발할 것이오",
    "8:1162:0": "대대로 권력자들의 숭경을 받아 온 이쓰쿠시마 신사도\n전란으로 쇠락하고 있습니다\n우리 손으로 부흥시키는 건 어떻겠습니까",
    "8:1163:0": "다자이후 덴만구마저 전화로 불탔지만\n우리 손으로 재건한다면\n무언가 가호를 얻을지도 모르네",
    "8:1164:0": "좋은 인연을 맺으려면 먼저 악연을 끊어야 합니다\n릿샤쿠지는 악연을 끊기로 유명하니\n기부해 보시는 건 어떻겠습니까",
    "8:1165:0": "아쓰타 신궁에 기부한다면\n구사나기의 검의 가호를 얻어\n더는 맞설 자가 없을 것입니다",
    "8:1166:0": "군신을 모시는 스와 대사에 기부한다면\n병사들의 사기가 높아지는 것은 물론\n어떤 가호를 얻을지도 모릅니다",
    "8:1167:0": "항해신 오모노누시의 가호가 있다면\n우리 해운도 더욱 번성할 것입니다",
    "8:1168:0": "수험도 총본산 긴푸센지에 기부해\n승려들의 호감을 얻는다면\n그들도 기꺼이 절을 세울 것입니다",
    "8:1169:0": "쌀이 없으면 민심도 어지러워진다\n이럴 때는 구마노 대신에게 기부해\n가호를 받도록 하자",
    "8:1170:0": "미카와 무사는 충의가 두터우니\n마쓰다이라 가문의 보리사인 다이주지에 기부하면\n좋은 선전이 될 것입니다",
    "8:1171:0": "이 신사는 오랫동안 방치되어 황폐했지만\n전신 스와 대신을 모시고 있으니\n가호를 받으면 병사들도 안정을 찾을 것입니다",
    "8:1172:0": "동국의 최고 학부인 아시카가 학교를\n지원하면 가신들도 학문을 닦아\n더욱 성장할지도 모릅니다",
    "8:1173:0": "동국 최대의 성지에 자리한 만간지에 기부하면\n우리의 통치를 알리는 좋은 선전이 되고\n병사들을 이끄는 힘도 커질 것입니다",
    "8:1174:0": "예로부터 조정과 지방관의 숭경을 받아 온 센겐 신사도\n전란으로 점차 황폐해지고 있습니다\n우리 손으로 부흥시킵시다",
    "8:1175:0": "호쿠리쿠도의 총수호라 불리는 게히 신궁도\n이 난세에 점차 쇠락하고 있습니다\n우리 손으로 다시 일으켜 세웁시다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S559", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
