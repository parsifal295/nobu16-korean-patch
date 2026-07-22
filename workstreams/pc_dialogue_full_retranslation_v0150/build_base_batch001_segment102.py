#!/usr/bin/env python3
"""Build Base authoring segment 102 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S102.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s102", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1658:0": "돈이 모자라 정책을 유지할 수 없군요…\n일단 모든 정책을 백지로 돌려 두었습니다\n필요한 것만 추려 다시 발령해 주십시오",
    "6:1659:0": "금전이 부족하여\n정책을 유지할 수 없어 중지했습니다\n서둘러 재검토해 주십시오",
    "6:1660:0": "돈이 모자라 정책을 유지할 수 없는 듯하여\n미안하지만 모든 정책을 중지시켰소\n항목을 추려 신중히 다시 발령해 주시오",
    "6:1661:0": "금전 부족으로 정책을 유지할 수 없다는 보고가…\n우선 모든 정책을 중지시켰습니다\n우리 가문에 필요한 항목만 추려 다시 검토합시다",
    "6:1662:0": "돈이 모자라 정책을 유지할 수 없어\n발령했던 모든 정책을 중지했습니다\n되도록 서둘러 다시 검토해 주십시오",
    "6:1663:0": "유감스럽지만 금전 부족으로 정책을 유지하지 못해\n모든 정책을 중지할 수밖에 없었습니다\n모두를 위해 필요한 항목만 추립시다",
    "6:1676:0": "정책을 발령하여 세력을 강화합니다",
    "6:1677:0": "정책 변경을 확정하지 않았습니다\n변경 내용이 취소됩니다. 계속하시겠습니까?",
}

REPORT_FRAGMENTS: dict[int, tuple[str, str]] = {
    1664: (
        "금전 부족으로 재정을 유지할 수 없어\n다음 부문의 수준이",
        "감소했습니다\n권농",
    ),
    1665: (
        "돈이 모자라 살림이 쪼들리는군…\n다음 부문의 수준이",
        "떨어져 버렸어\n권농",
    ),
    1666: (
        "금전 부족으로 재정 유지가 어려워져\n다음 부문의 수준이",
        "감소한 듯합니다\n권농",
    ),
    1667: (
        "재정에 문제가 생긴 듯하오. 금전 부족으로\n다음 부문의 수준이",
        "감소했다고 하오\n권농",
    ),
    1668: (
        "재정에 문제가… 금전 부족으로 유지가 어려워져\n다음 부문의 수준이",
        "감소하고 말았습니다\n권농",
    ),
    1669: (
        "간략히 보고하겠습니다. 금전 부족으로 재정난이…\n그 결과 다음 부문의 수준이",
        "감소했다\n권농",
    ),
    1670: (
        "재정에 관해 보고가 있습니다. 금전 부족으로\n다음 부문의 수준이",
        "감소하였습니다\n권농",
    ),
    1671: (
        "보고드릴 것이 있습니다. 금전 부족에 따른 재정난으로\n다음 부문의 수준이",
        "감소했다고 합니다\n권농",
    ),
    1672: (
        "금전이 부족해 재정을 유지할 수 없게 되어서 말이야\n다음 부문의 수준이",
        "감소한 모양이구나\n권농",
    ),
    1673: (
        "금전 부족으로 재정을 유지할 수 없어\n다음 부문의 수준이",
        "감소했습니다\n권농",
    ),
    1674: (
        "금전 부족으로 재정을 유지할 수 없어\n다음 부문의 수준이",
        "낮아졌다고 합니다\n권농",
    ),
    1675: (
        "금전 부족으로 재정 유지가 어려워져\n다음 부문의 수준이",
        "감소한 듯합니다…\n권농",
    ),
}

for record_id, (opening, decrease) in REPORT_FRAGMENTS.items():
    TRANSLATIONS[f"6:{record_id}:0"] = opening
    TRANSLATIONS[f"6:{record_id}:1"] = decrease
    TRANSLATIONS[f"6:{record_id}:2"] = ", 상공"
    TRANSLATIONS[f"6:{record_id}:3"] = ", 토목"
    TRANSLATIONS[f"6:{record_id}:4"] = ", 문화"
    TRANSLATIONS[f"6:{record_id}:5"] = ", 치안"

DYNAMIC_RUNTIME_COORDINATES = {
    f"6:{record_id}:{literal_id}"
    for record_id in REPORT_FRAGMENTS
    for literal_id in range(6)
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
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
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
                "segment": "base_msggame_B001_S102",
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
