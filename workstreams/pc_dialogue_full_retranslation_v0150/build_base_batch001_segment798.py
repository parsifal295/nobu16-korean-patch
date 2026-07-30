#!/usr/bin/env python3
"""Build Base authoring segment 798 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S798.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s798", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
RAW_TRANSLATIONS: dict[str, str] = {
    "14:154:0": "【부대 아이콘】\n",
    "14:154:1": (
        "부대에는 현재 상태를 나타내는 아이콘이 표시됩니다.\n"
        "\n"
        "∑ … 포위 중\n"
        "∮ … 강공 중\n"
        "┸ … 명령 불가\n"
        "╂ … 교전 중\n"
        "㍾ … 협격 중\n"
        "㍽ … 요새와 교전 중\n"
        "㍼ … 정지 중\n"
        "⊿ … 진군 방향의 길이나 군이 빌 때까지 대기 중\n"
        "∟ … 다른 부대의 합류 대기 중\n"
        "\n"
        "이와 별도로 「합전 가능」이라고 표시된 경우에는\n"
        "다이묘 부대의 메뉴에서 합전을 할 수 있습니다."
    ),
    "14:155:0": "【일문】\n",
    "14:155:1": (
        "일문 무장은 다이묘 또는 그 배우자와 혈연 관계인 무장입니다.\n"
        "다이묘와 그 배우자의 양부도 일문에 포함됩니다.\n"
        "\n"
        "일문 무장은 무장 정보의 「인물」 탭에서 확인할 수 있습니다.\n"
        "「○」가 표시된 인물이 다이묘의 일문입니다.\n"
        "\n"
    ),
    "14:155:2": "◇일문 무장의 특징",
    "14:155:3": (
        "\n"
        "・세력의 후계자가 될 수 있다\n"
        "・혼인 동맹을 맺을 때 후보가 된다\n"
        "・충성이 오른다\n"
        "・적에게 포박되면 등용 제의에 응하기 어려워진다\n"
        "\n"
        "일문 무장이 없는 상태에서 다이묘가 사망하면 게임 오버가 되므로\n"
        "후계자로 적합한 무장이 있다면 미리 결연을 맺어 두는 것이 좋습니다."
    ),
    "15:217:0": "좋은 방안",
    "15:217:1": "\n성공은 틀림없",
    "15:218:0": "좋은 방안",
    "15:218:1": "\n아마 잘될 것",
    "15:219:0": "승산은 반반 정도",
    "15:219:1": "입니다만\n시도해 볼 가치는 있습니다.",
    "15:220:0": "다소 어려운 일",
    "15:220:1": "입니다.",
    "15:220:2": "\n신중히 판단하",
    "15:220:3": "십시오.",
    "15:221:0": "상당히 어려운 일입니다",
    "15:221:1": "…\n큰 기대는 하기 어렵습니다.",
    "15:222:0": "거의 틀림없이\n유망한 인재를 찾을 수 있습니다.",
    "15:223:0": (
        "유망한 인재를 찾기는 어려운 법…\n"
        "허나 이번에는 승산이 있어 보이니"
    ),
    "15:223:1": "\n이 기회를 놓치지 마십시오.",
    "15:224:0": (
        "사람 찾기는 어려운 일이라 성패는 운에 달려 있습니다\n"
        "허나 충분히 찾아볼 가치는\n"
        "있다고 봅니다"
    ),
}
STATIC_RECORD_ARITIES = {154: 2, 155: 4}
DYNAMIC_RECORD_ARITIES = {217: 2, 218: 2, 219: 2, 220: 4, 221: 2, 222: 1, 223: 2, 224: 1}
DYNAMIC_COORDINATES = {
    f"15:{record_id}:{literal_id}"
    for record_id, arity in DYNAMIC_RECORD_ARITIES.items()
    for literal_id in range(arity)
}
STATIC_DIVERGENCES = {"JP": {154}, "SC": {154, 155}, "TC": {154}}
PK_ONLY_RECORD_IDS = {218, 219}
EXPECTED_SOURCE_GAPS = {
    217: ("", "01431a0200000143c8020000", "014356020000050505"),
    218: ("", "01431a0200000143c8020000", "01431e010000050505"),
    219: ("", "01435c020000", "0143520000000143c8020000050505"),
    220: ("", "014384040000", "01435a040000", "01438a040000", "014396010000050505"),
    221: ("", "01431e010000", "0143e0020000050505"),
    222: ("", "01431e010000050505"),
    223: ("", "01433c040000", "050505"),
    224: ("", "0143e2000000050505"),
}
EXPECTED_CURRENT_GAPS = {
    217: EXPECTED_SOURCE_GAPS[217],
    218: EXPECTED_SOURCE_GAPS[218],
    219: ("", "", "050505"),
    220: ("", "", "", "", "050505"),
    221: ("", "", "050505"),
    222: ("", "050505"),
    223: ("", "", "050505"),
    224: EXPECTED_SOURCE_GAPS[224],
}
PROTECTED_GLYPHS = set("∑∮┸╂㍾㍽㍼⊿∟◇○")
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－")
ASCII_PUNCTUATION = str.maketrans(
    {
        "【": "[",
        "】": "]",
        "「": '"',
        "」": '"',
        "／": "/",
        "，": ",",
        "。": ".",
        "・": "·",
        "…": "...",
    }
)
STATIC_BASIS = (
    "pristine_base_pc_jp_authoritative_with_base_sc_tc_and_explicit_"
    "mapped_pk_jp_en_sc_tc_auxiliary_context_pk_only_expansions_excluded"
)
DYNAMIC_BASIS = (
    "pristine_base_pc_jp_authoritative_dynamic_fragments_with_base_sc_tc_"
    "and_exact_offset_plus_3_pk_jp_en_sc_tc_context_current_pc_outer_"
    "literal_arity_and_opcode_skeleton_preserved_runtime_assembly_pending"
)


def mapped_pk_record_id(block_id: int, base_record_id: int) -> int:
    if block_id == 14:
        mapping = {154: 217, 155: 220}
        try:
            return mapping[base_record_id]
        except KeyError as exc:
            raise RuntimeError(f"segment 798 static record has no PK mapping: {base_record_id}") from exc
    if block_id == 15 and base_record_id in DYNAMIC_RECORD_ARITIES:
        return base_record_id + 3
    raise RuntimeError(f"segment 798 record has no PK mapping: {block_id}:{base_record_id}")


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def gaps_from_hex(values: tuple[str, ...]) -> tuple[bytes, ...]:
    return tuple(bytes.fromhex(value) for value in values)


def expected_static_gaps(arity: int) -> tuple[bytes, ...]:
    return tuple([b"\x1b\x43\x49", b"\x1b\x43\x5a"] * (arity // 2) + [b"\x05\x05\x05"])


def line_edge(text: str) -> tuple[str, str]:
    return (
        text[: len(text) - len(text.lstrip(" \t\u3000"))],
        text[len(text.rstrip(" \t\u3000")) :],
    )


def adopt_current_layout(raw: str, current: str) -> str:
    raw_lines = raw.split("\n")
    current_lines = current.split("\n")
    if len(raw_lines) != len(current_lines):
        raise RuntimeError("raw translation LF count differs from current layout")
    rendered = []
    for raw_line, current_line in zip(raw_lines, current_lines):
        leading, trailing = line_edge(current_line)
        visible = raw_line.strip(" \t\u3000").translate(ASCII_PUNCTUATION)
        rendered.append(leading + visible + trailing)
    return "\n".join(rendered)


def layout_signature(text: str) -> tuple[object, ...]:
    lines = text.split("\n")
    protected = ENGINE.protected_signature(text)
    return (
        text.count("\n"),
        tuple(line_edge(line) for line in lines),
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


def resolved_translations(current_records: dict[tuple[int, int], Any]) -> dict[str, str]:
    translations = {}
    for coordinate, raw in RAW_TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[literal_id].text
        translations[coordinate] = adopt_current_layout(raw, current)
    return translations


def assert_context_mappings(
    source_records: dict[tuple[int, int], Any],
    pk_source_records: dict[tuple[int, int], Any],
    base_context: dict[str, dict[tuple[int, int], Any]],
    pk_context: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if {mapped_pk_record_id(14, record_id) for record_id in STATIC_RECORD_ARITIES} & PK_ONLY_RECORD_IDS:
        raise RuntimeError("segment 798 mapped a PK-only block-14 expansion")
    for language, base_records, pk_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context["SC"], pk_context["SC"]),
        ("TC", base_context["TC"], pk_context["TC"]),
    ):
        static_divergences = {
            record_id
            for record_id in STATIC_RECORD_ARITIES
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(14, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    pk_records[(14, mapped_pk_record_id(14, record_id))]
                )
            ]
        }
        if static_divergences != STATIC_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 798 static PK {language} divergences drifted: {sorted(static_divergences)}"
            )
        dynamic_divergences = {
            record_id
            for record_id in DYNAMIC_RECORD_ARITIES
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(15, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    pk_records[(15, mapped_pk_record_id(15, record_id))]
                )
            ]
        }
        if dynamic_divergences:
            raise RuntimeError(
                f"segment 798 dynamic PK {language} exact +3 mappings drifted: {sorted(dynamic_divergences)}"
            )


def assert_scope(prepared: Any, translations: dict[str, str]) -> None:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    source_records = ENGINE.archive_records(base.pristine_archive)
    current_records = ENGINE.archive_records(base.current_archive)
    pk_source_records = ENGINE.archive_records(pk.pristine_archive)
    base_context = {
        language: ENGINE.archive_records(archive)
        for language, archive in base.context_archives.items()
    }
    pk_context = {
        language: ENGINE.archive_records(archive)
        for language, archive in pk.context_archives.items()
    }
    assert_context_mappings(source_records, pk_source_records, base_context, pk_context)

    expected_coordinates = set()
    for record_id, arity in STATIC_RECORD_ARITIES.items():
        source_record = source_records[(14, record_id)]
        current_record = current_records[(14, record_id)]
        if len(ENGINE.parse_record_literals(source_record)) != arity or len(
            ENGINE.parse_record_literals(current_record)
        ) != arity:
            raise RuntimeError(f"segment 798 static arity drifted: 14:{record_id}")
        expected_gaps = expected_static_gaps(arity)
        if record_gaps(source_record) != expected_gaps or record_gaps(current_record) != expected_gaps:
            raise RuntimeError(f"segment 798 static skeleton drifted: 14:{record_id}")
        expected_coordinates.update(f"14:{record_id}:{literal_id}" for literal_id in range(arity))

    for record_id, arity in DYNAMIC_RECORD_ARITIES.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        if len(ENGINE.parse_record_literals(source_record)) != arity or len(
            ENGINE.parse_record_literals(current_record)
        ) != arity:
            raise RuntimeError(f"segment 798 dynamic arity drifted: 15:{record_id}")
        if record_gaps(source_record) != gaps_from_hex(EXPECTED_SOURCE_GAPS[record_id]):
            raise RuntimeError(f"segment 798 source dynamic skeleton drifted: 15:{record_id}")
        if record_gaps(current_record) != gaps_from_hex(EXPECTED_CURRENT_GAPS[record_id]):
            raise RuntimeError(f"segment 798 current dynamic skeleton drifted: 15:{record_id}")
        expected_coordinates.update(f"15:{record_id}:{literal_id}" for literal_id in range(arity))

    for coordinate in ("14:156:0", "15:216:0"):
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        source_literal = ENGINE.parse_record_literals(source_records[(block_id, record_id)])[literal_id]
        current_literal = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[literal_id]
        if ENGINE.is_visible_translation_candidate(source_literal.text) or ENGINE.is_visible_translation_candidate(
            current_literal.text
        ):
            raise RuntimeError(f"segment 798 excluded blank became visible: {coordinate}")
        if coordinate in translations:
            raise RuntimeError(f"segment 798 blank must remain excluded: {coordinate}")

    if set(translations) != expected_coordinates or len(translations) != 22:
        raise RuntimeError("segment 798 decision/static/runtime count drifted")
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[literal_id].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"segment 798 layout signature drifted: {coordinate}")
        if glyph_skeleton(translation) != glyph_skeleton(current_text):
            raise RuntimeError(f"segment 798 protected glyphs drifted: {coordinate}")
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"segment 798 forbidden script/control drifted: {coordinate}")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"segment 798 retains fullwidth punctuation: {coordinate}")

    if translations["15:217:0"] != translations["15:218:0"]:
        raise RuntimeError("segment 798 exact 良案 translation drifted")
    joined = "\n".join(translations.values())
    if any(term not in joined for term in ("요새", "합전 가능", "일문 무장", "인물", "결연")):
        raise RuntimeError("segment 798 required terminology drifted")
    if any(term in joined for term in ("성채", "연조", "호족")):
        raise RuntimeError("segment 798 retains a forbidden legacy term")


def assert_isolated_overlay_roundtrip(
    prepared: Any, translations: dict[str, str]
) -> None:
    base = prepared.resources["base_msggame"]
    current_records = ENGINE.archive_records(base.current_archive)
    replacements = {}
    reverse_replacements = {}
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = (block_id, record_id, literal_id)
        replacements[key] = translation
        reverse_replacements[key] = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
    rebuilt = ENGINE.rebuild_packed_with_literals(base.current_blob, replacements)
    rebuilt_records = ENGINE.archive_records(ENGINE.parse_packed_msggame(rebuilt).archive)
    if len(current_records) != 19152 or len(rebuilt_records) != 19152:
        raise RuntimeError("segment 798 record count drifted from 19152")
    target_records = {(14, record_id) for record_id in STATIC_RECORD_ARITIES} | {
        (15, record_id) for record_id in DYNAMIC_RECORD_ARITIES
    }
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 798 changed an out-of-scope record: {key}")
    for key in target_records:
        if record_gaps(rebuilt_records[key]) != record_gaps(current_records[key]):
            raise RuntimeError(f"segment 798 target skeleton drifted: {key}")
    for key, translation in replacements.items():
        if ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text != translation:
            raise RuntimeError(f"segment 798 UTF-16 round-trip failed: {key}")
    if any(
        ENGINE.is_visible_translation_candidate(
            ENGINE.parse_record_literals(rebuilt_records[(block_id, record_id)])[literal_id].text
        )
        for block_id, record_id, literal_id in ((14, 156, 0), (15, 216, 0))
    ):
        raise RuntimeError("segment 798 changed an excluded blank")
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 798 reverse overlay is not byte-exact")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    translations = resolved_translations(current_records)
    assert_scope(prepared, translations)
    assert_isolated_overlay_roundtrip(prepared, translations)
    rows = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets[("base_msggame", block_id, record_id, literal_id)]
        dynamic = coordinate in DYNAMIC_COORDINATES
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
                "basis": DYNAMIC_BASIS if dynamic else STATIC_BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 798 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S798",
                "decision_count": len(rows),
                "retranslated": len(rows) - len(DYNAMIC_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_COORDINATES),
                "excluded_non_display": 2,
                "steam_write_performed": False,
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "dynamic_assembly_basis": {
                    "15:217-218": "current_pc_middle_and_final_personality_opcodes_retained",
                    "15:219-223": "current_pc_flattened_jp_inflection_opcodes_fragments_concatenate",
                    "15:224": "current_pc_final_personality_opcode_retained",
                },
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
