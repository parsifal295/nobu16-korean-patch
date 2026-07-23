#!/usr/bin/env python3
"""Build Base authoring segment 709 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S709.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s709", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:3291:0": "고지에서 사격하는 건 어떻겠소\n적을 마음껏 겨냥해 쏠 수 있소이다",
    "9:3292:0": "고지에서 쏘아 내려야 할 것이오\n화살 세례로 많은 적을 쓰러뜨릴 수 있소이다",
    "9:3293:0": "고지에서 쏘아 내리는 건 어떻소?\n사격으로 우위를 점합시다",
    "9:3294:0": "고지에서 쏘아 내릴 수 있소이다\n화살 비로 많은 적을 쓰러뜨립시다",
    "9:3295:0": "전망이 좋은 고지로군\n여기서 적에게 활을 쏘는 것도 한 방법이오",
    "9:3296:0": "고지에서 사격할 것을 제안하오\n전투를 유리하게 이끌 수 있을 것이오",
    "9:3297:0": "고지에서 쏘아 내리지 않겠소?\n힘들이지 않고 많은 적을 쓰러뜨릴 수 있소",
    "9:3298:0": "고지에서 사격하는 건 어떻겠습니까\n적을 마음껏 겨냥해 쏠 수 있습니다",
    "9:3299:0": "고지에서 쏘아 내려야 할 듯하오\n적을 골라 겨냥해 쏩시다",
    "9:3300:0": "고지에서 사격할 것을 제안합니다\n적의 수를 줄이는 데 가장 좋을 듯합니다",
    "9:3301:0": "고지에서 쏘아 내리는 건 어떻소?\n사격으로 우위를 점합시다",
    "9:3302:0": "요충지를 노리는 자가 있다\n누군가를 보내는 편이 좋겠다",
    "9:3303:0": "요충지를 노리는 적군이 있습니다\n즉시 대응해야 할 듯합니다",
    "9:3304:0": "적이 요충지를 노리는 듯하다\n서둘러 부대를 파견해야 한다",
    "9:3305:0": "적의 목표는 요충지인 듯합니다\n누군가를 보내 지키게 합시다",
    "9:3306:0": "적은 요충지를 노리고 있군\n부대를 일부 떼어 대비해야 할 듯하오",
    "9:3307:0": "요충지를 노리는 무리가 있습니다\n미리 손을 써 두어야겠군요",
    "9:3308:0": "요충지로 향하는 적군이…\n서둘러 대응해야 할 것입니다",
    "9:3309:0": "요충지를 노리는 괘씸한 자가 있습니다\n부대를 보내야 할 것입니다",
    "9:3310:0": "적이 요충지를 노리는 듯합니다\n즉시 대응합시다!",
    "9:3311:0": "적이 요충지를 노린다고!?\n즉시 요격해야 하오!",
    "9:3312:0": "적군이 요충지로 향하고 있습니다\n누군가에게 수비를 맡깁시다",
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
                "segment": "base_msggame_B001_S709",
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
