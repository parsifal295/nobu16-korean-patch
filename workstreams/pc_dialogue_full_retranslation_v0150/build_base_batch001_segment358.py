#!/usr/bin/env python3
"""Build Base authoring segment 358 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S358.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s358", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:863:0": "이(가) 이 성으로 온다……\n서둘러 기병에 맞설 채비를 갖추어",
    "7:864:0": "호적수여, 잘 왔다\n",
    "7:864:1": "이(가) 자랑하는 정예 가신들이여\n그 진면목을 보여 다오!",
    "7:865:0": "경박한 의를 떠벌리며 난동을 부리다니, 구제할 길이 없다\n백성을 짊어진",
    "7:865:1": "에게 패배란 용납되지 않는다",
    "7:866:0": "마침내 「",
    "7:866:1": "」이(가) 왔는가……!\n",
    "7:866:2": "의 무용이 얼마나 통할지\n그야말로 중대한 고비라 할 수 있",
    "7:867:0": "그 꼬맹이가 제법 건방져졌구나\n오래 알고 지낸 사이라 해도 봐주지는 않겠다",
    "7:868:0": "놈이 나타나",
    "7:868:1": "는가\n정예 미카와 병사를 이끈다더군\n모두, 방심하지 않",
    "7:868:2": "도록 하라",
    "7:869:0": "조부 대부터 인연이 깊은 두 가문이지만\n백성을 위해 여기서 물러설 수는 없다",
    "7:870:0": "의 이름에 걸맞은 진용……\n이를 끝까지 막아 내기란\n상당한 난관이 되",
    "7:871:0": "기묘한 인연이로다, 한때 서로 돕던 우리 두 가문……\n이제 이렇듯 서로 싸우게 될 줄이야!",
    "7:872:0": "마침내 야심을 드러냈는가\n천하의 평온을 위하여, 「",
    "7:872:1": "」의 기세를\n더는 좌시할 수 없다!",
    "7:873:0": "을(를) 노하게 하고 말",
    "7:873:1": "는가……\n그렇다면 그 송곳니를 막아야 하",
    "7:874:0": "의 행차이신가!\n큰 공을 세울 절호의 기회로구나!",
}

STATIC_COORDINATES: set[str] = {"7:867:0", "7:869:0", "7:871:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S358", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
