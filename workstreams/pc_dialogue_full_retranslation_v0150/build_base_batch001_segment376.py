#!/usr/bin/env python3
"""Build Base authoring segment 376 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S376.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s376", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1119:0": "의 침공입니다\n주군께서 아무 대책 없이 싸움에 임하시지는 않겠지요\n다른 가문에서 원군을 부르시는 것이 어떠신지요……?",
    "7:1120:0": "이(가) 쳐들어왔습니다\n원군을 불러 유리하게 싸움을 이끄는 것……\n이것이야말로 주군의 현명한 판단에 부합할 듯합니다",
    "7:1121:0": "이(가) 쳐들어왔습니다\n외람되오나 적의 힘은 우리와 대등하니\n다른 가문의 원군을 빌리심이 어떠실지요",
    "7:1122:0": "이(가) 난입했다 하옵니다\n방심하면 좋지 않은 결과를 부를 것이니\n원군을 청해 만전을 기하시옵소서",
    "7:1123:0": "이(가) 쳐들어왔소이다\n정면으로 맞서기보다는\n다른 가문의 원군을 빌리시는 것이 어떠신지요?",
    "7:1124:0": "이(가) 난입하였소\n얕볼 수 없는 적…… 다른 가문에서 원군을 불러\n철저히 쳐부숩시다",
    "7:1125:0": "이(가) 쳐들어왔습니다\n만전의 태세로 맞아 싸워야 합니다\n다른 가문에서 원군을 부르도록 하지요",
    "7:1126:0": "이(가) 침입했습니다\n이곳은 다른 가문에 원군을 청해\n힘을 합쳐 몰아내야 할 듯합니다",
    "7:1127:0": "이(가) 내습했습니다!\n적과 아군의 전력은 팽팽하니\n다른 가문의 원군이 필요할 듯합니다",
    "7:1128:0": "의 침공입니다!\n다른 가문에서 원군을 부르도록 하지요\n이 어리석은 짓을 후회하게 만드는 겁니다",
    "7:1129:0": "이(가) 난입했습니다\n부디 원군을 청하시옵소서\n얕보았다가는 적에게 집어삼켜질 것이옵니다",
    "7:1130:0": "이(가) 쳐들어왔다 하옵니다\n방심할 수 없는 상대이니……\n원군과 함께 맞서시옵소서",
    "7:1131:0": "이(가) 쳐들어왔습니다\n단독으로 맞서기에는 버거운 상대이니\n다른 가문의 원군을 빌려야 할 듯하옵니다",
    "7:1132:0": "의 침공이오\n대책을 세운 뒤 맞서야 하오!\n다른 가문에서 원군을 불러오십시다",
    "7:1133:0": "강대한 「",
    "7:1133:1": "」의 침공……\n장수로서의 그릇이 시험받을 때가 왔군\n출진령을 내려라! 맞아 싸우자!",
    "7:1134:0": "이(가) 쳐들어왔는가\n적은 강대하고 아군은 약소하도다\n어쩔 수 없다! 치고 나가리라!",
    "7:1135:0": "의 침공이옵니다!\n적은 강대하오나……\n겁을 내실 주군은 아니시겠지요?",
    "7:1136:0": "이(가) 접근하고 있사옵니다\n상당한 병력을 이끌고 왔군요\n우리는 사력을 다할 각오이옵니다",
    "7:1137:0": "이(가) 대군을 이끌고 내습했습니다!\n여기서 앉아만 있어서는\n무사의 면목이 서지 않사옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S376", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
