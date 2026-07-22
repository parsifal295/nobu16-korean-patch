#!/usr/bin/env python3
"""Build Base authoring segment 150 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S150.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s150", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2756:1": "에 맞설 수도 있습니다",
    "6:2757:0": "우리가 지금 쓰러뜨려야 할 상대는,",
    "6:2757:1": "이다. 그렇다면\n여기서 그 실마리를 잡아야겠군",
    "6:2758:0": "눈앞의 적은,",
    "6:2758:1": "이지만 외교로도\n무언가 손을 쓸 수 있을 것이다",
    "6:2759:0": "영내를 돌보지 않으면 싸움도 못 하지. 그렇다고\n바깥일도 내팽개칠 수 없다니 성가신 일이야",
    "6:2760:0": "병량과 병사가 부족해. 지금은 정무에\n전념하고 싶은데, 외교도 정무란 말이지",
    "6:2761:0": "지금은 우리 가문의 힘을 키워야 할 때. 그렇다면\n외교도 소홀히 할 수는 없겠지",
    "6:2762:0": "내 무용에 걸맞은 병사를 기르려면\n외교로도 손을 써 두어야겠군",
    "6:2763:0": "언젠가 닥칠 쟁란의 때를 대비해\n교섭에도 힘을 쏟아야 하느니라",
    "6:2764:0": "안에 힘을 쏟아야 할 때일수록\n바깥으로도 눈을 돌려야 한다",
    "6:2765:0": "주된 적이 없는 지금이야말로\n바깥과의 교류를 중히 여겨야 한다",
    "6:2766:0": "지금은 정무에 힘을 쏟아야 할 때지만\n그렇다고 외교를 소홀히 할 수는 없다",
    "6:2767:0": "전쟁이 없어도 대비는 해야 한다\n이 외교도 그 일환이니라",
    "6:2768:0": "전쟁이 없으면 내 창이 녹슬겠지만\n전쟁만으로도 살아남지 못하지. 자, 외교다",
    "6:2769:0": "바깥과 교류해 적을 줄이고\n아군을 만든다. 이 또한 병마의 길이다",
    "6:2770:0": "흐음, 힘을 기를 때지만 외교를 통해\n다음 적과 아군을 가려낼 수도 있겠군",
    "6:2771:0": "적이라 부를 상대가 없다면 안으로 힘을 쏟는다\n하지만 바깥일도 내버려 둘 수는 없겠군",
    "6:2772:0": "정무에 힘을 쏟는 때일수록\n외교에서도 이득을 얻어야겠지",
    "6:2773:0": "적이 없을 때는 정무와 외교에 힘써야 하니\n마음 편히 쉴 틈도 없구나",
}

DYNAMIC_COORDINATES = {"6:2756:1", "6:2757:0", "6:2757:1", "6:2758:0", "6:2758:1"}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        dynamic = coordinate in DYNAMIC_COORDINATES
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved",
                     "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                     "layout_review": "unchanged_from_current", "runtime_review": "pending" if dynamic else "not_required",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S150", "decision_count": len(rows),
                             "retranslated": len(rows) - len(DYNAMIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
