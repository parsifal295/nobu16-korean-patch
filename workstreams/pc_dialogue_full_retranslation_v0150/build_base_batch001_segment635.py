#!/usr/bin/env python3
"""Build Base authoring segment 635 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S635.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s635", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1819:0": "이대로 끌고 가게\n둘 수는 없으리라",
    "9:1820:0": "되찾을 방책을\n궁리해야 한다……",
    "9:1821:0": "구해 낼 방도가\n없는 건 아니지만……",
    "9:1822:0": "어디…… 구출할 방도가\n없으려나……?",
    "9:1823:0": "포박당한 치욕이라니\n참으로 안타깝구나……",
    "9:1824:0": "큰일이로다!\n어서 구해야 한다!",
    "9:1825:0": "어떻게든 구출하고\n싶은데 말이지요……",
    "9:1826:0": "에게서\n되찾아 오고 싶지만",
    "9:1827:0": "이(가)……\n구출하러 가야 한다!",
    "9:1828:0": "을(를)\n구할 방도가 없을까……",
    "9:1829:0": "걱정을 끼쳐서\n미안하군……",
    "9:1830:0": "상처까지 입고……\n면목이 없소",
    "9:1831:0": "마음 써 주니 고맙소……",
    "9:1832:0": "송구합니다, 상처가……\n다소 깊은 듯합니다",
    "9:1833:0": "방심하여 당하고 말다니……!",
    "9:1834:0": "커헉…… 윽……\n참으로 어처구니없는 일이군……",
    "9:1835:0": "각오가……\n부족했사옵니다……",
    "9:1836:0": "별것 아니다! 아직 멀쩡……\n아야야야……!",
    "9:1837:0": "송구합니다……\n심려를 끼쳐 드렸습니다……",
    "9:1838:0": "미안하오……\n방심했소……",
    "9:1839:0": "염려해 주시니\n황송할 따름입니다……",
    "9:1840:0": "의 탓에……\n면목이 없소……",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1826:0",
    "9:1827:0",
    "9:1828:0",
    "9:1840:0",
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
                "segment": "base_msggame_B001_S635",
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
