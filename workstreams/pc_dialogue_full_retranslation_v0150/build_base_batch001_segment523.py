#!/usr/bin/env python3
"""Build Base authoring segment 523 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S523.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s523", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:598:0": "이곳을 다스린 지도 제",
    "8:598:1": "년이 되었으니 충분하겠지\n다음 사람에게 맡기도록 하자",
    "8:599:0": "년 동안\n이 땅도 몰라볼 만큼 발전했구나",
    "8:600:0": "돌이켜 보니 어언 제",
    "8:600:1": "년이로군\n어쩐지 이 땅에 애착이 생길 만도 하구나",
    "8:601:0": "년이나 되었군요…\n돌이켜 보면 좋은 추억뿐이로군요",
    "8:602:0": "이 땅을 다스린 지도 제",
    "8:602:1": "년인가…\n백성들의 얼굴을 떠올리면 떠나기 어렵구나",
    "8:603:0": "돌이켜 보니 어언 제",
    "8:603:1": "년인가…\n참으로 눈 깜짝할 사이였구나…",
    "8:604:0": "년이나 이곳에 머물렀습니까…\n어쩐지 나이를 먹을 만도 하군요",
    "8:605:0": "년이나 다스렸으니…\n역시… 떠나기 어렵군요…",
    "8:606:0": "년이나 다스린 땅을 떠나야 하는가…\n외, 외롭지는 않다!",
    "8:607:0": "년 동안 훌륭한 병사들을 내어 주었구나\n전장에서 보낸 나날은 잊지 않으마",
    "8:608:0": "년이나 머물렀으니 고향이나 다름없소\n다음 땅도 새로운 고향이 되겠지요",
    "8:609:0": "년 동안 이곳을 다스려 왔습니다만…\n모두 저 따위는\n잊어버리고 말겠지요…",
    "8:610:0": "년 동안 그 땅을 다스렸습니다\n막상 내놓으려니 아쉽게 느껴지는군요…",
    "8:611:0": "년…\n길었던 듯도, 짧았던 듯도 하구나",
    "8:612:0": "잘린 건가…\n뭐, 나 같은 놈이니 어쩔 수 없지",
    "8:613:0": "줄곧 참을 수 없어 속이 끓었는데…\n잘도 이런 짓을 하는군…",
    "8:614:0": "더욱 줄어들다니…\n지출을 줄여야겠군…",
    "8:615:0": "이래서는…!\n제대로 전장에 나서지도 못하겠구나…",
    "8:616:0": "으으음, 내 평가는 떨어지기만 하는가…",
}

STATIC_COORDINATES = {f"8:{record_id}:0" for record_id in range(612, 617)}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S523", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
