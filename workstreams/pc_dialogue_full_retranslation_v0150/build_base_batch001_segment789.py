#!/usr/bin/env python3
"""Build Base authoring segment 789 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S789.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s789", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:107:0": "[전투에서 이기려면]",
    "14:107:1": (
        "\n"
        "병력, 기마 LV, 철포 LV가 높은 성의 성주로 능력이 뛰어난 무장을 임명해\n"
        "자세력 부대를 최대한 강화하는 것이 중요합니다.\n"
        "전투에 적합한 특성을 보유한 무장을 더하면 부대를 한층 강화할 수 있습니다.\n"
        "\n"
    ),
    "14:107:2": "◇그 밖의 수단 예시",
    "14:107:3": (
        "\n"
        "\u3000·공략 목표 명령으로 군비를 갖추어 부대를 일시적으로 강화한다\n"
        " ·사전에 조략 명령으로 적의 힘을 약화시킨다\n"
        " ·적 부대를 협격하여 능력을 떨어뜨린다\n"
        " ·공성전에서는 여러 길에서 성을 포위하도록 공격한다\n"
        " ·성하 시설이나 정책의 효과로 휴대 군량을 늘린다\n"
        " ·다른 세력과 동맹을 맺고 원군을 부른다"
    ),
    "14:108:0": "[적의 침공으로부터 자세력 영지를 지키려면]",
    "14:108:1": (
        "\n"
        "적의 침공이 예상되는 전선 성의 방어 능력을 높입시다.\n"
        '또한 동맹 세력과 교섭하여 "중개"를 요청하면 정전할 수도 있습니다.\n'
        "강대한 세력의 공격에 대비해 동맹을 맺어 두는 것도 좋습니다.\n"
        "\n"
    ),
    "14:108:2": "◇방어 능력을 높이려면",
    "14:108:3": (
        "\n"
        "\u3000·지행 명령으로 능력이 뛰어난 무장을 성주로 임명한다\n"
        ' ·성하 시설 명령으로 성하 시설 "망루"를 건설한다\n'
        ' ·정책 명령으로 정책 "성곽 조영"을 발령한다\n'
        ' ·군 개발 명령으로 침공 예상 경로의 군에 "요새"를 건설한다'
    ),
    "14:109:0": "[대관]",
    "14:109:1": (
        "\n"
        "본거지의 군에 대관을 임명할 수 있습니다.\n"
        "대관은 스스로 군을 개발하며, 다이묘 부대의 일원으로 출진할 수도 있습니다.\n"
        "\n"
    ),
    "14:109:2": "◇대관의 특징",
    "14:109:3": (
        "\n"
        "\u3000·신분과 관계없이 임명할 수 있다\n"
        " ·자유롭게 임명하거나 해임할 수 있다\n"
        "  ※대관을 해임하려면 대관 선택 화면에서 임명 중인 무장("
    ),
    "14:109:4": "┝",
    "14:109:5": (
        ")을 선택하십시오\n"
        " ·대상 군을 통치하고 취락 장악 등을 수행한다\n"
        " ·영주와 달리 군 개발을 직접 지시할 수도 있다\n"
        " ·다이묘보다 능력이 높거나 상성이 좋으면 본거지의 성 능력이 상승한다\n"
        " ·다이묘 부대의 일원으로 출진한다"
    ),
    "14:110:0": "[실행 무장으로 임명할 수 있는 무장]",
    "14:110:1": (
        "\n"
        '"성하 시설 건설"이나 "정책 발령" 같은 임무는\n'
        "무장에게 맡겨야 합니다.\n"
        "\n"
    ),
    "14:110:2": '◇임무를 맡길 수 있는 "직명"',
    "14:110:3": (
        "\n"
        '직명이 "측근" 또는 "성주"인 무장을 실행 무장으로 임명할 수 있습니다.\n'
        "기본적으로 다이묘 군단의 무장 중에서 선택하지만, 다음 명령은 일부 차이가 있습니다.\n"
        " ·성하 시설 ... 측근과 해당 성의 성주만\n"
        ' ·친선 ... 신분이 "부장" 이상\n'
        ' ·정책 ... 신분이 "부장" 이상이며, 휘하 군단의 측근이나 성주도 선택 가능\n'
        "\n"
    ),
    "14:110:4": "◇주의 사항",
    "14:110:5": (
        "\n"
        "\u3000·여러 임무를 겸임할 수 없다\n"
        "  (단, 건의는 임무가 아니므로 겸할 수 있다)\n"
        " ·임무를 수행 중인 성주는 성하 방침에 따른 건설을 하지 않는다"
    ),
}

EXPECTED_GAPS = {
    107: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
    108: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
    109: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x52",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
    110: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
}
EXPECTED_ARITIES = {107: 4, 108: 4, 109: 6, 110: 6}
BASE_PK_DIVERGENCES = {
    "JP": {107},
    "SC": {107, 108},
    "TC": {107, 108},
}
PK_ONLY_RECORD_IDS = {144, 146, 148, 150, 155, 157, 159, 160}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
CONTROLLER_GLYPHS = set("┝")
BASIS = (
    "pristine_base_pc_jp_authoritative_with_base_sc_tc_and_explicit_"
    "mapped_pk_jp_en_sc_tc_auxiliary_context"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {107: 147, 108: 149, 109: 151, 110: 152}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 789 record has no configured PK mapping: {base_record_id}") from exc


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
    if {mapped_pk_record_id(record_id) for record_id in EXPECTED_ARITIES} & PK_ONLY_RECORD_IDS:
        raise RuntimeError("segment 789 mapped through a PK-only expansion record")

    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in EXPECTED_ARITIES
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
                f"segment 789 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    for record_id, expected_arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 789 literal arity drifted: 14:{record_id}")
        if record_gaps(source_records[(14, record_id)]) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 789 pristine literal/opcode boundary drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 789 current literal/opcode boundary drifted: 14:{record_id}")
        if any(not literal.text.strip() for literal in source_literals + current_literals):
            raise RuntimeError(f"segment 789 unexpectedly contains a blank literal: 14:{record_id}")

    source_109 = ENGINE.parse_record_literals(source_records[(14, 109)])
    source_34 = ENGINE.parse_record_literals(source_records[(14, 34)])
    if source_109[4].text != source_34[6].text:
        raise RuntimeError("segment 789 pristine exact controller reuse drifted")
    if TRANSLATIONS["14:109:4"] != prior_translation("14:34:6"):
        raise RuntimeError("14:109:4 must reuse the approved controller glyph")
    if not TRANSLATIONS["14:109:3"].endswith("(") or not TRANSLATIONS["14:109:5"].startswith(")"):
        raise RuntimeError("14:109 controller-glyph assembly boundary drifted")

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
        "14:107:3": 1,
        "14:108:3": 1,
        "14:109:3": 1,
        "14:110:5": 1,
    }
    actual_u3000 = {
        coordinate: translation.count("\u3000")
        for coordinate, translation in TRANSLATIONS.items()
        if "\u3000" in translation
    }
    if actual_u3000 != expected_u3000:
        raise RuntimeError("segment 789 protected U+3000 coordinates drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "기마 LV",
        "철포 LV",
        "협격",
        "공성전",
        "휴대 군량",
        "중개",
        "지행",
        "망루",
        "성곽 조영",
        "요새",
        "대관",
        "상성",
        "직명",
        "측근",
        "부장",
        "성하 방침",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 789 required terminology drifted")
    if any(
        term in joined
        for term in (
            "궁합",
            "협공",
            "허리 병량",
            "가재",
            "귀신 병법",
            "기병 강화",
            "직담",
            "방어 거점",
            "방위 거점",
            "지원 거점",
            "성 역할",
        )
    ):
        raise RuntimeError("segment 789 retains a forbidden term or imported PK-only guidance")

    expected_coordinates = {
        f"14:{record_id}:{literal_id}"
        for record_id, arity in EXPECTED_ARITIES.items()
        for literal_id in range(arity)
    }
    if len(TRANSLATIONS) != 20 or set(TRANSLATIONS) != expected_coordinates:
        raise RuntimeError("segment 789 decision/static classification count drifted")


def assert_isolated_overlay_roundtrip(prepared: Any) -> None:
    base = prepared.resources["base_msggame"]
    current_records = ENGINE.archive_records(base.current_archive)
    replacements: dict[tuple[int, int, int], str] = {}
    reverse_replacements: dict[tuple[int, int, int], str] = {}
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = (block_id, record_id, literal_id)
        replacements[key] = translation
        reverse_replacements[key] = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text

    rebuilt = ENGINE.rebuild_packed_with_literals(base.current_blob, replacements)
    rebuilt_records = ENGINE.archive_records(ENGINE.parse_packed_msggame(rebuilt).archive)
    if len(current_records) != 19152 or len(rebuilt_records) != 19152:
        raise RuntimeError("segment 789 Base record count drifted from 19152")

    target_records = {(14, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 789 changed an out-of-scope record: {key}")
    for record_key in target_records:
        if record_gaps(rebuilt_records[record_key]) != record_gaps(current_records[record_key]):
            raise RuntimeError(f"segment 789 changed a target nonstring skeleton: {record_key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(f"segment 789 literal failed UTF-16 round-trip: {key}")

    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 789 reverse overlay is not byte-exact")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_scope(prepared)
    assert_isolated_overlay_roundtrip(prepared)
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
                "segment": "base_msggame_B001_S789",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
                "confirmed_non_display": 0,
                "steam_write_performed": False,
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
