#!/usr/bin/env python3
"""Build Base authoring segment 782 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S782.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s782", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:71:0": "[건의]",
    "14:71:1": (
        "\n"
        "건의는 상황에 따라 가신이 다이묘에게 올리는 제언입니다.\n"
        "승인하면 가신은 건의를 실행에 옮깁니다. 거부도 가능합니다.\n"
        "성주·대관·측근 무장이 건의합니다.\n"
        "\n"
    ),
    "14:71:2": "◇건의의 종류",
    "14:71:3": (
        "\n"
        "건의에는 몇 가지 종류가 있으며, 아이콘으로 구별할 수 있습니다.\n"
        "·고쇼의 건의 ...\u3000"
    ),
    "14:71:4": "┨",
    "14:71:5": "\u3000튜토리얼에서 다음에 할 일을 건의한다\n·조언 ...\u3000",
    "14:71:6": "┯",
    "14:71:7": (
        "\u3000상황에 따라 지금 해야 할 일을 건의한다\n"
        "·일반 건의 ... 가신이 필요하다고 판단한 일을 건의한다\n"
        "금전이나 노동력이 필요하며 실패할 수도 있다\n"
        "·세력 목표 건의 ... 현재 설정된 세력 목표를 표시한다"
    ),
    "14:72:0": "[머리 올리기]",
    "14:72:1": (
        "\n"
        '연초(1월)에 다이묘의 딸이 15세가 되면 "머리 올리기" 의식을 치릅니다.\n'
        '머리 올리기를 마친 딸은 "공주"로 세력에 합류합니다.\n'
        "이때 새 이름으로 바꿀 수도 있습니다.\n"
        "※단, 실존했던 공주는 이름을 바꿀 수 없습니다\n"
        "\n"
    ),
    "14:72:2": "[공주]",
    "14:72:3": (
        "\n"
        "공주는 가신이나 다른 세력과 혼인 관계를 맺어 세력 발전에 힘을 보탭니다.\n"
        "\n"
    ),
    "14:72:4": "◇공주가 할 수 있는 일",
    "14:72:5": (
        "\n\u3000"
        "·가신과의 결연\n"
        "·다른 세력과의 혼인\n"
        "\n"
    ),
    "14:72:6": "[공주 무장]",
    "14:72:7": (
        "\n"
        '시나리오 설정에서 "공주 무장: 있음"으로 설정했다면\n'
        '게임 중에 등장하는 공주는 "공주 무장"이 됩니다.\n'
        "공주 무장은 공주로서뿐 아니라 무장으로도 다룰 수 있습니다.\n"
        "\n"
    ),
    "14:72:8": "◇공주 무장이 할 수 있는 일",
    "14:72:9": (
        "\n\u3000"
        "·가신과의 결연, 다른 세력과의 혼인\n"
        "·무장과 마찬가지로 내정과 군사 등에 참여"
    ),
    "14:73:0": "[조작 설명]",
    "14:73:1": (
        "\n\u3000"
        "·왼쪽 클릭 ... 선택/결정\n"
        "·오른쪽 클릭 ... 명령 메뉴 열기(메인 화면)\n"
        "              취소\n"
        "              (각종 메뉴나 창을 열어 둔 상태)\n"
        "\n"
        "·왼쪽 버튼 길게 누르기+드래그 ... 카메라 이동\n"
        "·오른쪽 버튼 길게 누르기+드래그 ... 카메라 회전/각도 변경\n"
        "·마우스 휠 위아래 ... 카메라 확대/축소\n"
        "\n"
        "·Space 키 ... 시간 진행/정지(메인 화면)\n"
        "             ※시간 진행 버튼을 누른 것과 동일\n"
        "             ※각종 메뉴가 열려 있는 동안은 시간 정지\n"
        "·, 키 ... 시간 진행 속도를 낮춤\n"
        "·. 키 ... 시간 진행 속도를 높임\n"
        "\n"
        "·Shift+드래그 ... 여러 부대 선택"
    ),
}

EXPECTED_GAPS = {
    71: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x50",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x50",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
    72: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
    73: (b"\x1b\x43\x49", b"\x1b\x43\x5a", b"\x05\x05\x05"),
}
EXPECTED_ARITIES = {71: 8, 72: 10, 73: 2}
BASE_PK_DIVERGENCES = {
    "JP": {71, 73},
    "SC": {71, 73},
    "TC": {71, 73},
}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
CONTROLLER_GLYPHS = set("㍑㌍㌦㍗㍍㎝㌣㌘㌃㌔㌢㌧㌫㌶㍉㍑㍗┨┯")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {71: 97, 72: 99, 73: 100}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 782 record has no configured PK mapping: {base_record_id}") from exc


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


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


def layout_signature(text: str) -> tuple[object, ...]:
    protected = ENGINE.protected_signature(text)
    return (
        text.count("\n"),
        tuple(line.count("\u3000") for line in text.split("\n")),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(protected["non_layout_controls"]),
        protected["leading_whitespace"],
        protected["trailing_whitespace"],
    )


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
            for record_id in range(71, 74)
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(14, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(14, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences != BASE_PK_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 782 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    for record_id, expected_arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 782 literal arity drifted: 14:{record_id}")
        if record_gaps(source_records[(14, record_id)]) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 782 pristine literal/opcode boundary drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 782 current literal/opcode boundary drifted: 14:{record_id}")
        if any(not literal.text.strip() for literal in source_literals + current_literals):
            raise RuntimeError(f"segment 782 unexpectedly contains a blank literal: 14:{record_id}")

    source_71 = ENGINE.parse_record_literals(source_records[(14, 71)])
    current_71 = ENGINE.parse_record_literals(current_records[(14, 71)])
    source_412 = ENGINE.parse_record_literals(source_records[(13, 412)])
    current_412 = ENGINE.parse_record_literals(current_records[(13, 412)])
    for local_literal, prior_literal in ((4, 1), (6, 3)):
        if source_71[local_literal].text != source_412[prior_literal].text:
            raise RuntimeError(f"pristine exact controller reuse drifted: 14:71:{local_literal}")
        if current_71[local_literal].text != current_412[prior_literal].text:
            raise RuntimeError(f"current exact controller reuse drifted: 14:71:{local_literal}")
        if TRANSLATIONS[f"14:71:{local_literal}"] != prior_translation(
            f"13:412:{prior_literal}"
        ):
            raise RuntimeError(f"14:71:{local_literal} must reuse the approved controller glyph")

    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[
            literal_id
        ].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"{coordinate} LF/U+3000/token layout signature drifted")
        if "\r" in translation:
            raise RuntimeError(f"{coordinate} must not add CR")
        if ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"{coordinate} retains kana or CJK Han text")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")
        if glyph_skeleton(translation) != glyph_skeleton(current_text):
            raise RuntimeError(f"{coordinate} controller-glyph skeleton drifted")

    expected_u3000 = {
        "14:71:3": 1,
        "14:71:5": 2,
        "14:71:7": 1,
        "14:72:5": 1,
        "14:72:9": 1,
        "14:73:1": 1,
    }
    actual_u3000 = {
        coordinate: translation.count("\u3000")
        for coordinate, translation in TRANSLATIONS.items()
        if "\u3000" in translation
    }
    if actual_u3000 != expected_u3000:
        raise RuntimeError("segment 782 protected U+3000 coordinates drifted")
    if TRANSLATIONS["14:72:0"] != "[머리 올리기]":
        raise RuntimeError("14:72 must distinguish the female 머리 올리기 ritual from 원복")
    if "원복" in "\n".join(
        TRANSLATIONS[f"14:72:{literal_id}"] for literal_id in range(10)
    ):
        raise RuntimeError("14:72 incorrectly flattened the female ritual to 원복")
    if any(term in TRANSLATIONS["14:71:7"] for term in ("보상", "기한", "OFF")):
        raise RuntimeError("14:71 imported the PK-only clan-target submission explanation")
    if any(term in TRANSLATIONS["14:73:1"] for term in ("중계점", "경유점")):
        raise RuntimeError("14:73 imported the PK-only waypoint control")
    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "건의",
        "고쇼",
        "노동력",
        "머리 올리기",
        "공주",
        "공주 무장",
        "결연",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 782 required terminology drifted")
    if any(term in joined for term in ("시동", "노력", "연조", "히메")):
        raise RuntimeError("segment 782 retains a forbidden legacy term")
    if len(TRANSLATIONS) != 20:
        raise RuntimeError("segment 782 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S782",
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
