#!/usr/bin/env python3
"""Build Base authoring segment 758 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S758.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s758", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:282:0": '"성하 시설"-시간 진행-',
    "13:283:0": "시간을 진행하여\n성하 시설 건설이 완료되기를\n기다려 봅시다.",
    "13:284:0": "왼쪽 위의 시간 진행 버튼(또는",
    "13:284:1": ")",
    "13:285:0": '성하 시설 건설을 명하셨군요\n"시간 진행"으로 시간을 진행하여\n경과를 지켜봅시다',
    "13:286:0": "금전 수입 늘리기",
    "13:287:0": "국력을 강화하려면 금전이\n필요합니다. 복습을 겸해 내정을 시행하여\n월 수지를 400 이상으로 올려 봅시다.",
    "13:288:0": "군 개발과 성하 시설 건설 실행",
    "13:289:0": "세력을 발전시키려면 금전이 필수입니다\n당분간 내정에 전념하여\n금전 수입을 늘려 봅시다",
    "13:290:0": "금전 수입 늘리기",
    "13:291:0": "복습을 겸해 두 달 정도 내정을 시행하여\n금전 수입을 늘려 봅시다.\n목표는 월 수입 100 증가입니다.",
    "13:292:0": "군 개발과 성하 시설 건설 실행",
    "13:293:0": "세력을 발전시키려면 금전이 필수입니다\n당분간 내정에 전념하여\n금전 수입을 늘려 봅시다",
    "13:294:0": '"대관 임명"',
    "13:295:0": '"대관" 명령으로 본거지의 군에 대관을 임명할 수 있습니다.\n대관은 스스로 군을 개발하고, 다이묘 부대의 일원으로 출진할 수도 있습니다.\n\n【대관 임명의 이점】\n◇개발 … 취락을 장악하거나 건설한다\n◇출진 … 다이묘 부대의 일원으로 출진할 수 있다',
    "13:296:0": "【추천 무장】\n◇성 능력 중시 … 능력이 높거나 다이묘와 상성이 좋은 무장\n◇특성 중시 … 상황에 알맞은 특성을 지닌 무장",
    "13:297:0": '"군 개발"-장악과 건설-',
    "13:298:0": "본거지의 군에서는",
    "13:298:1": "㊤금전",
    "13:298:2": "과",
    "13:298:3": "㈹노동력",
    "13:298:4": '을 소비하여 직접 군 개발을 명령할 수 있습니다.\n\n【명령의 종류】\n◇장악 … 기존 취락을 완전히 복속시켜 수입을 늘린다\n◇건설 … 새로운 취락을 건설한다\n\n※무엇을 할지 고민된다면 "시장"을 장악하여 금전 수입을 높여 봅시다\n※튜토리얼에서는 처음에 한해 비용과 노동력이 들지 않으며, 기간도 단축됩니다',
}

RUNTIME_RECORD_IDS = {284}
DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in RUNTIME_RECORD_IDS
}
EXPECTED_GAPS = {
    284: (b"", b"\x02\x3c", b"\x05\x05\x05"),
    298: (
        b"",
        b"\x1b\x43\x52",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x52",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
}
BLANK_RECORD_IDS = {299, 300}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
)


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def mapped_pk_record_id(base_record_id: int) -> int:
    if 282 <= base_record_id <= 284:
        return base_record_id + 21
    if 285 <= base_record_id <= 300:
        return base_record_id + 22
    raise RuntimeError(f"segment 758 record has no configured PK mapping: {base_record_id}")


def prior_translation(coordinate: str) -> str:
    decision_dir = OUTPUT.parent
    for decision_path in sorted(decision_dir.glob("base_msggame_B001_S*.private.v1.jsonl")):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate:
                return str(row["translation"])
    raise RuntimeError(f"prior exact translation is absent: {coordinate}")


def assert_scope(prepared: Any) -> None:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    source_records = ENGINE.archive_records(base.pristine_archive)
    current_records = ENGINE.archive_records(base.current_archive)
    pk_source_records = ENGINE.archive_records(pk.pristine_archive)
    base_context_records = {
        language: ENGINE.archive_records(archive)
        for language, archive in base.context_archives.items()
    }
    pk_context_records = {
        language: ENGINE.archive_records(archive)
        for language, archive in pk.context_archives.items()
    }

    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(282, 301)
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(13, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(13, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences:
            raise RuntimeError(
                f"segment 758 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )

    for record_id, expected in EXPECTED_GAPS.items():
        if record_gaps(source_records[(13, record_id)]) != expected:
            raise RuntimeError(f"pristine literal/opcode boundary drifted: 13:{record_id}")
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current literal/opcode boundary drifted: 13:{record_id}")

    for record_id in BLANK_RECORD_IDS:
        source_literals = ENGINE.parse_record_literals(source_records[(13, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(13, record_id)])
        if [literal.text for literal in source_literals] != [""]:
            raise RuntimeError(f"pristine blank classification drifted: 13:{record_id}")
        if [literal.text for literal in current_literals] != [""]:
            raise RuntimeError(f"current blank classification drifted: 13:{record_id}")
        if any(coordinate.startswith(f"13:{record_id}:") for coordinate in TRANSLATIONS):
            raise RuntimeError(f"blank record must not receive a decision: 13:{record_id}")

    duplicate_groups = ((286, 290), (288, 292), (289, 293))
    for left, right in duplicate_groups:
        if source_records[(13, left)].data != source_records[(13, right)].data:
            raise RuntimeError(f"pristine raw duplicate drifted: 13:{left} != 13:{right}")
        if current_records[(13, left)].data != current_records[(13, right)].data:
            raise RuntimeError(f"current raw duplicate drifted: 13:{left} != 13:{right}")
        if TRANSLATIONS[f"13:{left}:0"] != TRANSLATIONS[f"13:{right}:0"]:
            raise RuntimeError(f"duplicate translations differ: 13:{left}/13:{right}")

    prior_time = (
        prior_translation("13:228:0"),
        prior_translation("13:228:1"),
    )
    current_time = (TRANSLATIONS["13:284:0"], TRANSLATIONS["13:284:1"])
    if current_time != prior_time:
        raise RuntimeError("13:284 must exactly reuse the approved 13:228 button translation")
    if source_records[(13, 284)].data != source_records[(13, 228)].data:
        raise RuntimeError("pristine exact reuse drifted: 13:284 != 13:228")
    if current_records[(13, 284)].data != current_records[(13, 228)].data:
        raise RuntimeError("current exact reuse drifted: 13:284 != 13:228")

    for translation in TRANSLATIONS.values():
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError("segment 758 must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 758 retains banned fullwidth punctuation")
    if TRANSLATIONS["13:298:1"] != "㊤금전":
        raise RuntimeError("13:298 must preserve the gold glyph literal")
    if TRANSLATIONS["13:298:3"] != "㈹노동력":
        raise RuntimeError("13:298 must translate 労力 as 노동력 and preserve its glyph")
    if len(TRANSLATIONS) != 22 or len(DYNAMIC_RUNTIME_COORDINATES) != 2:
        raise RuntimeError("segment 758 decision/classification count drifted")


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
                "basis": BASIS,
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
                "segment": "base_msggame_B001_S758",
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
