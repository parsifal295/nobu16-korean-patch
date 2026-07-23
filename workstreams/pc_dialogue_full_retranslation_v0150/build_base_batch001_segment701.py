#!/usr/bin/env python3
"""Build Base authoring segment 701 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S701.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s701", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3154:0": "의 요충지가 함락되었다고!?\n이러고 있을 때가 아니다!",
    "9:3155:0": "의 요충지가 함락되다니…\n서둘러 탈환해야 한다",
    "9:3156:0": "의 요충지가 함락되었다고!?\n당장 탈환해야 한다…",
    "9:3157:0": "요충지가 함락됐나…\n제때 도착하지 못하다니 면목없군!",
    "9:3158:0": "구원하지 못하다니…\n요충지가 함락되면 군의 사기도 꺾이거늘…",
    "9:3159:0": "큭, 제때 도착하지 못했나!\n요충지를 빼앗기고 말다니…",
    "9:3160:0": "요충지는 적의 손에…\n구원하지 못했습니다…",
    "9:3161:0": "요충지가 적에게 넘어갔나…\n불찰이었구나",
    "9:3162:0": "요충지가 적의 것이 되었군…\n구해 주지 못하다니…",
    "9:3163:0": "요충지를 끝까지 지키지 못하다니…\n조금만 더 빨리 대응했더라면…",
    "9:3164:0": "으음, 제때 도착하지 못했군…\n요충지를 속수무책으로 내주다니…",
    "9:3165:0": "요충지가 함락된 건가…?\n구하지 못하다니…",
    "9:3166:0": "요충지가 함락되었다고!?\n제때 도착하지 못하다니 면목 없군…!",
    "9:3167:0": "요충지를 구하지 못하다니…\n조금만 더…",
    "9:3167:1": "이(가) 빨랐다면…",
    "9:3168:0": "요충지를 구원하지 못했나…\n구원조차 못 하다니 면목없군…",
    "9:3169:0": "퇴각로가 파괴되었다고!?\n각오를 굳힐 수밖에 없겠군…",
    "9:3170:0": "퇴로가 끊겼나…\n배수진을 치고 맞설 수밖에 없겠군…",
    "9:3171:0": "퇴로가 차단됐다고…?\n공세로 나서지 않으면 패한다…",
    "9:3172:0": "퇴각로를 빼앗겼습니까…\n만회할 방도를 강구해야…",
    "9:3173:0": "퇴로가 끊겼다면…\n사력을 다해 싸울 뿐…!",
    "9:3174:0": "흠, 퇴로가 차단됐나…\n체면을 따질 때가 아니군…",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:3154:0",
    "9:3155:0",
    "9:3156:0",
    "9:3167:0",
    "9:3167:1",
}


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
                "segment": "base_msggame_B001_S701",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
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
