#!/usr/bin/env python3
"""Build Base authoring segment 703 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S703.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s703", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3196:0": "적의 기세에 휩쓸렸군요…\n더 싸워도 소용없습니다, 철수합시다",
    "9:3197:0": "이렇게까지 몰렸으니…\n철수한다!\u3000모두 살아서 돌아가라!",
    "9:3198:0": "완패라 할 수밖에 없겠군…\n모두를 서둘러 철수시켜라!",
    "9:3199:0": "힘으로 밀어붙이는 적에게 당할 줄이야…\n철수하라, 헛된 죽음은 용납하지 않겠다!",
    "9:3200:0": "이만하면 잘 버틴 편이로구나…\n모두, 지금은 철수하는 게다!",
    "9:3201:0": "이렇게 밀려서는…\n여러분, 철수해 주십시오!",
    "9:3202:0": "속수무책으로 당하고 말았군…\n분하지만 지금은 철수다…",
    "9:3203:0": "마구 짓밟히고 말았군요…\n여기서는 물러납시다…",
    "9:3204:0": "이제 승산은 없다\n철수다!\u3000모두 살아서 돌아가라",
    "9:3205:0": "물러나는 건…",
    "9:3205:1": "인가\n괜찮은 거냐…?",
    "9:3206:0": "님께서 패주하셨나?\n전투의 흐름을 잃으셨나",
    "9:3207:0": "이(가) 물러나고 있다\n무사히 물러나면 좋겠는데",
    "9:3208:0": "님께서 후퇴하고 계시다…\n가는 길이 걱정되는군요",
    "9:3209:0": "이(가) 물러나는가…\n적에게 붙잡히지 않아야 할 텐데",
    "9:3210:0": "후퇴하는 이는…",
    "9:3210:1": "인가\n무리는 금물이오",
    "9:3211:0": "이(가) 철수하는가\n아무 일도 없으면 좋겠는데",
    "9:3212:0": "이(가) 물러나고 있군…\n무사히 전열을 가다듬으면 좋겠는데",
    "9:3213:0": "후퇴하고 있는 이는…",
    "9:3213:1": "인가요?\n아무 일도 없어야 할 텐데요",
    "9:3214:0": "이(가) 후퇴하다니…?\n큰일로 번지지 않아야 할 텐데",
    "9:3215:0": "님께서 후퇴하고 계시다\n무사히 물러나시면 좋겠습니다만",
    "9:3216:0": "이(가) 물러나는가…\n무사히 물러나면 좋겠군",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:3205:0",
    "9:3205:1",
    "9:3206:0",
    "9:3207:0",
    "9:3208:0",
    "9:3209:0",
    "9:3210:0",
    "9:3210:1",
    "9:3211:0",
    "9:3212:0",
    "9:3213:0",
    "9:3213:1",
    "9:3214:0",
    "9:3215:0",
    "9:3216:0",
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
                "segment": "base_msggame_B001_S703",
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
