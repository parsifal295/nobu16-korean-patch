#!/usr/bin/env python3
"""Build Base authoring segment 487 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S487.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s487", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:171:0": "제 영지가 발전하여\n영민들도 기뻐하고 있사옵니다",
    "8:172:0": "좋아, 맡겨 둬!\n번화한 땅으로 만들면 되는 거지",
    "8:173:0": "고맙다!\n멋지게 완성해 주마",
    "8:174:0": "에게 맡겨 주시옵소서\n타국이 부러워할 영지로 만들어 보이겠나이다",
    "8:175:0": "은(는) 「",
    "8:175:1": "」을(를)\n높이 평가해 주시는 것이로군",
    "8:176:0": "너그럽기만 해서는 통치할 수 없다\n백성에게는 당근과 채찍을",
    "8:177:0": "오오, 주군을 섬기길 잘했구나……",
    "8:178:0": "문제없습니다\n좋은 통치 방안을 떠올렸습니다",
    "8:179:0": "참으로 다스릴 보람이 있는 영지로군\n벌써부터 팔이 근질거리는구려",
    "8:180:0": "알겠사옵니다\n논밭을 늘려 풍요로운 영지로 만들겠습니다",
    "8:181:0": "이 지행이 있으면\n반드시 무훈을 세울 수 있으리라",
    "8:182:0": "사람이 오가는 영지로 만들면\n수입도 자연히 늘겠지요",
    "8:183:0": "에게 맡겨 두면 안심이라는 것을\n",
    "8:183:1": "께서는 알고 계신 듯하군",
    "8:184:0": "어떻게 다스리고 어떻게 지킬 것인가\n그 방도는 알고 있소이다",
    "8:185:0": "맡은 이상\n기대에 부응해야겠군",
    "8:186:0": "백성이 기뻐하도록\n분골쇄신하여 다스리겠소이다!",
    "8:187:0": "지행을 받게 되다니 고마운 일이로다\n이 은의는 반드시 갚아야지",
    "8:188:0": "맡겨 주십시오!\n풍요로운 땅으로 만들어 보이겠습니다",
}

STATIC_COORDINATES: set[str] = {
    *(f"8:{record_id}:0" for record_id in range(171, 174)),
    *(f"8:{record_id}:0" for record_id in range(176, 183)),
    *(f"8:{record_id}:0" for record_id in range(184, 189)),
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S487", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
