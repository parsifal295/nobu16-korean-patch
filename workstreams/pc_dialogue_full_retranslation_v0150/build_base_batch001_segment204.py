#!/usr/bin/env python3
"""Build Base authoring segment 204 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S204.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s204", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3489:0": "에잇, 아랫것들이 해이해졌구나!\n",
    "6:3489:1": "님께 훈공 1위를 내주다니 어쩔 셈이냐!\n더 악착같이 공을 세우지 못하겠느냐!",
    "6:3490:0": "으로(로)서 훈공 1위…\n최고의 영예라 할 수 있겠지요\n앞으로도 늘 이 자리를 지키고 싶습니다!",
    "6:3491:0": "정상에 올랐는가…\n기회를 준",
    "6:3491:1": "에게는\n감사를 이루 말할 수 없군…",
    "6:3492:0": "고생이 보답받을 때가 왔군요…\n",
    "6:3492:1": "을(를) 섬길 수 있어 행복합니다\n오래도록 곁에서 모시겠어요",
    "6:3493:0": "이토록 크게 중용해 주신\n",
    "6:3493:1": "의 깊은 은혜…\n평생 잊지 않겠사옵니다",
    "6:3494:0": "나날의 활약을 인정받",
    "6:3494:1": "는가\n앞으로도 한층 더 정진하",
    "6:3495:0": ",",
    "6:3495:1": "이(가)",
    "6:3495:2": "에…\n",
    "6:3495:3": "이(가) 이 판단을 후회하지 않도록\n지위에 부끄럽지 않은 활약을",
    "6:3496:0": "에게 승진의 기회가 찾아오다니\n참으로 감사한 일",
    "6:3496:1": "인가",
    "6:3497:0": "으로(로) 발탁해 주시다니…\n이에 자만하지 않고\n더 큰 훈공을 세워 나가",
    "6:3498:0": "쯤 되면\n책임도 그에 걸맞게 무거워지",
    "6:3498:1": "\n마음이 절로 다잡히는 기분이",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S204", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
