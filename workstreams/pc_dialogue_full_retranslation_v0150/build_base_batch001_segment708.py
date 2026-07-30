#!/usr/bin/env python3
"""Build Base authoring segment 708 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S708.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s708", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:3275:0": ", 사로잡히고",
    "9:3275:1": "…!\n그 밖에도 행방을 알 수 없는 자가 있다고…",
    "9:3276:0": ", 베어 죽였도다!",
    "9:3277:0": ", 사로잡았도다!",
    "9:3278:0": "보아하니…",
    "9:3278:1": "의 위치라면\n협격을 노려볼 만하겠군!",
    "9:3279:0": "의 빈틈을 찌를 호기입니다\n지금이라면 협격도 노릴 수 있습니다!",
    "9:3280:0": "에게서 빈틈이 보이는구려\n협격도 손쉬울 것이오",
    "9:3281:0": "의 부대를 격파할 절호의 기회입니다\n지금이라면 협격이 가능할 것입니다",
    "9:3282:0": "에게 일격을 가해야 하오!\n양쪽에서 협격합시다!",
    "9:3283:0": "적진에 빈틈이 보이는구려\n",
    "9:3283:1": "에게 협격을 가하는 것이 상책일 듯하오",
    "9:3284:0": "의 빈틈을 찌를 호기요!\n지금이라면 협격도 노릴 수 있겠구려!",
    "9:3285:0": "보아하니…",
    "9:3285:1": "의 위치라면\n아마 협격을 노릴 수 있겠소!",
    "9:3286:0": "협격할 절호의 기회이옵니다!\n",
    "9:3286:1": "의 빈틈을 노립시다",
    "9:3287:0": "협격할 때는 지금이다!\n",
    "9:3287:1": "에 대한 공격을 명하십시오!",
    "9:3288:0": "의 빈틈을 노립시다\n지금이라면 협격할 수 있을 것이오",
    "9:3289:0": "보아하니…",
    "9:3289:1": "의 위치라면\n아마 협격을 노릴 수 있겠소!",
    "9:3290:0": "고지에서 사격하는 건 어때?\n위에서 쏘면 마음껏 해치울 수 있지!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if not coordinate.startswith("9:3290:")
}
STATIC_COORDINATES = set(TRANSLATIONS).difference(DYNAMIC_RUNTIME_COORDINATES)


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
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_"
                    "context_where_available"
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
                "segment": "base_msggame_B001_S708",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
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
