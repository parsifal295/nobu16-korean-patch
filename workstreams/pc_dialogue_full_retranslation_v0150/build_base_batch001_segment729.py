#!/usr/bin/env python3
"""Build Base authoring segment 729 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S729.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s729", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3680:0": "아군은 상당히 열세인 데다\n적진에는 지장·",
    "9:3680:1": "까지 있어 빈틈없이 포진했습니다\n",
    "9:3680:2": "마저 속일 방책이 필요할지도 모릅니다…",
    "9:3681:0": "아군은 상당히 열세",
    "9:3681:1": ", 하지만\n적진에 이름난 장수는",
    "9:3681:2": "\n승산은 충분",
    "9:3681:3": "군",
    "9:3682:0": "퇴각로 파괴야말로\n승리로 가는 지름길",
    "9:3683:0": "요충지를 많이 제압해\n지리적 이점을 얻",
    "9:3684:0": "수비를 중시해\n견실하게 싸우",
    "9:3685:0": "강적과 맞서 싸우기를\n벌써부터 기다릴 수 없",
    "9:3686:0": "고전하는 아군이 있다면\n즉시 지원하",
    "9:3687:0": "좌익에 부대를 집중시켜\n적진 돌파와 포위를 꾀합니다\n중앙의 방어전도 긴요합니다",
    "9:3688:0": "중앙과 벼랑 위에 병력을 두텁게 배치해\n벼랑 아래로 진격해 오는 적을\n돌과 화살로 요격합니다",
    "9:3689:0": "우익을 두텁게 하고\n벼랑 위에서 적 중앙을 견제하며\n퇴각로 제압을 노리는 포진입니다",
    "9:3690:0": "우익에 부대를 집중시켜\n적진 돌파와 포위를 꾀합니다\n중앙의 방어전도 긴요합니다",
    "9:3691:0": "중앙과 벼랑 위에 병력을 두텁게 배치해\n벼랑 아래로 진격해 오는 적을\n돌과 화살로 요격합니다",
    "9:3692:0": "좌익을 두텁게 하고\n벼랑 위에서 적 중앙을 견제하며\n퇴각로 제압을 노리는 포진입니다",
    "9:3693:0": "주력으로 중앙 가도를 장악합니다\n적을 퇴각로까지 밀어붙이면\n남은 적은 없는 것이나 다름없습니다",
    "9:3694:0": "좌익의 전진을 우선하는 포진입니다\n벼랑 위에 포진할 수 있다면\n중앙에서도 유리하게 싸울 수 있습니다",
    "9:3695:0": "우익을 강화해 돌파를 꾀합니다\n신속히 적 좌익을 격파하면\n호숫가에서 적의 배후를 칠 수 있습니다",
    "9:3696:0": "주력으로 중앙 가도를 장악합니다\n적을 퇴각로까지 밀어붙이면\n남은 적은 없는 것이나 다름없습니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    f"9:{record_id}:{literal_id}"
    for record_id in range(3680, 3687)
    for literal_id in range(3 if record_id == 3680 else 4 if record_id == 3681 else 1)
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
                "segment": "base_msggame_B001_S729",
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
