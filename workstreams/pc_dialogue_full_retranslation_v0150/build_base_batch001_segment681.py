#!/usr/bin/env python3
"""Build Base authoring segment 681 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S681.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s681", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:2711:0": "요충지는 우리가 차지하겠습니다\n승기를 끌어오는 겁니다",
    "9:2712:0": "저 요충지를 노린다!\n형세를 바꿔 주마",
    "9:2713:0": "모두, 요충지를 빼앗아라!\n차지하면 이긴 것이나 다름없다!",
    "9:2714:0": "요충지를 빼앗자!\n승리를 확실히 하리라!",
    "9:2715:0": "요충지를 장악하라!\n놈들을 더욱 몰아붙이리라",
    "9:2716:0": "요충지도 장악하겠습니다\n우리의 우세를 살립시다",
    "9:2717:0": "요충지를 빼앗는다!\n그리하면 승리는 눈앞이다!",
    "9:2718:0": "긴장을 늦추지 말고 공격하라\n요충지를 빼앗으러 간다",
    "9:2719:0": "여기서는 공격해야 한다\n지금 요충지를 빼앗는다",
    "9:2720:0": "여기서는 요충지를 노릴까\n유리해도 방심은 금물이다",
    "9:2721:0": "우세에 안주하지 않고\n요충지를 확보하겠습니다!",
    "9:2722:0": "우세하다고 자만하지 마라\n요충지를 차지하러 간다!",
    "9:2723:0": "요충지를 차지합시다\n빼앗으면 이긴 것이나 다름없습니다",
    "9:2724:0": "요충지를 제압하라!\n그리하면 이긴 것이나 다름없다!",
    "9:2725:0": "이렇게 된 이상 요충지를 노린다\n그것 말고는 승산이 없어",
    "9:2726:0": "요충지를 강습한다!\n달리 방도는 없다!",
    "9:2727:0": "앞으로 나아갈 수밖에 없다!\n요충지를 빼앗아라!",
    "9:2728:0": "요충지를 노리지 않고서는\n우리에게 승산이 없다…!",
    "9:2729:0": "요충지를 빼앗는다!\n달리 이길 방도는 없다!",
    "9:2730:0": "기사회생을 노린다!\n요충지를 빼앗아라!",
    "9:2731:0": "무리인 줄은 알고 있다\n그래도 요충지를 빼앗는다!",
    "9:2732:0": "아군은 열세다…\n요충지를 노릴 수밖에 없겠군",
}

DYNAMIC_RUNTIME_COORDINATES: set[str] = set()
STATIC_COORDINATES = set(TRANSLATIONS)


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
                "segment": "base_msggame_B001_S681",
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
