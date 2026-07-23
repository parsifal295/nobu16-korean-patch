#!/usr/bin/env python3
"""Build Base authoring segment 556 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S556.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s556", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:1059:0": "굶주린 백성들을 위해\n식량을 배급하",
    "8:1059:1": "\n모두 무척 감사하고",
    "8:1060:0": "백성들을 설득하",
    "8:1060:1": "\n어려운 일일수록 모두 힘을 모아\n함께 이겨 내",
    "8:1061:0": "굶주린 백성을 구하려고\n구호 급식을 시행했으며\n백성들도 무척 감사하고",
    "8:1063:0": "피해를 입은 백성들을 위해\n살 집을 새로 마련하",
    "8:1063:1": "\n예전의 활기를 되찾은 듯",
    "8:1064:0": "토사를 치우고 가도를 정비하",
    "8:1064:1": "\n사람들의 왕래가 늘고\n장사도 활기를 띠",
    "8:1065:0": "피해를 입은 마을을 복구하고\n제방도 수리하",
    "8:1065:1": "\n더 이상의 피해는 생기지 않을 것",
    "8:1067:0": "상대에게 사과하고 오",
    "8:1067:1": "\n백성의 삶을 위협하지 않도록\n불필요한 분쟁은 피하지 않으면",
    "8:1068:0": "분쟁을 수습하고 오",
    "8:1068:1": "\n원인은 사소한 일이었던 듯……\n이로써 영내도 원래대로 돌아오",
    "8:1069:0": "인접 군이 전쟁을 준비한다는 건 오판이었던 듯",
    "8:1069:1": "\n하마터면 섣부른 짐작만으로\n큰 전쟁이 벌어질 뻔",
    "8:1083:0": "주손지를 수리하던 중\n목수들이 건축에 유용한\n잊힌 기술을 발견했습니다",
    "8:1084:0": "고토쿠인이 옛 광채를 되찾자\n국인중도 그 위광에 굴복해\n우리에게 더욱 충성할 것을 맹세했습니다",
    "8:1085:0": "도다이지를 재흥하자\n백성들도 깊이 감사하며\n전보다 더욱 힘써 일하게 되었습니다",
    "8:1086:0": "이세 신궁에 기진한 일로\n조정에서도 우리 가문에 감사를 표하여\n여러 다이묘 사이에서 위신이 높아졌습니다",
    "8:1087:0": "이즈모 대사 덕분에\n병사들의 기세가 좋아져\n파죽지세로 적을 공격할 수 있을 것입니다",
    "8:1088:0": "이쓰쿠시마 신사를 재흥한 뒤\n다른 가문을 상대로 한 책략이 잘 풀리게 되어\n무나카타 대신의 가호일지도 모릅니다",
    "8:1089:0": "다자이후 덴만구를 재건한 뒤\n가신들의 영지 관리 솜씨가\n더욱 빛을 발하게 되었습니다",
}

STATIC_COORDINATES: set[str] = {
    "8:1083:0",
    "8:1084:0",
    "8:1085:0",
    "8:1086:0",
    "8:1087:0",
    "8:1088:0",
    "8:1089:0",
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
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S556", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
