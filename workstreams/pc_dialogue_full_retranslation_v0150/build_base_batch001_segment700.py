#!/usr/bin/env python3
"""Build Base authoring segment 700 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S700.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s700", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:3132:0": "전선이 멀어져 버렸군\n원호하기 좋은 위치로 이동한다",
    "9:3133:0": "미안하지만, 그건 못 따르겠어",
    "9:3134:0": "송구하오나\n그 명은 받들 수 없소",
    "9:3135:0": "그것은 무리한 일이오\n다시 생각해 주시오",
    "9:3136:0": "받아들이기 어렵습니다\n부디 전황 전체를 살펴 주십시오",
    "9:3137:0": "안 되는 것은 안 된다",
    "9:3138:0": "그리할 수는 없소\n다시 생각해 주시오",
    "9:3139:0": "명령이라 하셔도\n그 명에는 따를 수 없소",
    "9:3140:0": "농담을 하시는 것이오?\n그것은 들어드릴 수 없소",
    "9:3141:0": "죄송합니다만\n그것은 할 수 없습니다…",
    "9:3142:0": "미안하나, 그건 들어줄 수 없소",
    "9:3143:0": "유감스럽지만 그 요청에는\n응해 드릴 수 없습니다…",
    "9:3144:0": "그것은 들어드릴 수 없소\n목숨을 헛되이 잃게 할 수는 없으니",
    "9:3145:0": "의 요충지가 함락됐어!?\n얼른 되찾아야 해!",
    "9:3146:0": "의 요충지가 함락됐다고!?\n당장 되찾아야 한다!",
    "9:3147:0": "의 요충지가 함락됐나…\n서둘러 되찾아야겠군",
    "9:3148:0": "의 요충지를 빼앗기다니…\n신속히 탈환책을 세워야 한다",
    "9:3149:0": "의 요충지를 빼앗겼다고!?\n서둘러 되찾아야 한다!",
    "9:3150:0": "의 요충지가 함락됐나\n되찾을 방도를 마련해야겠군",
    "9:3151:0": "의 요충지가 함락됐다…?\n서둘러 탈환해야겠군",
    "9:3152:0": "의 요충지가 제압됐다고!?\n탈환을 서둘러야 한다…",
    "9:3153:0": "의 요충지가 함락됐다고?\n되찾을 방도를 마련해야겠어…",
}

DYNAMIC_RUNTIME_COORDINATES = {f"9:{record_id}:0" for record_id in range(3145, 3154)}
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
        static = coordinate in STATIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required" if static else "pending",
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
                "segment": "base_msggame_B001_S700",
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
