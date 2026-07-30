#!/usr/bin/env python3
"""Build Base authoring segment 587 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S587.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s587", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:794:0": "을(를)\n포박했습니다",
    "9:795:0": "\n사로잡았노라!",
    "9:796:0": "은(는)\n내 손에 들어왔다",
    "9:797:0": "쯤 되는 자가\n포로 신세라니……",
    "9:798:0": "\n포로로 삼았다!",
    "9:799:0": "을(를)\n붙잡았습니다!",
    "9:800:0": "은(는)\n우리 수중에 있다!",
    "9:801:0": "을(를)\n단단히 결박했습니다",
    "9:802:0": "을(를)\n붙잡았소이다",
    "9:803:0": "을(를) 얕본 벌이다!",
    "9:804:0": "눈부신 무예에\n감복하였소!",
    "9:805:0": "적도 우리 군을\n두려워하게 되었겠지",
    "9:806:0": "이제 적도\n조금은 혼쭐이 났겠지요",
    "9:807:0": "흠…… 훌륭한 무예로다",
    "9:808:0": "따위는\n적수가 아니었군",
    "9:809:0": "우리에게 대적한 대가\n……이겠군요",
    "9:810:0": "아깝구나…… 조금만 더 했으면\n베어 쓰러뜨렸을 것을",
    "9:811:0": "쪽이\n한 수 위였군요!",
    "9:812:0": "적도 우리 군의 강함을\n뼈저리게 깨달았겠지!",
    "9:813:0": "이제 적의 기세도\n꺾이겠지요",
    "9:814:0": "우리의 힘을 충분히\n알렸군요",
    "9:815:0": "상처는 입혔다!\n다음에는 반드시 베어 쓰러뜨릴 수 있어",
}

STATIC_COORDINATES: set[str] = {
    "9:804:0",
    "9:805:0",
    "9:806:0",
    "9:807:0",
    "9:809:0",
    "9:810:0",
    "9:812:0",
    "9:813:0",
    "9:814:0",
    "9:815:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S587", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
