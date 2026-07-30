#!/usr/bin/env python3
"""Build Base authoring segment 642 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S642.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s642", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1964:0": "을(를) 설득하여\n아군으로 삼을 수 있다면……",
    "9:1965:0": "적을 몸소 사로잡다니\n용맹하구나―",
    "9:1966:0": "훌륭한 전공이로다…… 포로는\n여러모로 쓸모가 있지",
    "9:1967:0": "역시 대단하오\n감복했소이다",
    "9:1968:0": "인가\n용케도 사로잡았구나!",
    "9:1969:0": "설마 사로잡아\n버릴 줄이야!",
    "9:1970:0": "생포하다니\n제법이군!",
    "9:1971:0": "누가 보아도 분명한\n전공이군요!",
    "9:1972:0": "괴멸에 그치지 않고\n포박까지…… 과연 대단하구나",
    "9:1973:0": "이 정도쯤이야\n식은 죽 먹기다!",
    "9:1974:0": "내 무예라면\n쉬운 일이지",
    "9:1975:0": "이 정도는 당연하다",
    "9:1976:0": "계책이 제대로\n맞아떨어졌군요",
    "9:1977:0": "단칼에 베지 못했군\n……내 수련이 부족하구나",
    "9:1978:0": "죽이는 것보다 부상자가……\n적의 일손을 더 묶는 법이니라",
    "9:1979:0": "가엾은 꼴이 되었구나\n",
    "9:1979:1": ", 몸조리 잘하시게",
    "9:1980:0": "좀 살살 할 걸\n그랬나 보구나!",
    "9:1981:0": "후우…… 아직도\n가슴이 두근거립니다",
    "9:1982:0": "격의 차이를\n보여 주었다!",
    "9:1983:0": "이 정도쯤은\n해내 보이겠어요",
    "9:1984:0": "뭐, 대강\n이 정도로군",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1964:0",
    "9:1965:0",
    "9:1968:0",
    "9:1979:0",
    "9:1979:1",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required" if static else "pending",
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available"
                ),
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
                "segment": "base_msggame_B001_S642",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
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
