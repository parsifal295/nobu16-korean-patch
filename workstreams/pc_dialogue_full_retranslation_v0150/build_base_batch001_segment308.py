#!/usr/bin/env python3
"""Build Base authoring segment 308 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S308.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s308", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:158:1": "」의 협력을 얻어\n우리 편으로 끌어들이는 것이 상책입니다",
    "7:159:0": "성을 공격하기 전에 저 요새부터\n함락해야 할 것입니다",
    "7:160:0": "성을 공격하려면 저 요새를\n먼저 제압해야 할 줄 아옵니다",
    "7:161:0": "이 요새는 방해되는군요.\n먼저 함락해야 할 것입니다",
    "7:162:0": "이 요새가 공성에 방해가\n되지 않도록 먼저 무너뜨려야 합니다",
    "7:163:0": "저 요새만 제압해 두면\n성 공략이 수월해질 것입니다",
    "7:164:0": "성 공략에 앞서 저 요새를\n공격해 두어야 합니다",
    "7:165:0": "저 요새를 손에 넣으면,\n여러모로 이로울 것입니다",
    "7:166:0": "공격하든 수비하든,\n요새부터 확보하는 것이 좋겠습니다",
    "7:167:0": "요새를 우리 가문의 것으로 삼으면,\n여러모로 도움이 될 것입니다",
    "7:168:0": "이 요새는 지금\n미리 장악해 두어야 하옵니다",
    "7:169:0": "저 요새를 손에 넣으면,\n공격도 수비도 뜻대로 할 수 있습니다",
    "7:170:0": "이 요새가 적의 손에 있는 것은\n참으로 아깝사옵니다",
    "7:171:0": "망루를 먼저 제압하지 않으면,\n행군에 방해가 될 것입니다",
    "7:172:0": "저 망루가 눈엣가시군요.\n서둘러 우리 것으로 삼읍시다",
    "7:173:0": "군을 움직일 때 망루는\n방해가 될 것입니다",
    "7:174:0": "저 망루를 남겨 두면 훗날\n우환이 될지도 모릅니다",
    "7:175:0": "저 망루는 먼저\n제압해 두어야 할 것입니다",
    "7:176:0": "저 망루를 제압하지 않으면,\n뒤에 골칫거리가 남을 것입니다",
    "7:177:0": "적의 망루를 남겨 두면\n훗날 화근이 될 것입니다",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS) - {"7:158:1"}


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
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S308", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
