#!/usr/bin/env python3
"""Build Base authoring segment 802 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S802.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s802", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "15:262:0": "끼어들어 송구하옵니다",
    "15:262:1": (
        "!\n"
        "이럴 때야말로 시노비가 솜씨를 보일 때이니\n"
        "더 교묘한 계책을 아뢰겠사옵니다"
    ),
    "15:263:0": (
        "외람되오나 귀를 기울여 주십시오!\n"
        "이럴 때는 상인의 지혜를 보태겠사오니"
    ),
    "15:263:1": "\n전국 난세에는 금전이 곧 힘이옵니다",
    "15:264:0": "한 말씀",
    "15:264:1": "\n이럴 때는",
    "15:264:2": "이(가) 재지를 발휘하여",
    "15:264:3": "\n누구도 생각지 못할 묘안을 올리",
    "15:265:0": "주제넘은 말씀이오",
    "15:265:1": "나…\n신앙의 힘은 얕볼 수 없는 법\n",
    "15:265:2": "에게도 한 가지 계책이 있",
    "15:266:0": "외람되오나…\n",
    "15:266:1": "이(가) 바테렌에게서 한 가지 방안을 얻었",
    "15:266:2": "\n시세를 앞서 내다본 방안이니,",
    "15:267:0": "잠시",
    "15:267:1": "\n이토록 중대한 일을 속된 무리에게 맡길 수는 없",
    "15:267:2": "\n이곳은 고귀한 혈통이신",
    "15:267:3": "께서 나설 차례",
    "15:268:0": "아마 잘될 것입니다",
    "15:269:0": "승산은 반반 정도",
    "15:269:1": "인 듯합니다",
    "15:270:0": "다소 어려운 일",
    "15:270:1": "입니다.",
}

EXPECTED_SOURCE_ARITIES = {
    262: 2,
    263: 2,
    264: 4,
    265: 3,
    266: 3,
    267: 4,
    268: 1,
    269: 2,
    270: 2,
}
EXPECTED_CURRENT_ARITIES = dict(EXPECTED_SOURCE_ARITIES)
EXPECTED_SOURCE_GAPS = {
    262: ("", "01439c040000", "01438e000000050505"),
    263: ("", "01431e040000", "0143520000000143f6010000050505"),
    264: ("", "01430c040000014324010000", "014301000000", "014342010000", "01435a040000050505"),
    265: ("", "01431a020000", "014301000000", "014330010000050505"),
    266: ("", "014301000000", "014368020000", "014330010000050505"),
    267: ("", "014382030000", "014330040000", "014301000000", "014352000000050505"),
    268: ("", "01431e010000050505"),
    269: ("", "01435c020000", "050505"),
    270: ("", "014384040000", "01435a040000050505"),
}
EXPECTED_CURRENT_GAPS = {
    262: ("", "", "050505"),
    263: ("", "", "050505"),
    264: ("", "01430c040000014324010000", "014301000000", "014342010000", "01435a040000050505"),
    265: ("", "01431a020000", "014301000000", "014330010000050505"),
    266: ("", "014301000000", "014368020000", "014330010000050505"),
    267: ("", "014382030000", "014330040000", "014301000000", "014352000000050505"),
    268: ("", "01431e010000050505"),
    269: ("", "01435c020000", "050505"),
    270: ("", "", "050505"),
}
BASE_PK_DIVERGENCES = {"JP": set(), "SC": set(), "TC": set()}
PK_ONLY_RECORD_IDS = {242, 243, 244}
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
        raise RuntimeError(f"segment 802 record has no configured PK mapping: {base_record_id}")
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


def prior_translation_if_present(coordinate: str) -> str | None:
    for decision_path in sorted(OUTPUT.parent.glob("base_msggame_B001_S*.private.v1.jsonl")):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate:
                return str(row["translation"])
    return None


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
        raise RuntimeError("segment 802 mapped through a PK-only insertion record")
    if mapped_ids != set(range(265, 274)):
        raise RuntimeError("segment 802 Base-to-PK +3 mapping drifted")

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
                f"segment 802 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )
    for record_id in EXPECTED_SOURCE_ARITIES:
        english = ENGINE.parse_record_literals(
            pk_context_records["EN"][(15, mapped_pk_record_id(record_id))]
        )
        if not "".join(literal.text for literal in english).strip():
            raise RuntimeError(f"segment 802 mapped PK EN context is blank: 15:{record_id}")

    for record_id in EXPECTED_SOURCE_ARITIES:
        source_literals = ENGINE.parse_record_literals(source_records[(15, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(15, record_id)])
        if len(source_literals) != EXPECTED_SOURCE_ARITIES[record_id]:
            raise RuntimeError(f"segment 802 source literal arity drifted: 15:{record_id}")
        if len(current_literals) != EXPECTED_CURRENT_ARITIES[record_id]:
            raise RuntimeError(f"segment 802 current literal arity drifted: 15:{record_id}")
        if record_gaps_hex(source_records[(15, record_id)]) != EXPECTED_SOURCE_GAPS[record_id]:
            raise RuntimeError(f"segment 802 pristine opaque gaps drifted: 15:{record_id}")
        if record_gaps_hex(current_records[(15, record_id)]) != EXPECTED_CURRENT_GAPS[record_id]:
            raise RuntimeError(f"segment 802 current opaque gaps drifted: 15:{record_id}")
        if any(not literal.text.strip() for literal in source_literals + current_literals):
            raise RuntimeError(f"segment 802 unexpectedly contains a blank literal: 15:{record_id}")

    source_245 = ENGINE.parse_record_literals(source_records[(15, 245)])
    source_268 = ENGINE.parse_record_literals(source_records[(15, 268)])
    if source_245[0].text != source_268[0].text:
        raise RuntimeError("15:245:0/15:268:0 exact-source repeat drifted")
    if TRANSLATIONS["15:268:0"] != "아마 잘될 것입니다":
        raise RuntimeError("15:268:0 exact-source translation drifted")
    prior_245 = prior_translation_if_present("15:245:0")
    if prior_245 is not None and TRANSLATIONS["15:268:0"] != prior_245:
        raise RuntimeError("15:268:0 differs from generated 15:245:0 exact translation")

    source_251 = ENGINE.parse_record_literals(source_records[(15, 251)])
    source_266 = ENGINE.parse_record_literals(source_records[(15, 266)])
    if source_251[0].text != source_266[0].text:
        raise RuntimeError("15:251:0/15:266:0 exact-source repeat drifted")
    if TRANSLATIONS["15:266:0"] != "외람되오나…\n":
        raise RuntimeError("15:266:0 exact-source translation drifted")
    prior_251 = prior_translation_if_present("15:251:0")
    if prior_251 is not None and TRANSLATIONS["15:266:0"] != prior_251:
        raise RuntimeError("15:266:0 differs from generated 15:251:0 exact translation")

    source_219 = ENGINE.parse_record_literals(source_records[(15, 219)])
    source_269 = ENGINE.parse_record_literals(source_records[(15, 269)])
    if source_219[0].text != source_269[0].text:
        raise RuntimeError("15:219:0/15:269:0 exact-source repeat drifted")
    if TRANSLATIONS["15:269:0"] != "승산은 반반 정도":
        raise RuntimeError("15:269:0 exact-source translation drifted")
    prior_219 = prior_translation_if_present("15:219:0")
    if prior_219 is not None and TRANSLATIONS["15:269:0"] != prior_219:
        raise RuntimeError("15:269:0 differs from generated 15:219:0 exact translation")
    if TRANSLATIONS["15:269:1"] != "인 듯합니다":
        raise RuntimeError("15:269:1 context-sensitive probability ending drifted")

    source_220 = ENGINE.parse_record_literals(source_records[(15, 220)])
    source_270 = ENGINE.parse_record_literals(source_records[(15, 270)])
    if source_220[0].text != source_270[0].text or source_220[1].text != source_270[1].text:
        raise RuntimeError("15:220:0/1 and 15:270:0/1 exact-source repeat drifted")
    if (
        TRANSLATIONS["15:270:0"] != "다소 어려운 일"
        or TRANSLATIONS["15:270:1"] != "입니다."
    ):
        raise RuntimeError("15:270 exact-source translation drifted")
    for prior_coordinate, coordinate in (("15:220:0", "15:270:0"), ("15:220:1", "15:270:1")):
        prior = prior_translation_if_present(prior_coordinate)
        if prior is not None and TRANSLATIONS[coordinate] != prior:
            raise RuntimeError(f"{coordinate} differs from generated {prior_coordinate} exact translation")

    if not TRANSLATIONS["15:264:2"].startswith("이(가) "):
        raise RuntimeError("15:264:2 must attach a batchim-safe subject particle to the runtime name")
    if not TRANSLATIONS["15:264:3"].endswith("올리"):
        raise RuntimeError("15:264:3 must preserve the stem completed by its live morphology opcode")
    if not (
        TRANSLATIONS["15:262:0"].endswith("송구하옵니다")
        and TRANSLATIONS["15:262:1"].endswith("아뢰겠사옵니다")
        and TRANSLATIONS["15:263:0"].endswith("보태겠사오니")
        and TRANSLATIONS["15:263:1"].endswith("힘이옵니다")
    ):
        raise RuntimeError("15:262/263 elevated formal voice drifted")
    if not TRANSLATIONS["15:265:1"].startswith("나…\n"):
        raise RuntimeError("15:265:0/1 concessive assembly drifted")
    if not TRANSLATIONS["15:265:2"].startswith("에게도 "):
        raise RuntimeError("15:265:2 must attach dative-additive grammar to the runtime name")
    if not TRANSLATIONS["15:266:1"].startswith("이(가) "):
        raise RuntimeError("15:266:1 must attach a batchim-safe subject particle to the runtime name")
    if "바테렌" not in TRANSLATIONS["15:266:1"]:
        raise RuntimeError("15:266:1 must preserve the historical 伴天連 term as 바테렌")
    if not TRANSLATIONS["15:266:2"].endswith(","):
        raise RuntimeError("15:266:2 must leave its closing phrase to the live morphology opcode")
    if TRANSLATIONS["15:267:0"] != "잠시":
        raise RuntimeError("15:267:0 must leave its polite continuation to the live morphology opcode")
    if not (
        TRANSLATIONS["15:267:3"].startswith("께서 ")
        and TRANSLATIONS["15:267:3"].endswith("차례")
    ):
        raise RuntimeError("15:267:3 must honorifically attach to the runtime noble name")
    if "고귀한 혈통" not in TRANSLATIONS["15:267:2"]:
        raise RuntimeError("15:267:2 lost the 貴種 noble-lineage meaning")

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
    required_terms = (
        "시노비",
        "상인",
        "재지",
        "신앙",
        "바테렌",
        "고귀한 혈통",
        "계책",
        "방안",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 802 required persona/historical terminology drifted")
    if any(term in joined for term in ("닌자", "선교사", "속된 무리의 차례")):
        raise RuntimeError("segment 802 retains a forbidden term or broken assembly")

    expected_coordinates = {
        f"15:{record_id}:{literal_id}"
        for record_id, arity in EXPECTED_CURRENT_ARITIES.items()
        for literal_id in range(arity)
    }
    if len(TRANSLATIONS) != 23 or set(TRANSLATIONS) != expected_coordinates:
        raise RuntimeError("segment 802 decision/runtime classification count drifted")


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
        raise RuntimeError("segment 802 Base record count drifted from 19152")

    target_records = {(15, record_id) for record_id in EXPECTED_CURRENT_ARITIES}
    outside_exact = 0
    for key, current_record in current_records.items():
        if key not in target_records:
            if rebuilt_records[key].data != current_record.data:
                raise RuntimeError(f"segment 802 changed an out-of-scope record: {key}")
            outside_exact += 1
    if outside_exact != 19143:
        raise RuntimeError("segment 802 outside-scope byte-exact record count drifted")
    for record_key in target_records:
        if record_gaps_hex(rebuilt_records[record_key]) != record_gaps_hex(
            current_records[record_key]
        ):
            raise RuntimeError(f"segment 802 changed a target opaque skeleton: {record_key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(f"segment 802 literal failed UTF-16 round-trip: {key}")

    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 802 reverse overlay is not byte-exact")


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
                "segment": "base_msggame_B001_S802",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
                "confirmed_non_display": 0,
                "excluded_non_display": 0,
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
