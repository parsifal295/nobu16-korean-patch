#!/usr/bin/env python3
"""Build Base authoring segment 791 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S791.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s791",
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
    "14:115:0": "[외교 자세를 개선하는 방법]",
    "14:115:1": (
        '\n\u3000·조략 "공물"을 실행한다\n'
        " ·역직을 부여한다(자세력이 막부 세력일 때만)\n"
        " ·동맹 세력을 줄인다\n"
        '  ※AI 레벨 "표준" 이상에서는 동맹 상대가 많은 세력이 경계받기 때문'
    ),
    "14:116:0": "[가신을 늘리는 방법]",
    "14:116:1": (
        "\n\u3000·적 세력을 멸망시키고 포박한 무장을 등용한다\n"
        ' ·영내 제책 "무장 탐색"을 실행한다\n'
        ' ·"○○중 두령" 이외의 무장이 있는 국인중을 대상으로 '
        '영내 제책 "국인중 편입"을 실행한다'
    ),
    "14:117:0": "[훈공]",
    "14:117:1": (
        '\n무장이 세력에 공헌하여 훈공을 얻으면 "신분"이 오릅니다.\n'
        "신분이 오르면 더 책임 있는 자리에 임명할 수 있으므로\n"
        "눈여겨보는 무장이 훈공을 얻도록 명령을 내립시다.\n"
        "다음과 같은 행동으로 훈공을 얻을 수 있습니다.\n"
        "\n"
    ),
    "14:117:2": "◇내정",
    "14:117:3": (
        '\n\u3000·"성주", "영주", "대관"으로서 군이나 성을 개발한다\n'
        ' ·"조두"로서 하급 업무를 맡는다\n'
        '  (정책 "호로슈 결성" 발령 필요)\n'
        " ·실행 무장으로 명령을 수행한다\n"
        "  (성하 시설, 정책, 조략, 영내 제책)\n"
        "\n"
    ),
    "14:117:4": "◇건의",
    "14:117:5": (
        "\n\u3000·제안한 건의를 성공시킨다\n"
        ' ·"영내 문제"를 해결한다\n'
        "\n"
    ),
    "14:117:6": "◇군사",
    "14:117:7": (
        "\n\u3000·적 부대를 격파하거나 적 성을 제압한다\n"
        " ·합전에서 공헌한다"
    ),
    "14:118:0": "[병량 고갈을 막으려면]",
    "14:118:1": (
        "\n\u3000·성의 저장 병량이 출진 병력 이상 쌓인 뒤 출진한다\n"
        ' ·성하 시설 "치중 집결소"를 건설한다\n'
        ' ·정책 "치중대 배치"를 발령한다\n'
        " ·공략 목표를 설정해 임전 상태로 만든다\n"
        " ·자세력의 성 위에서 대기한다\n"
        "  ※출진한 성의 병량을 사용할 수 있기 때문"
    ),
    "14:119:0": "[약소 다이묘를 위한 힌트]",
    "14:119:1": (
        "\n내정으로 국력을 높이는 것도 중요하지만\n"
        "그것만으로는 힘의 차이를 좁히지 못할 때가 있습니다.\n"
        "\n"
        "혼자서는 달리 방도가 없는 상황이라면\n"
        "동맹을 맺거나 신종하여 다른 세력의 힘을 빌리는 것이 효과적입니다.\n"
        "\n"
        "또한 주변 세력이 침공당해 피폐해지는 등\n"
        "공격할 기회를 놓치지 않도록 주변 상황을 살핍시다."
    ),
    "14:120:0": "[중견 다이묘를 위한 힌트]",
    "14:120:1": (
        "\n주변에 자신보다 약한 세력이 있다면\n"
        "공격하여 영토와 무장을 빼앗읍시다.\n"
        "\n"
        "자리를 비운 사이 다른 세력의 공격을 받지 않도록\n"
        "내정으로 영지를 지킬 병력을 늘리거나\n"
        "미리 위험한 상대와 동맹을 맺으면 더욱 안전합니다.\n"
        "\n"
        "전쟁이 길어질 듯하면 합전을 벌여\n"
        "단숨에 결판을 내는 것도 효과적입니다."
    ),
    "14:121:0": "[대다이묘를 위한 힌트]",
    "14:121:1": (
        "\n지나치게 넓은 영토를 다이묘 혼자 다스리기는 어려우므로\n"
        "군단을 만들어 휘하 무장에게 맡기는 것이 중요합니다.\n"
        "\n"
        "약소 세력은 외교로 종속시킬 수 있는 경우가 있습니다.\n"
        "불필요한 전쟁을 피하는 것도 천하통일의 지름길이 될 것입니다."
    ),
    "14:122:0": "[조략]",
    "14:122:1": (
        "\n다른 세력에 약화나 공격 등의 공작을 벌입니다.\n"
        '"다이묘", "성주", "측근"이 실행할 수 있습니다.\n'
        "\n"
        "·유언비어 ... 대상 무장의 충성을 낮춘다\n"
        "·빼내기 ... 충성이 낮은 무장을 자세력으로 빼낸다\n"
        "·선동 ... 대상 성의 군에서 잇키를 일으킨다\n"
        "·파괴 ... 대상 성의 내구와 병력을 줄인다\n"
        "·방화 ... 대상 성의 병량과 병력을 줄인다\n"
        "·공물 ... 대상 세력에 가보를 보내 외교 자세를 개선한다\n"
        "\n"
    ),
    "14:122:2": "◇주의",
    "14:122:3": (
        '\n"조략" 명령은 원하는 때에 실행할 수 있는 대신\n'
        "가신의 건의보다 금전과 노동력, 효과와 기간 면에서 효율이 낮습니다."
    ),
}

EXPECTED_ARITIES = {115: 2, 116: 2, 117: 8, 118: 2, 119: 2, 120: 2, 121: 2, 122: 4}
EXPECTED_DIVERGENCES = {
    "JP": {115, 116, 117, 118, 120, 121, 122},
    "SC": {115, 117, 118, 120, 121, 122},
    "TC": {115, 117, 118, 120, 121, 122},
}
PK_ONLY_RECORD_IDS = {162, 165, 167, 172}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
PROTECTED_GLYPHS = set("◇○※")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {
        115: 161,
        116: 163,
        117: 164,
        118: 166,
        119: 168,
        120: 169,
        121: 170,
        122: 171,
    }
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 791 record has no configured PK mapping: {base_record_id}"
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
        raise RuntimeError("segment 791 mapped a PK-only expansion or variant")
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
                f"segment 791 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 791 arity drifted: 14:{record_id}")
        expected = expected_gaps(arity)
        if record_gaps(source_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 791 pristine opcode gaps drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 791 current opcode gaps drifted: 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                raise RuntimeError(f"segment 791 contains a blank target: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 791 decision is missing: {coordinate}")
            if line_layout_signature(translation) != line_layout_signature(literal.text):
                raise RuntimeError(f"segment 791 layout signature drifted: {coordinate}")
            if glyph_skeleton(translation) != glyph_skeleton(literal.text):
                raise RuntimeError(f"segment 791 protected-glyph skeleton drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 791 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 791 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(
                    f"segment 791 retains banned fullwidth punctuation: {coordinate}"
                )
    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 24:
        raise RuntimeError("segment 791 decision universe drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "외교 자세",
        "조략",
        "공물",
        "역직",
        "무장 탐색",
        "국인중 편입",
        "훈공",
        "신분",
        "호로슈 결성",
        "건의",
        "병량",
        "치중 집결소",
        "치중대 배치",
        "공략 목표",
        "임전",
        "신종",
        "대다이묘",
        "유언비어",
        "빼내기",
        "선동",
        "파괴",
        "방화",
        "노동력",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 791 required terminology drifted")
    forbidden_terms = (
        "호족",
        "호족 포섭",
        "유언 ...",
        "인발",
        "화공",
        "노력",
        "보급 거점",
        "감장",
        "직명에 임명",
    )
    if any(term in joined for term in forbidden_terms):
        raise RuntimeError("segment 791 retains a forbidden legacy or PK-only term")
    if "동맹이나 종속 관계" in TRANSLATIONS["14:115:1"]:
        raise RuntimeError("14:115 imported the PK-only added diplomacy method")
    if "외교" in TRANSLATIONS["14:117:3"] or "공성전" in TRANSLATIONS["14:117:7"]:
        raise RuntimeError("14:117 imported PK-only honor guidance")
    if "공물 ..." not in TRANSLATIONS["14:122:1"]:
        raise RuntimeError("14:122 drifted toward the PK-only no-tribute variant")
    if "영토" not in TRANSLATIONS["14:120:1"] or "영토" not in TRANSLATIONS["14:121:1"]:
        raise RuntimeError("14:120/121 Base 領土 semantics drifted toward mapped PK")


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
                "segment": "base_msggame_B001_S791",
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
