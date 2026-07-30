#!/usr/bin/env python3
"""Build Base authoring segment 776 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S776.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s776",
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
    "14:37:0": "◇성하 방침",
    "14:37:1": (
        "\n성하 방침을 설정하면 성주가 자율적으로 성하 시설을 건설합니다.\n"
        "또한 영주도 성하 방침에 따른 취락을 개발 용지에 건설합니다.\n"
        '정책 "제도 개신" LV1을 발령하면 설정할 수 있게 됩니다.\n'
        "성을 특정 용도에 특화할 수 있으므로\n"
        "원하는 성하 방침을 선택할 수 있도록 무장의 지행지를 조정해 봅시다.\n"
        "※건설 속도와 증축 가능한 LV 상한은 성 능력에 따라 다릅니다"
    ),
    "14:38:0": "[지행]",
    "14:38:1": (
        "\n본거지 이외의 군이나 성을 무장에게 내려 통치를 맡깁니다.\n"
        '군을 받은 무장은 "영주"로서 받은 군의 발전에 종사합니다.\n'
        '성을 받은 무장은 "성주"로서 받은 성의 발전에 종사합니다.\n'
        "\n"
        "본거지 이외의 군이나 성은 영주/성주가 없으면 발전하지 않으므로\n"
        "측근을 몇 명 남기되, 적극적으로 영주/성주로 임명하기를 권합니다.\n"
        "\n"
    ),
    "14:38:2": '◇"┫"에 대하여\n',
    "14:38:3": (
        '어느 무장에게도 지행지로 주어지지 않은 군에는 "┫"가 표시됩니다.\n'
        '특히 노란색 "┫"가 표시된 군은 농촌이나 시장을 장악해 나가면\n'
        '상위 취락인 "대농촌"이나 "대시장"을 건설할 수 있게 되므로\n'
        "우선하여 무장에게 내리는 것이 좋습니다."
    ),
    "14:39:0": "[취락 장악과 건설]",
    "14:39:1": "\n취락을 장악하거나 건설하면 군이 강해집니다.\n\n",
    "14:39:2": "◇장악",
    "14:39:3": (
        '\n"농촌"과 "시장"을 대상으로 합니다.\n'
        '농촌을 장악하면 "석고"가 상승하여 해당 성의 병량 수입과 병력이 늘어납니다.\n'
        '시장을 장악하면 "상업"이 상승하여 군단의 금전 수입이 늘어납니다.\n'
        "\n"
    ),
    "14:39:4": "◇건설",
    "14:39:5": (
        '\n"개발 용지"에 새로운 취락을 건설할 수 있습니다.\n'
        "취락에 따라 군의 생산력과 병력 조달 능력이 향상됩니다.\n"
        "\n"
        '또한 일부 군에서는 "영내 문제"를 해결하면 상위 취락을 건설할 수 있습니다.\n'
        "대관의 통치와 다이묘의 개발 지시는 동시에 진행할 수 있습니다."
    ),
    "14:40:0": "◇대관 임명",
    "14:40:1": "\n군에 대관을 임명하여 통치를 맡길 수 있습니다.\n\n",
    "14:40:2": "◇대관을 임명하면",
    "14:40:3": (
        "\n　·취락의 장악과 건설을 대관이 스스로 수행한다\n"
        " ·상황에 따라 군비 등을 수행한다\n"
        "※대관은 신분에 관계없이 어떤 무장도 임명할 수 있고, 조건 없이 교체할 수 있습니다"
    ),
    "14:41:0": "[영내 제책]",
    "14:41:1": (
        "\n영내를 발전시키는 제책을 실행할 수 있습니다.\n"
        "\n"
        "효과량과 성공률은 명령받은 무장의 능력과 특성에 따라 달라지므로\n"
        "명령 내용에 알맞은 무장을 실행 무장으로 선택합시다.\n"
        "\n"
    ),
    "14:41:2": "◇실행 무장에 대하여",
    "14:41:3": '\n"다이묘", "성주", "측근"을 실행 무장으로 선택할 수 있습니다.',
}

EXPECTED_ARITIES = {37: 2, 38: 4, 39: 6, 40: 4, 41: 4}
EXPECTED_DIVERGENCES = {
    "JP": {37, 38},
    "SC": {37},
    "TC": {37},
}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
CONTROLLER_GLYPHS = set("┫")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_exact_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {37: 57, 38: 59, 39: 61, 40: 62, 41: 63}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 776 record has no configured PK mapping: {base_record_id}"
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
    return tuple([b"\x1b\x43\x49", b"\x1b\x43\x5a"] * (arity // 2) + [b"\x05\x05\x05"])


def line_layout_signature(text: str) -> tuple[object, ...]:
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
    )


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in CONTROLLER_GLYPHS]


def assert_available_duplicate_decision(coordinate: str, translation: str) -> None:
    if not OUTPUT.parent.is_dir():
        return
    for decision_path in OUTPUT.parent.glob("base_msggame_B001_S*.private.v1.jsonl"):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate and row.get("translation") != translation:
                raise RuntimeError(f"duplicate translation differs from {coordinate}")


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
            for record_id in range(37, 42)
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
                f"segment 776 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 776 arity drifted: 14:{record_id}")
        expected = expected_gaps(arity)
        if record_gaps(source_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 776 pristine opcode gaps drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 776 current opcode gaps drifted: 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                raise RuntimeError(f"segment 776 contains a blank target: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 776 decision is missing: {coordinate}")
            if line_layout_signature(translation) != line_layout_signature(literal.text):
                raise RuntimeError(f"segment 776 layout signature drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 776 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 776 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(f"segment 776 retains banned fullwidth punctuation: {coordinate}")
            if glyph_skeleton(translation) != glyph_skeleton(literal.text):
                raise RuntimeError(f"segment 776 controller-glyph skeleton drifted: {coordinate}")

    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 20:
        raise RuntimeError("segment 776 decision universe drifted")
    source_37 = ENGINE.parse_record_literals(source_records[(14, 37)])[0].text
    source_50 = ENGINE.parse_record_literals(source_records[(14, 50)])[4].text
    current_37 = ENGINE.parse_record_literals(current_records[(14, 37)])[0].text
    current_50 = ENGINE.parse_record_literals(current_records[(14, 50)])[4].text
    if source_37 != source_50 or current_37 != current_50:
        raise RuntimeError("14:37:0/14:50:4 exact 城下方針 literal drifted")
    if TRANSLATIONS["14:37:0"] != "◇성하 방침":
        raise RuntimeError("14:37:0 exact 성하 방침 translation drifted")
    assert_available_duplicate_decision("14:50:4", TRANSLATIONS["14:37:0"])
    if TRANSLATIONS["14:38:2"] != '◇"┫"에 대하여\n':
        raise RuntimeError("14:38:2 exact assembled glyph heading drifted")
    if glyph_skeleton(TRANSLATIONS["14:38:3"]) != ["┫", "┫"]:
        raise RuntimeError("14:38:3 exact assembled glyph occurrences drifted")

    pk_extra_58 = ENGINE.parse_record_literals(pk_source_records[(14, 58)])
    pk_extra_60 = ENGINE.parse_record_literals(pk_source_records[(14, 60)])
    if pk_extra_58[0].text != "◇設備の建設" or len(pk_extra_58) != 2:
        raise RuntimeError("PK-only 14:58 equipment-construction page drifted")
    if pk_extra_60[0].text != "【知行】" or len(pk_extra_60) != 6:
        raise RuntimeError("PK-only 14:60 expanded fief page drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "성하 방침",
        "성하 시설",
        "지행",
        "지행지",
        "취락",
        "장악",
        "대관",
        "영내 제책",
        "석고",
        "병량",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 776 required terminology drifted")
    if any(
        term in joined
        for term in ("노력", "호족", "설비", "명소", "본거 이외", "어느 무장의 영지도")
    ):
        raise RuntimeError("segment 776 retains a forbidden or PK-only term")


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
                "segment": "base_msggame_B001_S776",
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
