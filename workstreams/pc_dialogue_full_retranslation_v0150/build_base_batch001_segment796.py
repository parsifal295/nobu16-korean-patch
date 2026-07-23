#!/usr/bin/env python3
"""Build Base authoring segment 796 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S796.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s796",
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
    "14:142:0": "[성]",
    "14:142:1": (
        '\n"성주"가 다스립니다.\n'
        "성의 통치는 원칙적으로 성주에게 맡깁니다.\n\n"
    ),
    "14:142:2": "◇다이묘가 지시할 수 있는 일",
    "14:142:3": (
        '\n\u3000·"성하 시설" 명령\n'
        ' ·"영내 제책" 명령'
    ),
    "14:143:0": "[군]",
    "14:143:1": (
        '\n본거지 이외의 군은 "영주"가 다스립니다.\n'
        "군의 발전은 영주에게 맡깁니다.\n\n"
    ),
    "14:143:2": "◇특징",
    "14:143:3": (
        '\n\u3000·"지행" 명령으로 가신에게 군을 맡길 수 있다\n'
        " ·임명된 가신은 영주로서 군을 발전시킨다\n"
        " ·영주가 우수할수록 발전이 빠르다\n"
        " ·영주의 임명과 해임에는 신분이나 정책 조건이 있다"
    ),
    "14:144:0": "[게임의 기본적인 진행 방법]",
    "14:144:1": (
        "\n먼저 기본 명령을 사용해 게임의 흐름을 익힙시다.\n"
        "익숙하지 않을 때는 튜토리얼에 따라 플레이하기를 권합니다.\n\n"
    ),
    "14:144:2": "◇게임 시작 시",
    "14:144:3": (
        '\n\u3000●"대관", "지행" 명령\n'
        "  본거지의 군에는 대관을, 그 밖의 군에는 영주를 각각 임명할 수 있습니다.\n"
        "  대관이나 영주에게 군을 맡기면 스스로 발전시켜 금전과 병력이 늘어납니다.\n"
        '  아무에게도 맡기지 않은 성이나 군이 있다면 "대관", "지행" 명령으로 임명합시다.\n'
        "\n"
        ' ●"군 개발" 명령\n'
        "  본거지의 군에 실행합니다.\n"
        "  군 개발로 금전과 병력을 늘릴 수 있습니다.\n"
        "  처음에는 비용이 적게 드는 군 개발부터 진행하는 것이 좋습니다."
    ),
    "14:145:0": "[게임의 기본적인 진행 방법]\n◇다음으로",
    "14:145:1": (
        '\n\u3000●"성하 시설" 명령\n'
        "  성하 시설을 건설하면 해당 성에 다양한 효과를 얻을 수 있습니다.\n"
        "  금전이나 노동력에 여유가 있다면 건설해 봅시다.\n"
        "\n"
        ' ●"정책" 명령\n'
        "  세력 전체를 강화하여 큰 효과를 얻을 수 있습니다.\n"
        "  매달 비용이 들므로 수입에 여유가 있다면 발령합시다.\n"
        '  우선 할 수 있는 일을 늘려 주는 "제도 개신" 발령을 목표로 삼는 것이 좋습니다.\n'
        "  여러 정책이 있으므로 상황과 플레이 스타일에 맞춰 발령합시다.\n"
        "\n"
        ' ●"영내 제책" 명령\n'
        "  본거지 이외의 성주에게 여러 지시를 내릴 수 있습니다.\n"
        '  "석고 증강"과 "상업 발전"은 해당 성을 빨리 발전시키고 싶을 때 사용합시다.\n'
        "\n"
    ),
    "14:145:2": "◇발전한 뒤에는",
    "14:145:3": (
        '\n\u3000●"출진" 명령\n'
        "  적의 성을 공격하여 자기 세력을 확대합시다.\n"
        "  적 세력보다 병력이 많다면 공격할 기회일지도 모릅니다.\n"
        "  다만 적에게 강한 무장이 있다면 주의해야 합니다.\n"
        "  적의 성 능력을 확인하고 승산이 있어 보이면 출진해 봅시다."
    ),
    "14:146:0": "[게임 힌트]",
    "14:146:1": (
        "\n게임을 진행할 때는 주로 다음 사항을 염두에 둡시다.\n\n"
    ),
    "14:146:2": "◇항상 유의할 점①",
    "14:146:3": (
        "\n\u3000●자신이 이끄는 다이묘 가문의 상황\n"
        "  ·금전 수입과 병력은 어느 정도인가\n"
        "  ·자신보다 성이나 병력이 많은 세력이 주변에 있는가\n"
        "  ·자신보다 성이나 병력이 적은 세력이 주변에 있는가\n"
        "\n"
        " ●발전하지 않은 성이나 군은 없는가\n"
        '  ·아무에게도 맡기지 않은 군이 있다면 "지행"을 실행합시다\n'
        "   적과 가까워 전투가 예상되는 성을 우선해도 좋습니다\n"
        '  ·"성하 시설/성하 방침"으로 성을 강화합시다\n'
        "   성하 방침은 성주에게 맡기는 대신 비용이 들지 않습니다\n"
        "  ·군 하나를 완전히 개발하면 보너스를 얻어 더욱 발전합니다"
    ),
    "14:147:0": "[게임 힌트]\n◇항상 유의할 점②",
    "14:147:1": (
        "\n\u3000●금전이 충분한가\n"
        "  ·금전이 부족해 명령 실행이 불편하다면\n"
        "   상업을 늘려 금전 수입을 높일 수 있습니다\n"
        '  ·상업을 늘리려면 주로 "군 개발" 명령,\n'
        '   "성하 시설" 명령과 "영내 제책" 명령을 실행합시다\n'
        "  ·남는 병량이 있다면 거래로 매각할 수도 있습니다\n"
        "\n"
        " ●병력이 충분한가\n"
        "  ·병력이 부족해 전투가 어렵다면 석고를 늘립시다\n"
        '  ·석고를 늘리려면 주로 "군 개발" 명령,\n'
        '   "성하 시설" 명령과 "영내 제책" 명령을 실행합시다\n'
        '  ·"성하 시설" 명령으로 병력을 직접 늘릴 수도 있습니다'
    ),
}

EXPECTED_ARITIES = {142: 4, 143: 4, 144: 4, 145: 4, 146: 4, 147: 2}
EXPECTED_DIVERGENCES = {
    "JP": set(),
    "SC": {147},
    "TC": set(),
}
PK_ONLY_RECORD_IDS = {201, 203, 206, 207}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－＆"
)
PROTECTED_GLYPHS = set("◇●①②")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {142: 198, 143: 199, 144: 200, 145: 202, 146: 204, 147: 205}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 796 record has no configured PK mapping: {base_record_id}"
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
        raise RuntimeError("segment 796 mapped a PK-only expansion or variant")
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
                f"segment 796 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 796 arity drifted: 14:{record_id}")
        expected = expected_gaps(arity)
        if record_gaps(source_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 796 pristine opcode gaps drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 796 current opcode gaps drifted: 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                raise RuntimeError(f"segment 796 contains a blank target: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 796 decision is missing: {coordinate}")
            if line_layout_signature(translation) != line_layout_signature(literal.text):
                raise RuntimeError(f"segment 796 layout signature drifted: {coordinate}")
            if glyph_skeleton(translation) != glyph_skeleton(literal.text):
                raise RuntimeError(f"segment 796 protected-glyph skeleton drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 796 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 796 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(
                    f"segment 796 retains banned fullwidth punctuation: {coordinate}"
                )
    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 22:
        raise RuntimeError("segment 796 decision universe drifted")

    source_97 = ENGINE.parse_record_literals(source_records[(14, 97)])[2].text
    source_141 = ENGINE.parse_record_literals(source_records[(14, 141)])
    source_143 = ENGINE.parse_record_literals(source_records[(14, 143)])
    if source_141[0].text != source_143[0].text:
        raise RuntimeError("14:141:0/14:143:0 exact-source title reuse drifted")
    if source_97 != source_141[2].text or source_141[2].text != source_143[2].text:
        raise RuntimeError("14:97:2/14:141:2/14:143:2 exact-source heading reuse drifted")
    if TRANSLATIONS["14:143:0"] != "[군]" or TRANSLATIONS["14:143:2"] != "◇특징":
        raise RuntimeError("segment 796 exact prior-approved translation drifted")
    assert_prior_exact_decision("14:97:2", TRANSLATIONS["14:143:2"])

    pk_201 = [literal.text for literal in ENGINE.parse_record_literals(pk_source_records[(14, 201)])]
    pk_203 = [literal.text for literal in ENGINE.parse_record_literals(pk_source_records[(14, 203)])]
    pk_206 = [literal.text for literal in ENGINE.parse_record_literals(pk_source_records[(14, 206)])]
    pk_207 = [literal.text for literal in ENGINE.parse_record_literals(pk_source_records[(14, 207)])]
    if "●「城下施設」" not in pk_201[3]:
        raise RuntimeError("segment 796 PK-only expanded opening-progression page drifted")
    if "評定衆" not in pk_203[1]:
        raise RuntimeError("segment 796 PK-only council progression page drifted")
    if "◇状況によって考えること" not in pk_206[0] or "武将が足りない" not in pk_206[1]:
        raise RuntimeError("segment 796 PK-only situational-hints page drifted")
    if "防衛拠点" not in pk_207[1] or "恩賞" not in pk_207[1]:
        raise RuntimeError("segment 796 PK-only expanded situational-hints page drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "성주",
        "성하 시설",
        "영내 제책",
        "본거지",
        "영주",
        "지행",
        "신분",
        "대관",
        "군 개발",
        "튜토리얼",
        "노동력",
        "정책",
        "제도 개신",
        "석고 증강",
        "상업 발전",
        "출진",
        "성하 방침",
        "병량",
        "석고",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 796 required terminology drifted")
    forbidden_terms = (
        "본거 ",
        "본거의",
        "자세력",
        "노력",
        "커맨드",
        "군개발",
        "성하시설",
        "영내제책",
        "평정중",
        "방위 거점",
        "은상",
    )
    if any(term in joined for term in forbidden_terms):
        raise RuntimeError("segment 796 retains a forbidden legacy or PK-only term")
    if "평정" in TRANSLATIONS["14:145:1"]:
        raise RuntimeError("14:145 imported the PK-only council command")
    if "성하 시설" in TRANSLATIONS["14:144:3"]:
        raise RuntimeError("14:144 imported the PK-only opening-progression extension")
    if "상황에 따라" in TRANSLATIONS["14:147:0"]:
        raise RuntimeError("14:147 imported the PK-only situational-hints heading")
    if TRANSLATIONS["14:146:0"] != "[게임 힌트]":
        raise RuntimeError("14:146 established game-hints title drifted")
    if TRANSLATIONS["14:147:0"].splitlines()[0] != TRANSLATIONS["14:146:0"]:
        raise RuntimeError("14:146/147 repeated game-hints title drifted")


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
        raise RuntimeError("segment 796 Base record count drifted from 19152")
    target_records = {(14, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 796 changed an out-of-scope record: {key}")
    for record_key in target_records:
        if record_gaps(rebuilt_records[record_key]) != record_gaps(current_records[record_key]):
            raise RuntimeError(f"segment 796 changed a target nonstring skeleton: {record_key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(f"segment 796 literal failed UTF-16 round-trip: {key}")
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 796 reverse overlay is not byte-exact")


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
                "segment": "base_msggame_B001_S796",
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
