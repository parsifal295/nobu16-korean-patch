#!/usr/bin/env python3
"""Build Base authoring segment 609 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S609.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s609", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1273:0": "뭐라고!?\n어디에 숨어 있었던 거냐!?",
    "9:1274:0": "적이라고!? 속은 거야?",
    "9:1275:0": "적이라고!?\n병사들을 매복시켜 두었는가!",
    "9:1276:0": "움직일 수가 없어…… 발이 묶였나!",
    "9:1277:0": "큭! 움직일 수 없다니……",
    "9:1278:0": "건방진 수작을……\n움직일 수 없다……!",
    "9:1279:0": "발이 묶인 겁니까……",
    "9:1280:0": "에잇!\n나아가라! 못 나아가겠느냐!",
    "9:1281:0": "이, 이래서는\n꼼짝할 수가 없다!",
    "9:1282:0": "당했군……\n발이 묶였구려……",
    "9:1283:0": "이게\n어찌 된 일이냐!",
    "9:1284:0": "윽……\n이래서는 움직일 수 없습니다",
    "9:1285:0": "아뿔싸!\n움직일 수 없다!",
    "9:1286:0": "이래서는\n움직일 수 없군요……!",
    "9:1287:0": "움직일 수 없다…… 적의 함정인가!",
    "9:1288:0": "우리 편이 되고 싶은 거냐?\n좋아!",
    "9:1289:0": "도우러 와 줘서 고맙다!",
    "9:1290:0": "호오, 도우러 왔는가……\n기특한 마음가짐이로구나",
    "9:1291:0": "가세해 주셔서 감사합니다",
    "9:1292:0": "이 고을 사람들도\n우리 편이다!",
    "9:1293:0": "왔는가……\n후후, 예상대로군",
    "9:1294:0": "오오, 우리에게\n가담하고 싶다는 말인가",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available"
                ),
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S609",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
