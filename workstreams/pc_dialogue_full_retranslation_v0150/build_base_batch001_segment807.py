#!/usr/bin/env python3
"""Build Base authoring segment 807 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S807.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s807", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "15:317:0": (
        "라는 낭인이\n"
        "기세를 탄 우리 가문을 꼭 섬기고 싶다 하니\n"
        "한 번 만나 보시는 것도"
    ),
    "15:317:1": "까 하옵니다",
    "15:318:0": "(이)라는 자가",
    "15:318:1": (
        "에\n"
        "지난날의 기세가 없다고 여겼는지 출분하여\n"
        "우리 가문에 사관하기를 바라며"
    ),
    "15:319:0": "지난 패전으로",
    "15:319:1": "을(를) 저버렸는지\n",
    "15:319:2": "(이)라는 자가 출분하여\n우리 가문에 사관하기를 바라며",
    "15:320:0": "라는 낭인을 성하에서 봤다\n등용을 권하고 올까?",
    "15:321:0": "성하에서",
    "15:321:1": (
        "라는 자를\n"
        "보았다는 보고를 받았사옵니다\n"
        "등용해도 되겠습니까?"
    ),
    "15:322:0": "낭인·",
    "15:322:1": (
        "인가 하는 자를\n"
        "성하에서 보았다고 하옵니다\n"
        "등용을 권해 보고자 하옵니다"
    ),
    "15:323:0": (
        "을(를) 등용해 보시지요\n"
        "그 낭인은 지금 성하에 머물고 있다 하옵니다\n"
        "부디 설득을 제게 맡겨 주십시오"
    ),
    "15:324:0": (
        "라는 낭인을 등용하시는 것이 어떨는지요\n"
        "그자는 낭인 신세로 두기에는 아까운 인물인 듯하옵니다"
    ),
    "15:325:0": (
        "라는 자를 등용하심이 어떻겠습니까?\n"
        "그자는 지금 성하에서\n"
        "낭인으로 떠돌고 있사옵니다"
    ),
    "15:326:0": (
        "을(를) 등용하시는 것이 어떻겠사옵니까?\n"
        "마침 사관할 곳을 찾고 있다 하니...\n"
        "말을 건네 보아도 되겠사옵니까"
    ),
    "15:327:0": (
        "라는 낭인이 있사옵니다\n"
        "우리 가문에서 등용을 제의해도\n"
        "되겠습니까?"
    ),
    "15:328:0": "라는 낭인을 등용함이 어떻습니까?\n마침 성하에 와 있는 듯합니다",
    "15:329:0": (
        "을(를) 등용하는 것이 어떻겠소\n"
        "성하에 있다 하니\n"
        "말을 건네고 올까 하오"
    ),
}
EXPECTED_ARITIES = {
    317: 2,
    318: 2,
    319: 3,
    320: 1,
    321: 2,
    322: 2,
    323: 1,
    324: 1,
    325: 1,
    326: 1,
    327: 1,
    328: 1,
    329: 1,
}
EXPECTED_GAPS = {
    317: ("024833", "01430c040000", "050505"),
    318: ("024833", "025032", "0143b2000000050505"),
    319: ("", "025032", "024833", "0143b2000000050505"),
    320: ("024833", "050505"),
    321: ("", "024833", "050505"),
    322: ("", "024833", "050505"),
    323: ("024833", "050505"),
    324: ("024833", "050505"),
    325: ("024833", "050505"),
    326: ("024833", "050505"),
    327: ("024833", "050505"),
    328: ("024833", "050505"),
    329: ("024833", "050505"),
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
    mapping = {317: 322, 318: 323, 319: 325}
    if base_record_id in mapping:
        return mapping[base_record_id]
    if 320 <= base_record_id <= 329:
        return base_record_id + 7
    raise RuntimeError(f"segment 807 record has no PK mapping: {base_record_id}")


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
        raise RuntimeError("segment 807 mapped through a PK-only insertion")
    if mapped_ids != {322, 323, 325, *range(327, 337)}:
        raise RuntimeError("segment 807 explicit Base-to-PK mapping drifted")
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
                f"segment 807 PK {language} mapped divergence drifted: {sorted(divergences)}"
            )
    return source_records, current_records


def assert_cross_segment_exact(
    source_records: dict[tuple[int, int], Any],
) -> None:
    if ENGINE.parse_record_literals(source_records[(15, 313)])[1].text != ENGINE.parse_record_literals(
        source_records[(15, 317)]
    )[1].text:
        raise RuntimeError("segment 806/807 exact かと source drifted")
    prior_path = OUTPUT.parent / "base_msggame_B001_S806.private.v1.jsonl"
    if prior_path.is_file():
        for line in prior_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = ENGINE.json.loads(line)
            if row.get("coordinate") == "15:313:1":
                if row.get("translation") != TRANSLATIONS["15:317:1"]:
                    raise RuntimeError("segment 806/807 exact かと translation drifted")
                break
        else:
            raise RuntimeError("segment 806 exact 15:313:1 decision is missing")
    reference = ENGINE.parse_record_literals(source_records[(15, 321)])[0].text
    if any(
        ENGINE.parse_record_literals(source_records[(15, record_id)])[0].text != reference
        for record_id in (287, 295, 297)
    ):
        raise RuntimeError("segment 807 cross-segment exact 城下にて source drifted")
    if TRANSLATIONS["15:321:0"] != "성하에서":
        raise RuntimeError("segment 807 established 城下にて translation drifted")
    reference = ENGINE.parse_record_literals(source_records[(15, 322)])[0].text
    if any(
        ENGINE.parse_record_literals(source_records[(15, record_id)])[0].text != reference
        for record_id in (288, 290, 296)
    ):
        raise RuntimeError("segment 807 cross-segment exact 牢人の source drifted")


def assert_scope(prepared: Any) -> None:
    source_records, current_records = assert_context_mappings(prepared)
    expected_coordinates = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 807 source/current arity drifted: 15:{record_id}")
        if record_gaps_hex(source_record) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 807 source opcode skeleton drifted: 15:{record_id}")
        if record_gaps_hex(current_record) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 807 current opcode skeleton drifted: 15:{record_id}")
        for literal_id, current_literal in enumerate(current_literals):
            coordinate = f"15:{record_id}:{literal_id}"
            if not ENGINE.is_visible_translation_candidate(current_literal.text):
                raise RuntimeError(f"segment 807 unexpected blank literal: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 807 decision is missing: {coordinate}")
            if layout_signature(translation) != layout_signature(current_literal.text):
                raise RuntimeError(f"segment 807 layout/outer signature drifted: {coordinate}")
            if glyph_skeleton(translation) != glyph_skeleton(current_literal.text):
                raise RuntimeError(f"segment 807 protected ellipsis drifted: {coordinate}")
            if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 807 forbidden script/control drifted: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(f"segment 807 retains banned fullwidth punctuation: {coordinate}")
    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 19:
        raise RuntimeError("segment 807 decision universe drifted")
    assert_cross_segment_exact(source_records)

    joined = "\n".join(TRANSLATIONS.values())
    for required in ("우리 가문", "낭인", "사관", "등용", "성하", "출분"):
        if required not in joined:
            raise RuntimeError(f"segment 807 required terminology drifted: {required}")
    if any(term in joined for term in ("당가", "임관", "접견", "、")):
        raise RuntimeError("segment 807 retains a forbidden legacy term")


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
        raise RuntimeError("segment 807 Base record count drifted")
    targets = {(15, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in targets and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 807 changed out-of-scope record: {key}")
    for key in targets:
        if record_gaps_hex(rebuilt_records[key]) != record_gaps_hex(current_records[key]):
            raise RuntimeError(f"segment 807 changed target skeleton: {key}")
    for key, translation in replacements.items():
        if ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text != translation:
            raise RuntimeError(f"segment 807 UTF-16 round-trip failed: {key}")
    if ENGINE.rebuild_packed_with_literals(rebuilt, reverse) != base.current_blob:
        raise RuntimeError("segment 807 reverse overlay is not byte-exact")


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
        raise RuntimeError("segment 807 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S807",
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
