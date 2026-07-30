#!/usr/bin/env python3
"""Build Base authoring segment 772 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S772.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s772",
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
    "14:19:0": "[상인과 거래]",
    "14:19:1": (
        "\n병량과 가보는 상인과 사고팔 수 있습니다.\n"
        "병량 시세는 계절이나 풍작, 흉작 등에 따라 변합니다.\n\n"
    ),
    "14:19:2": "◇포인트",
    "14:19:3": (
        "\n　·병량 거래 가능량에는 상한이 있으며 계절마다 갱신된다\n"
        "  (1월, 4월, 7월, 10월)\n"
        " ·계절과 풍작 등의 요인에 따라 병량 시세가 변한다\n"
        " ·본거지의 병량만 거래에 사용된다\n"
        " ·구입할 수 있는 가보는 계절마다 바뀐다\n"
        ' ·등급이 높은 가보를 구입하려면 정책 "라쿠이치라쿠자"를 발령해야 한다\n'
        " ·가보를 가신에게 주면 가신의 충성을 높일 수 있다\n"
        ' ·조략 "공물"로 다른 세력에 가보를 보내면 외교 관계를 개선할 수 있다'
    ),
    "14:20:0": "[친선]",
    "14:20:1": (
        "\n다른 세력이나 막부(다이묘가 정이대장군인 세력)와의 관계 개선을 꾀합니다.\n"
        '중개자를 정하고 월말에 금전을 소비하면 매달 "신용"을 얻을 수 있습니다.\n\n'
    ),
    "14:20:2": "◇중개자에 대하여",
    "14:20:3": (
        '\n"다이묘" 또는 신분이 "부장" 이상인 "성주"와 "측근"을 중개자로 임명할 수 있습니다.\n\n'
    ),
    "14:20:4": "◇신용이 오르기 쉬운 정도\n",
    "14:20:5": (
        "신용이 오르기 쉬운 정도는 다음 요인에 따라 달라집니다.\n"
        " ·외교 자세(우호>협조>보통>불신>적대)\n"
        " ·중개자 무장의 정무\n"
        " ·신용 증감에 영향을 주는 중개자 무장의 특성\n"
        " ·자세력과 상대 세력의 위신 차이\n"
        " ·상대 세력이 자세력에 종속되어 있음"
    ),
    "14:21:0": "◇외교 자세에 대하여",
    "14:21:1": (
        "\n상대의 외교 자세가 좋을수록 친선으로 신용을 올리기 쉬워집니다.\n"
        "외교 자세는 상황에 따라 변합니다.\n"
        "\n"
        "외교 자세가 좋은 순서는 다음과 같습니다.\n"
        "\n"
        "우호>협조>보통>불신>적대\n"
        "\n"
        "외교 자세는 어디까지나 겉으로 내세우는 태도이므로\n"
        '"우호"인 세력도 공격해 올 수 있습니다.\n'
        "\n"
        '또한 AI 레벨이 "표준" 이상일 때 다른 세력과 동맹을 맺으면\n'
        "이를 경계해 외교 관계가 악화될 수 있습니다.\n"
        "그 밖에도 외교 자세가 변하는 경우가 있으므로\n"
        "동맹을 맺고 싶은 상대와는 관계가 좋을 때 친선을 행합시다."
    ),
    "14:22:0": "[교섭]",
    "14:22:1": (
        "\n친선으로 높인 신용을 바탕으로 다른 세력이나 막부와 교섭합니다.\n"
        "신용이 충분하고 조건을 충족하면 반드시 성공합니다.\n\n"
    ),
    "14:22:2": "◇교섭 내용에 대하여",
    "14:22:3": (
        "\n　·동맹 ... 12개월 동안 동맹을 맺는다\n"
        "       ※동맹 상대에게 종속 세력이 있으면 그 세력과도 동맹을 맺는다\n"
        " ·원군 ... 적의 성을 공격할 공략 원군을 요청한다\n"
        " ·방어 ... 자세력이나 신종 세력의 성을 방어할 방어 원군을 요청한다\n"
        " ·중개 ... 교전 중인 다른 세력과의 정전을 중개받는다\n"
        "       정전하려는 세력보다 한 단계 영향력이 큰 세력에 요청할 수 있다\n"
        "       ※영향력이란 위신과 병력을 종합한 힘을 말한다\n"
        " ·혼인 ... 공주가 시집가는 형태로 혼인 동맹을 맺는다\n"
        "       혼인한 무장이 사망하거나 세력을 떠나면 6개월 동맹으로 전환된다\n"
        " ·파기 ... 동맹이나 종속 관계를 일방적으로 파기한다\n"
        "       주변 세력과의 외교 관계가 악화된다\n"
        "       외교 관계를 파기한 뒤에는 3개월간 정전에 들어간다\n"
        " ·종속 ... 상대 세력을 자세력에 종속시킨다\n"
        " ·신종 ... 상대 세력에 종속을 신청한다\n"
        " ·역직 ... 막부 역직을 요구한다(상대가 막부일 때만)"
    ),
    "14:23:0": "[조정]",
    "14:23:1": (
        "\n관직을 얻기 위해 조정에 헌금합니다.\n"
        '무장을 "중개자"로 임명해 헌금하면 매달 "신용"을 얻을 수 있습니다.\n'
        "얻을 수 있는 관직은 현재 보유한 관직보다 위계가 높은 것에 한합니다.\n\n"
    ),
    "14:23:2": "◇중개자에 대하여",
    "14:23:3": (
        '\n"다이묘" 또는 신분이 "부장" 이상인 "성주"와 "측근"을 중개자로 임명할 수 있습니다.\n\n'
    ),
    "14:23:4": "◇관직의 이점",
    "14:23:5": (
        "\n관직을 얻으면 관위의 높이에 따라 세력의 위신이 높아집니다.\n"
        "또한 새 관직을 받으면 이전 관직은\n"
        '"상벌" 명령으로 가신에게 수여해 충성을 높일 수 있습니다.\n'
        "※위신 증가에 영향을 주는 것은 보유한 관직 중 관위가 가장 높은 것뿐입니다"
    ),
}

EXPECTED_ARITIES = {19: 4, 20: 6, 21: 2, 22: 4, 23: 6}
EXPECTED_DIVERGENCES = {"JP": {23}, "SC": {22, 23}, "TC": {22, 23}}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_exact_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_semantics_priority"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {19: 27, 20: 29, 21: 30, 22: 32, 23: 35}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 772 record has no configured PK mapping: {base_record_id}"
        ) from exc


def line_layout_signature(text: str) -> tuple[object, ...]:
    lines = text.split("\n")
    leading = tuple(
        line[: len(line) - len(line.lstrip(" \t\u3000"))]
        for line in lines
    )
    trailing = tuple(
        line[len(line.rstrip(" \t\u3000")) :]
        for line in lines
    )
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
            for record_id in range(19, 24)
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
                f"segment 772 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, expected_arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 772 arity drifted at 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                raise RuntimeError(f"segment 772 unexpectedly contains a blank target: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 772 decision is missing: {coordinate}")
            if line_layout_signature(translation) != line_layout_signature(literal.text):
                raise RuntimeError(f"segment 772 layout signature drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 772 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 772 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(f"segment 772 retains banned fullwidth punctuation: {coordinate}")

    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 22:
        raise RuntimeError("segment 772 decision universe drifted")
    for literal_id in (2, 3):
        if TRANSLATIONS[f"14:20:{literal_id}"] != TRANSLATIONS[f"14:23:{literal_id}"]:
            raise RuntimeError(f"14:20:{literal_id}/14:23:{literal_id} exact translation drifted")
    if TRANSLATIONS["14:19:2"] != "◇포인트":
        raise RuntimeError("14:19:2 must use the centrally synchronized duplicate wording")
    assert_available_duplicate_decision("14:27:2", TRANSLATIONS["14:19:2"])

    for left, right in (((19, 2), (27, 2)), ((20, 2), (23, 2)), ((20, 3), (23, 3))):
        source_left = ENGINE.parse_record_literals(source_records[(14, left[0])])[left[1]].text
        source_right = ENGINE.parse_record_literals(source_records[(14, right[0])])[right[1]].text
        current_left = ENGINE.parse_record_literals(current_records[(14, left[0])])[left[1]].text
        current_right = ENGINE.parse_record_literals(current_records[(14, right[0])])[right[1]].text
        if source_left != source_right:
            raise RuntimeError(f"pristine exact literal drifted: 14:{left[0]}:{left[1]} != 14:{right[0]}:{right[1]}")
        if current_left != current_right:
            raise RuntimeError(f"current exact literal drifted: 14:{left[0]}:{left[1]} != 14:{right[0]}:{right[1]}")

    base_court = ENGINE.parse_record_literals(source_records[(14, 23)])
    pk_court = ENGINE.parse_record_literals(
        pk_source_records[(14, mapped_pk_record_id(23))]
    )
    if "位階" not in base_court[1].text or "官位" in base_court[1].text:
        raise RuntimeError("14:23:1 Base rank terminology contract drifted")
    if "官位" not in base_court[5].text or "位階" in base_court[5].text:
        raise RuntimeError("14:23:5 Base court-rank terminology contract drifted")
    if "信用が上がると官職を得られます" not in pk_court[1].text:
        raise RuntimeError("14:23 mapped PK trust expansion contract drifted")
    if "官職の位階が高いほど必要な献金の量は増加します" not in pk_court[1].text:
        raise RuntimeError("14:23 mapped PK donation expansion contract drifted")
    if "위계" not in TRANSLATIONS["14:23:1"] or "관위" in TRANSLATIONS["14:23:1"]:
        raise RuntimeError("14:23:1 must translate 位階 as 위계")
    if "관위" not in TRANSLATIONS["14:23:5"] or "위계" in TRANSLATIONS["14:23:5"]:
        raise RuntimeError("14:23:5 must translate 官位 as 관위")
    if "적의 성" not in TRANSLATIONS["14:22:3"] or "적성" in TRANSLATIONS["14:22:3"]:
        raise RuntimeError("14:22:3 must disambiguate 敵城 as 적의 성")
    if " ·방어 ..." not in TRANSLATIONS["14:22:3"] or "방어 원군" not in TRANSLATIONS["14:22:3"]:
        raise RuntimeError("14:22:3 must use the established 방어/방어 원군 terms")
    if "공략 원군" not in TRANSLATIONS["14:22:3"]:
        raise RuntimeError("14:22:3 must use the established 공략 원군 term")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "병량",
        "본거지",
        "조략",
        "공물",
        "중개자",
        "외교 자세",
        "영향력",
        "역직",
        "관직",
        "위계",
        "관위",
        "라쿠이치라쿠자",
        "공략 원군",
        "방어 원군",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 772 required terminology drifted")
    if any(
        term in joined
        for term in ("취차", "중개역", "군량", "아군 세력", "방위", "낙시낙좌")
    ):
        raise RuntimeError("segment 772 retains a forbidden legacy term")
    if any(
        phrase in TRANSLATIONS["14:23:1"]
        for phrase in ("신용이 오르면 관직", "관위가 높을수록 필요한 헌금")
    ):
        raise RuntimeError("14:23 imported a PK-only Imperial Court expansion")


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
        target = prepared.visible_targets.get(
            ("base_msggame", block_id, record_id, literal_id)
        )
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
        raise RuntimeError(
            "validated decision count differs from the segment translation count"
        )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S772",
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
