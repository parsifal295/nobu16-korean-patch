#!/usr/bin/env python3
"""Build Base authoring segment 795 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S795.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s795",
        ENGINE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:137:0": "[통치 범위]",
    "14:137:1": (
        "\n다이묘나 군단장이 있는 성에서 멀리 떨어진 성은\n"
        "통치 범위 밖이 되어 금전 수입이 크게 줄어듭니다.\n"
        "\n"
        "본거지 이전이나 군단 신설을 통해\n"
        "성이 통치 범위 밖이 되지 않도록 주의합시다.\n\n"
    ),
    "14:137:2": "◇통치 범위 확인",
    "14:137:3": (
        "\n통치 범위는 다음 화면과 명령에서 확인할 수 있습니다.\n"
        " ·군단 뷰\n"
        ' ·"지행" 명령\n'
        ' ·"본거지 이전" 명령\n'
        ' ·"군단" 명령'
    ),
    "14:138:0": "[군 개발, 성하 시설, 영내 제책의 활용법]",
    "14:138:1": (
        "\n세 명령 모두 영내 발전에 효과적이지만 저마다 특징이 있습니다.\n"
        "세력 상황에 따라 어떤 수단을 쓸지 판단합시다.\n\n"
    ),
    "14:138:2": "◇군 개발",
    "14:138:3": (
        "\n\u3000·필요한 노동력과 금전이 적어 남는 노동력으로 실행할 수 있다\n"
        " ·본거지의 군에만 명령할 수 있다\n\n"
    ),
    "14:138:4": "◇성하 시설",
    "14:138:5": (
        "\n\u3000·모든 성에 명령할 수 있다\n"
        " ·효과는 크지만 건설 가능한 수가 한정되므로 무엇을 지을지가 중요하다\n"
        " ·증축 조건을 충족하려면 군 개발 등으로 영내를 발전시켜야 한다\n"
        " ·성하 방침을 설정하면 노동력과 금전을 절약할 수 있다\n\n"
    ),
    "14:138:6": "◇영내 제책",
    "14:138:7": (
        "\n\u3000·본거지 이외의 성에만 명령할 수 있다\n"
        " ·필요한 금전이 많으므로 여유가 있을 때만 실행하는 것이 좋다"
    ),
    "14:139:0": "[기본 사항]",
    "14:139:1": (
        "\n게임의 기본 사항을 확인할 수 있습니다.\n"
        " ·성과 군이란\n"
        " ·게임의 기본적인 진행 방법\n"
        " ·게임 힌트\n"
        " ·엔딩 조건\n"
        "\n"
        '그 밖의 자세한 설명은 화면 오른쪽 위의 "?" 버튼에서 확인할 수 있습니다.'
    ),
    "14:140:0": "[본거지]",
    "14:140:1": (
        "\n다이묘가 있는 성을 본거지라 합니다.\n"
        "성주는 다이묘가 맡습니다.\n\n"
    ),
    "14:140:2": "◇본거지에서 주로 할 수 있는 일",
    "14:140:3": (
        '\n\u3000·"군 개발" 명령\n'
        ' ·"성하 시설" 명령\n'
        ' ·"대관" 명령'
    ),
    "14:141:0": "[군]",
    "14:141:1": "\n본거지의 군은 다이묘가 다스립니다.\n\n",
    "14:141:2": "◇특징",
    "14:141:3": (
        '\n\u3000·"군 개발" 명령으로 군을 발전시킬 수 있다\n'
        ' ·"대관" 명령으로 가신에게 군을 맡길 수 있다\n'
        " ·임명된 가신은 대관으로서 군을 발전시킨다\n"
        " ·대관이 우수할수록 발전이 빠르다\n"
        " ·대관을 자유롭게 임명하거나 해임할 수 있다"
    ),
}

EXPECTED_ARITIES = {137: 4, 138: 8, 139: 2, 140: 4, 141: 4}
EXPECTED_DIVERGENCES = {
    "JP": {137, 141},
    "SC": {141},
    "TC": {141},
}
PK_ONLY_RECORD_IDS = {193}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－＆"
)
PROTECTED_GLYPHS = set("◇?")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {137: 192, 138: 194, 139: 195, 140: 196, 141: 197}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 795 record has no configured PK mapping: {base_record_id}"
        ) from exc


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def expected_gaps(arity: int) -> tuple[bytes, ...]:
    return tuple(
        [b"\x1b\x43\x49", b"\x1b\x43\x5a"] * (arity // 2)
        + [b"\x05\x05\x05"]
    )


def line_layout_signature(text: str) -> tuple[object, ...]:
    lines = text.split("\n")
    protected = ENGINE.protected_signature(text)
    return (
        text.count("\n"),
        tuple(line[: len(line) - len(line.lstrip(" \t\u3000"))] for line in lines),
        tuple(line[len(line.rstrip(" \t\u3000")) :] for line in lines),
        tuple(line.count("\u3000") for line in lines),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(protected["non_layout_controls"]),
        protected["leading_whitespace"],
        protected["trailing_whitespace"],
    )


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in PROTECTED_GLYPHS]


def assert_prior_exact_decision(coordinate: str, expected_translation: str) -> None:
    prior_path = OUTPUT.parent / "base_msggame_B001_S786.private.v1.jsonl"
    if not prior_path.is_file():
        return
    for line in prior_path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        if row.get("coordinate") == coordinate:
            if row.get("translation") != expected_translation:
                raise RuntimeError(f"prior exact translation differs at {coordinate}")
            return
    raise RuntimeError(f"prior exact decision is missing at {coordinate}")


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

    mapped_ids = {mapped_pk_record_id(record_id) for record_id in EXPECTED_ARITIES}
    if mapped_ids.intersection(PK_ONLY_RECORD_IDS):
        raise RuntimeError("segment 795 mapped a PK-only expansion or variant")
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
                f"segment 795 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 795 arity drifted: 14:{record_id}")
        expected = expected_gaps(arity)
        if record_gaps(source_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 795 pristine opcode gaps drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 795 current opcode gaps drifted: 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                raise RuntimeError(f"segment 795 contains a blank target: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 795 decision is missing: {coordinate}")
            if line_layout_signature(translation) != line_layout_signature(literal.text):
                raise RuntimeError(f"segment 795 layout signature drifted: {coordinate}")
            if glyph_skeleton(translation) != glyph_skeleton(literal.text):
                raise RuntimeError(f"segment 795 protected-glyph skeleton drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 795 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 795 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(
                    f"segment 795 retains banned fullwidth punctuation: {coordinate}"
                )
    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 22:
        raise RuntimeError("segment 795 decision universe drifted")

    source_feature = ENGINE.parse_record_literals(source_records[(14, 97)])[2].text
    source_141 = ENGINE.parse_record_literals(source_records[(14, 141)])
    if source_feature != source_141[2].text:
        raise RuntimeError("14:141:2 exact-source reuse against 14:97:2 drifted")
    if TRANSLATIONS["14:141:2"] != "◇특징":
        raise RuntimeError("14:141:2 exact prior-approved heading drifted")
    assert_prior_exact_decision("14:97:2", TRANSLATIONS["14:141:2"])

    pk_193 = [literal.text for literal in ENGINE.parse_record_literals(pk_source_records[(14, 193)])]
    if "伝馬制" not in pk_193[1]:
        raise RuntimeError("segment 795 PK-only governance-range page drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "통치 범위",
        "군단 뷰",
        "본거지 이전",
        "군단 신설",
        "노동력",
        "본거지",
        "군 개발",
        "성하 시설",
        "성하 방침",
        "영내 제책",
        "성과 군",
        "대관",
        "가신",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 795 required terminology drifted")
    forbidden_terms = (
        "본거 ",
        "본거의",
        "노력",
        "커맨드",
        "영지",
        "전마제",
        "활용 구분",
        "우측 상단",
        "군개발",
        "성하시설",
        "영내제책",
    )
    if any(term in joined for term in forbidden_terms):
        raise RuntimeError("segment 795 retains a forbidden legacy or PK-only term")
    if "전마" in TRANSLATIONS["14:137:1"]:
        raise RuntimeError("14:137 imported the PK-only governance-range policy")
    if TRANSLATIONS["14:141:0"] != "[군]":
        raise RuntimeError("14:141 imported the mapped PK-only title qualifier")


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
        raise RuntimeError("segment 795 Base record count drifted from 19152")
    target_records = {(14, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 795 changed an out-of-scope record: {key}")
    for record_key in target_records:
        if record_gaps(rebuilt_records[record_key]) != record_gaps(current_records[record_key]):
            raise RuntimeError(f"segment 795 changed a target nonstring skeleton: {record_key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(f"segment 795 literal failed UTF-16 round-trip: {key}")
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 795 reverse overlay is not byte-exact")


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
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S795",
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
