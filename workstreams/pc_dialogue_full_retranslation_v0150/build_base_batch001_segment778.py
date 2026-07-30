#!/usr/bin/env python3
"""Build Base authoring segment 778 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S778.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s778",
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
    "14:46:0": "[국인중 회유]",
    "14:46:1": "\n국인중의 종속도를 높여 원군을 요청할 수 있게 합니다.\n\n",
    "14:46:2": "◇조건",
    "14:46:3": (
        "\n·국인중이 실행 군단의 성에 소속되어 있음\n"
        "·원군 요청이 불가능함\n"
        "\n"
    ),
    "14:46:4": "◇효과에 영향을 주는 요소",
    "14:46:5": '\n·능력 "정무"가 성공률에 영향',
    "14:47:0": "[국인중 편입]",
    "14:47:1": (
        "\n종속도가 높은 국인중을 편입하여\n"
        "실존 무장이 있으면 그 무장과 병력도 자세력 산하에 둡니다.\n"
        "\n"
    ),
    "14:47:2": "◇조건",
    "14:47:3": (
        "\n·국인중이 실행 군단의 성에 소속되어 있음\n"
        "·종속도가 최대임\n"
        "\n"
    ),
    "14:47:4": "◇보충",
    "14:47:5": (
        "\n국인중을 회유하면 종속도가 높아집니다.\n"
        '"국인중 회유"를 실행할 수 없는 국인중은 '
        "무장이 영내 행동으로 회유할 때까지 기다립시다."
    ),
    "14:48:0": "[본거지 이전]",
    "14:48:1": (
        "\n본거지를 이전하면 본거지와 직할령을 변경할 수 있습니다.\n"
        "현재 성에서 멀수록 비용이 늘어납니다.\n"
        "\n"
    ),
    "14:48:2": "◇본거지",
    "14:48:3": (
        "\n본거지는 다이묘가 직접 통치하며 대관을 임명할 수 있는 성입니다.\n"
        "군이 많은 성일수록 더 많은 대관을 임명할 수 있습니다.\n"
        "\n"
    ),
    "14:48:4": "◇통치 범위",
    "14:48:5": (
        "\n다이묘와 군단장의 본거지를 중심으로 지시가 닿는 성의 범위입니다.\n"
        "범위 밖의 성에는 지시가 닿지 않아 금전 수입이 크게 줄어듭니다.\n"
        "통치 범위 밖에 성이 있다면 본거지를 이전하여\n"
        "되도록 통치 범위 안에 두도록 합시다.\n"
        "그래도 범위 밖에 성이 남는다면 군단 편제를 권합니다."
    ),
    "14:49:0": "[성하 시설]",
    "14:49:1": (
        "\n성의 구획에는 금전과 노동력을 사용하여 성하 시설을 건설할 수 있습니다.\n"
        '건설하려면 "측근" 또는 시설을 지을 성의 "성주"를\n'
        "실행 무장으로 임명해야 하며, 완료까지 일정 기간이 걸립니다.\n"
        '건설한 시설은 "증축"하거나 "철거"할 수도 있습니다.\n'
        '"성하 방침"을 정하면 성주도 자율적으로 건설합니다.\n'
        "\n"
    ),
    "14:49:2": "◇구획",
    "14:49:3": (
        "\n구획 수는 성마다 다릅니다.\n"
        "평지에 있는 성일수록 많고 산속에 있는 성일수록 적은 경향이 있습니다.\n"
        "\n"
    ),
    "14:49:4": "◇건설 조건",
    "14:49:5": (
        "\n시설에 따라서는 금전과 노동력 외에 특수한 건설 조건이 필요합니다.\n"
        '조건에는 "일정 수준 이상의 석고와 상업", "정책 발령", "상위 취락 건설"이 있습니다.'
    ),
}

EXPECTED_ARITIES = {46: 6, 47: 6, 48: 6, 49: 6}
EXPECTED_DIVERGENCES = {"JP": {48}, "SC": set(), "TC": set()}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_exact_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {46: 68, 47: 69, 48: 70, 49: 72}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 778 record has no configured PK mapping: {base_record_id}"
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
    leading = tuple(line[: len(line) - len(line.lstrip(" \t\u3000"))] for line in lines)
    trailing = tuple(line[len(line.rstrip(" \t\u3000")) :] for line in lines)
    return (
        text.count("\n"),
        leading,
        trailing,
        tuple(line.count("\u3000") for line in lines),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
    )


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

    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(46, 50)
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
                f"segment 778 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 778 arity drifted: 14:{record_id}")
        expected = expected_gaps(arity)
        if record_gaps(source_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 778 pristine opcode gaps drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 778 current opcode gaps drifted: 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                raise RuntimeError(f"segment 778 contains a blank target: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 778 decision is missing: {coordinate}")
            if line_layout_signature(translation) != line_layout_signature(literal.text):
                raise RuntimeError(f"segment 778 layout signature drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 778 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 778 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(f"segment 778 retains banned fullwidth punctuation: {coordinate}")

    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 24:
        raise RuntimeError("segment 778 decision universe drifted")

    condition_source = {
        ENGINE.parse_record_literals(source_records[(14, record_id)])[2].text
        for record_id in range(42, 48)
    }
    condition_current = {
        ENGINE.parse_record_literals(current_records[(14, record_id)])[2].text
        for record_id in range(42, 48)
    }
    if condition_source != {"◇条件"} or condition_current != {"◇조건"}:
        raise RuntimeError("14:42:2~14:47:2 exact condition heading contract drifted")
    for record_id in (46, 47):
        if TRANSLATIONS[f"14:{record_id}:2"] != "◇조건":
            raise RuntimeError(f"14:{record_id}:2 exact condition translation drifted")
    for record_id in range(42, 46):
        assert_available_duplicate_decision(f"14:{record_id}:2", "◇조건")

    influence_source = {
        ENGINE.parse_record_literals(source_records[(14, record_id)])[4].text
        for record_id in range(42, 47)
    }
    influence_current = {
        ENGINE.parse_record_literals(current_records[(14, record_id)])[4].text
        for record_id in range(42, 47)
    }
    if influence_source != {"◇効果に影響する要素"} or influence_current != {
        "◇효과에 영향을 주는 요소"
    }:
        raise RuntimeError("14:42:4~14:46:4 exact influence heading contract drifted")
    if TRANSLATIONS["14:46:4"] != "◇효과에 영향을 주는 요소":
        raise RuntimeError("14:46:4 exact influence translation drifted")
    for record_id in range(42, 46):
        assert_available_duplicate_decision(
            f"14:{record_id}:4", TRANSLATIONS["14:46:4"]
        )

    source_42_5 = ENGINE.parse_record_literals(source_records[(14, 42)])[5].text
    source_46_5 = ENGINE.parse_record_literals(source_records[(14, 46)])[5].text
    current_42_5 = ENGINE.parse_record_literals(current_records[(14, 42)])[5].text
    current_46_5 = ENGINE.parse_record_literals(current_records[(14, 46)])[5].text
    if source_42_5 != source_46_5 or current_42_5 != current_46_5:
        raise RuntimeError("14:42:5/14:46:5 exact success-factor literal drifted")
    assert_available_duplicate_decision("14:42:5", TRANSLATIONS["14:46:5"])

    source_47_4 = ENGINE.parse_record_literals(source_records[(14, 47)])[4].text
    source_80_4 = ENGINE.parse_record_literals(source_records[(14, 80)])[4].text
    current_47_4 = ENGINE.parse_record_literals(current_records[(14, 47)])[4].text
    current_80_4 = ENGINE.parse_record_literals(current_records[(14, 80)])[4].text
    if source_47_4 != source_80_4 or current_47_4 != current_80_4:
        raise RuntimeError("14:47:4/14:80:4 exact 補足 literal drifted")
    if TRANSLATIONS["14:47:4"] != "◇보충":
        raise RuntimeError("14:47:4 exact 보충 translation drifted")
    assert_available_duplicate_decision("14:80:4", TRANSLATIONS["14:47:4"])

    pk_extra_71 = ENGINE.parse_record_literals(pk_source_records[(14, 71)])
    if pk_extra_71[0].text != "【本拠移転】" or len(pk_extra_71) != 6:
        raise RuntimeError("PK-only 14:71 expanded base-relocation page drifted")
    if "直談" not in pk_extra_71[1].text or "伝馬制" not in pk_extra_71[5].text:
        raise RuntimeError("PK-only 14:71 direct-talk/transmission-system clauses drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "국인중",
        "국인중 회유",
        "국인중 편입",
        "실존 무장",
        "본거지 이전",
        "성하 시설",
        "성하 방침",
        "노동력",
        "석고",
        "취락",
        "◇보충",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 778 required terminology drifted")
    if any(
        term in joined
        for term in (
            "호족",
            "취입",
            "노력",
            "본거 ",
            "직담",
            "전마제",
            "전마제도",
            "사실 무장",
        )
    ):
        raise RuntimeError("segment 778 retains a forbidden or PK-only term")


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
                "segment": "base_msggame_B001_S778",
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
