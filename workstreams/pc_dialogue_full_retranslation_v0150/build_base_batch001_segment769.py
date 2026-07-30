#!/usr/bin/env python3
"""Build Base authoring segment 769 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S769.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s769", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:509:0": '"군 약탈"',
    "13:510:0": (
        "영내의 군을 적에게 빼앗겼습니다.\n"
        "군을 빼앗기면 다음과 같은 악영향이 발생합니다.\n"
        "부대를 출진시켜 서둘러 탈환합시다.\n"
        "\n"
        "[군을 빼앗기면]\n"
        "·취락 장악이 해제된다\n"
        "·개발 용지의 취락이 파괴된다\n"
        "·영주가 일시적으로 해임된다"
    ),
    "13:511:0": '"막부와의 외교"',
    "13:512:0": (
        "막부(다이묘가 정이대장군인 세력)와 외교하여 역직을 얻을 수 있습니다.\n"
        "역직을 얻어 위신이 높아지면 여러 이점이 생깁니다.\n"
        "※막부 세력과는 거리에 상관없이 외교할 수 있습니다\n"
        "\n"
        "【위신을 높이는 이점】\n"
        "·정책을 발령할 수 있다\n"
        "·상대보다 위신이 높으면 침공한 적병이 위축되어 유리하게 싸울 수 있다\n"
        "·자신보다 위신이 낮은 세력과의 외교가 유리해진다"
    ),
    "13:513:0": '"포진 변경"',
    "13:514:0": (
        "포진 변경에서는 합전 시작 시 부대 배치를 바꿀 수 있습니다.\n"
        "강력한 부대는 특수 요충지나 방비가 약한 경로의 전선에 두는 것이 좋습니다.\n"
        "◆전방 부대의 주요 역할\n"
        "·초반 적과 접촉하고 전선을 구축한다\n"
        "·퇴각로와 요충지를 공략한다\n"
        "◆후방 부대의 주요 역할\n"
        "·퇴각로와 요충지를 방어한다\n"
        "·체력이 줄어든 전방 부대와 교대한다"
    ),
    "14:3:0": "자세히 알아보기:",
    "14:4:0": "[메인 화면 보는 법]",
    "14:4:1": (
        "\n"
        "메인 화면에는 다음 항목이 표시됩니다.\n"
        "·시간 진행 버튼\n"
        "·세력 정보\n"
        "·보조 명령\n"
        "·행동 목록\n"
        "·부대 목록\n"
        "·국인중\n"
        "·부대\n"
        "·로그"
    ),
    "14:5:0": "[시간 진행/정지]",
    "14:5:1": (
        "\n"
        "게임 내 시간을 진행하거나 정지할 수 있습니다.\n"
        "진행 중에 누르면 정지하고, 정지 중에 누르면 진행을 시작합니다.\n"
        "진행 속도는 3단계 중에서 선택할 수 있습니다."
    ),
    "14:6:0": "[세력 정보]",
    "14:6:2": "㊤",
    "14:6:3": (
        "금전 … 다이묘 군단의 금전\n"
        "       성하 시설과 정책 등 주로 내정에 사용\n"
        '       군의 "상업"을 높이면 수입이 증가\n'
        "\u3000"
    ),
    "14:6:4": "㊥",
    "14:6:5": (
        "병량 … 본거지의 병량\n"
        "       출진할 때 사용\n"
        '       군의 "석고"를 높이면 수입이 증가\n'
        "\u3000"
    ),
    "14:6:6": "㈲",
    "14:6:7": (
        "위신 … 세력이 지닌 권위\n"
        "       위신이 높으면 전투에서 유리하고 정책을 발령할 수 있음\n"
        "\u3000"
    ),
    "14:6:8": "㈹",
    "14:6:9": (
        "노동력 … 다이묘 군단의 노동력\n"
        "       성하 시설, 건의, 군 개발 등을 실행할 때 사용\n"
        "       실행한 명령이 끝나면 소비한 노동력이 반환"
    ),
}

EXPECTED_GAPS = {
    (14, 4): (b"\x1b\x43\x49", b"\x1b\x43\x5a", b"\x05\x05\x05"),
    (14, 5): (b"\x1b\x43\x49", b"\x1b\x43\x5a", b"\x05\x05\x05"),
    (14, 6): (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x52",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x52",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x52",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x52",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
}
BASE_PK_DIVERGENCES = {
    "JP": {(13, 514), (13, 515), (13, 516)},
    "SC": {(13, 514), (13, 515), (13, 516), (14, 6)},
    "TC": {(13, 514), (13, 515), (13, 516)},
}
BLANK_LITERALS = {
    (13, 515, 0): "",
    (13, 516, 0): "",
    (14, 2, 0): "",
    (14, 6, 1): "\n\u3000",
}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）")
CONTROLLER_GLYPHS = set("㍑㌍㌦㍗㍍㎝㌣㌘㊤㊥㈲㈹┥┝")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
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


def mapped_pk_coordinate(block_id: int, record_id: int) -> tuple[int, int]:
    if block_id == 13:
        if 509 <= record_id <= 510:
            return 13, record_id + 44
        if 511 <= record_id <= 516:
            return 13, record_id + 45
    if block_id == 14:
        if 2 <= record_id <= 4:
            return 14, record_id
        if record_id == 5:
            return 14, 6
        if record_id == 6:
            return 14, 7
    raise RuntimeError(f"segment 769 record has no configured PK mapping: {block_id}:{record_id}")


def prior_translation(coordinate: str) -> str:
    for decision_path in sorted(OUTPUT.parent.glob("base_msggame_B001_S*.private.v1.jsonl")):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate:
                return str(row["translation"])
    raise RuntimeError(f"prior exact translation is absent: {coordinate}")


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in CONTROLLER_GLYPHS]


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
    scope_records = (
        [(13, record_id) for record_id in range(509, 517)]
        + [(14, record_id) for record_id in range(2, 7)]
    )

    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            coordinate
            for coordinate in scope_records
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[coordinate])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[mapped_pk_coordinate(*coordinate)]
                )
            ]
        }
        if divergences != BASE_PK_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 769 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    for coordinate, expected in EXPECTED_GAPS.items():
        if record_gaps(source_records[coordinate]) != expected:
            raise RuntimeError(f"pristine literal/opcode boundary drifted: {coordinate}")
        if record_gaps(current_records[coordinate]) != expected:
            raise RuntimeError(f"current literal/opcode boundary drifted: {coordinate}")

    expected_arities = {
        **{(13, record_id): 1 for record_id in range(509, 517)},
        (14, 2): 1,
        (14, 3): 1,
        (14, 4): 2,
        (14, 5): 2,
        (14, 6): 10,
    }
    for coordinate, expected_arity in expected_arities.items():
        source_literals = ENGINE.parse_record_literals(source_records[coordinate])
        current_literals = ENGINE.parse_record_literals(current_records[coordinate])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 769 literal arity drifted: {coordinate}")

    for (block_id, record_id, literal_id), expected_text in BLANK_LITERALS.items():
        source_text = ENGINE.parse_record_literals(source_records[(block_id, record_id)])[literal_id].text
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[literal_id].text
        if source_text != expected_text or current_text != expected_text:
            raise RuntimeError(f"blank/whitespace-only contract drifted: {block_id}:{record_id}:{literal_id}")
        if f"{block_id}:{record_id}:{literal_id}" in TRANSLATIONS:
            raise RuntimeError(f"blank/whitespace-only literal received a decision: {block_id}:{record_id}:{literal_id}")

    if source_records[(13, 512)].data != source_records[(13, 352)].data:
        raise RuntimeError("pristine exact reuse drifted: 13:512 != 13:352")
    if current_records[(13, 512)].data != current_records[(13, 352)].data:
        raise RuntimeError("current exact reuse drifted: 13:512 != 13:352")
    if TRANSLATIONS["13:512:0"] != prior_translation("13:352:0"):
        raise RuntimeError("13:512 must exactly reuse the approved 13:352 translation")

    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[literal_id].text
        if translation.count("\n") != current_text.count("\n"):
            raise RuntimeError(f"{coordinate} line-count contract drifted")
        if "\r" in translation:
            raise RuntimeError(f"{coordinate} must not add CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")
        if glyph_skeleton(translation) != glyph_skeleton(current_text):
            raise RuntimeError(f"{coordinate} controller-glyph skeleton drifted")

    expected_u3000 = {"14:6:3", "14:6:5", "14:6:7"}
    actual_u3000 = {
        coordinate for coordinate, translation in TRANSLATIONS.items() if "\u3000" in translation
    }
    if actual_u3000 != expected_u3000:
        raise RuntimeError("segment 769 protected U+3000 coordinates drifted")
    if any(TRANSLATIONS[coordinate].count("\u3000") != 1 for coordinate in expected_u3000):
        raise RuntimeError("segment 769 protected U+3000 count drifted")
    inherited_fullwidth_square = {
        coordinate
        for coordinate, translation in TRANSLATIONS.items()
        if "【" in translation or "】" in translation
    }
    if inherited_fullwidth_square != {"13:512:0"}:
        raise RuntimeError("segment 769 fullwidth square brackets escaped the prior exact reuse")
    if TRANSLATIONS["13:512:0"].count("【") != 1 or TRANSLATIONS["13:512:0"].count("】") != 1:
        raise RuntimeError("13:512 prior exact square-bracket pair drifted")
    if [TRANSLATIONS[f"14:6:{literal_id}"] for literal_id in (2, 4, 6, 8)] != [
        "㊤",
        "㊥",
        "㈲",
        "㈹",
    ]:
        raise RuntimeError("14:6 exact resource glyph literals drifted")
    if "◆전방 부대" not in TRANSLATIONS["13:514:0"] or "◆후방 부대" not in TRANSLATIONS["13:514:0"]:
        raise RuntimeError("13:514 must retain the Base JP branch markers")
    forbidden_pk_help = ("키를 누르면", "버튼을 누르면", "위치를 바꿀")
    if any(term in TRANSLATIONS["13:514:0"] for term in forbidden_pk_help):
        raise RuntimeError("13:514 imported the PK-only formation help")
    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "군",
        "정이대장군",
        "막부",
        "역직",
        "특수 요충지",
        "퇴각로",
        "병량",
        "노동력",
        "국인중",
        "건의",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 769 required terminology drifted")
    if "호족" in joined or "관직" in TRANSLATIONS["13:512:0"] or "노력" in joined:
        raise RuntimeError("segment 769 retains a forbidden legacy term")
    if len(TRANSLATIONS) != 20:
        raise RuntimeError("segment 769 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S769",
                "decision_count": len(rows),
                "retranslated": len(rows),
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
