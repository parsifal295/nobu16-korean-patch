#!/usr/bin/env python3
"""Build Base authoring segment 368 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S368.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s368", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:984:0": "에게 패할 정도라면\n",
    "7:984:1": "이(가) 우리를 지킬 수 있을지\n불안해지는군……",
    "7:985:0": "에게 패배라니……\n",
    "7:985:1": "도 끝인가\n새로운 주군을 찾아 두어야겠군",
    "7:986:0": "이(가) 「",
    "7:986:1": "」에게 패배하다니……\n인간 세상은 무상하고 성자필쇠라 하나\n설마 이 지경일 줄이야……",
    "7:987:0": "에게 패하다니\n",
    "7:987:1": ", 약하도다\n지나치게 의지하는 것은 위험하겠군",
    "7:988:0": "에게 패했다고\n",
    "7:988:1": "……믿을 만한 것인가……?\n다른 가문에도 눈을 돌려야겠군",
    "7:989:0": "에게 패한 것을 이러쿵저러쿵 말하지는 않겠으나\n하나를 보면 열을 안다고 하지\n앞으로의",
    "7:989:1": ", 믿을 수 있으랴",
    "7:990:0": "에게 패했다니……\n이 일이 화근이 되어 한순간에 추락할 수도 있지\n",
    "7:990:1": "말고 다른 세력을 의지해야 할까",
    "7:991:0": "이(가) 「",
    "7:991:1": "」에게 패배했다니……?\n따를 가치가 있는지\n알 수 없게 되었습니다……",
    "7:992:0": "에게 패배했다고!?\n",
    "7:992:1": "을(를) 따르고 있었다만\n그다지 미덥지 못한 모양이군",
    "7:993:0": "에게 진 것입니까……\n",
    "7:993:1": "도 많이 쇠락했군요\n거취를 생각해 보기로 하지요",
}

STATIC_COORDINATES: set[str] = set()


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S368", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
