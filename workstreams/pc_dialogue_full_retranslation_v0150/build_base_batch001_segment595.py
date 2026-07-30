#!/usr/bin/env python3
"""Build Base authoring segment 595 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S595.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s595", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:967:0": "이 한 수는 어떻습니까?",
    "9:968:0": "얌전히 있거라!",
    "9:969:0": "너무 날뛰지는\n말거라……",
    "9:970:0": "조금은 자중해\n주시겠습니까",
    "9:971:0": "분수를 알아라!",
    "9:972:0": "공세를 펼칩시다!",
    "9:973:0": "더 이상의 난동은\n용서하지 않겠다!",
    "9:974:0": "후회하게\n해 드리지요",
    "9:975:0": "적의 기세를 꺾어야 한다!",
    "9:976:0": "날려 버려 주마!",
    "9:977:0": "혼신의 힘으로 제압하겠다!",
    "9:978:0": "내 오의, 견뎌 보아라!",
    "9:979:0": "적의 병력 수를 줄여\n둘까요",
    "9:980:0": "받아라, 나의 오의!",
    "9:981:0": "계책은 저마다 다른 법……\n그 결과를 지켜보아라",
    "9:982:0": "자, 사라져\n주시지요!",
    "9:983:0": "하아앗!\n받아라아아앗!",
    "9:984:0": "조금이라도 타격을\n입혀야 한다!",
    "9:985:0": "이 기술을\n받아 보아라!",
    "9:986:0": "여기서 적의 병력 수를 줄이겠습니다!",
    "9:987:0": "이 한 수로\n전황을 바꾸겠다!",
    "9:988:0": "이걸로 놀라게 해 주마!",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S595", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
