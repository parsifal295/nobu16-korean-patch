#!/usr/bin/env python3
"""Build Base authoring segment 582 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S582.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s582", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:689:0": "전의가 바닥까지 떨어지다니\n나도 참 꼴사납군……",
    "9:690:0": "병사들이 무너져서는 싸울 수 없다……\n물러나는 게다",
    "9:691:0": "죄송합니다……\n물러나겠습니다……",
    "9:692:0": "큭, 후퇴한다\n이 빚은 반드시……",
    "9:693:0": "죄송합니다……\n여기서 물러나겠습니다",
    "9:694:0": "면목이 없소\n물러나겠소",
    "9:695:0": "이봐……거짓말이지……!?",
    "9:696:0": "아직 은혜를 갚지도\n못했건만……",
    "9:697:0": "주군……전사하신 것인가……",
    "9:698:0": "이건……예상 밖이었습니다",
    "9:699:0": "이놈들……!\n이 원수는 반드시 갚겠다……!",
    "9:700:0": "주군께서 전사하시다니……\n이러고 있을 수는 없군……",
    "9:701:0": "정말인가!?\n그럴 수가……!",
    "9:702:0": "주군……애통하옵니다……!",
    "9:703:0": "거짓말……어째서 주군께서……",
    "9:704:0": "말도 안 된다!?\n",
    "9:704:1": "은(는) 인정할 수 없다……",
    "9:705:0": "어찌하여 이런 일이……",
    "9:706:0": "주군께서 전사하셨다고!?\n말도 안 된다……",
    "9:707:0": "아직……뒈질 수는……\n없……다……!",
    "9:708:0": "전사하는 것이야말로\n무사의 본망……!",
    "9:709:0": "의 목을……\n전공으로 삼아라……!",
    "9:710:0": "저승에서……\n기다리겠습니다……",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS) - {"9:704:0", "9:704:1", "9:709:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S582", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
