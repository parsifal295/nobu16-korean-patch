#!/usr/bin/env python3
"""Build Base authoring segment 800 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S800.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s800", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "15:242:0": "그리 많은 성과는\n바랄 수 없다",
    "15:242:1": "…",
    "15:243:0": "이번 방안은\n무리 없이 진행될 것입니다",
    "15:244:0": "좋은 방안",
    "15:244:1": "\n성공은 틀림없",
    "15:245:0": "아마 잘될 것입니다",
    "15:245:1": "\n시도해 볼 가치는 충분합니다",
    "15:246:0": "성공할 가능성은 반반입니다",
    "15:246:1": "\n신중히",
    "15:246:2": " 판단하십시오.",
    "15:247:0": "상당히 어려운 일입니다",
    "15:247:1": "…\n한 사람이라도 성공한다면\n그것만으로도 다행입니다",
    "15:248:0": "기회를 놓친 듯합니다",
    "15:248:1": "\n제 제안은 거두겠습니다",
    "15:249:0": (
        "아니, 잠시만 기다려 주십시오\n"
        "그 건의를 받아들이실 생각이라면\n"
    ),
    "15:249:1": "의 방안도 들어",
    "15:250:0": (
        "그 건의도 나쁘지는 않습니다만\n"
        "제 방안이야말로 선결이 아니겠습니까…?"
    ),
    "15:251:0": "외람되오나…\n",
    "15:251:1": "에게도 좋은 방안이 있",
    "15:252:0": "파괴의 건, 완성도는 눈감아",
    "15:252:1": "면\n시노비의 기술로 평소보다 빨리 해내 보이겠",
    "15:252:3": "의 계책도 꼭",
    "15:252:4": "고려",
}

EXPECTED_SOURCE_ARITIES = {
    242: 2,
    243: 1,
    244: 2,
    245: 2,
    246: 3,
    247: 2,
    248: 2,
    249: 2,
    250: 2,
    251: 2,
    252: 5,
}
EXPECTED_CURRENT_ARITIES = {
    242: 2,
    243: 1,
    244: 2,
    245: 2,
    246: 3,
    247: 2,
    248: 2,
    249: 2,
    250: 1,
    251: 2,
    252: 5,
}
EXPECTED_SOURCE_GAPS = {
    242: ("", "01431e010000", "050505"),
    243: ("", "01431e010000050505"),
    244: ("", "01431a0200000143c8020000", "01431e010000050505"),
    245: ("", "014356020000", "0143520000000143c8020000050505"),
    246: ("", "01431e010000", "01438a040000", "014396010000050505"),
    247: ("", "01431e010000", "01435c020000050505"),
    248: ("", "014326020000", "01433c040000050505"),
    249: ("", "014301000000", "014342010000050505"),
    250: ("", "0143da020000", "050505"),
    251: ("", "014301000000", "014336040000050505"),
    252: (
        "",
        "014396040000",
        "01431e040000",
        "014301000000",
        "01438a040000",
        "014396010000050505",
    ),
}
EXPECTED_CURRENT_GAPS = {
    242: ("", "01431e010000", "050505"),
    243: ("", "050505"),
    244: ("", "01431a0200000143c8020000", "01431e010000050505"),
    245: ("", "", "050505"),
    246: ("", "", "", "050505"),
    247: ("", "", "050505"),
    248: ("", "", "050505"),
    249: ("", "014301000000", "014342010000050505"),
    250: ("", "050505"),
    251: ("", "014301000000", "014336040000050505"),
    252: (
        "",
        "014396040000",
        "01431e040000",
        "014301000000",
        "01438a040000",
        "014396010000050505",
    ),
}
BASE_PK_DIVERGENCES = {"JP": set(), "SC": set(), "TC": set()}
PK_ONLY_RECORD_IDS = {242, 243, 244}
BLANK_NON_DISPLAY_COORDINATE = "15:252:2"
PROTECTED_GLYPHS = set("…")
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・／＜＞＝＋－"
)
BASIS = (
    "pristine_base_pc_jp_authoritative_with_exact_plus3_mapped_"
    "pk_jp_en_sc_tc_auxiliary_context_and_current_runtime_fragment_skeleton"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    if base_record_id not in EXPECTED_SOURCE_ARITIES:
        raise RuntimeError(f"segment 800 record has no configured PK mapping: {base_record_id}")
    return base_record_id + 3


def record_gaps_hex(record: Any) -> tuple[str, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gap.hex() for gap in gaps)


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

    mapped_ids = {mapped_pk_record_id(record_id) for record_id in EXPECTED_SOURCE_ARITIES}
    if mapped_ids & PK_ONLY_RECORD_IDS:
        raise RuntimeError("segment 800 mapped through a PK-only insertion record")
    if mapped_ids != set(range(245, 256)):
        raise RuntimeError("segment 800 Base-to-PK +3 mapping drifted")

    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in EXPECTED_SOURCE_ARITIES
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(15, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(15, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences != BASE_PK_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 800 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )
    for record_id in EXPECTED_SOURCE_ARITIES:
        english = ENGINE.parse_record_literals(
            pk_context_records["EN"][(15, mapped_pk_record_id(record_id))]
        )
        if not "".join(literal.text for literal in english).strip():
            raise RuntimeError(f"segment 800 mapped PK EN context is blank: 15:{record_id}")

    for record_id in EXPECTED_SOURCE_ARITIES:
        source_literals = ENGINE.parse_record_literals(source_records[(15, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(15, record_id)])
        if len(source_literals) != EXPECTED_SOURCE_ARITIES[record_id]:
            raise RuntimeError(f"segment 800 source literal arity drifted: 15:{record_id}")
        if len(current_literals) != EXPECTED_CURRENT_ARITIES[record_id]:
            raise RuntimeError(f"segment 800 current literal arity drifted: 15:{record_id}")
        if record_gaps_hex(source_records[(15, record_id)]) != EXPECTED_SOURCE_GAPS[record_id]:
            raise RuntimeError(f"segment 800 pristine opaque gaps drifted: 15:{record_id}")
        if record_gaps_hex(current_records[(15, record_id)]) != EXPECTED_CURRENT_GAPS[record_id]:
            raise RuntimeError(f"segment 800 current opaque gaps drifted: 15:{record_id}")

    source_252 = ENGINE.parse_record_literals(source_records[(15, 252)])
    current_252 = ENGINE.parse_record_literals(current_records[(15, 252)])
    mapped_252 = ENGINE.parse_record_literals(pk_source_records[(15, 255)])
    if source_252[2].text != "\n" or current_252[2].text != "\n" or mapped_252[2].text != "\n":
        raise RuntimeError("15:252:2 blank non-display literal drifted")
    if BLANK_NON_DISPLAY_COORDINATE in TRANSLATIONS:
        raise RuntimeError("15:252:2 blank non-display literal must remain excluded")
    for record_id in range(242, 252):
        if any(
            not literal.text.strip()
            for literal in ENGINE.parse_record_literals(source_records[(15, record_id)])
            + ENGINE.parse_record_literals(current_records[(15, record_id)])
        ):
            raise RuntimeError(f"segment 800 contains an unexpected blank literal: 15:{record_id}")

    source_242 = ENGINE.parse_record_literals(source_records[(15, 242)])
    for prior_record_id in (230, 234, 238):
        if [
            literal.text
            for literal in ENGINE.parse_record_literals(source_records[(15, prior_record_id)])
        ] != [literal.text for literal in source_242]:
            raise RuntimeError(f"15:242 exact-source repeat drifted from 15:{prior_record_id}")
    if TRANSLATIONS["15:242:0"] != "그리 많은 성과는\n바랄 수 없다":
        raise RuntimeError("15:242:0 must reuse the approved exact-source translation")
    if TRANSLATIONS["15:242:1"] != "…":
        raise RuntimeError("15:242:1 must preserve the approved one-glyph ellipsis")

    source_244 = ENGINE.parse_record_literals(source_records[(15, 244)])
    source_217 = ENGINE.parse_record_literals(source_records[(15, 217)])
    source_218 = ENGINE.parse_record_literals(source_records[(15, 218)])
    if source_244[0].text != source_217[0].text or source_244[0].text != source_218[0].text:
        raise RuntimeError("15:244:0 exact-source repeat drifted")
    if source_244[1].text != source_217[1].text:
        raise RuntimeError("15:244:1 exact-source repeat drifted")
    if TRANSLATIONS["15:244:0"] != "좋은 방안":
        raise RuntimeError("15:244:0 exact-source translation drifted")
    if TRANSLATIONS["15:244:1"] != "\n성공은 틀림없":
        raise RuntimeError("15:244:1 exact-source translation drifted")

    source_220 = ENGINE.parse_record_literals(source_records[(15, 220)])
    source_246 = ENGINE.parse_record_literals(source_records[(15, 246)])
    if source_246[1].text != source_220[2].text or source_246[2].text != source_220[3].text:
        raise RuntimeError("15:246 cautious-judgment exact-source repeat drifted")
    if TRANSLATIONS["15:246:1"] + TRANSLATIONS["15:246:2"] != "\n신중히 판단하십시오.":
        raise RuntimeError("15:246 cautious-judgment assembled Korean drifted")
    source_221 = ENGINE.parse_record_literals(source_records[(15, 221)])
    if source_246[0].text == source_221[0].text:
        raise RuntimeError("segment 800 unrelated evaluation source unexpectedly collapsed")
    if (
        ENGINE.parse_record_literals(source_records[(15, 247)])[0].text != source_221[0].text
        or TRANSLATIONS["15:247:0"] != "상당히 어려운 일입니다"
    ):
        raise RuntimeError("15:247:0 exact-source evaluation reuse drifted")

    if EXPECTED_SOURCE_ARITIES[250] != 2 or EXPECTED_CURRENT_ARITIES[250] != 1:
        raise RuntimeError("15:250 documented current merge classification drifted")
    if not all(
        phrase in TRANSLATIONS["15:250:0"] for phrase in ("건의", "나쁘지는", "선결")
    ):
        raise RuntimeError("15:250 merged translation lost source-clause meaning")

    if not TRANSLATIONS["15:252:0"].endswith("눈감아"):
        raise RuntimeError("15:252:0 must connect to the conditional fragment")
    if not TRANSLATIONS["15:252:1"].startswith("면\n"):
        raise RuntimeError("15:252:1 conditional assembly drifted")
    if not TRANSLATIONS["15:252:3"].startswith("의 "):
        raise RuntimeError("15:252:3 must attach genitively to the runtime officer name")
    if TRANSLATIONS["15:252:4"] != "고려":
        raise RuntimeError("15:252:4 consideration fragment drifted")

    if ENGINE.parse_record_literals(source_records[(15, 245)])[0].text != ENGINE.parse_record_literals(
        source_records[(15, 268)]
    )[0].text:
        raise RuntimeError("15:245:0/15:268:0 exact-source repeat drifted")
    if TRANSLATIONS["15:245:0"] != "아마 잘될 것입니다":
        raise RuntimeError("15:245:0 cross-segment exact translation drifted")
    if ENGINE.parse_record_literals(source_records[(15, 251)])[0].text != ENGINE.parse_record_literals(
        source_records[(15, 266)]
    )[0].text:
        raise RuntimeError("15:251:0/15:266:0 exact-source repeat drifted")
    if TRANSLATIONS["15:251:0"] != "외람되오나…\n":
        raise RuntimeError("15:251:0 cross-segment exact translation drifted")

    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[
            literal_id
        ].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"{coordinate} line/U+3000/outer/token signature drifted")
        if glyph_skeleton(translation) != glyph_skeleton(current_text):
            raise RuntimeError(f"{coordinate} protected-glyph skeleton drifted")
        if "\r" in translation:
            raise RuntimeError(f"{coordinate} must not add CR")
        if ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"{coordinate} retains kana or CJK Han text")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = ("건의", "방안", "선결", "파괴", "시노비", "계책")
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 800 required proposal terminology drifted")
    if any(term in joined for term in ("파괴 의식", "닌자", "소문", "인출", "화공")):
        raise RuntimeError("segment 800 retains a forbidden mistranslation")

    expected_coordinates = {
        f"15:{record_id}:{literal_id}"
        for record_id, arity in EXPECTED_CURRENT_ARITIES.items()
        for literal_id in range(arity)
        if f"15:{record_id}:{literal_id}" != BLANK_NON_DISPLAY_COORDINATE
    }
    if len(TRANSLATIONS) != 23 or set(TRANSLATIONS) != expected_coordinates:
        raise RuntimeError("segment 800 decision/runtime/blank classification count drifted")


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
        raise RuntimeError("segment 800 Base record count drifted from 19152")

    target_records = {(15, record_id) for record_id in EXPECTED_CURRENT_ARITIES}
    outside_exact = 0
    for key, current_record in current_records.items():
        if key not in target_records:
            if rebuilt_records[key].data != current_record.data:
                raise RuntimeError(f"segment 800 changed an out-of-scope record: {key}")
            outside_exact += 1
    if outside_exact != 19141:
        raise RuntimeError("segment 800 outside-scope byte-exact record count drifted")
    for record_key in target_records:
        if record_gaps_hex(rebuilt_records[record_key]) != record_gaps_hex(
            current_records[record_key]
        ):
            raise RuntimeError(f"segment 800 changed a target opaque skeleton: {record_key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(f"segment 800 literal failed UTF-16 round-trip: {key}")
    if ENGINE.parse_record_literals(rebuilt_records[(15, 252)])[2].text != "\n":
        raise RuntimeError("15:252:2 blank non-display literal changed during overlay")

    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 800 reverse overlay is not byte-exact")


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
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S800",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
                "confirmed_non_display": 0,
                "excluded_non_display": 1,
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
