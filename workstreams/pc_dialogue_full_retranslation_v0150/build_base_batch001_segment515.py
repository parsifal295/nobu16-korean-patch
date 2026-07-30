#!/usr/bin/env python3
"""Build Base authoring segment 515 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S515.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s515", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:453:0": "천하포무, 끝내 이루지 못하였는가\n정녕 몽환과도 같구나…",
    "8:454:0": "여기까지 왔으면 제법 잘한 셈인가…\n내 한평생, 꿈속의 꿈이었구나…",
    "8:455:0": "대망을 품었으나, 이 손이 닿지 못하였는가\n하지만 후회는 없다…",
    "8:456:0": "훗, 내 명이 다하기 전에\n천하를 손에 넣지 못하였는가",
    "8:457:0": "내 삶은 의와 함께하였으니\n내가 죽더라도 의는 사라지지 않으리라",
    "8:458:0": "이토록 오래 살 줄은\n이 모토나리조차 내다보지 못했구나…",
    "8:459:0": "하고 싶은 대로 살았건만, 아직도\n다 이루지 못한 꿈만 남았구나…",
    "8:460:0": "목숨도 명예도 아끼지 않고 달려왔건만\n천하의 평온에는 끝내 이르지 못했는가…",
    "8:461:0": "설마 다다미 위에서 죽을 줄이야\n꿈에도 생각지 못했는데…",
    "8:462:0": "제법 잘 살았지. 후회가 있다면\n전장에서 최후를 맞지 못한 것뿐이군…",
    "8:463:0": "내 무용으로도\n천하에는 끝내 닿지 못했는가…",
    "8:464:0": "갈고닦은 무예도 세월은 이기지 못하는가\n내 한평생, 과연 무언가를 이루기는 했는가…",
    "8:465:0": "나는 천하를 다스릴 만한 그릇이\n아니었다는 말인가…",
    "8:466:0": "이 손은 끝내 천하에 닿지 못했는가\n후후, 환상을 뒤쫓는 듯한 삶이었구나…",
    "8:467:0": "지용, 신의, 무위, 천운…\n천하를 얻기에 부족했던 것은 무엇이었는가…",
    "8:468:0": "누구를 위해, 무엇을 위해 계속 싸웠던가…\n물음은 마지막 순간까지도 끝이 없는 법이로다…",
    "8:469:0": "서슬 퍼런 칼날 아래를 헤치고 시산혈하를 건넜으니\n죄 많고도 즐거운 삶이었노라…",
    "8:470:0": "아무래도 내 목숨은 여기까지인 듯하구나\n모두들, 참으로 잘 섬겨 주었다. 잘 있거라!",
    "8:471:0": "천하를 손에 넣지는 못했으나\n이 지모로 살아남았으니, 후회는 없다",
    "8:472:0": "어떠냐, 먹느냐 먹히느냐 하는 세상에서\n이 몸, 여기까지 살아남았노라…",
}

STATIC_COORDINATES = set(TRANSLATIONS)


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S515", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
