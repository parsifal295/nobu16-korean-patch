#!/usr/bin/env python3
"""Build Base authoring segment 744 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S744.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s744", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:23:0": "그러기 위해서는 무엇보다\n병량을 비축해야 합니다.",
    "13:24:0": "이미 공격할 준비는 갖추었으나\n국력을 더 길러 두는 것도 한 방법일 듯하옵니다.",
    "13:25:0": "우리 가문 가까이에는\n",
    "13:25:1": "이(가) 자리 잡고",
    "13:26:0": "보다 더 강한 상대...\n맞설 만한 힘을 기르려면\n우선 내정에 힘써야 한다고",
    "13:27:0": "무엇을 하든 먼저 필요한 것은 돈입니다.\n돈이 없으면 세력을 넓힐 수도 없습니다.\n우선 내정을 재정비해 수입을 늘려야 합니다.",
    "13:28:0": "우리 가문은 먼저 타국을 공격할 수 있을 만큼\n국력을 기르는 것을 목표로 삼아야 합니다.\n당분간은 내정에 힘쓰는 것이 좋겠습니다.",
    "13:29:0": "그렇군\n그렇다면 이를 위한 방책은 무엇인가?",
    "13:30:0": "군을 강화하는 것은 어떻겠습니까?\n하나의 성은 여러 군으로 이루어져 있으니...",
    "13:31:0": "군의 금전 수입은 세력의 수입으로서 다이묘에게\n보내집니다. 병량은 성에 비축되며\n부대가 출진할 때 사용됩니다.",
    "13:32:0": "또한 모든 군을\n직접 돌볼 필요는 없습니다.",
    "13:33:0": "각 군은 가신에게 맡길 수 있으며, 각 무장은\n자신의 판단에 따라 자기 영지를 다스립니다.",
    "13:36:0": "그렇게 군의 개발이 차츰 진행되면\n생산성이 높아지고 재정도 넉넉해진다는\n것입니다.",
    "13:39:0": "그렇군, 군에 대해서는 이해했다\n그런데 가신에게 군을 맡기려면\n먼저 우리 가문의 현황을 정리해 두어야겠군",
    "13:40:0": "분부대로!\n그러면 무엇부터 시작할까요?",
    "13:42:0": "외교 관계에 대하여",
    "13:43:0": "신분에 대하여",
    "13:44:0": "가신에 대하여",
    "13:45:0": "이제 됐다, 수고했다",
    "13:46:0": "적국을 힘으로 멸하는 것만이\n천하로 나아가는 유일한 길은 아니다.",
    "13:48:0": "음\n싸우지 않는다는 선택도\n때로는 필요하겠지",
    "13:49:0": "외교로 타국과 우호 관계를 맺고\n동맹을 체결해 원군을 요청하는 것...\n이 또한 천하로 나아가는 중요한 수단입니다.",
}

RUNTIME_RECORD_IDS = {25, 26}
DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in RUNTIME_RECORD_IDS
}
EXPECTED_LITERAL_COUNTS = {
    24: (2, 1),
    27: (3, 1),
    28: (2, 1),
    30: (2, 1),
    40: (2, 1),
}
BLANK_RECORD_IDS = {34, 35, 37, 38, 41, 47}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」")


def assert_scope(prepared: Any) -> None:
    source_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    for record_id, expected in EXPECTED_LITERAL_COUNTS.items():
        actual = (
            len(ENGINE.parse_record_literals(source_records[(13, record_id)])),
            len(ENGINE.parse_record_literals(current_records[(13, record_id)])),
        )
        if actual != expected:
            raise RuntimeError(f"literal-count mapping drift at 13:{record_id}: {actual}")
    for record_id in BLANK_RECORD_IDS:
        literals = ENGINE.parse_record_literals(current_records[(13, record_id)])
        if any(ENGINE.is_visible_translation_candidate(literal.text) for literal in literals):
            raise RuntimeError(f"expected blank record became visible: 13:{record_id}")
    for opcode in (b"\x02\x50\x32", b"\x01\x43"):
        if opcode not in current_records[(13, 25)].data:
            raise RuntimeError(f"expected live token is absent from 13:25: {opcode.hex()}")
    if current_records[(13, 26)].data.count(b"\x01\x43") != 2:
        raise RuntimeError("13:26 must retain two live 0143 tokens")
    for translation in TRANSLATIONS.values():
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError("segment 744 must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 744 retains banned fullwidth punctuation")
    if any("당가" in translation for translation in TRANSLATIONS.values()):
        raise RuntimeError("segment 744 must use 우리 가문 for 当家")


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
                    "pristine_base_pc_jp_with_base_sc_tc_and_same_coordinate_pk_jp_en_sc_tc_context_where_available"
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
                "segment": "base_msggame_B001_S744",
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
