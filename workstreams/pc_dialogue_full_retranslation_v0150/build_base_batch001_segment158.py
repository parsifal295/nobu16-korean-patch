#!/usr/bin/env python3
"""Build Base authoring segment 158 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S158.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s158", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2872:0": "을(를) 버리고 우리에게 붙다니\n제법 배짱 있는 놈이잖아\n앞으로 기대하마",
    "6:2873:0": "흠,", "6:2873:1": "을(를) 버리고 왔다니\n용기 있는 결단을 저버릴 수는 없지\n앞으로는 우리 가문에 맡기시오",
    "6:2874:0": "을(를) 버리고 왔는가\n궁한 새가 품에 들면 사냥꾼도 죽이지 않는 법\n앞으로는 우리 가문이 지켜 주겠노라",
    "6:2875:0": "과연,", "6:2875:1": "을(를) 버리는 겁니까\n우리 가문을 뒷배로 고른 것은 현명하군요\n앞으로의 활약을 기대하겠습니다",
    "6:2876:0": "의 밑을 떠나 우리 가문에 붙겠는가\n나쁘지 않군\n이제부터는 반드시 지켜 주마",
    "6:2877:0": "호오,", "6:2877:1": "을(를) 버리고 우리 가문을 따르겠다고\n눈치가 빠른 모양이군\n앞으로의 활약도 기대하겠다",
    "6:2878:0": "호호,", "6:2878:1": "을(를) 저버리고\n나를 따르다니\n그대의 활약을 기대하겠네",
    "6:2879:0": "호오,", "6:2879:1": "을(를) 버리고\n우리에게 붙겠다는 것인가\n사람 보는 눈이 제법이로군",
    "6:2880:0": "을(를) 버리다니\n혜안을 지니신 모양이군요\n자, 저와 함께 천하를 노려 봅시다",
    "6:2881:0": "호오,", "6:2881:1": "을(를) 버리고\n우리에게 붙는 것인가\n내 밑에서 마음껏 힘쓰도록 하라",
    "6:2882:0": "을(를) 저버리고\n우리에게 빌붙으려 하다니…\n그 각오가 어느 정도인지 보여 주시지요",
    "6:2883:0": "호오,", "6:2883:1": "을(를) 버리고\n우리에게 붙다니 현명한 판단이다\n산하에서의 활약을 기대하마",
    "6:2884:0": "은(는) 믿을 만하지 않아…\n앞으로 잘 부탁한다",
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S158", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
