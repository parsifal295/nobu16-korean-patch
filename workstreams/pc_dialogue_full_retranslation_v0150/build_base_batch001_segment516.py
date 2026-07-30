#!/usr/bin/env python3
"""Build Base authoring segment 516 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S516.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s516", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:473:0": "후회가 없다고는 할 수 없으나,\n",
    "8:473:1": "이(가) 할 수 있는 일은 다 했다고 믿자…",
    "8:474:0": "언제 끝날지도 모르는 삶이었으나\n잘 살아왔다고 해도 되려나…",
    "8:475:0": "그저 살아가기에는 길고, 무언가 이루기에는 짧은 것\n그것이 사람의 삶이라는 게지…",
    "8:476:0": "후후, 이 지경에 이르러서도 아직 삶을 바라다니\n참으로 추한 노릇이로구나…",
    "8:477:0": "제 손은 끝내 천하에 닿지 못했습니다…\n미련은 남지만 어쩔 도리가 없군요…",
    "8:478:0": "제 삶은 이로써 끝나지만, 우리 가문을\n다음 대에 물려준 것은 자랑해도 되겠지요…",
    "8:479:0": "후후, 전장에서 죽는 것이 꿈이었건만\n이제는 몸이 움직이지 않으니, 단념해야겠군…",
    "8:480:0": "최후는 전장에서 화려하게 맞으리라 여겼건만\n사람의 삶이란 뜻대로 되지 않는 법이로다…",
    "8:481:0": "여기가 저의 끝인가요…\n힘이 닿는 데까지 다했다고 생각했습니다만…",
    "8:482:0": "저는 여기까지인 듯하군요…\n뒷일을, 우리 가문을 부탁드립니다…",
    "8:483:0": "이 전란의 세상을 살아남았으니, 그것만은\n내 삶에서 자랑으로 삼아도 되겠지…",
    "8:484:0": "아아, 아직 죽고 싶지 않은데…\n못다 한 일이 너무도 많구나…",
    "8:485:0": "헤헤, 「",
    "8:485:1": "」을 따라 더\n실컷 날뛰고 싶었는데…",
    "8:486:0": "미안하다, 이제 몸이 움직이질 않는군\n아아, 다시 전장에서 싸우고 싶었는데…",
    "8:487:0": "내 무용은 어디까지 이르렀던가…\n그 정점은 끝내 보지 못할 곳에 있었구려…",
    "8:488:0": "내 무용이 「",
    "8:488:1": "」께 조금이나마 보탬이 되었다면\n이번 생에 여한은 없사옵니다…",
    "8:489:0": "을(를) 천하인으로 만드는 것이 제 꿈이었으나\n제 힘이 미치지 못하여 송구하옵니다…",
}

STATIC_COORDINATES = {
    f"8:{record_id}:0"
    for start, end in ((474, 484), (486, 487))
    for record_id in range(start, end + 1)
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S516", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
