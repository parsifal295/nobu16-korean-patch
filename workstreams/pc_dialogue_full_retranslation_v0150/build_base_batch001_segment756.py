#!/usr/bin/env python3
"""Build Base authoring segment 756 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S756.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s756", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:242:0": '"외교"',
    "13:243:0": '외교의 핵심은 "중개"와 "신용"입니다.\n중개를 설정해 얻은 상대의 신용을 바탕으로\n동맹 등의 교섭을 진행할 수 있습니다.',
    "13:244:0": " > 외교 > 친선",
    "13:245:0": '내정 다음은 "외교"입니다\n다른 다이묘 가문과 우호 관계를 맺으면\n동맹 체결이나 원군 요청을 할 수 있사옵니다',
    "13:246:0": '"영내 제책"',
    "13:247:0": "영내를 발전시키기 위한 시책을 명합니다.\n노동력이나 금전을 소비하므로,\n사용할 때를 잘 판단합시다.",
    "13:248:0": " > 내정 > 영내 제책",
    "13:249:0": '군 개발이나 성하 시설 건설 외에도\n영내를 발전시키는 방법이 있습니다\n"영내 제책"을 활용해 봅시다',
    "13:250:0": '"논공행상"',
    "13:251:0": "가신은 활약에 따라 훈공을 얻습니다.\n계절마다 논공행상이 이루어지며,\n훈공이 충분한 무장은 승진합니다.",
    "13:252:0": " > 평정 > 논공행상",
    "13:253:0": "지난 계절의 논공행상이 이루어진 듯합니다\n누군가 승진했을지도 모릅니다\n확인해 봅시다",
    "13:254:0": '"상황 확인"',
    "13:255:0": "◇보고　…　자세력의 상황과 수지를 확인할 수 있다\n◇헌언　…　가신이 현 상황을 알려 준다",
    "13:256:0": '화면 오른쪽 위의 "보고" 또는 "헌언"',
    "13:257:0": "무엇을 해야 할지 막막하다면\n현 상황을 확인해 봅시다",
    "13:258:0": '"헌언"',
    "13:259:0": "언제든 가신의 헌언을 들을 수 있습니다.\n지금 해야 할 일 등을 알려 주므로\n망설여질 때는 귀를 기울여 봅시다.",
    "13:260:0": '화면 오른쪽 위의 "헌언"',
    "13:261:0": "지금 해야 할 일에 대해\n가신의 헌언을 들을 수 있소\n부디 귀를 기울여 주시오",
}

RUNTIME_RECORD_IDS = {244, 248, 252}
DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in RUNTIME_RECORD_IDS
}
EXPECTED_GAPS = {
    244: (b"\x02\x3c", b"\x05\x05\x05"),
    248: (b"\x02\x3c", b"\x05\x05\x05"),
    252: (b"\x02\x3c", b"\x05\x05\x05"),
}
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
    if 229 <= base_record_id <= 269:
        return base_record_id + 2
    raise RuntimeError(f"segment 756 record has no configured PK mapping: {base_record_id}")


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
            for record_id in range(242, 262)
            if [literal.text for literal in ENGINE.parse_record_literals(base_records[(13, record_id)])]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(13, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences != {255}:
            raise RuntimeError(
                f"segment 756 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    for record_id, expected in EXPECTED_GAPS.items():
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current literal/opcode boundary drifted: 13:{record_id}")
        literal = ENGINE.parse_record_literals(current_records[(13, record_id)])[0]
        if ENGINE.protected_signature(literal.text)["leading_whitespace"] != " ":
            raise RuntimeError(f"13:{record_id}:0 must preserve one leading ASCII space")
    for coordinate, translation in TRANSLATIONS.items():
        expected_u3000 = 4 if coordinate == "13:255:0" else 0
        if translation.count("\u3000") != expected_u3000 or "\r" in translation:
            raise RuntimeError(f"{coordinate} U+3000/CR contract drifted")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 756 retains banned fullwidth punctuation")
    if "중개" not in TRANSLATIONS["13:243:0"] or "주선" in TRANSLATIONS["13:243:0"]:
        raise RuntimeError("13:243 must use the public UI action term 중개")
    if "원군 요청" not in TRANSLATIONS["13:245:0"]:
        raise RuntimeError("13:245 must preserve the public UI term 원군 요청")
    if "성하 시설" not in TRANSLATIONS["13:249:0"]:
        raise RuntimeError("13:249 must preserve the public UI term 성하 시설")
    if "노동력" not in TRANSLATIONS["13:247:0"] or "노력이나" in TRANSLATIONS["13:247:0"]:
        raise RuntimeError("13:247 must preserve the public resource term 労力=노동력")
    if TRANSLATIONS["13:251:0"].count("훈공") != 2:
        raise RuntimeError("13:251 must preserve 勲功=훈공 twice")
    for record_id in (255, 256, 258, 259, 260, 261):
        if "헌언" not in TRANSLATIONS[f"13:{record_id}:0"]:
            raise RuntimeError(f"13:{record_id} must preserve 献言=헌언")
    if "진언" in "".join(TRANSLATIONS.values()) or "건의" in TRANSLATIONS["13:255:0"]:
        raise RuntimeError("segment 756 flattened 献言 into another counsel term")
    if len(TRANSLATIONS) != 20 or len(DYNAMIC_RUNTIME_COORDINATES) != 3:
        raise RuntimeError("segment 756 decision/classification count drifted")


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
                "segment": "base_msggame_B001_S756",
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
