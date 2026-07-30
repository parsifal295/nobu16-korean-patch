#!/usr/bin/env python3
"""Build Base authoring segment 727 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S727.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s727", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3655:0": "이 정도로 내 마음을 흔들 수 있을 줄 알았느냐",
    "9:3656:0": "강자와 싸우는 것이야말로 나의 바람이자\n싸움의 참맛이다!",
    "9:3657:0": "에게 도전하겠다는\n겁 모르는 자가 네놈이냐!",
    "9:3658:0": "놓치지 마라!\n철저히 짓밟아라!",
    "9:3659:0": "놈들과는 거의 호각이다!\n우선 가까운 요충지를 빼앗아\n적의 사기를 떨어뜨리자!",
    "9:3660:0": "전력 차는 거의 없사옵니다\n요충지를 빼앗아 적의 사기를 떨어뜨리면\n절로 승기가 보일 것이옵니다",
    "9:3661:0": "전력은 백중지세입니다\n착실히 요충지를 함락해 나가며\n적의 사기를 꺾는 것이 좋을 듯합니다",
    "9:3662:0": "전력은 호각이라 할 수 있겠소\n요충지를 함락해 적의 사기를 떨어뜨리면\n승리가 보일 것이오",
    "9:3663:0": "전력은 백중지세\n요충지를 제압해 적의 사기를 떨어뜨리고\n합전을 유리하게 이끌고 싶군",
    "9:3664:0": "전력에 큰 차이는 없사옵니다\n수비가 허술한 요충지부터 무너뜨려\n적의 사기를 꺾는 것이 승리의 길인 줄로 아옵니다",
    "9:3665:0": "전력은 백중지세라 방심할 수 없습니다\n요충지 확보를 우선해\n적의 사기를 떨어뜨리는 것이 좋겠습니다",
    "9:3666:0": "전력은 호각이로군요\n요충지를 함락해 적의 사기를 떨어뜨리는 것이\n승리의 관건이 되겠지요!",
    "9:3667:0": "전력은 백중지세입니다\n함락할 수 있는 요충지부터 제압해 나가며\n적의 사기를 떨어뜨리면 승기가 보일 것입니다",
    "9:3668:0": "전력은 호각이라 할 만하다\n요충지를 차례로 무너뜨려\n적의 사기를 떨어뜨린 뒤에는 쳐부수기만 하면 된다",
    "9:3669:0": "전력은 백중지세이옵니다\n요충지를 얼마나 제압해 사기를 떨어뜨리느냐가\n승패의 갈림길이 될 것이옵니다",
    "9:3670:0": "전력은 백중지세입니다\n수비가 허술한 요충지부터 차례로 제압해\n적의 사기를 떨어뜨리는 것이 상책일 듯합니다",
    "9:3671:0": "전력은 호각이라 할 만하군",
    "9:3671:1": "\n적장 「",
    "9:3671:2": "」, 싸움에 능하기로 이름난 무장이니\n주의해 맞서야 할 것입니다",
    "9:3672:0": "전력은 호각이라 할 만하군",
    "9:3672:1": "\n적장 「",
    "9:3672:2": "」, 맹장으로 이름 높으니\n어설픈 부대로는 단숨에 짓눌리",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:3657:0",
    "9:3671:0",
    "9:3671:1",
    "9:3671:2",
    "9:3672:0",
    "9:3672:1",
    "9:3672:2",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
                "segment": "base_msggame_B001_S727",
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
