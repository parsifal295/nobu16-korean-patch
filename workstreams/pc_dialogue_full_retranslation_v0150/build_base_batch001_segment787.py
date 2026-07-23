#!/usr/bin/env python3
"""Build Base authoring segment 787 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S787.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s787", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:99:0": "[노동력]",
    "14:99:1": (
        "\n"
        "노동력은 일부 명령을 실행하는 데 필요합니다.\n"
        "규모가 큰 작업이나 여러 작업을 동시에 진행하려면\n"
        "많은 노동력이 필요합니다.\n"
        "※성주나 영주가 스스로 판단해 내정을 할 때는 노동력이 필요하지 않습니다\n"
        "\n"
    ),
    "14:99:2": "◇노동력의 기본 사항",
    "14:99:3": (
        "\n\u3000"
        "·군단의 석고에 따라 노동력이 늘어난다\n"
        "  ※성의 증감이나 석고 저하로 줄어들 수도 있다\n"
        " ·작업이 끝나면 사용한 노동력이 반환된다\n"
        ' ·"보고"에서 사용 상황을 확인할 수 있다\n'
        "\n"
    ),
    "14:99:4": "◇노동력을 사용하는 명령",
    "14:99:5": (
        "\n\u3000"
        "·군 개발\n"
        " ·성하 시설\n"
        " ·영내 제책\n"
        " ·조략\n"
        ' ·성하 방침 (정책 "재량권 위양"으로 노동력 소비를 없앨 수 있다)\n'
        " ※그 밖에도 건의와 영내 문제 해결에 사용"
    ),
    "14:100:0": "[다른 세력의 친선 제안]",
    "14:100:1": (
        "\n"
        "다른 세력도 전국시대의 난세를 살아남기 위해 외교를 펼칩니다. 친선을 승낙하면\n"
        "훗날 요구에 응해야 하지만 그 대가로 금전을 받을 수 있습니다.\n"
        "\n"
    ),
    "14:100:2": "◇친선 승낙 후",
    "14:100:3": (
        "\n\u3000"
        "·친선을 승낙한 뒤 기간 중에는 매달 금전 수입을 얻는다\n"
        " ·기간이 끝나면 필요할 때 약속한 내용을 대가로 요구받는다\n"
        " ·약속을 거부하면 상대의 신용과 주변 세력의 외교 자세가 악화된다"
    ),
    "14:101:0": "[휴대 군량]",
    "14:101:1": (
        "\n"
        "부대는 출진할 때 병량을 가지고 나가며, 이 병량이 바닥나면 병력이 계속 줄어듭니다.\n"
        "휴대 군량이 적어지면 부대 아이콘 색이 바뀌므로 주의합시다.\n"
        "\n"
    ),
    "14:101:2": "◇휴대 군량 규칙",
    "14:101:3": (
        "\n\u3000"
        "·성의 병량이 병력보다 적으면 출진 시 휴대 군량 일수가 줄어든다\n"
        " ·부대 아이콘은 휴대 군량이 60일 이하면 노란색, 30일 이하면 빨간색이 된다\n"
        " ·자세력의 성에 머무는 동안에는 휴대 군량 대신 출진지의 병량을 소비한다\n"
        "  ※이때 부대 아이콘이 깜빡인다\n"
        "  ※출진지에 병량이 없으면 부대의 휴대 군량을 소비한다"
    ),
    "14:102:0": "[재해와 풍작]",
    "14:102:2": "◇재해",
    "14:102:3": (
        "\n"
        "달 초에는 여러 자연재해가 일어나기도 합니다.\n"
        "재해가 발생한 군은 피해를 입을 뿐 아니라 영내 문제도 생길 수 있습니다.\n"
        "영내 문제를 빨리 해결하지 않으면 잇키가 일어나기도 합니다.\n"
        ' ·홍수 ... 5월에 발생하며 "시장"의 장악을 모두 해제한다\n'
        ' ·태풍 ... 6월에 발생하며 "농촌"의 장악을 모두 해제한다\n'
        " ·흉작 ... 7월에 발생하며 석고가 일시적으로 줄어 병량 수입과 병력에 영향을 준다\n"
        "\n"
    ),
    "14:102:4": "◇재해 대책",
    "14:102:5": (
        "\n"
        "다음을 활용하면 재해 피해를 피할 수 있습니다.\n"
        ' ·정책 "관개 정비"\n'
        ' ·성하 시설 "관개 수로"\n'
        ' ·특성 "방재"\n'
        "\n"
    ),
    "14:102:6": "◇풍작",
    "14:102:7": (
        "\n"
        "재해와 반대로 7월에는 풍작이 들기도 합니다.\n"
        "풍작이 든 군은 석고가 일시적으로 늘어 병량 수입과 병력에 영향을 줍니다."
    ),
}

EXPECTED_ARITIES = {99: 6, 100: 4, 101: 4, 102: 8}
EXPECTED_DIVERGENCES = {
    "JP": {99, 100, 101, 102},
    "SC": {99, 101, 102},
    "TC": {99, 101, 102},
}
BLANK_LITERALS = {(14, 102, 1): "\n"}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－＆"
)
CONTROLLER_GLYPHS = set("㍑㌍㌦㍗㍍㎝㌣㌘㌃㌔㌢㌧㌫㌶㍉┨┯")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {99: 136, 100: 137, 101: 138, 102: 140}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 787 record has no configured PK mapping: {base_record_id}"
        ) from exc


def expected_gaps(arity: int) -> tuple[bytes, ...]:
    return tuple(
        part
        for _ in range(arity // 2)
        for part in (b"\x1b\x43\x49", b"\x1b\x43\x5a")
    ) + (b"\x05\x05\x05",)


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in CONTROLLER_GLYPHS]


def layout_signature(text: str) -> tuple[object, ...]:
    protected = ENGINE.protected_signature(text)
    lines = text.split("\n")
    leading = tuple(line[: len(line) - len(line.lstrip(" \t\u3000"))] for line in lines)
    trailing = tuple(line[len(line.rstrip(" \t\u3000")) :] for line in lines)
    return (
        text.count("\n"),
        leading,
        trailing,
        tuple(line.count("\u3000") for line in lines),
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
        if divergences != EXPECTED_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 787 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 787 literal arity drifted: 14:{record_id}")
        expected = expected_gaps(arity)
        if record_gaps(source_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 787 pristine opcode gaps drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 787 current opcode gaps drifted: 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                continue
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 787 decision is missing: {coordinate}")
            if layout_signature(translation) != layout_signature(literal.text):
                raise RuntimeError(f"segment 787 layout signature drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 787 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 787 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(
                    f"segment 787 retains banned fullwidth punctuation: {coordinate}"
                )
            if glyph_skeleton(translation) != glyph_skeleton(literal.text):
                raise RuntimeError(
                    f"segment 787 controller-glyph skeleton drifted: {coordinate}"
                )

    for (block_id, record_id, literal_id), expected_text in BLANK_LITERALS.items():
        source_text = ENGINE.parse_record_literals(
            source_records[(block_id, record_id)]
        )[literal_id].text
        current_text = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
        if source_text != expected_text or current_text != expected_text:
            raise RuntimeError(
                f"segment 787 blank literal drifted: {block_id}:{record_id}:{literal_id}"
            )
        if f"{block_id}:{record_id}:{literal_id}" in TRANSLATIONS:
            raise RuntimeError(
                f"segment 787 blank literal received a decision: {block_id}:{record_id}:{literal_id}"
            )

    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 21:
        raise RuntimeError("segment 787 decision universe drifted")

    pk_mapped_136 = ENGINE.parse_record_literals(pk_source_records[(14, 136)])
    pk_mapped_140 = ENGINE.parse_record_literals(pk_source_records[(14, 140)])
    pk_extra_139 = ENGINE.parse_record_literals(pk_source_records[(14, 139)])
    if len(pk_mapped_136) != 6 or "月の初め" not in pk_mapped_136[3].text:
        raise RuntimeError("mapped PK 14:136 monthly labor extension drifted")
    if len(pk_mapped_140) != 8 or "一年間" not in pk_mapped_140[3].text:
        raise RuntimeError("mapped PK 14:140 one-year disaster extension drifted")
    if len(pk_extra_139) != 4 or "補給拠点" not in pk_extra_139[3].text:
        raise RuntimeError("PK-only 14:139 portable-provisions extension drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "노동력",
        "석고",
        "성하 방침",
        "재량권 위양",
        "친선",
        "친선 제안",
        "신용",
        "휴대 군량",
        "출진지",
        "병량",
        "관개 정비",
        "관개 수로",
        "방재",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 787 required terminology drifted")
    if any(
        term in joined
        for term in (
            "노력",
            "재량권 이양",
            "보급 거점",
            "보급 군량",
            "매월 초",
            "1년간",
            "일 년간",
            "출진한 성",
        )
    ):
        raise RuntimeError("segment 787 retains a legacy term or imports a PK-only rule")
    if TRANSLATIONS["14:102:3"].count("일시적으로") != 1:
        raise RuntimeError("14:102:3 must preserve the Base temporary crop-failure duration")
    if TRANSLATIONS["14:102:7"].count("일시적으로") != 1:
        raise RuntimeError("14:102:7 must preserve the Base temporary harvest duration")


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
        raise RuntimeError("segment 787 Base record count drifted from 19152")

    target_records = {(14, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 787 changed an out-of-scope record: {key}")
    for record_key in target_records:
        if record_gaps(rebuilt_records[record_key]) != record_gaps(current_records[record_key]):
            raise RuntimeError(f"segment 787 changed a target nonstring skeleton: {record_key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(f"segment 787 literal failed UTF-16 round-trip: {key}")

    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 787 reverse overlay is not byte-exact")


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
        target = prepared.visible_targets.get(
            ("base_msggame", block_id, record_id, literal_id)
        )
        if target is None:
            raise RuntimeError(
                f"decision target is absent from the current Base universe: {coordinate}"
            )
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
        raise RuntimeError(
            "validated decision count differs from the segment translation count"
        )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S787",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
                "confirmed_non_display": 1,
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
