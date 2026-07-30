#!/usr/bin/env python3
"""Build Base authoring segment 785 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S785.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s785", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:88:0": "[합전: 응용]",
    "14:88:1": (
        "\n"
        "정면으로 싸우는 것만이 합전의 전부는 아닙니다.\n"
        "무장의 제안에 귀 기울여도 좋고 스스로 호기를 찾아내도 좋습니다.\n"
        "상황에 맞게 판단하여 전황을 유리하게 이끕시다.\n"
        "\n"
    ),
    "14:88:2": "◇유리하게 싸우려면",
    "14:88:3": (
        "\n\u3000"
        "·전법을 발동한다\n"
        " ·적 부대를 협격한다\n"
        " ·고지대에서 사격한다"
    ),
    "14:89:0": "◇전법 발동",
    "14:89:1": (
        "\n"
        "전법을 발동하면 강력한 효과를 얻습니다.\n"
        "모든 무장이 보유하고 있으며 각자 판단하여 발동합니다.\n"
        "\n"
        "전법 버튼을 오른쪽 클릭하면\n"
        "전법을 수동 발동으로 전환할 수도 있습니다.\n"
        "※왼쪽 클릭으로 수동 발동할 수 있습니다"
    ),
    "14:90:0": "◇전법 발동",
    "14:90:1": (
        "\n"
        "전법을 발동하면 강력한 효과를 얻습니다.\n"
        "모든 무장이 보유하고 있으며 각자 알맞은 때에 발동합니다.\n"
        "\n"
        "부대 목록에서 부대를 선택하고 ㌘+㌦을 누르면\n"
        "전법을 수동으로만 발동하도록 전환할 수도 있습니다.\n"
        "※㌦로 수동 발동할 수 있습니다"
    ),
    "14:91:0": "◇협격",
    "14:91:1": (
        "\n"
        "적 부대를 여러 방향에서 동시에 공격하면 협격이 됩니다.\n"
        "협격 중에는 적의 병력과 체력에 큰 피해를 줄 수 있습니다.\n"
        "\n"
    ),
    "14:91:2": "◇사격",
    "14:91:3": (
        "\n"
        "고지대의 요충지 중에는 활 아이콘이 표시된 곳이\n"
        "있습니다.\n"
        "이 요충지의 부대는 절벽 아래 적 부대를 사격할 수 있습니다.\n"
        "사격은 병력에 큰 피해를 주며 반격도 받지 않습니다."
    ),
    "14:92:0": "[석고와 상업]",
    "14:92:2": "◇석고",
    "14:92:3": (
        "\n\u3000"
        "·병량 수입량과 최대 병력에 영향\n"
        " ·군의 석고는 주로 장악한 취락(특히 농촌)의 효과로 결정된다\n"
        " ·성의 석고는 성에 속한 군의 석고 합계\n"
        "\n"
    ),
    "14:92:4": "◇상업",
    "14:92:5": (
        "\n\u3000"
        "·상업은 금전 수입량에 영향\n"
        " ·군의 상업은 주로 장악한 취락(특히 시장)의 효과로 결정된다\n"
        " ·성의 상업은 성에 딸린 군의 상업 합계"
    ),
    "14:93:0": "[엔딩 조건]",
    "14:93:1": (
        "\n"
        '"노부나가의 야망·신생"에는 네 종류의 엔딩이 있습니다.\n'
        "\n"
        "1. 지방 통일 엔딩\n"
        "  조건: 시나리오 시작 시 본거지가 있는 지방의 모든 성을 지배하에 둔다\n"
        "\n"
        "2. 삼직 추임 엔딩\n"
        "  조건: 전국 성의 과반수를 지배하에 둔다\n"
        "     기나이(야마시로, 야마토, 가와치, 이즈미, 셋쓰)에 있는 모든 성을 지배하에 둔다\n"
        "\n"
        "3. 종속 통일 엔딩\n"
        "  조건: 전국 성의 과반수를 지배하에 둔다\n"
        "     자세력 이외의 모든 다이묘 가문을 종속시킨다\n"
        "\n"
        "4. 전국 통일 엔딩\n"
        "  조건: 일본 전국의 모든 성을 지배하에 둔다\n"
        "\n"
        "※지방은 다음 아홉 곳입니다\n"
        " ①도호쿠/②간토/③호쿠리쿠/④고신/⑤도카이/⑥긴키/⑦주고쿠/⑧시코쿠/⑨규슈\n"
        "※지방 통일 엔딩 후에도 게임을 계속할 수 있습니다\n"
        "※시나리오 시작 시 많은 성을 지배한 세력은\n"
        " 지방 통일 엔딩이 발생하지 않습니다\n"
        "※이미 삼직(정이대장군/관백/태정대신)에 취임했다면\n"
        " 삼직 추임 엔딩이 발생하지 않습니다"
    ),
}

EXPECTED_ARITIES = {88: 4, 89: 2, 90: 2, 91: 4, 92: 6, 93: 2}
EXPECTED_DIVERGENCES = {
    "JP": {88},
    "SC": {88},
    "TC": {88, 91},
}
BLANK_LITERALS = {(14, 92, 1): "\n"}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－＆"
)
CONTROLLER_GLYPHS = set("㍑㌍㌦㍗㍍㎝㌣㌘㌃㌔㌢㌧㌫㌶㍉┨┯")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {88: 120, 89: 121, 90: 122, 91: 123, 92: 124, 93: 126}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 785 record has no configured PK mapping: {base_record_id}"
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
                f"segment 785 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 785 literal arity drifted: 14:{record_id}")
        expected = expected_gaps(arity)
        if record_gaps(source_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 785 pristine opcode gaps drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 785 current opcode gaps drifted: 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                continue
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 785 decision is missing: {coordinate}")
            if layout_signature(translation) != layout_signature(literal.text):
                raise RuntimeError(f"segment 785 layout signature drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 785 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 785 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(
                    f"segment 785 retains banned fullwidth punctuation: {coordinate}"
                )
            if glyph_skeleton(translation) != glyph_skeleton(literal.text):
                raise RuntimeError(
                    f"segment 785 controller-glyph skeleton drifted: {coordinate}"
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
                f"segment 785 blank literal drifted: {block_id}:{record_id}:{literal_id}"
            )
        if f"{block_id}:{record_id}:{literal_id}" in TRANSLATIONS:
            raise RuntimeError(
                f"segment 785 blank literal received a decision: {block_id}:{record_id}:{literal_id}"
            )

    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 19:
        raise RuntimeError("segment 785 decision universe drifted")

    for archive_records in (source_records, current_records):
        left = ENGINE.parse_record_literals(archive_records[(14, 89)])[0].text
        right = ENGINE.parse_record_literals(archive_records[(14, 90)])[0].text
        if left != right:
            raise RuntimeError("14:89:0/14:90:0 exact source/current reuse drifted")
    if TRANSLATIONS["14:89:0"] != TRANSLATIONS["14:90:0"]:
        raise RuntimeError("14:89:0 and 14:90:0 must translate exactly alike")
    if glyph_skeleton(TRANSLATIONS["14:90:1"]) != ["㌘", "㌦", "㌦"]:
        raise RuntimeError("14:90:1 controller-glyph occurrences drifted")

    pk_extra_125 = ENGINE.parse_record_literals(pk_source_records[(14, 125)])
    pk_extra_127 = ENGINE.parse_record_literals(pk_source_records[(14, 127)])
    if len(pk_extra_125) != 6 or "補給兵糧" not in pk_extra_125[5].text:
        raise RuntimeError("PK-only 14:125 supply-provisions extension drifted")
    if len(pk_extra_127) != 2 or "支配する勢力を従属させる" not in pk_extra_127[1].text:
        raise RuntimeError("PK-only 14:127 subordinate-ending extension drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "합전",
        "전법",
        "협격",
        "사격",
        "석고",
        "병량",
        "삼직 추임",
        "정이대장군",
        "관백",
        "태정대신",
        "본거지",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 785 required terminology drifted")
    if any(
        term in joined
        for term in ("보급 군량", "종속시킨 세력의 성", "본거가 있는 지방")
    ):
        raise RuntimeError("segment 785 imported a PK-only rule")


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
        raise RuntimeError("segment 785 Base record count drifted from 19152")

    target_records = {(14, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 785 changed an out-of-scope record: {key}")
    for record_key in target_records:
        if record_gaps(rebuilt_records[record_key]) != record_gaps(current_records[record_key]):
            raise RuntimeError(f"segment 785 changed a target nonstring skeleton: {record_key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(f"segment 785 literal failed UTF-16 round-trip: {key}")

    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 785 reverse overlay is not byte-exact")


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
                "segment": "base_msggame_B001_S785",
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
