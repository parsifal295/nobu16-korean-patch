#!/usr/bin/env python3
"""Build Base authoring segment 801 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S801.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s801", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "15:253:0": "유언비어의 건, 환술로 적을 현혹시키겠사옵니다",
    "15:253:1": "\n장치를 마련하려면 얼마간 금전이 들겠사오",
    "15:253:2": "나\n더 많은 적을 끌어들일 수 있사옵니다",
    "15:254:0": "선동의 건, 비용이 더 늘",
    "15:254:1": "지만\n병기를 사들여 성하의 백성에게 풀",
    "15:254:3": "의 방안이야말로 빈틈없다고 생각하",
    "15:255:0": (
        "파괴의 건은 잠시 기다려 주십시오\n"
        "간자를 써서 안에서부터 무너뜨려 보이겠습니다"
    ),
    "15:255:1": "\n승산은 이쪽이 더 높습니다",
    "15:256:0": "방화의 건, 잠시 기다려 주신다",
    "15:256:1": "면\n성을 지키는 병사를 회유하여 급소를 장악해 보이겠",
    "15:256:2": "\n승산은 이쪽이 더 높습니다",
    "15:257:0": (
        "요지에 집중하여 선동을 벌이면\n"
        "잇키의 규모는 작아지겠지만\n"
        "더 빨리 일으킬 수 있습니다"
    ),
    "15:258:0": "빼내기의 건, 다소 위험한 방안",
    "15:258:1": "이지만\n친족까지 함께 권유해 보는 것은",
    "15:258:2": "\n잘 풀리면 모두 함께 돌아설지도 모",
    "15:259:0": "선동의 건, 잠시 기다려 주신다",
    "15:259:1": "면\n",
    "15:259:2": "이(가) 행각하며 두루 동지를 모으고\n널리 잇키를 선동해 보이겠",
    "15:260:0": (
        "파괴의 건, 남만 상인에게서 카논포를 사들여\n"
        "적의 성을 포격하는 데 쓰는 것은 어떻겠습니까?"
    ),
    "15:260:1": "\n값은 비싸지만 위력은 막강합니다",
    "15:261:0": "선동의 건, 얼마간 자금을 마련해 주신다",
    "15:261:1": "면\n",
    "15:261:2": "교서를 내려 백성에게 호소하겠습니다",
    "15:261:3": "\n그리하면 선동은 확실히 성공할 것입니다",
}

EXPECTED_SOURCE_ARITIES = {
    253: 3,
    254: 4,
    255: 3,
    256: 3,
    257: 3,
    258: 3,
    259: 3,
    260: 2,
    261: 4,
}
EXPECTED_CURRENT_ARITIES = {
    253: 3,
    254: 4,
    255: 2,
    256: 3,
    257: 1,
    258: 3,
    259: 3,
    260: 2,
    261: 4,
}
EXPECTED_SOURCE_GAPS = {
    253: ("", "01431e040000", "0143b4010000", "01431e040000050505"),
    254: ("", "0143b4010000", "01437e040000", "014301000000", "01433c040000050505"),
    255: ("", "014390040000", "01431e040000", "01431e010000050505"),
    256: ("", "014390040000", "01431e040000", "01431e010000050505"),
    257: ("", "01431e040000", "014336040000", "01431e040000050505"),
    258: ("", "01431a020000", "0143b0020000014324010000", "01434e040000050505"),
    259: ("", "014390040000", "014301000000", "01437e01000001431e040000050505"),
    260: ("", "01431e010000", "014302020000050505"),
    261: ("", "014396040000", "014301000000", "014300040000", "01435a040000050505"),
}
EXPECTED_CURRENT_GAPS = {
    253: ("", "", "", "050505"),
    254: ("", "0143b4010000", "01437e040000", "014301000000", "01433c040000050505"),
    255: ("", "", "050505"),
    256: ("", "014390040000", "01431e040000", "01431e010000050505"),
    257: ("", "050505"),
    258: ("", "01431a020000", "0143b0020000014324010000", "01434e040000050505"),
    259: ("", "014390040000", "014301000000", "01437e01000001431e040000050505"),
    260: ("", "", "050505"),
    261: ("", "", "", "", "050505"),
}
BASE_PK_DIVERGENCES = {"JP": set(), "SC": set(), "TC": set()}
PK_ONLY_RECORD_IDS = {242, 243, 244}
BLANK_NON_DISPLAY_COORDINATE = "15:254:2"
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
        raise RuntimeError(f"segment 801 record has no configured PK mapping: {base_record_id}")
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


def prior_translation(coordinate: str) -> str:
    for decision_path in sorted(OUTPUT.parent.glob("base_msggame_B001_S*.private.v1.jsonl")):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate:
                return str(row["translation"])
    raise RuntimeError(f"prior exact translation is absent: {coordinate}")


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
        raise RuntimeError("segment 801 mapped through a PK-only insertion record")
    if mapped_ids != set(range(256, 265)):
        raise RuntimeError("segment 801 Base-to-PK +3 mapping drifted")

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
                f"segment 801 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )
    for record_id in EXPECTED_SOURCE_ARITIES:
        english = ENGINE.parse_record_literals(
            pk_context_records["EN"][(15, mapped_pk_record_id(record_id))]
        )
        if not "".join(literal.text for literal in english).strip():
            raise RuntimeError(f"segment 801 mapped PK EN context is blank: 15:{record_id}")

    for record_id in EXPECTED_SOURCE_ARITIES:
        source_literals = ENGINE.parse_record_literals(source_records[(15, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(15, record_id)])
        if len(source_literals) != EXPECTED_SOURCE_ARITIES[record_id]:
            raise RuntimeError(f"segment 801 source literal arity drifted: 15:{record_id}")
        if len(current_literals) != EXPECTED_CURRENT_ARITIES[record_id]:
            raise RuntimeError(f"segment 801 current literal arity drifted: 15:{record_id}")
        if record_gaps_hex(source_records[(15, record_id)]) != EXPECTED_SOURCE_GAPS[record_id]:
            raise RuntimeError(f"segment 801 pristine opaque gaps drifted: 15:{record_id}")
        if record_gaps_hex(current_records[(15, record_id)]) != EXPECTED_CURRENT_GAPS[record_id]:
            raise RuntimeError(f"segment 801 current opaque gaps drifted: 15:{record_id}")

    source_254 = ENGINE.parse_record_literals(source_records[(15, 254)])
    current_254 = ENGINE.parse_record_literals(current_records[(15, 254)])
    mapped_254 = ENGINE.parse_record_literals(pk_source_records[(15, 257)])
    if source_254[2].text != "\n" or current_254[2].text != "\n" or mapped_254[2].text != "\n":
        raise RuntimeError("15:254:2 blank non-display literal drifted")
    if BLANK_NON_DISPLAY_COORDINATE in TRANSLATIONS:
        raise RuntimeError("15:254:2 blank non-display literal must remain excluded")
    for record_id in (*range(253, 254), *range(255, 262)):
        if any(
            not literal.text.strip()
            for literal in ENGINE.parse_record_literals(source_records[(15, record_id)])
            + ENGINE.parse_record_literals(current_records[(15, record_id)])
        ):
            raise RuntimeError(f"segment 801 contains an unexpected blank literal: 15:{record_id}")

    if EXPECTED_SOURCE_ARITIES[255] != 3 or EXPECTED_CURRENT_ARITIES[255] != 2:
        raise RuntimeError("15:255 documented current merge classification drifted")
    if EXPECTED_SOURCE_ARITIES[257] != 3 or EXPECTED_CURRENT_ARITIES[257] != 1:
        raise RuntimeError("15:257 documented current merge classification drifted")
    if TRANSLATIONS["15:255:0"].count("\n") != 1 or not all(
        term in TRANSLATIONS["15:255:0"] for term in ("파괴", "간자", "안에서부터")
    ):
        raise RuntimeError("15:255 merged translation lost the wait/agent/internal-collapse meaning")
    if TRANSLATIONS["15:257:0"].count("\n") != 2 or not all(
        term in TRANSLATIONS["15:257:0"] for term in ("요지", "선동", "잇키", "더 빨리")
    ):
        raise RuntimeError("15:257 merged translation lost the focused-incitement tradeoff")

    source_255 = ENGINE.parse_record_literals(source_records[(15, 255)])
    source_256 = ENGINE.parse_record_literals(source_records[(15, 256)])
    if source_255[2].text != source_256[2].text:
        raise RuntimeError("15:255/15:256 exact-source success-probability line drifted")
    if TRANSLATIONS["15:255:1"] != TRANSLATIONS["15:256:2"]:
        raise RuntimeError("15:255/15:256 success-probability translation reuse drifted")
    if not (
        TRANSLATIONS["15:253:0"].endswith("겠사옵니다")
        and TRANSLATIONS["15:253:1"].endswith("들겠사오")
        and TRANSLATIONS["15:253:2"].endswith("있사옵니다")
    ):
        raise RuntimeError("15:253 formal 사옵니다 voice drifted across its three fragments")

    source_259 = ENGINE.parse_record_literals(source_records[(15, 259)])
    source_261 = ENGINE.parse_record_literals(source_records[(15, 261)])
    source_4152 = ENGINE.parse_record_literals(source_records[(6, 4152)])
    if source_259[1].text != source_261[1].text or source_259[1].text != source_4152[2].text:
        raise RuntimeError("15:259:1/15:261:1/6:4152:2 exact-source conditional drifted")
    approved_conditional = prior_translation("6:4152:2")
    if (
        TRANSLATIONS["15:259:1"] != approved_conditional
        or TRANSLATIONS["15:261:1"] != approved_conditional
    ):
        raise RuntimeError("15:259:1 and 15:261:1 must reuse approved 면+LF conditional")
    if not TRANSLATIONS["15:259:2"].startswith("이(가) "):
        raise RuntimeError("15:259:2 must attach a batchim-safe subject particle to the runtime name")
    if EXPECTED_CURRENT_GAPS[261][2] or EXPECTED_CURRENT_GAPS[261][3]:
        raise RuntimeError("15:261 current skeleton unexpectedly restored the omitted runtime name")
    if not TRANSLATIONS["15:261:2"].startswith("교서를 내려 "):
        raise RuntimeError("15:261:2 must remain grammatical without a current runtime-name insertion")

    if not TRANSLATIONS["15:254:0"].endswith("늘"):
        raise RuntimeError("15:254:0 must connect to the adversative fragment")
    if not TRANSLATIONS["15:254:1"].startswith("지만\n"):
        raise RuntimeError("15:254:1 adversative assembly drifted")
    if not TRANSLATIONS["15:254:3"].startswith("의 "):
        raise RuntimeError("15:254:3 must attach genitively to the runtime officer name")
    if not TRANSLATIONS["15:256:0"].endswith("주신다"):
        raise RuntimeError("15:256:0 must connect to the conditional 면 fragment")
    if not TRANSLATIONS["15:256:1"].startswith("면\n"):
        raise RuntimeError("15:256:1 conditional assembly drifted")
    if not TRANSLATIONS["15:258:1"].startswith("이지만\n"):
        raise RuntimeError("15:258:1 adversative assembly drifted")
    if not TRANSLATIONS["15:258:2"].endswith("모"):
        raise RuntimeError("15:258:2 must preserve the stem completed by its live morphology opcode")
    if not TRANSLATIONS["15:259:0"].endswith("주신다"):
        raise RuntimeError("15:259:0 must connect to the approved conditional fragment")
    if "행각하며 두루" not in TRANSLATIONS["15:259:2"]:
        raise RuntimeError("15:259:2 lost the monk's 行脚 register and widespread gathering")
    if not TRANSLATIONS["15:261:0"].endswith("주신다"):
        raise RuntimeError("15:261:0 must connect to the approved conditional fragment")

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
        "유언비어",
        "파괴",
        "방화",
        "선동",
        "빼내기",
        "간자",
        "카논포",
        "잇키",
        "교서",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 801 required named-term terminology drifted")
    if any(
        term in joined
        for term in (
            "유언의 건",
            "소문",
            "파괴 의식",
            "방화의 계략",
            "선동의 계략",
            "인출",
            "화공",
            "캐논포",
            "폭동",
        )
    ):
        raise RuntimeError("segment 801 retains a forbidden term or mistranslation")

    expected_coordinates = {
        f"15:{record_id}:{literal_id}"
        for record_id, arity in EXPECTED_CURRENT_ARITIES.items()
        for literal_id in range(arity)
        if f"15:{record_id}:{literal_id}" != BLANK_NON_DISPLAY_COORDINATE
    }
    if len(TRANSLATIONS) != 24 or set(TRANSLATIONS) != expected_coordinates:
        raise RuntimeError("segment 801 decision/runtime/blank classification count drifted")


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
        raise RuntimeError("segment 801 Base record count drifted from 19152")

    target_records = {(15, record_id) for record_id in EXPECTED_CURRENT_ARITIES}
    outside_exact = 0
    for key, current_record in current_records.items():
        if key not in target_records:
            if rebuilt_records[key].data != current_record.data:
                raise RuntimeError(f"segment 801 changed an out-of-scope record: {key}")
            outside_exact += 1
    if outside_exact != 19143:
        raise RuntimeError("segment 801 outside-scope byte-exact record count drifted")
    for record_key in target_records:
        if record_gaps_hex(rebuilt_records[record_key]) != record_gaps_hex(
            current_records[record_key]
        ):
            raise RuntimeError(f"segment 801 changed a target opaque skeleton: {record_key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(f"segment 801 literal failed UTF-16 round-trip: {key}")
    if ENGINE.parse_record_literals(rebuilt_records[(15, 254)])[2].text != "\n":
        raise RuntimeError("15:254:2 blank non-display literal changed during overlay")

    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 801 reverse overlay is not byte-exact")


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
                "segment": "base_msggame_B001_S801",
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
