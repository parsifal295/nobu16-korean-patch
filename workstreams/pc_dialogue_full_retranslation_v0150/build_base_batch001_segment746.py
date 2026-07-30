#!/usr/bin/env python3
"""Build Base authoring segment 746 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S746.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s746", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:71:0": "그렇군… 활용하기 나름이라는 말인가\n그렇다면 우리 영내에는 어떤\n국인중이 있는가?",
    "13:73:0": "은(는)\n현재로서는 아군이 되지 않을 것입니다\n더구나 타국에 붙을 수도 있는 상황입니다…",
    "13:74:0": "흠…\n회유할 필요가 있을지도 모르겠군\n성공하면 원군도 얻을 수 있겠지",
    "13:75:0": "은(는),",
    "13:75:1": "에게 우호적입니다\n전투가 벌어지면 원군을\n보내 줄 것입니다",
    "13:76:0": "더욱 회유한다면\n우리 가문으로 편입하는 것도 꿈은 아니옵니다",
    "13:77:0": "은(는)\n",
    "13:77:1": "을(를) 따르겠다는 뜻을 보이고 있습니다",
    "13:78:0": "우리 가문으로 편입하는 방안도\n검토해 두어야 한다고 생각합니다",
    "13:79:0": "현재 우리 영내에는\n눈여겨볼 만한 국인중이 없습니다",
    "13:80:0": "강력한 아군이 될 수 있으니\n인근의 국인중을 포섭하는 것도 좋겠습니다",
    "13:81:0": "다음 의제는 무엇으로 하시겠습니까?",
    "13:82:0": "같은 가신이라 해도\n여러 신분이 있었을 터인데…\n어디 보자… 무엇이었더라",
    "13:83:0": "낮은 순서부터\n조두, 아시가루 대장, 사무라이 대장, 부장, 가로, 숙로\n이렇게 여섯 신분이 있습니다",
    "13:84:0": "출세하려면 훈공이 필요합니다\n아무런 성과도 내지 못한 자를\n출세시킬 수는 없기 때문입니다",
    "13:85:0": "합전에서 활약하거나 군을 다스려\n훈공을 인정받으면 출세의 길이\n열린다는 말이군",
    "13:86:0": "하지만 군을 영지로 내리려면\n아시가루 대장 이상의 신분이 필요하다",
    "13:87:0": "우선 본거지에 속한 군의 대관으로\n훈공을 세우고 신분을 올린 뒤\n지행지를 맡기는 것이 좋겠습니다",
    "13:88:0": "가신의 신분이 올라가면\n성주나 군단장으로 임명하는 것도\n가능해집니다",
    "13:89:0": "눈여겨본 무장에게는 적극적으로\n일을 맡겨 훈공을 세우게 해야겠군!\n가신끼리 경쟁시키는 것도 좋겠어…",
    "13:90:0": "(가신들로서는 한시도 마음을 놓지 못하니\n　견딜 노릇이 아니겠지만…)",
    "13:91:0": "그런데 우리 가문의 가신 중에는\n어떤 자들이 있었더라?",
    "13:92:0": "참으로 유감스럽지만 우리 가문에는 딱히\n특기할 만한 가신이 없습니다. 우선\n재야 무장을 등용하여 진용을 갖춰야겠습니다…",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "13:73:0",
    "13:75:0",
    "13:75:1",
    "13:77:0",
    "13:77:1",
}
EXPECTED_GAPS = {
    73: (b"\x02\x8c\x32", b"\x05\x05\x05"),
    75: (b"\x02\x8c\x32", b"\x01\x43\x07\x00\x00\x00", b"\x05\x05\x05"),
    77: (b"\x02\x8c\x32", b"\x01\x43\x07\x00\x00\x00", b"\x05\x05\x05"),
}


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    if not literals:
        return (record.data,)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def assert_runtime_scope(prepared: Any) -> None:
    source_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    source_blank = ENGINE.parse_record_literals(source_records[(13, 72)])
    current_blank = ENGINE.parse_record_literals(current_records[(13, 72)])
    if [literal.text for literal in source_blank] != [""] or [literal.text for literal in current_blank] != [""]:
        raise RuntimeError("13:72 must remain a single blank, undecided literal")
    for record_id, expected in EXPECTED_GAPS.items():
        if record_gaps(source_records[(13, record_id)]) != expected:
            raise RuntimeError(f"pristine literal/opcode boundary drifted: 13:{record_id}")
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current literal/opcode boundary drifted: 13:{record_id}")
    if sum(value.count("\u3000") for value in TRANSLATIONS.values()) != 1:
        raise RuntimeError("segment must contain exactly one U+3000")
    if TRANSLATIONS["13:90:0"].count("\u3000") != 1:
        raise RuntimeError("13:90:0 must restore exactly one U+3000")
    if set(TRANSLATIONS) & {"13:72:0"}:
        raise RuntimeError("blank 13:72 must not receive a decision")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_runtime_scope(prepared)
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
                "segment": "base_msggame_B001_S746",
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
