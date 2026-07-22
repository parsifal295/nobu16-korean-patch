#!/usr/bin/env python3
"""Build Base authoring segment 52 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S52.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s52", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:717:0": "신참은 괴롭힘을\n당하는 걸까요…",
    "6:718:0": "적응하지 못하겠사옵니다…\n돌아가고 싶사옵니다…",
    "6:719:0": "이 긴장을 주위에\n들키지 않도록 해야겠군",
    "6:720:0": "이 평정… 나는\n없어도 되는 게 아닌가",
    "6:721:0": "놈…\n신참 주제에 잘난 척은",
    "6:722:0": "의 저 얼굴!\n완전히 우쭐해졌군",
    "6:723:0": "신참",
    "6:723:1": "에게\n질 수는 없느니라",
    "6:724:0": "놈…\n건방지구나…",
    "6:725:0": "따위와\n한자리에 앉게 되다니",
    "6:726:0": "을(를) 평정에…\n주군께서는 무슨 생각이신가",
    "6:727:0": "…\n건방져 보이는 자군요",
    "6:728:0": "…역시\n긴장하고 있군요",
    "6:729:0": "마음에 들지 않는 얼굴이 있군\n누구라고는 말하지 않겠다만…",
    "6:730:0": "놈…\n엄히 지도해야겠구나",
    "6:731:0": "이(가)\n평정중에 발탁되다니… 납득할 수 없다!",
    "6:732:0": "나의 재주가…",
    "6:732:1": "와\n필적한다고 여기셨는가",
    "6:733:0": "주군의\n솜씨를 지켜보겠소…",
    "6:734:0": "님께는\n여러 가지를 가르쳐 드려야겠군",
    "6:735:0": "놈에게\n고참의 솜씨를 보여 주마",
    "6:736:0": "요즘은",
    "6:736:1": "이라도\n평정에 낄 수 있는 건가",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {721, 722, 723, 724, 725, 726, 727, 728, 730, 731, 732, 734, 735, 736}
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
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
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
                "segment": "base_msggame_B001_S52",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
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
