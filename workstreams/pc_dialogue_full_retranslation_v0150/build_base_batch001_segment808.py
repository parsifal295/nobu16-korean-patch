#!/usr/bin/env python3
"""Build Base authoring segment 808 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S808.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s808", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "15:330:0": "낭인·",
    "15:330:1": (
        "을(를) 등용하시는 것이 어떨는지요?\n"
        "아무래도 성하에 있는 모양입니다\n"
        "사람은 많을수록 좋은 법이지요"
    ),
    "15:331:0": (
        "을(를) 등용하시지요\n"
        "성하에 머무르고 있다 하니\n"
        "이야기를 나누려면 지금이 적기인 줄로 아옵니다"
    ),
    "15:332:0": "흥미로운 낭인이 있다더군\n",
    "15:332:1": "이(가) 이야기를 매듭짓고 오겠다\n뭐, 내게 맡겨 두게",
    "15:333:0": (
        "성하에서 유망해 보이는 낭인을\n"
        "보았다는 보고가 있었소이다\n"
        "등용해도 되겠소이까"
    ),
    "15:334:0": (
        "재기 넘치는 낭인이 있사옵니다\n"
        "어떻게든 설복하여\n"
        "우리 가문에 끌어들여 보이겠사옵니다"
    ),
    "15:335:0": (
        "인재야말로 나라의 근본이옵니다\n"
        "성하에 유망한 자가 있다 하니\n"
        "지금이야말로 등용할 호기인 듯하옵니다"
    ),
    "15:336:0": (
        "유망한 낭인을 찾았사옵니다\n"
        "다른 가문에 빼앗기기 전에\n"
        "우리 가문에 끌어들여야 하옵니다"
    ),
    "15:337:0": (
        "성하에서 훌륭한 낭인을 찾았사옵니다\n"
        "그자를 사관시킬 수 있다면\n"
        "우리 가문에 큰 힘이 될 것입니다"
    ),
    "15:338:0": (
        "재기 넘치는 낭인을 찾았사옵니다\n"
        "무슨 수를 써서라도 등용하고자 하옵니다"
    ),
    "15:339:0": (
        "제법 훌륭한 낭인을 찾았습니다\n"
        "우리 가문을 위해 어떻게든 등용하여\n"
        "우리의 동료로 삼읍시다"
    ),
    "15:340:0": (
        "성하에서 재기 넘치는 낭인을\n"
        "보았다는 소문을 들었사옵니다\n"
        "말을 걸어 보고자 하옵니다"
    ),
    "15:341:0": "성하에서 제법 쓸 만한 낭인을 보았소\n등용하지 않고 놓칠 수는 없소",
    "15:342:0": (
        "성하에 재주 있는 낭인이 머물고 있다 하옵니다...\n"
        "우리 가문에 사관을 권하여\n"
        "도움을 청하고자 하옵니다"
    ),
    "15:343:0": "재주 있는 낭인을 찾았다고 하옵니다\n꼭 등용하고자 하옵니다",
    "15:344:0": "친히 불러 주시다니...\n기꺼이 섬기겠사옵니다",
    "15:345:0": "이(가) 왔다고!\n",
    "15:345:1": "의 힘이 되도록 온 힘을 다하지\n",
    "15:345:2": "의 활약을 기대하라고!",
    "15:346:0": "은(는)",
    "15:346:1": "(이)라 하오\n",
    "15:346:2": "을(를) 섬기는 것은 무사의 영예\n더할 나위 없는 기쁨이오",
    "15:347:0": "은(는)",
    "15:347:1": "(이)라 하오\n",
    "15:347:2": "의 패업을 돕고자\n몸이 부서져라 일하겠소",
    "15:348:0": "(이)라 하옵니다\n인연이 닿아",
    "15:348:1": "을(를) 섬기게 된 이상\n반드시 보탬이 되겠사옵니다",
}
EXPECTED_ARITIES = {
    330: 2,
    331: 1,
    332: 2,
    333: 1,
    334: 1,
    335: 1,
    336: 1,
    337: 1,
    338: 1,
    339: 1,
    340: 1,
    341: 1,
    342: 1,
    343: 1,
    344: 1,
    345: 3,
    346: 3,
    347: 3,
    348: 2,
}
EXPECTED_GAPS = {
    330: ("", "024833", "050505"),
    331: ("024833", "050505"),
    332: ("", "014301000000", "050505"),
    333: ("", "050505"),
    334: ("", "050505"),
    335: ("", "050505"),
    336: ("", "050505"),
    337: ("", "050505"),
    338: ("", "050505"),
    339: ("", "050505"),
    340: ("", "050505"),
    341: ("", "050505"),
    342: ("", "050505"),
    343: ("", "050505"),
    344: ("", "050505"),
    345: ("024633", "014308000000", "014301000000", "050505"),
    346: ("014301000000", "024633", "014308000000", "050505"),
    347: ("014301000000", "024633", "014308000000", "050505"),
    348: ("024633", "014308000000", "050505"),
}
PK_ONLY_RECORD_IDS = {317, 319, 324, 326}
PROTECTED_GLYPHS: set[str] = set()
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－＆"
)
BASIS = (
    "pristine_base_pc_jp_authoritative_with_base_sc_tc_and_explicit_"
    "mapped_pk_jp_en_sc_tc_auxiliary_context_current_pc_runtime_name_"
    "inflection_and_outer_opcode_skeleton_preserved"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    if base_record_id not in EXPECTED_ARITIES:
        raise RuntimeError(f"segment 808 record has no PK mapping: {base_record_id}")
    return base_record_id + 7


def record_gaps_hex(record: Any) -> tuple[str, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gap.hex() for gap in gaps)


def line_edge(text: str) -> tuple[str, str]:
    return (
        text[: len(text) - len(text.lstrip(" \t\u3000"))],
        text[len(text.rstrip(" \t\u3000")) :],
    )


def layout_signature(text: str) -> tuple[object, ...]:
    protected = ENGINE.protected_signature(text)
    return (
        text.count("\n"),
        tuple(line_edge(line) for line in text.split("\n")),
        tuple(line.count("\u3000") for line in text.split("\n")),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(protected["non_layout_controls"]),
        protected["leading_whitespace"],
        protected["trailing_whitespace"],
    )


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in PROTECTED_GLYPHS]


def assert_context_mappings(prepared: Any) -> tuple[dict[tuple[int, int], Any], dict[tuple[int, int], Any]]:
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
    mapped_ids = {mapped_pk_record_id(record_id) for record_id in EXPECTED_ARITIES}
    if mapped_ids & PK_ONLY_RECORD_IDS:
        raise RuntimeError("segment 808 mapped through a PK-only insertion")
    if mapped_ids != set(range(337, 356)):
        raise RuntimeError("segment 808 Base-to-PK +7 mapping drifted")
    for language, base_records, pk_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context["SC"], pk_context["SC"]),
        ("TC", base_context["TC"], pk_context["TC"]),
    ):
        divergences = {
            record_id
            for record_id in EXPECTED_ARITIES
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(15, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    pk_records[(15, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences:
            raise RuntimeError(
                f"segment 808 PK {language} mapped divergence drifted: {sorted(divergences)}"
            )
    return source_records, current_records


def assert_cross_segment_exact(source_records: dict[tuple[int, int], Any]) -> None:
    if ENGINE.parse_record_literals(source_records[(15, 322)])[0].text != ENGINE.parse_record_literals(
        source_records[(15, 330)]
    )[0].text:
        raise RuntimeError("segment 807/808 exact 牢人の source drifted")
    prior_path = OUTPUT.parent / "base_msggame_B001_S807.private.v1.jsonl"
    if prior_path.is_file():
        for line in prior_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = ENGINE.json.loads(line)
            if row.get("coordinate") == "15:322:0":
                if row.get("translation") != TRANSLATIONS["15:330:0"]:
                    raise RuntimeError("segment 807/808 exact 牢人の translation drifted")
                break
        else:
            raise RuntimeError("segment 807 exact 15:322:0 decision is missing")
    if ENGINE.parse_record_literals(source_records[(15, 346)])[1].text != ENGINE.parse_record_literals(
        source_records[(15, 347)]
    )[1].text:
        raise RuntimeError("segment 808 exact と申す source drifted")
    if TRANSLATIONS["15:346:1"] != TRANSLATIONS["15:347:1"]:
        raise RuntimeError("segment 808 exact と申す translation drifted")
    if ENGINE.parse_record_literals(source_records[(15, 346)])[0].text != ENGINE.parse_record_literals(
        source_records[(15, 352)]
    )[0].text:
        raise RuntimeError("segment 808/C exact は source drifted")
    if ENGINE.parse_record_literals(source_records[(15, 347)])[0].text != ENGINE.parse_record_literals(
        source_records[(15, 355)]
    )[0].text:
        raise RuntimeError("segment 808/C exact Japanese comma source drifted")


def assert_scope(prepared: Any) -> None:
    source_records, current_records = assert_context_mappings(prepared)
    expected_coordinates = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 808 source/current arity drifted: 15:{record_id}")
        if record_gaps_hex(source_record) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 808 source opcode skeleton drifted: 15:{record_id}")
        if record_gaps_hex(current_record) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 808 current opcode skeleton drifted: 15:{record_id}")
        for literal_id, current_literal in enumerate(current_literals):
            coordinate = f"15:{record_id}:{literal_id}"
            if not ENGINE.is_visible_translation_candidate(current_literal.text):
                raise RuntimeError(f"segment 808 unexpected blank literal: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 808 decision is missing: {coordinate}")
            if layout_signature(translation) != layout_signature(current_literal.text):
                raise RuntimeError(f"segment 808 layout/outer signature drifted: {coordinate}")
            if glyph_skeleton(translation) != glyph_skeleton(current_literal.text):
                raise RuntimeError(f"segment 808 protected ellipsis drifted: {coordinate}")
            if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 808 forbidden script/control drifted: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(f"segment 808 retains banned fullwidth punctuation: {coordinate}")
    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 28:
        raise RuntimeError("segment 808 decision universe drifted")
    assert_cross_segment_exact(source_records)

    joined = "\n".join(TRANSLATIONS.values())
    for required in ("우리 가문", "낭인", "사관", "등용", "성하", "무사", "패업"):
        if required not in joined:
            raise RuntimeError(f"segment 808 required terminology drifted: {required}")
    if any(term in joined for term in ("당가", "임관", "접견", "、")):
        raise RuntimeError("segment 808 retains a forbidden legacy term or Japanese comma")
    if TRANSLATIONS["15:345:0"] != "이(가) 왔다고!\n":
        raise RuntimeError("segment 808 15:345:0 natural subject boundary drifted")
    if TRANSLATIONS["15:347:0"] != "은(는)":
        raise RuntimeError("segment 808 15:347:0 natural Korean particle boundary drifted")


def assert_isolated_overlay_roundtrip(prepared: Any) -> None:
    base = prepared.resources["base_msggame"]
    current_records = ENGINE.archive_records(base.current_archive)
    replacements = {}
    reverse = {}
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = (block_id, record_id, literal_id)
        replacements[key] = translation
        reverse[key] = ENGINE.parse_record_literals(current_records[key[:2]])[literal_id].text
    rebuilt = ENGINE.rebuild_packed_with_literals(base.current_blob, replacements)
    rebuilt_records = ENGINE.archive_records(ENGINE.parse_packed_msggame(rebuilt).archive)
    if len(current_records) != 19152 or len(rebuilt_records) != 19152:
        raise RuntimeError("segment 808 Base record count drifted")
    targets = {(15, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in targets and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 808 changed out-of-scope record: {key}")
    for key in targets:
        if record_gaps_hex(rebuilt_records[key]) != record_gaps_hex(current_records[key]):
            raise RuntimeError(f"segment 808 changed target skeleton: {key}")
    for key, translation in replacements.items():
        if ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text != translation:
            raise RuntimeError(f"segment 808 UTF-16 round-trip failed: {key}")
    if ENGINE.rebuild_packed_with_literals(rebuilt, reverse) != base.current_blob:
        raise RuntimeError("segment 808 reverse overlay is not byte-exact")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_scope(prepared)
    assert_isolated_overlay_roundtrip(prepared)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets[("base_msggame", block_id, record_id, literal_id)]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
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
        raise RuntimeError("segment 808 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S808",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
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
