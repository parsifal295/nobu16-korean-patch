#!/usr/bin/env python3
"""Build Base authoring segment 793 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S793.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s793",
        ENGINE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
COMMON_RELATION_CONDITIONS = (
    "\n·동맹, 종속, 정전 관계가 아니며 동맹 상대의 종속 세력도 아님\n"
    "·자세력과 인접한 성임\n"
)
COMMON_SUCCESS_FACTORS = (
    "\n·실행 무장의 지략이 성공률에 영향을 준다\n"
    '·대상 무장의 소속 성에 특성 "이닌도"가 발현되어 있으면 실패한다'
)
TRANSLATIONS: dict[str, str] = {
    "14:127:0": "[방화]",
    "14:127:1": "\n적 성의 병력과 병량을 줄입니다.\n\n",
    "14:127:2": "◇조건",
    "14:127:3": COMMON_RELATION_CONDITIONS + "\n",
    "14:127:4": "◇효과에 영향을 주는 요소",
    "14:127:5": COMMON_SUCCESS_FACTORS,
    "14:128:0": "[공물]",
    "14:128:1": "\n다른 세력에 가보를 보내 외교 자세를 개선합니다.\n\n",
    "14:128:2": "◇조건",
    "14:128:3": (
        "\n·보낼 수 있는 가보가 있음\n"
        "·인접한 세력임\n"
        "·외교 자세가 협조, 보통, 불신, 적대 중 하나임\n"
        '·특성 "교언"을 보유한 무장 또는 다이묘\n'
        "\n"
    ),
    "14:128:4": "◇효과에 영향을 주는 요소",
    "14:128:5": (
        "\n·실행 무장의 지략이 기간에 영향을 준다\n"
        "·가보의 등급이 외교 자세 개선도와 효과 지속 기간에 영향을 준다"
    ),
    "14:129:0": "[영내 문제]",
    "14:129:1": (
        "\n영내의 군에서는 무장을 파견하지 않으면 해결하기 어려운 문제가 생기기도 합니다.\n"
        '그럴 때는 "성주"나 "측근"을 지명하여 해결하게 합시다.\n'
        '영내 문제에는 "영내 황폐", "국경 분쟁", "상위 취락 건설"이 있습니다.\n'
        "\n"
    ),
    "14:129:2": "◇영내 황폐",
    "14:129:3": (
        "\n\u3000·전투나 조략, 재해로 피해를 입은 군에서 발생하기도 한다\n"
        " ·보통 해결하기까지 오랜 기간이 필요하다\n"
        " ·해결할 때까지 해당 군에서 금전/병량 수입을 얻을 수 없다\n"
        " ·무장을 파견하지 않고 방치하면 잇키가 일어나기도 한다\n"
        "  ※파견 중에는 잇키가 발생하지 않는다\n"
        " ·다이묘가 지시하면 해결에 필요한 기간이 크게 단축된다"
    ),
    "14:130:0": "◇국경 분쟁",
    "14:130:1": (
        '\n\u3000·성주가 특성 "혈기"를 지녔거나 '
        '"무용 60 이상, 지략 60 미만"이면 발생하기도 한다\n'
        " ·해결할 때까지 해당 성의 모든 군에서 금전/병량 수입을 얻을 수 없다\n"
        " ·무장을 파견하지 않으면 적의 군을 제압하려고 독단으로 출진하기도 한다\n"
        "  ※파견 중에는 독단으로 출진하지 않는다\n"
        " ·독단으로 군을 제압하면 공성전까지 이어질 수도 있다\n"
        " ·출진한 부대는 지시를 받지 않는다\n"
        "\n"
    ),
    "14:130:2": "◇상위 취락 건설",
    "14:130:3": (
        "\n\u3000·군 내 취락을 일정 수준까지 장악/건설하면 발생한다\n"
        " ·문제를 해결하면 상위 취락이 건설된다\n"
        "  ※무장을 파견하지 않고 방치하면 건설되지 않는다\n"
        " ·건설된 군은 상위 취락의 효과를 얻는다\n"
        "  ※상위 취락에 따라 정책 발령에 필요한 것도 있다"
    ),
    "14:131:0": "[전봉]",
    "14:131:1": (
        "\n다이묘 군단 내 무장의 지행지를 한꺼번에 변경할 수 있습니다.\n"
        '정책 "제도 개신" LV2로 해금됩니다.\n'
        "\n"
    ),
    "14:131:2": "◇변경 방법",
    "14:131:3": (
        "\n\u3000·이동 ... 두 성 사이에서 무장의 지행지를 서로 바꾼다\n"
        "       ※본거지의 무장은 지행지가 없으므로 선택할 수 없다\n"
        " ·소환 ... 군단 내 무장을 불러들여 지정한 성의 군을 내린다\n"
        "\n"
        "※성주에게 여러 군을 맡기려면 화면 왼쪽 아래 버튼에서 설정할 수 있습니다"
    ),
}

EXPECTED_ARITIES = {127: 6, 128: 6, 129: 4, 130: 4, 131: 4}
EXPECTED_DIVERGENCES = {"JP": {127}, "SC": {130}, "TC": {130}}
PK_ONLY_RECORD_IDS = {180, 182}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
PROTECTED_GLYPHS = set("◇※")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {127: 177, 128: 178, 129: 179, 130: 181, 131: 183}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 793 record has no configured PK mapping: {base_record_id}"
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
    return tuple([b"\x1b\x43\x49", b"\x1b\x43\x5a"] * (arity // 2) + [b"\x05\x05\x05"])


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


def assert_available_duplicate_decision(coordinate: str, translation: str) -> None:
    if not OUTPUT.parent.is_dir():
        return
    for decision_path in OUTPUT.parent.glob("base_msggame_B001_S*.private.v1.jsonl"):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate and row.get("translation") != translation:
                raise RuntimeError(f"duplicate translation differs from {coordinate}")


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
        raise RuntimeError("segment 793 mapped a PK-only landmark expansion")
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
                f"segment 793 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 793 arity drifted: 14:{record_id}")
        expected = expected_gaps(arity)
        if record_gaps(source_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 793 pristine opcode gaps drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 793 current opcode gaps drifted: 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                raise RuntimeError(f"segment 793 contains a blank target: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 793 decision is missing: {coordinate}")
            if line_layout_signature(translation) != line_layout_signature(literal.text):
                raise RuntimeError(f"segment 793 layout signature drifted: {coordinate}")
            if glyph_skeleton(translation) != glyph_skeleton(literal.text):
                raise RuntimeError(f"segment 793 protected-glyph skeleton drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 793 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 793 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(
                    f"segment 793 retains banned fullwidth punctuation: {coordinate}"
                )
    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 24:
        raise RuntimeError("segment 793 decision universe drifted")

    if TRANSLATIONS["14:127:2"] != TRANSLATIONS["14:128:2"]:
        raise RuntimeError("14:127/128 exact condition heading drifted")
    if TRANSLATIONS["14:127:4"] != TRANSLATIONS["14:128:4"]:
        raise RuntimeError("14:127/128 exact influence heading drifted")
    assert_available_duplicate_decision("14:126:2", TRANSLATIONS["14:127:2"])
    assert_available_duplicate_decision("14:126:3", TRANSLATIONS["14:127:3"])
    assert_available_duplicate_decision("14:126:4", TRANSLATIONS["14:127:4"])
    assert_available_duplicate_decision("14:126:5", TRANSLATIONS["14:127:5"])
    assert_available_duplicate_decision("13:480:0", '"전봉"')

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "방화",
        "병량",
        "공물",
        "외교 자세",
        "교언",
        "영내 문제",
        "영내 황폐",
        "국경 분쟁",
        "상위 취락",
        "공성전",
        "전봉",
        "지행지",
        "제도 개신",
        "소환",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 793 required terminology drifted")
    if any(
        term in joined for term in ("화공", "호출", "호족", "명소", "노력", "적시")
    ):
        raise RuntimeError("segment 793 retains a forbidden legacy or PK-only term")
    if "명소" in TRANSLATIONS["14:129:1"]:
        raise RuntimeError("14:129 imported the PK-only landmark problem")
    if "공성전" not in TRANSLATIONS["14:130:1"]:
        raise RuntimeError("14:130 Base 城攻め semantics drifted toward mapped PK context")
    if TRANSLATIONS["14:131:1"].splitlines()[1:] != [
        "다이묘 군단 내 무장의 지행지를 한꺼번에 변경할 수 있습니다.",
        '정책 "제도 개신" LV2로 해금됩니다.',
        "",
    ]:
        raise RuntimeError("14:131 prior-approved core explanation drifted")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_scope(prepared)
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
                "segment": "base_msggame_B001_S793",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
                "confirmed_non_display": 0,
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
