#!/usr/bin/env python3
"""Build Base authoring segment 366 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S366.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s366", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:963:2": "의 힘을 조금 얕보았다만\n이건 반가운 오산이구먼!",
    "7:964:0": "에게 승리를 거두다니\n",
    "7:964:1": "은(는) 또한 당대의 패권자인가……\n마음 놓고 있을 수는 없겠군",
    "7:965:0": "에게 이겼는가, 훌륭하군……!\n",
    "7:965:1": "의 각오, 똑똑히 지켜보았다\n내 호적수에 걸맞은 강자로다",
    "7:966:0": "에게 승리했는가\n허나 의가 없는 힘은 무와 같으니\n",
    "7:966:1": "에게 의가 있는가? 흥미롭군",
    "7:967:0": "에 대한 승리가 실력인가 요행인가\n어느 쪽이든",
    "7:967:1": "의 기세는 얕볼 수 없군\n호의적으로 지켜보겠다",
    "7:968:0": "에게 이기다니\n",
    "7:968:1": "은(는) 얕볼 수 없도다!\n그 힘을 이용하지 않을 수 없겠군!",
    "7:969:0": "이(가) 이겼는가\n승자에게 빌붙어야 하는 것이 세상의 이치\n후우, 참으로 무략이란 무사의 거짓말이로다……",
    "7:970:0": "에게 이겼다고!?\n",
    "7:970:1": "……제법이잖아!\n어디까지 성장할지 기대되는군!",
    "7:971:0": "은(는) 승리했는가\n무를 숭상하는 이 세상에서 승리는 긍지이니\n우리 가문을 비롯한 여러 가문이 모두 칭송할 것이오",
    "7:972:0": "에게 승리했다고……?\n",
    "7:972:1": ", 제법 만만치 않은 자로다\n약자라 얕본 것이 잘못이었는가",
    "7:973:0": "이(가) 「",
    "7:973:1": "」에게 승리했군요……\n그런 용맹한 자가 일본에 있다는 것은\n든든하면서도 두렵군요",
    "7:974:0": "에게 이겼는가!\n장하도다, 「",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S366", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
