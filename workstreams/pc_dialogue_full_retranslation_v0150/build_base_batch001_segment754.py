#!/usr/bin/env python3
"""Build Base authoring segment 754 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S754.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s754", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:202:0": "대관 임명",
    "13:203:0": "본거지에 속한 군에는 대관을 임명할 수 있습니다\n대관의 판단에 따라 군이 발전합니다",
    "13:204:0": " > 임명 > 대관",
    "13:205:0": "본거지에 속한 군에 대관을\n임명해 주시겠습니까?",
    "13:206:0": "'군 개발' - 본거지의 군 -",
    "13:207:0": "다이묘가 있는 성(본거지)에 속한 영지(군)는\n다른 성과 달리 직접 개발을 명해야 합니다\n개발을 진행하여 국력을 높입시다",
    "13:208:0": " > 내정 > 군 개발",
    "13:209:0": "군의 발전은 영지 경영의 기초입니다\n본거지의 군을 발전시켜 수입을 늘리는\n방법을 확인해 봅시다",
    "13:210:0": "'성하 시설' - 성 강화 -",
    "13:211:0": "성에는 성하 시설을 지을 수 있습니다\n비용이 들지만\n취락보다 큰 효과를 기대할 수 있습니다",
    "13:212:0": " > 내정 > 성하 시설",
    "13:213:0": "군을 발전시키면 효과가 더 큰\n'성하 시설'을 건설할 수 있게\n됩니다. 지금 바로 지어 봅시다",
    "13:214:0": "'지행' - 군 부여 -",
    "13:215:0": "가신에게 군을 영지(지행)로 내리면\n각자의 판단으로 군을 발전시켜\n수입을 늘리는 데 힘씁니다",
    "13:216:0": " > 임명 > 지행",
    "13:217:0": "국력을 높이려면 가신에게 영지를 내리고\n군의 개발을 진행하는 것이 중요합니다\n'지행'을 시작해 봅시다",
    "13:218:0": "'공략 목표 설정'",
    "13:219:0": "공략할 성을 목표로 설정하면\n가신이 군비를 시작하여 출진할 때 유리해집니다",
    "13:220:0": " > 군사 > 공략 목표",
}

RUNTIME_RECORD_IDS = {204, 208, 212, 216, 220}
DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in RUNTIME_RECORD_IDS
}
EXPECTED_CURRENT_GAPS: dict[int, tuple[bytes, ...]] = {
    record_id: (b"\x02\x3c", b"\x05\x05\x05")
    for record_id in RUNTIME_RECORD_IDS
}
BASE_PK_DIVERGENT_RECORD_IDS = {203, 219}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」")


def record_gaps(record: Any) -> tuple[bytes, ...]:
    gaps: list[bytes] = []
    cursor = 0
    for literal in ENGINE.parse_record_literals(record):
        gaps.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def assert_scope(prepared: Any) -> None:
    base_resource = prepared.resources["base_msggame"]
    pk_resource = prepared.resources["pk_msggame"]
    current_records = ENGINE.archive_records(base_resource.current_archive)
    source_records = ENGINE.archive_records(base_resource.pristine_archive)
    pk_records = ENGINE.archive_records(pk_resource.pristine_archive)
    for record_id, expected in EXPECTED_CURRENT_GAPS.items():
        if record_gaps(source_records[(13, record_id)]) != expected:
            raise RuntimeError(f"pristine runtime skeleton drift: 13:{record_id}")
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current runtime skeleton drift: 13:{record_id}")
        if not TRANSLATIONS[f"13:{record_id}:0"].startswith(" "):
            raise RuntimeError(f"leading ASCII space must be preserved: 13:{record_id}:0")
    for record_id in BASE_PK_DIVERGENT_RECORD_IDS:
        source_literals = [literal.text for literal in ENGINE.parse_record_literals(source_records[(13, record_id)])]
        pk_literals = [literal.text for literal in ENGINE.parse_record_literals(pk_records[(13, record_id)])]
        if source_literals == pk_literals:
            raise RuntimeError(f"expected Base/PK source divergence is absent: 13:{record_id}")
        if len(source_literals) != 1:
            raise RuntimeError(f"Base source literal-count drift: 13:{record_id}")
    for translation in TRANSLATIONS.values():
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError("segment 754 must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 754 retains banned fullwidth punctuation")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_scope(prepared)
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
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_jp_en_sc_tc_context"
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
                "segment": "base_msggame_B001_S754",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "confirmed_non_display": 0,
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
