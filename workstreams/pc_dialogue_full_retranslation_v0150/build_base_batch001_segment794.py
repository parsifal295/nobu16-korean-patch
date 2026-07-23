#!/usr/bin/env python3
"""Build Base authoring segment 794 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S794.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s794",
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
    "14:132:0": "[충성이 낮은 무장]",
    "14:132:1": (
        "\n충성이 낮은 무장은 세력에 불리한 행동을 하기도 합니다.\n"
        "주의합시다.\n\n"
    ),
    "14:132:2": "◇불리한 행동의 예",
    "14:132:3": (
        "\n\u3000·출분하여 세력을 떠난다\n"
        " ·성주라면 적의 공격을 받을 때 성이 함락되기 전에 항복한다\n"
        " ·불리한 상황이 되면 독단으로 철수한다"
    ),
    "14:133:0": "[위풍]",
    "14:133:1": (
        '\n다수의 적 부대를 상대로 한 합전에서 승리하면\n'
        '그 명성은 "위풍"이 되어 주변까지 퍼지며 영향을 미칩니다.\n\n'
    ),
    "14:133:2": "◇위풍의 효과",
    "14:133:3": (
        "\n\u3000·패배한 세력의 군이나 성이 승리한 쪽으로 돌아선다\n"
        " ·주변 세력의 외교 자세가 변동한다\n"
        " ·주변 국인중의 종속도가 변동한다\n"
        " ·양쪽 세력에 속한 무장의 충성이 변동한다"
    ),
    "14:134:0": "[군 완전 개발]",
    "14:134:1": (
        "\n군 하나를 완전히 개발하면 석고가 더 오릅니다.\n"
        "또 성의 지배하에 있는 모든 군을 개발하면 상업이 더 오릅니다.\n"
        "세력을 발전시키려면 군을 적극적으로 개발합시다.\n\n"
    ),
    "14:134:2": "◇군을 완전히 개발하려면",
    "14:134:3": (
        "\n\u3000·모든 농촌과 시장을 장악한다\n"
        " ·모든 개발 용지에 건설한다\n"
        " ·모든 상위 취락을 건설한다\n\n"
    ),
    "14:134:4": "◇군의 성장을 앞당기려면",
    "14:134:5": (
        "\n\u3000통솔이 높은 무장을 영주/대관에 임명한다\n"
        ' "군 개발"과 "영내 제책" 명령을 실행한다'
    ),
    "14:135:0": "[무장의 능력 성장]",
    "14:135:1": (
        "\n전투나 내정 등에서 무장이 능력을 사용하면 경험치를 얻습니다.\n"
        "경험치가 쌓이면 무장의 능력이 성장하므로\n"
        "아끼는 무장에게 많은 경험을 쌓게 해 줍시다.\n\n"
    ),
    "14:135:2": "◇경험치를 얻으려면",
    "14:135:3": (
        "\n\u3000·적 부대를 격파하거나 적 성을 제압한다\n"
        " ·군단장으로서 군단을 지휘한다\n"
        " ·영주나 대관으로서 군을 통치한다\n"
        " ·성하 시설을 건설하거나 정책을 발령한다\n"
        " ·건의나 영내 제책, 조략을 실행한다\n"
        " ·영내 문제를 해결한다\n"
        " ·외교 중개를 맡는다"
    ),
    "14:136:0": "[세력 목표]",
    "14:136:1": (
        "\n세력 목표로\n"
        "성하 시설 건설이나 영토 확장 등이 제안되기도 합니다.\n"
        "\n"
        "제안된 내용을 기한 안에 달성하면 보상을 얻을 수 있으므로\n"
        "달성을 노려 보는 것도 좋습니다.\n"
        "※달성하지 못해도 불이익은 없습니다\n"
        "※설정>시나리오에서 OFF로 바꿀 수도 있습니다"
    ),
}

EXPECTED_ARITIES = {132: 4, 133: 4, 134: 6, 135: 4, 136: 2}
EXPECTED_DIVERGENCES = {
    "JP": {132, 133, 135, 136},
    "SC": {132, 133, 136},
    "TC": {132, 133, 136},
}
PK_ONLY_RECORD_IDS = {186, 189, 191}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－＆"
)
PROTECTED_GLYPHS = set("◇※")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {132: 184, 133: 185, 134: 187, 135: 188, 136: 190}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 794 record has no configured PK mapping: {base_record_id}"
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
        raise RuntimeError("segment 794 mapped a PK-only expansion or variant")
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
                f"segment 794 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 794 arity drifted: 14:{record_id}")
        expected = expected_gaps(arity)
        if record_gaps(source_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 794 pristine opcode gaps drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 794 current opcode gaps drifted: 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                raise RuntimeError(f"segment 794 contains a blank target: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 794 decision is missing: {coordinate}")
            if line_layout_signature(translation) != line_layout_signature(literal.text):
                raise RuntimeError(f"segment 794 layout signature drifted: {coordinate}")
            if glyph_skeleton(translation) != glyph_skeleton(literal.text):
                raise RuntimeError(f"segment 794 protected-glyph skeleton drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 794 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 794 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(
                    f"segment 794 retains banned fullwidth punctuation: {coordinate}"
                )
    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 20:
        raise RuntimeError("segment 794 decision universe drifted")

    pk_184 = [literal.text for literal in ENGINE.parse_record_literals(pk_source_records[(14, 184)])]
    pk_186 = [literal.text for literal in ENGINE.parse_record_literals(pk_source_records[(14, 186)])]
    pk_189 = [literal.text for literal in ENGINE.parse_record_literals(pk_source_records[(14, 189)])]
    pk_191 = [literal.text for literal in ENGINE.parse_record_literals(pk_source_records[(14, 191)])]
    if "降伏した城主は相手勢力の登用に必ず応じる" not in pk_184[3]:
        raise RuntimeError("segment 794 mapped PK low-loyalty extension drifted")
    if "攻城戦" not in pk_186[1] or "動揺" not in pk_186[3]:
        raise RuntimeError("segment 794 PK-only siege authority page drifted")
    if "直談「教練」" not in pk_189[3]:
        raise RuntimeError("segment 794 PK-only ability-growth page drifted")
    if "特別報酬" not in pk_191[3]:
        raise RuntimeError("segment 794 PK-only clan-goal page drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "출분",
        "위풍",
        "외교 자세",
        "국인중",
        "종속도",
        "석고",
        "상업",
        "상위 취락",
        "통솔",
        "영주/대관",
        "군 개발",
        "영내 제책",
        "경험치",
        "군단장",
        "조략",
        "외교 중개",
        "세력 목표",
        "영토",
        "설정>시나리오",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 794 required terminology drifted")
    forbidden_terms = (
        "호족",
        "외교 태도",
        "노력",
        "커맨드",
        "영지 확장",
        "감장",
        "특별 보상",
        "직담",
        "공성전",
        "동요",
    )
    if any(term in joined for term in forbidden_terms):
        raise RuntimeError("segment 794 retains a forbidden legacy or PK-only term")
    if "항복한 성주" in TRANSLATIONS["14:132:3"]:
        raise RuntimeError("14:132 imported the mapped PK surrender-recruitment rule")
    if "영토" not in TRANSLATIONS["14:136:1"] or "영지" in TRANSLATIONS["14:136:1"]:
        raise RuntimeError("14:136 Base 領土 semantics drifted toward mapped PK")


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
        raise RuntimeError("segment 794 Base record count drifted from 19152")
    target_records = {(14, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 794 changed an out-of-scope record: {key}")
    for record_key in target_records:
        if record_gaps(rebuilt_records[record_key]) != record_gaps(current_records[record_key]):
            raise RuntimeError(f"segment 794 changed a target nonstring skeleton: {record_key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(f"segment 794 literal failed UTF-16 round-trip: {key}")
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 794 reverse overlay is not byte-exact")


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
                "segment": "base_msggame_B001_S794",
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
