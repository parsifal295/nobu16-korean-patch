#!/usr/bin/env python3
"""Build Base authoring segment 790 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S790.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s790", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:111:0": "[무장 능력이 영향을 주는 항목]",
    "14:111:1": (
        "\n"
        "무장의 능력은 명령, 건의, 합전 등 여러 요소에 영향을 줍니다.\n"
        "다음 페이지를 참고하여 가신에게 지행을 줄 때 고려합시다.\n"
        '※부대나 성주를 실행 무장으로 선택할 때는 "성 능력"을 참고합니다\n'
        "※건의는 종류마다 영향을 주는 능력이 다릅니다\n"
        "\n"
    ),
    "14:111:2": "[성 능력]",
    "14:111:3": (
        "\n"
        "성주(다이묘)의 능력을 기준으로\n"
        "영주(대관)의 능력과 상성에 따른 보너스를 더한 능력을 말합니다.\n"
        "성주가 실행 무장을 맡을 때와 부대에는 성 능력이 적용됩니다.\n"
        "\n"
        "또한 각 성 능력이 80 이상과 90 이상에 도달할 때마다\n"
        "해당 능력에 대응하는 특성이 강화됩니다."
    ),
    "14:112:0": "[무장 능력의 주요 영향 항목 목록]",
    "14:112:2": "◇통솔",
    "14:112:3": (
        "\n"
        "\u3000·부대와 성의 방어\n"
        " ·취락 장악 속도\n"
        ' ·통솔 70 이상이면 성하 방침 "방위"를 선택할 수 있다\n'
        "\n"
    ),
    "14:112:4": "◇무용",
    "14:112:5": (
        "\n"
        "\u3000·부대와 성의 공격\n"
        ' ·무용 70 이상이면 성하 방침 "공격"을 선택할 수 있다\n'
        "\n"
    ),
    "14:112:6": "◇지략",
    "14:112:7": (
        "\n"
        "\u3000·부대의 포위와 성의 대포위\n"
        " ·조략 성공률\n"
        " ·지략 60 이상이면 영주가 인접 군을 조략하기도 한다\n"
        ' ·지략 70 이상이면 성하 방침 "진군"을 선택할 수 있다\n'
        "\n"
    ),
    "14:112:8": "◇정무",
    "14:112:9": (
        "\n"
        "\u3000·성하 시설과 취락의 건설 속도\n"
        " ·정책 발령 속도\n"
        " ·외교 친선에 따른 신용 상승량\n"
        ' ·정무 70 이상이면 성하 방침 "내정"을 선택할 수 있다'
    ),
    "14:113:0": "[신분]",
    "14:113:1": (
        "\n"
        '자세력 내의 지위를 "신분"이라고 합니다.\n'
        '신분이 높을수록 다양한 "직명"에 임명될 수 있지만\n'
        "승진하려면 더 많은 훈공이 필요합니다.\n"
        "신분에는 다음 단계가 있습니다.\n"
        "\n"
        " ·숙로 ... 가장 높은 신분\n"
        '         "군단장", "성주", "영주", "대관"에 임명 가능\n'
        " ·가로 ... 숙로와 같은 직명에 임명 가능\n"
        ' ·부장 ... "성주", "영주", "대관"에 임명 가능\n'
        " ·사무라이 대장 ... 부장과 같은 직명에 임명 가능\n"
        ' ·아시가루 대장 ... "영주", "대관"에 임명 가능\n'
        ' ·조두 ... "대관"에 임명 가능 \n'
        "\n"
        "※신분에 걸맞은 직명을 주지 않으면 가신이 불만을 품고 충성이 내려갑니다"
    ),
    "14:114:0": "[충성 변동]",
    "14:114:1": (
        "\n"
        "충성은 여러 요인에 따라 변동합니다.\n"
        '충성이 낮은 무장에게는 "영지를 준다", "관직이나 가보를 준다"와\n'
        "같은 대책이 효과적입니다.\n"
        "\n"
    ),
    "14:114:2": "◇충성이 오르는 요인",
    "14:114:3": (
        "\n"
        "\u3000·충의가 두터운 성격이다\n"
        " ·다이묘의 일문이거나 배우자이거나, 다이묘와의 상성이 좋다\n"
        " ·오랫동안 다이묘 가문을 섬겼거나 신분이 높다\n"
        " ·관직이나 가보를 받았다\n"
        " ·합전에서 승리하여 위풍이 발생했다\n"
        " ·특성이나 정책의 영향\n"
        "\n"
    ),
    "14:114:4": "◇충성이 내려가는 요인",
    "14:114:5": (
        "\n"
        "\u3000·야심이 강한 성격이다\n"
        " ·다이묘에게 원한이 있거나 상성이 나쁘다\n"
        " ·새로운 다이묘를 받아들이지 못한다\n"
        " ·신분에 걸맞은 지행지를 받지 못했다\n"
        " ·자신의 영지가 공격받고 있거나 이미 빼앗겼다\n"
        " ·원래 가지고 있던 가보가 다이묘에게 몰수되었다\n"
        " ·다이묘가 외교 상대와의 약속을 깨는 등 불명예스러운 행동을 했다\n"
        " ·합전에서 패배하여 상대의 위풍이 발생했다\n"
        ' ·정책이나 조략 "유언비어"의 영향'
    ),
}

EXPECTED_GAPS = {
    111: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
    112: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
    113: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
    114: (
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x49",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
}
EXPECTED_ARITIES = {111: 4, 112: 10, 113: 2, 114: 6}
BASE_PK_DIVERGENCES = {
    "JP": set(),
    "SC": {113},
    "TC": {113},
}
PK_ONLY_RECORD_IDS = {144, 146, 148, 150, 155, 157, 159, 160}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
BASE_JP_TYPO_COORDINATE = "14:112:9"
BASE_JP_TYPO_CORRECTION_BASIS = (
    "Base JP says 知略70 in the 政務 section; Base SC/TC and Base JP 14:153:3 "
    "independently identify 政務70 as the 内政 unlock requirement"
)
BASIS = (
    "pristine_base_pc_jp_authoritative_with_base_sc_tc_and_explicit_"
    "mapped_pk_jp_en_sc_tc_auxiliary_context_except_documented_14_112_9_jp_typo"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {111: 153, 112: 154, 113: 156, 114: 158}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 790 record has no configured PK mapping: {base_record_id}") from exc


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


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
    if {mapped_pk_record_id(record_id) for record_id in EXPECTED_ARITIES} & PK_ONLY_RECORD_IDS:
        raise RuntimeError("segment 790 mapped through a PK-only expansion record")

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
        if divergences != BASE_PK_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 790 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    for record_id, expected_arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 790 literal arity drifted: 14:{record_id}")
        if record_gaps(source_records[(14, record_id)]) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 790 pristine literal/opcode boundary drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 790 current literal/opcode boundary drifted: 14:{record_id}")

    source_112 = ENGINE.parse_record_literals(source_records[(14, 112)])
    current_112 = ENGINE.parse_record_literals(current_records[(14, 112)])
    mapped_112 = ENGINE.parse_record_literals(pk_source_records[(14, 154)])
    if source_112[1].text != "\n" or current_112[1].text != "\n" or mapped_112[1].text != "\n":
        raise RuntimeError("14:112:1 blank non-display literal drifted")
    if "14:112:1" in TRANSLATIONS:
        raise RuntimeError("14:112:1 blank non-display literal must remain excluded")
    for record_id in (111, 113, 114):
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if any(not literal.text.strip() for literal in source_literals + current_literals):
            raise RuntimeError(f"segment 790 unexpectedly contains another blank literal: 14:{record_id}")
    if any(
        not literal.text.strip()
        for index, literal in enumerate(source_112 + current_112)
        if index % len(source_112) != 1
    ):
        raise RuntimeError("segment 790 14:112 contains an unexpected additional blank literal")

    source_111 = ENGINE.parse_record_literals(source_records[(14, 111)])
    source_36 = ENGINE.parse_record_literals(source_records[(14, 36)])
    if source_111[2].text != source_36[0].text:
        raise RuntimeError("segment 790 pristine exact 성 능력 heading reuse drifted")
    if TRANSLATIONS["14:111:2"] != prior_translation("14:36:0"):
        raise RuntimeError("14:111:2 must reuse the approved 성 능력 heading")

    sc_112 = ENGINE.parse_record_literals(base_context_records["SC"][(14, 112)])
    tc_112 = ENGINE.parse_record_literals(base_context_records["TC"][(14, 112)])
    source_153 = ENGINE.parse_record_literals(source_records[(14, 153)])
    if "知略70以上" not in source_112[9].text:
        raise RuntimeError("documented Base JP 14:112:9 typo changed unexpectedly")
    if "政务达70以上" not in sc_112[9].text or "政務達70以上" not in tc_112[9].text:
        raise RuntimeError("Base SC/TC no longer corroborate the 14:112:9 typo correction")
    if "内政" not in source_153[3].text or "政務70以上" not in source_153[3].text:
        raise RuntimeError("Base JP cross-record no longer corroborates the 14:112:9 correction")
    if "정무 70 이상" not in TRANSLATIONS[BASE_JP_TYPO_COORDINATE]:
        raise RuntimeError(
            f"{BASE_JP_TYPO_COORDINATE} must apply the documented correction: "
            f"{BASE_JP_TYPO_CORRECTION_BASIS}"
        )

    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[
            literal_id
        ].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"{coordinate} LF/U+3000/token layout signature drifted")
        if "\r" in translation:
            raise RuntimeError(f"{coordinate} must not add CR")
        if ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"{coordinate} retains kana or CJK Han text")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")

    expected_u3000 = {
        "14:112:3": 1,
        "14:112:5": 1,
        "14:112:7": 1,
        "14:112:9": 1,
        "14:114:3": 1,
        "14:114:5": 1,
    }
    actual_u3000 = {
        coordinate: translation.count("\u3000")
        for coordinate, translation in TRANSLATIONS.items()
        if "\u3000" in translation
    }
    if actual_u3000 != expected_u3000:
        raise RuntimeError("segment 790 protected U+3000 coordinates drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "성 능력",
        "상성",
        "대포위",
        "조략",
        "성하 방침",
        "정무 70 이상",
        "숙로",
        "가로",
        "부장",
        "사무라이 대장",
        "아시가루 대장",
        "조두",
        "지행지",
        "유언비어",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 790 required terminology drifted")
    if any(
        term in joined
        for term in (
            "궁합",
            "사무라이대장",
            "아시가루대장",
            '조략 "유언"',
            "군단 전략",
            "광역",
            "양동",
            "보급 병량",
            "평정중",
            "가재",
            "봉행",
            "감장",
            "직담",
            "약정",
            "공성전",
        )
    ):
        raise RuntimeError("segment 790 retains a forbidden term or imported PK-only guidance")

    expected_coordinates = {
        f"14:{record_id}:{literal_id}"
        for record_id, arity in EXPECTED_ARITIES.items()
        for literal_id in range(arity)
        if (record_id, literal_id) != (112, 1)
    }
    if len(TRANSLATIONS) != 21 or set(TRANSLATIONS) != expected_coordinates:
        raise RuntimeError("segment 790 decision/static classification count drifted")


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
        raise RuntimeError("segment 790 Base record count drifted from 19152")

    target_records = {(14, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 790 changed an out-of-scope record: {key}")
    for record_key in target_records:
        if record_gaps(rebuilt_records[record_key]) != record_gaps(current_records[record_key]):
            raise RuntimeError(f"segment 790 changed a target nonstring skeleton: {record_key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(f"segment 790 literal failed UTF-16 round-trip: {key}")
    if ENGINE.parse_record_literals(rebuilt_records[(14, 112)])[1].text != "\n":
        raise RuntimeError("14:112:1 blank non-display literal changed during overlay")

    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 790 reverse overlay is not byte-exact")


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
                "segment": "base_msggame_B001_S790",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
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
