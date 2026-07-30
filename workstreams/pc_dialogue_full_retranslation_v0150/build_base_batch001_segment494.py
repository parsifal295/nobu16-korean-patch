#!/usr/bin/env python3
"""Build Base authoring segment 494 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S494.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s494", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
BOUNTY_GROUP = (
    "을(를) 비롯해 풍작을 맞은\n",
    "개 군에서\n병량 수입이 증가",
    "\n백성들도 기뻐하고",
)
DAMAGE_GROUP = (
    "을(를) 비롯해 피해를 입은\n",
    "개 군에서\n연공미가 줄어들",
    ", 논의 황폐화는 억제되어\n민충도 그다지 떨어지지 않을 전망",
)
TRANSLATIONS = {
    **{
        f"8:{record_id}:{literal_id}": translation
        for record_id in range(260, 263)
        for literal_id, translation in enumerate(BOUNTY_GROUP)
    },
    "8:263:0": ", 올해는 흉작",
    "8:263:1": "\n미리 대책을 마련한 지역은\n화를 면하고",
    "8:264:0": "올해는 흉작이었으나, 이를 면한\n지역이",
    "8:264:1": ".",
    "8:264:2": "무슨 일이든 미리 대비해 두는 법이",
    "8:265:0": "흉작에도 끄떡없는 지역이",
    "8:265:1": "\n평소부터 대비를 게을리하지 않으시다니, 과연 훌륭한 일",
    "8:266:0": "올해에는 흉작이",
    "8:266:1": ",\n유비무환의 덕으로\n피해를 면한 지역이",
    "8:267:0": "올해는 흉작이었으나, 미리 손을 써 둔\n지역은 무사히 넘겼습니다",
    "8:267:1": "\n무슨 일이든 이처럼 대비해야 할 필요가",
    **{
        f"8:268:{literal_id}": translation
        for literal_id, translation in enumerate(DAMAGE_GROUP)
    },
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S494", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
