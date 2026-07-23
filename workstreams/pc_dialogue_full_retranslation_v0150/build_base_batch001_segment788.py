#!/usr/bin/env python3
"""Build Base authoring segment 788 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S788.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s788", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:103:0": "[상성]",
    "14:103:1": (
        "\n"
        "무장 사이에는 상성이 있으며, 여러 가지 영향을 줍니다.\n"
        "무장에게 지행지를 줄 때는 다른 무장과의 상성도 고려합시다.\n"
        "\n"
    ),
    "14:103:2": "◇성주와의 상성",
    "14:103:3": (
        "\n"
        "\u3000·성주와의 상성이 ◎ ... 성 능력이 상승한다\n"
        " ·그 외 ... 변화 없음\n"
        "\n"
    ),
    "14:103:4": "◇다이묘와의 상성",
    "14:103:5": (
        "\n"
        "\u3000·다이묘와의 상성이 ◎ ... 휘하 무장의 충성이 오른다\n"
        " ·다이묘와의 상성이 ○ ... 변화 없음\n"
        " ·다이묘와의 상성이 △ ... 휘하 무장의 충성이 내려간다"
    ),
    "14:104:0": "[몸 상태]",
    "14:104:1": (
        "\n"
        "무장은 부상을 입거나 질병에 걸릴 수 있습니다.\n"
        "\n"
    ),
    "14:104:2": "◇부상·질병의 영향",
    "14:104:3": (
        "\n"
        "\u3000·무장의 능력이 일시적으로 크게 감소한다\n"
        " ·사망할 가능성이 있다"
    ),
    "14:105:0": "[금전을 늘리려면]",
    "14:105:1": (
        "\n"
        "자세력 영내를 개발하여 금전 수입을 늘리는 것이 중요합니다.\n"
        "수입 대부분을 정책 발령과 외교에 쓰면\n"
        "정작 필요할 때 금전이 부족할 수 있으니 주의합시다.\n"
        '※수지 내역은 "보고"에서 확인할 수 있습니다\n'
        "\n"
    ),
    "14:105:2": "◇구체적인 예",
    "14:105:3": (
        "\n"
        "\u3000·영주나 대관을 임명하여 각 군의 시장을 장악하게 한다\n"
        " ·군 개발 명령이나 성하 시설 명령으로 취락이나 성하 시설을 건설한다\n"
        ' ·정책 명령으로 정책 "라쿠이치라쿠자"를 발령한다\n'
        ' ·영내 제책 명령으로 "상업 발전"을 실행한다\n'
        " ·다른 세력의 친선 요청을 승인하고 대가를 받는다\n"
        " ·거래 명령으로 가보나 본거지의 병량을 매각한다\n"
        "\n"
    ),
    "14:105:4": "◇주의",
    "14:105:5": (
        "\n"
        '\u3000·성 능력의 정무가 높으면 "상업"이 같아도 금전 수입이 늘어난다\n'
        " ·정책이나 외교를 실행하는 동안에는 매달 금전을 소비한다\n"
        " ·건의에는 비용이 드는 경우가 많다\n"
        " ·통치 범위 밖의 성은 군단에 속하지 않으면 수입이 크게 줄어든다"
    ),
    "14:106:0": "[석고/병력을 늘리려면]",
    "14:106:1": (
        "\n"
        "자세력 영내를 개발하여 석고를 늘리면 병력도 증가합니다.\n"
        "성하 시설이나 정책으로 병력만 늘릴 수도 있으니 활용합시다.\n"
        "또한 성 능력의 정무가 높으면 석고가 같아도 병량 수입이 늘어납니다.\n"
        "\n"
    ),
    "14:106:2": "◇구체적인 예",
    "14:106:3": (
        "\n"
        "\u3000·영주나 대관을 임명하여 각 군의 농촌을 장악하게 한다\n"
        " ·군 개발 명령이나 성하 시설 명령으로 취락이나 성하 시설을 건설한다\n"
        ' ·정책 명령으로 정책 "상비병제"를 발령한다\n'
        ' ·영내 제책 명령으로 "석고 증강"을 실행한다\n'
        " ·영내 제책 명령으로 국인중을 자세력 영내에 편입한다"
    ),
}

EXPECTED_GAPS = {
    103: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
    104: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
    105: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
    106: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
}
EXPECTED_ARITIES = {103: 6, 104: 4, 105: 6, 106: 4}
BASE_PK_DIVERGENCES = {
    "JP": {105, 106},
    "SC": {105},
    "TC": {105},
}
PK_ONLY_RECORD_IDS = {144, 146, 148, 150, 155, 157, 159, 160}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
PROTECTED_GLYPHS = set("◎○△")
BASIS = (
    "pristine_base_pc_jp_authoritative_with_base_sc_tc_and_explicit_"
    "mapped_pk_jp_en_sc_tc_auxiliary_context"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {103: 141, 104: 142, 105: 143, 106: 145}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 788 record has no configured PK mapping: {base_record_id}") from exc


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
    return [character for character in text if character in PROTECTED_GLYPHS]


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
        raise RuntimeError("segment 788 mapped through a PK-only expansion record")

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
                f"segment 788 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    for record_id, expected_arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 788 literal arity drifted: 14:{record_id}")
        if record_gaps(source_records[(14, record_id)]) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 788 pristine literal/opcode boundary drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 788 current literal/opcode boundary drifted: 14:{record_id}")
        if any(not literal.text.strip() for literal in source_literals + current_literals):
            raise RuntimeError(f"segment 788 unexpectedly contains a blank literal: 14:{record_id}")

    source_105 = ENGINE.parse_record_literals(source_records[(14, 105)])
    source_106 = ENGINE.parse_record_literals(source_records[(14, 106)])
    if source_105[2].text != source_106[2].text:
        raise RuntimeError("segment 788 pristine exact heading reuse drifted")
    if TRANSLATIONS["14:105:2"] != TRANSLATIONS["14:106:2"]:
        raise RuntimeError("14:105:2 and 14:106:2 exact translation reuse drifted")

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
            raise RuntimeError(f"{coordinate} protected-glyph skeleton drifted")

    expected_u3000 = {
        "14:103:3": 1,
        "14:103:5": 1,
        "14:104:3": 1,
        "14:105:3": 1,
        "14:105:5": 1,
        "14:106:3": 1,
    }
    actual_u3000 = {
        coordinate: translation.count("\u3000")
        for coordinate, translation in TRANSLATIONS.items()
        if "\u3000" in translation
    }
    if actual_u3000 != expected_u3000:
        raise RuntimeError("segment 788 protected U+3000 coordinates drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "상성",
        "지행지",
        "성 능력",
        "몸 상태",
        "라쿠이치라쿠자",
        "상업 발전",
        "상비병제",
        "석고 증강",
        "국인중",
        "본거지",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 788 required terminology drifted")
    if any(
        term in joined
        for term in (
            "궁합",
            "체조",
            "낙시낙좌",
            "호족",
            "가재",
            "봉행",
            "50000",
            "방어 거점",
            "방위 거점",
            "지원 거점",
            "성 역할",
        )
    ):
        raise RuntimeError("segment 788 retains a forbidden term or imported PK-only guidance")

    expected_coordinates = {
        f"14:{record_id}:{literal_id}"
        for record_id, arity in EXPECTED_ARITIES.items()
        for literal_id in range(arity)
    }
    if len(TRANSLATIONS) != 20 or set(TRANSLATIONS) != expected_coordinates:
        raise RuntimeError("segment 788 decision/static classification count drifted")


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
        raise RuntimeError("segment 788 Base record count drifted from 19152")

    target_records = {(14, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 788 changed an out-of-scope record: {key}")
    for record_key in target_records:
        if record_gaps(rebuilt_records[record_key]) != record_gaps(current_records[record_key]):
            raise RuntimeError(f"segment 788 changed a target nonstring skeleton: {record_key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(f"segment 788 literal failed UTF-16 round-trip: {key}")

    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 788 reverse overlay is not byte-exact")


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
                "segment": "base_msggame_B001_S788",
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
