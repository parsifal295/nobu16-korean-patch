#!/usr/bin/env python3
"""Build Base authoring segment 519 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S519.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s519", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:522:0": "내 지행이 이 정도인가…\n아직 신용을 얻지 못한 모양이군요",
    "8:523:0": "이 지행조차 감당하지 못한다고 여기시지 않도록\n힘쓸 생각이옵니다…",
    "8:524:0": "이 정도 지행으로는 납득할 수 없다\n",
    "8:524:1": "에게도 지행을 더 나누어 주었으면 한다",
    "8:525:0": "지행을 맡겨 주신 안목은 훌륭하오… 다만\n나의 무용을 조금 더 높이 사 주시오",
    "8:526:0": "생각보다 나의 평가가 낮은 모양이군…",
    "8:527:0": ", 속내는 다 알고 있사옵니다\n제 재주를 온전히 발휘하게 하시려고\n지행을 더 내리고 싶으신 것이지요?",
    "8:528:0": "으음, 지행을 조금 더 받을 줄 알았건만…",
    "8:529:0": "지행을 더 받아도 문제없지요?\n「다다익선」이라 하지 않습니까",
    "8:530:0": "지행이 적군…\n아직 남은 땅이 있지 않은가",
    "8:531:0": "참으로 이 몸을 배려해 주시는군요\n이 정도 지행쯤이야 거뜬하고말고요\n아직 더 맡겨 주십시오!",
    "8:532:0": "아직도 인정받지 못했다는\n뜻이겠습니까…",
    "8:533:0": "더욱더 많은 지행을 받아\n더욱더 큰 도움이 되고 싶사옵니다…",
    "8:534:0": "모자라…\n조금만 더 있다면…",
    "8:535:0": "인색하게 굴 것 없다\n지행을 더 내놓아도 좋지 않느냐?",
    "8:536:0": "제 능력에 걸맞은 대우라고는\n생각하고 싶지 않습니다만…",
    "8:537:0": "아직 제게 지행을 더 내리실 수\n있는 것이지요…?",
    "8:538:0": "제 평가가 낮은 듯합니다\n지행을 더 내려 주실 수 없겠습니까",
    "8:539:0": "아아, 감사하오!\n지행을 더 가증해 주신다면\n더욱 감사하겠소",
    "8:540:0": "지행을 더 받고 싶다만…\n부족한 몫은 타국에서 빼앗을 수밖에 없겠군",
    "8:541:0": "이걸로는 부족하다만…\n어쩔 수 없군",
    "8:542:0": "우리 가문에는 뛰어난 자가 많으니\n이 정도도 어쩔 수 없겠구려…",
    "8:543:0": "지행이 조금 더 있으면 무훈도 세우기 쉬울 텐데…\n어쩔 수 없는가",
    "8:544:0": "지행은 더 받고 싶다만\n우리 가문에 여유가 없구려…",
}

STATIC_COORDINATES = {
    "8:522:0",
    "8:523:0",
    "8:525:0",
    "8:526:0",
    "8:528:0",
    "8:529:0",
    "8:530:0",
    "8:531:0",
    "8:532:0",
    "8:533:0",
    "8:534:0",
    "8:535:0",
    "8:536:0",
    "8:537:0",
    "8:538:0",
    "8:539:0",
    "8:540:0",
    "8:541:0",
    "8:542:0",
    "8:543:0",
    "8:544:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S519", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
