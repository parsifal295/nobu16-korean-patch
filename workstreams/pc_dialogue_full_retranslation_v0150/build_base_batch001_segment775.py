#!/usr/bin/env python3
"""Build Base authoring segment 775 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S775.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s775", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:33:0": "◇신분 목록",
    "14:33:1": (
        "\n\u3000·숙로   ... 가장 높은 신분\n"
        '         "군단장", "성주", "영주", "대관"에 임명 가능\n'
        "·가로   ... 숙로와 같은 직명에 임명 가능\n"
        '·부장   ... "성주", "영주", "대관"에 임명 가능\n'
        "·사무라이 대장 ... 부장과 같은 직명에 임명 가능\n"
        '·아시가루 대장 ... "영주", "대관"에 임명 가능\n'
        '·조두   ... "대관"에 임명 가능\n'
        "\n"
    ),
    "14:33:2": "◇직명 목록",
    "14:33:3": (
        "\n\u3000·다이묘  ... 자세력의 다이묘. 본거지 성주와 다이묘 군단의 군단장을 겸임\n"
        "·군단장 ... 다이묘 군단 이외의 군단을 이끄는 무장\n"
        '·성주  ... 본거지 이외의 "성"을 통치하는 무장\n'
        '·영주  ... 본거지가 아닌 성 영내의 "군"을 통치하는 무장\n'
        "·대관  ... 다이묘를 대신하여 본거지 영내의 군을 통치하는 무장\n"
        "·측근  ... 위에 해당하지 않는 무장\n"
        "\n"
        "※신분에 걸맞은 직명을 주지 않으면 가신은 불만을 품고 충성이 떨어집니다\n"
        "※적절히 영지를 넓혀 성주나 군단장으로 임명할 수 있도록 합시다"
    ),
    "14:34:0": "[영주 임명]",
    "14:34:1": (
        '\n신분이 "아시가루 대장" 이상인 무장을 "영주"로 임명할 수 있습니다.\n'
        "영주는 영지의 내정과 군비를 자율적으로 운영합니다.\n"
        "다만 한 군만 통치할 수 있으며 건의나 임무를 수행할 수 없게 됩니다.\n"
        "\n"
    ),
    "14:34:2": "◇영주가 할 수 있는 일",
    "14:34:3": (
        '\n\u3000"취락 장악/건설", "군비", "출진", "국인중 회유", "조략"\n'
        "\n"
    ),
    "14:34:4": "◇지행 힌트",
    "14:34:5": (
        "\n\u3000·영주의 능력  ... 성 능력 상승에 영향을 준다(4페이지 참조)\n"
        "·영주의 통솔  ... 영지의 군비와 취락 장악 속도에 영향을 준다\n"
        "·영주의 지략  ... 60 이상이면 인접한 적의 군에 자동으로 조략을 실행한다\n"
        "·영주의 정무  ... 개발 용지의 건설 속도에 영향을 준다\n"
        "·성주와의 상성 ... 성주와 상성이 ◎이면 성 능력이 오른다\n"
        "\n"
        '※영주로 임명하면 정책 "제도 개신" LV2를 발령할 때까지 바꿀 수 없습니다\n'
        "※변경할 수 있다면 무장 선택 시 임명 중인 무장("
    ),
    "14:34:6": "┝",
    "14:34:7": ")을 선택하면 해임할 수 있습니다\n※출진 중에는 영주를 변경할 수 없습니다",
    "14:35:0": "[성주 임명]",
    "14:35:1": (
        '\n신분이 "사무라이 대장" 이상인 무장을 "성주"로 임명할 수 있습니다.\n'
        '성주는 성이 있는 군을 "영지"로 삼아\n'
        "영주와 마찬가지로 내정과 군비를 자율적으로 운영합니다.\n"
        "※성주의 신분이 높을수록 더 많은 군을 영지로 삼을 수 있습니다\n"
        "\n"
        "또한 정책이나 성하 시설 등의 실행 무장으로 임명할 수도 있습니다.\n"
        "\n"
    ),
    "14:35:2": "◇영주와 성주의 차이",
    "14:35:3": (
        "\n\u3000·성주의 능력이 성 능력의 기준이 된다(4페이지 참조)\n"
        "·실행 무장으로 임명할 수 있다\n"
        '·신분이 "부장" 이상인 성주는 여러 군을 영지로 삼을 수 있다\n'
        "·신분이 높을수록 더 많은 군을 영지로 삼을 수 있다\n"
        "\n"
        '※성주로 임명하면 정책 "제도 개신" LV3를 발령할 때까지 바꿀 수 없습니다'
    ),
    "14:36:0": "[성 능력]",
    "14:36:1": (
        "\n성에도 무장과 마찬가지로 통솔, 무용, 지략, 정무 능력이 있습니다.\n"
        "내정이나 행군 등 성 단위로 이루어지는 행동에 사용됩니다.\n"
        "\n"
    ),
    "14:36:2": "◇성 능력의 영향",
    "14:36:3": (
        "\n\u3000·성 통솔 ... 출진 부대의 방어력, 성의 방어력\n"
        "·성 무용 ... 출진 부대의 공격력, 성의 공격력\n"
        "·성 지략 ... 출진 부대의 포위, 성의 대포위\n"
        "·성 정무 ... 성의 수입\n"
        "\n"
        "※성 능력이 80과 90을 각각 넘을 때마다\n"
        "  해당 능력의 특성이 강화됩니다\n"
        "\n"
    ),
    "14:36:4": "◇성 능력을 높이려면",
    "14:36:5": (
        "\n\u3000·능력이 높은 무장을 성주로 임명한다\n"
        "·성주보다 높은 능력이 있거나 성주와 상성이 좋은 무장을 영주로 임명한다"
    ),
}

BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
PROTECTED_GLYPHS = set("┝")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
)
EXPECTED_ARITY = {33: 4, 34: 8, 35: 4, 36: 6}


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {33: 50, 34: 52, 35: 54, 36: 56}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 775 record has no configured PK mapping: {base_record_id}") from exc


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in PROTECTED_GLYPHS]


def layout_signature(text: str) -> tuple[object, ...]:
    return (
        text.count("\n"),
        tuple(line.count("\u3000") for line in text.split("\n")),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(ENGINE.protected_signature(text)["non_layout_controls"]),
        ENGINE.protected_signature(text)["leading_whitespace"],
        ENGINE.protected_signature(text)["trailing_whitespace"],
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
    expected_divergences = {"JP": set(), "SC": {33, 34}, "TC": {33, 34}}
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(33, 37)
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
        if divergences != expected_divergences[language]:
            raise RuntimeError(
                f"segment 775 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    for record_id, expected_arity in EXPECTED_ARITY.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 775 literal arity drifted: 14:{record_id}")
    for coordinate, translation in TRANSLATIONS.items():
        _, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(14, record_id)])[literal_id].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"{coordinate} LF/U+3000/ESC layout signature drifted")
        if "\r" in translation:
            raise RuntimeError(f"{coordinate} retains CR")
        if ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"{coordinate} retains kana or CJK Han text")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")
        if glyph_skeleton(translation) != glyph_skeleton(current_text):
            raise RuntimeError(f"{coordinate} protected-glyph skeleton drifted")
    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "조두",
        "아시가루 대장",
        "사무라이 대장",
        "부장",
        "가로",
        "숙로",
        "직명",
        "영주",
        "성주",
        "대관",
        "측근",
        "국인중",
        "제도 개신",
        "포위",
        "대포위",
        "상성",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 775 required terminology drifted")
    if any(
        term in joined
        for term in (
            "호족",
            "아시가루대장",
            "사무라이대장",
            "제도개신",
            "포위 내성",
            "궁합",
            "평정중",
            "가재",
            "봉행",
            "소령 안도",
            "직담",
        )
    ):
        raise RuntimeError("segment 775 retains a forbidden legacy term")
    if TRANSLATIONS["14:34:6"] != "┝":
        raise RuntimeError("14:34:6 protected icon drifted")
    if not TRANSLATIONS["14:34:5"].endswith("(") or not TRANSLATIONS["14:34:7"].startswith(")"):
        raise RuntimeError("14:34:5+6+7 icon-gap assembly drifted")
    if len(TRANSLATIONS) != 22 or set(TRANSLATIONS) != {
        f"14:{record_id}:{literal_id}"
        for record_id, arity in EXPECTED_ARITY.items()
        for literal_id in range(arity)
    }:
        raise RuntimeError("segment 775 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S775",
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
