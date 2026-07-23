#!/usr/bin/env python3
"""Build Base authoring segment 731 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S731.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s731", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3719:0": "우익에 무게를 둔 포진입니다\n적을 강으로 몰아넣어 섬멸하고\n도하할 수 있다면 승리는 눈앞입니다",
    "9:3720:0": "다리에서 방어전을 벌이며 중앙을 장악합니다\n기회를 보아 다리를 불태워 끊으면\n적의 진군은 멈출 것입니다",
    "9:3721:0": "우익을 강화해 퇴각로를 노립니다\n적이 다리를 불태워 퇴로를 끊지 못하도록\n중앙에서도 방어전을 펼쳐야 합니다",
    "9:3722:0": "좌익에 무게를 둔 포진입니다\n벼랑 위에서 활을 쏠 수 있다면\n퇴각로를 장악하기도 수월합니다",
    "9:3735:0": "좌익을 미리 도하시킵니다\n요충지를 장악한 기세를 몰아\n적을 강으로 몰아넣읍시다",
    "9:3736:0": "우익으로 중앙의 요충지를 노립니다\n그곳을 장악하면 진퇴가 자유로워져\n우회도 돌파도 뜻대로 할 수 있습니다",
    "9:3737:0": "우익을 전진시켜 모래톱을 제압합니다\n여러 요충지를 아군이 굳게 지키면\n싸움을 유리하게 이끌 수 있습니다",
    "9:3738:0": "강 건너에 우익을 배치합니다\n요충지를 신속히 장악하면\n적의 퇴각로가 바로 지척입니다",
    "9:3739:0": "좌익으로 중앙의 요충지를 노립니다\n그곳은 마치 부채의 축과 같아\n장악하는 자가 싸움을 지배할 것입니다",
    "9:3740:0": "해안가의 좌익을 주공으로 삼습니다\n건너편 기슭에 우리 깃발이 나부끼면\n어떤 장수든 낯빛을 잃을 것이 분명합니다",
}

NON_DISPLAY_TEXT = {
    **{f"9:{3723 + offset}:0": f"006_jinei_{group}_{slot}" for offset, (group, slot) in enumerate(
        ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3))
    )},
    **{f"9:{3729 + offset}:0": f"007_jinei_{group}_{slot}" for offset, (group, slot) in enumerate(
        ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3))
    )},
}
NON_DISPLAY_COORDINATES = set(NON_DISPLAY_TEXT)
DYNAMIC_RUNTIME_COORDINATES: set[str] = set()


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    pristine_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    rows: list[dict[str, object]] = []
    coordinates = sorted(
        set(TRANSLATIONS) | NON_DISPLAY_COORDINATES,
        key=lambda value: tuple(int(part) for part in value.split(":")),
    )
    for coordinate in coordinates:
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        non_display = coordinate in NON_DISPLAY_COORDINATES
        if non_display:
            source_record = pristine_records[(block_id, record_id)]
            current_record = current_records[(block_id, record_id)]
            source_text = list(ENGINE.parse_record_literals(source_record))[literal_id].text
            current_text = list(ENGINE.parse_record_literals(current_record))[literal_id].text
            if (
                NON_DISPLAY_TEXT[coordinate] != source_text
                or source_text != current_text
                or not source_text.isascii()
                or source_record.data != current_record.data
                or not source_record.data.startswith(b"\x1bH\x07\x07\x01")
            ):
                raise RuntimeError(f"non-display formation identifier drift: {coordinate}")
        row: dict[str, object] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "base_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256": target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
            "semantic_review": "approved",
            "scope_classification": "confirmed_non_display" if non_display else "retranslated",
            "layout_review": "unchanged_from_current",
            "runtime_review": "not_required",
            "basis": (
                "pristine_base_pc_jp_with_base_sc_tc_and_exact_pk_record_context_where_available"
            ),
            "historic_korean_used": False,
            "switch_korean_used": False,
        }
        if not non_display:
            row["translation"] = TRANSLATIONS[coordinate]
        rows.append(row)
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    expected_count = len(TRANSLATIONS) + len(NON_DISPLAY_COORDINATES)
    if len(validated) != expected_count:
        raise RuntimeError("validated decision count differs from the segment decision count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S731",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS),
                "dynamic_runtime_review_pending": 0,
                "confirmed_non_display": len(NON_DISPLAY_COORDINATES),
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
