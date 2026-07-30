#!/usr/bin/env python3
"""Build Base authoring segment 745 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S745.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s745", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:50:0": "알겠네\n그런데 우리 가문의 외교 관계는\n어찌 되어 있는가?",
    "13:51:0": "현재 우리 가문은\n",
    "13:51:1": "에 종속되어",
    "13:52:0": "지금은 '",
    "13:52:1": "'의 비호 아래에서\n차분히 힘을 기르며\n독립할 기회를 엿보는 것이 상책...",
    "13:53:0": "이(가) 우리 가문의 지배 아래에",
    "13:53:1": "\n원군을 보내게 하는 등 영토 확장을 추진할 때\n최대한 활용하는 것이 좋을 듯하옵니다",
    "13:54:0": "현재 우리 가문은 '",
    "13:54:1": "'와(과) (",
    "13:54:2": "개월) 동안\n동맹 관계에",
    "13:55:0": "그 밖에도 우리 가문과 동맹을 맺은\n세력이 있습니다. 평정의\n'외교'에서 확인할 수 있습니다.",
    "13:56:0": "동맹이 유지되는 동안에는 공격받을 일이 없으니\n타국과의 싸움에 집중할 수 있겠지요",
    "13:57:0": "현재 우리 가문은 '",
    "13:57:1": "'와(과) 무기한\n동맹 관계에 있습니다",
    "13:58:0": "혼인으로 맺어진 관계이므로\n어느 한쪽이 파기하지 않는 한\n타국과의 싸움에 집중할 수 있을 것입니다",
    "13:59:0": "현 상황을 감안하면\n",
    "13:59:1": "와(과) 우호 관계를 맺어 두는 것이\n상책이라 생각합니다",
    "13:60:0": "흠\n가신을 파견해 친선을 도모해 봐도 좋겠군",
    "13:61:0": "다행히 주변에는 우리 가문에 필적할 만한\n대세력이 없습니다\n이참에 공세를 펼쳐도...",
    "13:62:0": "흠. 당장 공격할 것인가\n싸우지 않고 종속시킬 것인가...\n어느 쪽도 나쁘지 않은 방책이군",
    "13:63:0": "현재 우리 가문은 주변국과\n특별한 관계를 맺고 있지 않습니다",
    "13:64:0": "유사시에 동맹을 맺거나\n원군을 요청할 수 있도록\n미리 친선을 도모해 두는 것도 방법입니다",
    "13:65:0": "그렇다면 다음은",
    "13:66:0": "다이묘에게 직접 속하지 않고\n독립해서 행동하는 국인중...\n성가신 무리입니다",
    "13:67:0": "다만 잘 회유하면 전쟁 때\n원군을 보내 줄 것입니다. 친밀해지면\n우리 가문에 편입하는 것도 가능할지 모릅니다",
}

RUNTIME_RECORD_IDS = {51, 52, 53, 54, 57, 59}
DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in RUNTIME_RECORD_IDS
}
EXPECTED_LITERAL_COUNTS = {
    55: (2, 1),
}
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
    expected_opcodes = {
        51: (b"\x02\x50\x32", b"\x01\x43"),
        52: (b"\x02\x50\x32",),
        53: (b"\x02\x50\x32", b"\x01\x43"),
        54: (b"\x02\x50\x32", b"\x02\x32", b"\x01\x43"),
        57: (b"\x02\x50\x32",),
        59: (b"\x02\x50\x32",),
    }
    for record_id, opcodes in expected_opcodes.items():
        for opcode in opcodes:
            if opcode not in current_records[(13, record_id)].data:
                raise RuntimeError(f"expected live token is absent from 13:{record_id}: {opcode.hex()}")
    for translation in TRANSLATIONS.values():
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError("segment 745 must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 745 retains banned fullwidth punctuation")
    if "국인중" not in TRANSLATIONS["13:66:0"] or "호족" in TRANSLATIONS["13:66:0"]:
        raise RuntimeError("13:66 must use the central 国衆 term 국인중")
    if "종속" not in TRANSLATIONS["13:51:1"] or "종속" not in TRANSLATIONS["13:62:0"]:
        raise RuntimeError("13:51/62 must preserve the diplomatic system term 종속")
    if "회유" not in TRANSLATIONS["13:67:0"] or "편입" not in TRANSLATIONS["13:67:0"]:
        raise RuntimeError("13:67 must preserve 회유 and 편입 semantics")
    if any("당가" in translation for translation in TRANSLATIONS.values()):
        raise RuntimeError("segment 745 must use 우리 가문 for 当家")


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
                "segment": "base_msggame_B001_S745",
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
