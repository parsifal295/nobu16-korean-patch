#!/usr/bin/env python3
"""Build Base authoring segment 235 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S235.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s235", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3809:0": "혼인 제의를 받아들이지\n이제 우리는 인척이 되었군\n오래도록 좋은 교분을 이어 가세",
    "6:3810:0": "이 또한 가문을 지키기 위해서다\n너무 모질게 대하진 말아 달라고",
    "6:3811:0": "이 또한 가문을 지키기 위함…\n아무쪼록 잘 부탁드리오",
    "6:3812:0": "가문을 지키기 위한 결단이다\n부끄러워할 까닭이 어디 있겠는가…",
    "6:3813:0": "이 또한 가문을 지키기 위함…\n아무쪼록 잘 부탁드리오",
    "6:3814:0": "이 또한 가문을 지키기 위함이오…\n아무쪼록 잘 부탁드리오",
    "6:3815:0": "…가문만 지킬 수 있다면 어떻게든 될 터\n부디 잘 보살펴 주시오",
    "6:3816:0": "이 또한 가문을 지키기 위함…\n부디 부탁드리오",
    "6:3817:0": "이 또한 가문을 지키기 위함이로다…\n부디 잘 부탁하네…",
    "6:3818:0": "이 또한 가문을 지키기 위함입니다…\n아무쪼록 잘 부탁드립니다…",
    "6:3819:0": "이 또한 가문을 지키기 위함…\n부디 잘 부탁하오",
    "6:3820:0": "이 또한 가문을 지키기 위함입니다…\n부디 잘 부탁드립니다",
    "6:3821:0": "이 또한 가문을 지키기 위함…\n아무쪼록 잘 부탁드리오",
    "6:3822:0": "우리 가문을 따르겠다는 뜻, 분명히 알겠",
    "6:3822:1": "\n의지해 오는 자를 어찌 거절하",
    "6:3823:0": "지금이 난세이기에 더욱\n신의 없는 자는 살아남지 못함을 알라!",
    "6:3824:0": "뭐라고, 우리와 단교하겠다고!",
    "6:3825:0": "뭐라, 우리와 단교할 셈인가",
    "6:3826:0": "뭐라…우리와 단교하다니 어리석군",
    "6:3827:0": "말도 안 됩니다!\n우리와 단교하겠다는 겁니까!",
}

STATIC_COORDINATES: set[str] = {
    "6:3809:0",
    "6:3810:0",
    "6:3811:0",
    "6:3812:0",
    "6:3813:0",
    "6:3814:0",
    "6:3815:0",
    "6:3816:0",
    "6:3817:0",
    "6:3818:0",
    "6:3819:0",
    "6:3820:0",
    "6:3821:0",
    "6:3823:0",
    "6:3824:0",
    "6:3825:0",
    "6:3826:0",
    "6:3827:0",
}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S235", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
