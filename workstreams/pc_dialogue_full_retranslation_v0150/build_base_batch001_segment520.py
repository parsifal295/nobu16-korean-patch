#!/usr/bin/env python3
"""Build Base authoring segment 520 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S520.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s520", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:545:0": "이 정도 지행에 만족할 그릇으로 보이고 싶지는 않지만\n내줄 밑천이 없다는 것은 알고 있어",
    "8:546:0": "제 공에 비하면 턱없이 부족하지만\n지금은 참을 수밖에 없겠군요…",
    "8:547:0": "당가의 영지를 헤아리면\n이것이 최선의 지행이라는 것은 알고 있습니다만…",
    "8:548:0": "더 받아도 좋으련만\n지금 형편을 생각하면 어쩔 수 없나…",
    "8:549:0": "이 지행으로는 무용을 마음껏 떨칠 수 없군\n…허나, 어쩔 수 없나",
    "8:550:0": "조금 더 높이 평가해 주셨으면 합니다만\n욕심을 내 봐야 소용없겠지요",
    "8:551:0": "내 재주로 당가의 영토를 넓히지 않고서는\n흡족한 지행을 얻을 수 없겠는가…",
    "8:552:0": "영지에 여유가 있다면\n지행을 더 가증해 주셨으면 합니다만…",
    "8:553:0": "이 지행에 불만이 없다면 거짓말이겠지만\n없는 것을 내놓을 수는 없겠지요",
    "8:554:0": "지행이 더 많다면\n훌륭히 다스려 보일 터인데 말이지",
    "8:555:0": "당가에 영지가 조금만 더 있었다면\n",
    "8:555:1": "께서는 제게 지행에 대한 불만 따위 품게 하지 않으셨을 텐데…",
    "8:556:0": "영지가 한정되어 있으니\n더 바라는 것은 단념할 수밖에 없겠네요…",
    "8:557:0": "지금은 어쩔 수 없다…\n언젠가 당가가 영지를 넓히는 날에는…!",
    "8:558:0": "분하구나… 당가의 영지가 더 넓었다면\n더 많은 지행을 받았을 터인데",
    "8:559:0": "싸움이다, 싸움! 영지를 빼앗아\n나를 만족시킬 지행을 내놓아라",
    "8:560:0": "더 큰 가증을 기대하고 있었습니다만\n지금 형편으로는 어렵겠군요…",
    "8:561:0": "조금 더 받고 싶습니다만…\n제 욕심만 내세울 수는 없지요…",
    "8:562:0": "지행을 조금 더 받고 싶지만…\n그 마음은 누구나 같겠지요…",
    "8:563:0": "당가의 영지가 빠듯한 것이다\n불만은 속으로 삼켜 두자…",
}

STATIC_COORDINATES = {
    *(f"8:{record_id}:0" for record_id in range(545, 555)),
    *(f"8:{record_id}:0" for record_id in range(556, 564)),
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S520", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
