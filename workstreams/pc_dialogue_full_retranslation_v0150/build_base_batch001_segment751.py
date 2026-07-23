#!/usr/bin/env python3
"""Build Base authoring segment 751 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S751.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s751", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:142:0": "처, 천하를!?\n이건... 참으로 원대한 포부이십니다.\n하지만 그렇기에 보필할 보람도 있겠지요.",
    "13:143:0": "우리 가문은 아직 힘이 부족합니다\n천하를 노리려면 영토를 넓혀 국력을 기르고\n전국의 다이묘에게 힘을 인정받아야 합니다",
    "13:144:0": "영토를 넓히려면 타국에서 빼앗아야 한다\n그러면 당연히 전쟁이 벌어지겠지\n어떻게 승리를 거둘지 각자의 생각을 말해 보아라",
    "13:145:0": "알겠습니다\n그러면 무엇부터 아뢰올까요?",
    "13:146:0": "천하통일을 이루는 방법에 대하여",
    "13:147:0": "영지를 다스리는 방법에 대하여",
    "13:148:0": "가신의 신분에 대하여",
    "13:149:0": "이제 됐다, 수고했다",
    "13:150:0": "그렇다면 다음은",
    "13:151:0": "다음 의제는 무엇으로 하시겠습니까?",
    "13:152:0": "우선 이 지도를 살펴보십시오",
    "13:153:0": "이 어지러운 세상에서는\n수많은 다이묘가 저마다 영토를 차지하고\n전국 각지에 할거하고 있습니다",
    "13:154:0": "그들에게서 영토를 빼앗아 우리 것으로 삼으면\n천하통일에 한 걸음 더 가까워질 것입니다\n이를 위해 무력으로 적을 공격하는 것입니다",
    "13:155:0": "부대를 출진시켜 적의 성에 도착하면\n공성전이 시작됩니다\n제압에 성공하면 성과 주변 토지를 차지할 수 있습니다",
    "13:156:0": "적도 부대를 내보낼 수 있으므로\n전투가 벌어져도 승리할 수 있게\n충분한 전력을 갖춘 뒤 공격하는 것이 좋습니다",
    "13:157:0": "모든 성을 잃은 다이묘 가문은 멸망하고\n영토와 무장까지 빼앗기게 됩니다\n우리 가문이 멸망하지 않도록 주의해야 합니다",
    "13:158:0": "전국의 모든 성을 공략하려면\n헤아릴 수 없이 많은 전투가 필요하겠지\n대체 얼마나 시간이 걸릴지…",
    "13:159:0": "안심하십시오. 모든 세력을 멸망시키지 않아도\n천하를 제패할 수 있습니다\n구체적인 방법은 차차 설명드리겠습니다",
    "13:160:0": "영지 통치는 모든 일의 토대이며\n전쟁을 치르는 데에도 꼭 필요합니다\n바로 설명드리겠습니다",
}

B091_EXACT_REUSE = {
    "13:142:0": "처, 천하를!?\n이건... 참으로 원대한 포부이십니다.\n하지만 그렇기에 보필할 보람도 있겠지요.",
    "13:149:0": "이제 됐다, 수고했다",
    "13:150:0": "그렇다면 다음은",
    "13:151:0": "다음 의제는 무엇으로 하시겠습니까?",
}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」")


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def assert_scope(prepared: Any) -> None:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    source_records = ENGINE.archive_records(base.pristine_archive)
    current_records = ENGINE.archive_records(base.current_archive)
    source_count = len(ENGINE.parse_record_literals(source_records[(13, 142)]))
    current_count = len(ENGINE.parse_record_literals(current_records[(13, 142)]))
    if (source_count, current_count) != (2, 1):
        raise RuntimeError("merged-literal authority drifted at 13:142")
    if record_gaps(current_records[(13, 142)]) != (b"", b"\x05\x05\x05"):
        raise RuntimeError("merged current record retains an unexpected opcode: 13:142")
    source_blank = ENGINE.parse_record_literals(source_records[(13, 161)])
    current_blank = ENGINE.parse_record_literals(current_records[(13, 161)])
    if [literal.text for literal in source_blank] != [""] or [literal.text for literal in current_blank] != [""]:
        raise RuntimeError("13:161 must remain a single blank, undecided literal")
    if set(TRANSLATIONS) & {"13:161:0"}:
        raise RuntimeError("blank 13:161 must not receive a decision")
    if any(TRANSLATIONS[coordinate] != translation for coordinate, translation in B091_EXACT_REUSE.items()):
        raise RuntimeError("B091 exact-reuse translation drifted")
    base_155 = [literal.text for literal in ENGINE.parse_record_literals(source_records[(13, 155)])]
    pk_155_records = ENGINE.archive_records(pk.pristine_archive)
    pk_155 = [literal.text for literal in ENGINE.parse_record_literals(pk_155_records[(13, 155)])]
    if base_155 == pk_155 or "공성전" not in TRANSLATIONS["13:155:0"]:
        raise RuntimeError("13:155 must retain Base-specific siege-battle authority")
    if len(TRANSLATIONS) != 19:
        raise RuntimeError("segment 751 must contain exactly 19 visible decisions")
    for translation in TRANSLATIONS.values():
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError("segment 751 must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 751 retains banned fullwidth punctuation")


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
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
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
                "segment": "base_msggame_B001_S751",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS),
                "dynamic_runtime_review_pending": 0,
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
