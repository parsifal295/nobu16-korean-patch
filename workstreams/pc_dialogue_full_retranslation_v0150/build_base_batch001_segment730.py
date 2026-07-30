#!/usr/bin/env python3
"""Build Base authoring segment 730 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S730.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s730", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3697:0": "우익의 전진을 우선하는 포진입니다\n벼랑 위에 포진할 수 있다면\n중앙에서도 유리하게 싸울 수 있습니다",
    "9:3698:0": "좌익을 강화해 돌파를 꾀합니다\n신속히 적 우익을 격파하면\n호숫가에서 적의 배후를 칠 수 있습니다",
    "9:3699:0": "좌익을 전방에 포진시켜\n신속히 언덕을 장악하려는 것입니다\n호숫가의 적진 돌파도 좋은 방책일 듯합니다",
    "9:3700:0": "우익의 가도를 제압하는 포진입니다\n먼저 가도의 길목을 장악하면\n언덕 점령도 쉬워질 것입니다",
    "9:3701:0": "퇴각로 근처에서 적을 요격합니다\n공세에 지친 적이 물러나려 할 때\n그때가 바로 반격의 기회입니다",
    "9:3702:0": "좌익의 가도를 제압하는 포진입니다\n먼저 가도의 길목을 장악하면\n언덕 점령도 쉬워질 것입니다",
    "9:3703:0": "우익을 전방에 포진시켜\n신속히 언덕을 장악하려는 것입니다\n호숫가의 적진 돌파도 좋은 방책일 듯합니다",
    "9:3704:0": "퇴각로 근처에서 적을 요격합니다\n공세에 지친 적이 물러나려 할 때\n그때가 바로 반격의 기회입니다",
    "9:3705:0": "먼저 중앙을 장악하는 포진입니다\n도하하는 적을 차례로 공격하고\n맞은편 강기슭까지 추격해 치는 것이 좋겠습니다",
    "9:3706:0": "우익에 병력을 두텁게 배치해\n우안에서 적진으로 향합니다\n중앙은 적의 도하에 대비합시다",
    "9:3707:0": "좌익으로 언덕 점령을 노립니다\n전장을 내려다보는 고지를 빼앗으면\n싸움을 유리하게 이끌 수 있습니다 ",
    "9:3708:0": "먼저 중앙을 장악하는 포진입니다\n도하하는 적을 차례로 공격하고\n맞은편 강기슭까지 추격해 치는 것이 좋겠습니다",
    "9:3709:0": "좌익에 병력을 두텁게 배치해\n좌안에서 적진으로 향합니다\n중앙은 적의 도하에 대비합시다",
    "9:3710:0": "우익으로 언덕 점령을 노립니다\n전장을 내려다보는 고지를 빼앗으면\n싸움을 유리하게 이끌 수 있습니다 ",
    "9:3717:0": "다리에서 방어전을 벌이며 중앙을 장악합니다\n기회를 보아 다리를 불태워 끊으면\n적의 진군은 멈출 것입니다",
    "9:3718:0": "좌익을 강화해 퇴각로를 노립니다\n적이 다리를 불태워 퇴로를 끊지 못하도록\n중앙에서도 방어전을 펼쳐야 합니다",
}

NON_DISPLAY_TEXT = {
    "9:3711:0": "004_jinei_1_1",
    "9:3712:0": "004_jinei_1_2",
    "9:3713:0": "004_jinei_1_3",
    "9:3714:0": "004_jinei_2_1",
    "9:3715:0": "004_jinei_2_2",
    "9:3716:0": "004_jinei_2_3",
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
            source_text = list(ENGINE.parse_record_literals(pristine_records[(block_id, record_id)]))[literal_id].text
            current_text = list(ENGINE.parse_record_literals(current_records[(block_id, record_id)]))[literal_id].text
            if NON_DISPLAY_TEXT[coordinate] != source_text or source_text != current_text:
                raise RuntimeError(f"non-display identifier drift: {coordinate}")
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
                "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available"
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
                "segment": "base_msggame_B001_S730",
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
