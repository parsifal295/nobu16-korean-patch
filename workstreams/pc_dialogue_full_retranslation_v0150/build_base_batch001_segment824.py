#!/usr/bin/env python3
"""Build Base authoring segment 824 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment818 as SHARED


ENGINE = SHARED.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S824.private.v1.jsonl"
SEGMENT = 824
RAW_TRANSLATIONS: dict[str, str] = {
    "15:508:0": "전선과 가까운",
    "15:508:1": "이(가) 우리 편에 선다면\n전시에 든든한 힘이 된다",
    "15:508:2": "\n미리 회유해 두어 나쁠 것은 없을 듯하옵니다",
    "15:509:0": (
        "은(는) 거취를 정하지 못한 모양\n"
        "적의 영지와도 가까우니 금품이라도 보내\n"
        "확실히 우리 편으로 만들어 두"
    ),
    "15:510:0": "금품을 조금 보내",
    "15:510:1": "을(를)\n우리 편으로 삼아",
    "15:510:2": ". 전시에는\n도움도 기대할 수 있",
    "15:511:0": "적의 편에 설지, 우리 편이 될지…\n",
    "15:511:1": "의 향방이 마음에 걸려",
    "15:511:2": "\n금품으로 환심을 사 두는 것이 좋을 듯하옵니다",
    "15:512:0": "의",
    "15:512:1": (
        "을(를) 회유해 보는 것이 어떻겠사옵니까?\n"
        "적대를 멈춘 이들을 단숨에 우리 편으로 삼는 것이옵니다\n"
        "예나 지금이나, 결정적인 것은… 물자이옵니다"
    ),
    "15:513:0": "국인중을 회유합시다\n저래 봬도 제법 든든한 이들입니다",
    "15:514:0": (
        "국인중을 회유해 보심이 어떻겠소?\n"
        "물자를 보내 마음을 얻어 두면\n"
        "전시에 도움이 될 것이오"
    ),
    "15:515:0": (
        "국인중에게 물자를 보내 회유하는 것입니다\n"
        "유사시에 든든한 힘이 되어 줄 것입니다"
    ),
    "15:516:0": "국인중을 회유해야 한다\n전시에 원군을 받을 수 있다면 든든하지",
    "15:517:0": (
        "국인중을 회유해 보는 것이 어떻겠습니까\n"
        "유사시에 우리를 돕도록\n"
        "미리 친분을 다져 두어야겠지요…"
    ),
    "15:518:0": (
        "국인중에게 선물을 보내 회유하겠사옵니다\n"
        "전시에는 우리 편이 되어 줄 것이옵니다"
    ),
    "15:519:0": "의",
    "15:519:1": (
        "회유는 어떠냐?\n"
        "금품을 쥐여 주면 그들도 은혜를 느껴\n"
        "더 많은 원군을 보내올 것이다"
    ),
    "15:520:0": "의",
    "15:520:1": (
        "을(를) 회유하시지요\n"
        "지금도 우리 가문에 충분한 힘이 되고 있으나\n"
        "한 번 더 마음을 얻어 보심이 어떻겠사옵니까"
    ),
}
RECORD_ARITIES = {
    508: 3,
    509: 1,
    510: 3,
    511: 3,
    512: 2,
    513: 1,
    514: 1,
    515: 1,
    516: 1,
    517: 1,
    518: 1,
    519: 2,
    520: 2,
}
EXPECTED_BASE_GAPS = {
    508: ("", "028c32", "014356020000", "050505"),
    509: ("028c32", "0143ca000000050505"),
    510: ("", "028c32", "01431e040000", "01433c040000050505"),
    511: ("", "028c32", "014336040000", "050505"),
    512: ("029632", "028c32", "050505"),
    **{record_id: ("", "050505") for record_id in range(513, 519)},
    519: ("029632", "028c32", "050505"),
    520: ("029632", "028c32", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    508: ("", "028c32", "014362020000", "050505"),
    510: ("", "028c32", "01432a040000", "014348040000050505"),
    511: ("", "028c32", "014342040000", "050505"),
}
EXPECTED_PK_EN_ARITIES = {
    508: 2,
    509: 2,
    510: 2,
    511: 2,
    **{record_id: 1 for record_id in range(512, 521)},
}
EXPECTED_PK_EN_GAPS = {
    **{record_id: ("", "028c32", "050505") for record_id in range(508, 512)},
    **{record_id: ("", "050505") for record_id in range(512, 521)},
}
CURRENT_ELLIPSIS_COORDINATES = {"15:511:0", "15:512:1", "15:517:0"}
BASIS = (
    "pristine_base_pc_jp_authoritative_dynamic_kokujin_conciliation_and_"
    "reinforcement_fragments_with_exact_uniform_plus_7_pk_jp_sc_tc_arrays_"
    "pk_en_sc_tc_auxiliary_context_current_pc_line_token_gap_and_switch_stem_"
    "boundaries_preserved_cross_segment_exact_source_reuse_historical_"
    "kokujin_reinforcement_stage_and_person_voice_verified_runtime_assembly_pending"
)


def source_literals(
    records: dict[tuple[int, int], Any], record_id: int
) -> tuple[str, ...]:
    return tuple(
        literal.text for literal in ENGINE.parse_record_literals(records[(15, record_id)])
    )


def assert_context_mapping(
    *,
    segment: int,
    record_arities: dict[int, int],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    pk_en_arities: dict[int, int],
    pk_en_gaps: dict[int, tuple[str, ...]],
    source_records: dict[tuple[int, int], Any],
    pk_source_records: dict[tuple[int, int], Any],
    base_context: dict[str, dict[tuple[int, int], Any]],
    pk_context: dict[str, dict[tuple[int, int], Any]],
) -> None:
    mapped_ids = {record_id + 7 for record_id in record_arities}
    expected_mapped_ids = set(range(min(record_arities) + 7, max(record_arities) + 8))
    if mapped_ids != expected_mapped_ids or mapped_ids & SHARED.PK_ONLY_RECORD_IDS:
        raise RuntimeError(f"segment {segment} uniform +7 mapping drifted")

    for record_id, arity in record_arities.items():
        base_record = source_records[(15, record_id)]
        pk_record = pk_source_records[(15, record_id + 7)]
        base_literals = source_literals(source_records, record_id)
        pk_literals = source_literals(pk_source_records, record_id + 7)
        if len(base_literals) != arity or len(pk_literals) != arity:
            raise RuntimeError(f"segment {segment} mapped JP arity drifted: {record_id}")
        if base_literals != pk_literals:
            raise RuntimeError(f"segment {segment} mapped PK JP literal array drifted: {record_id}")
        if SHARED.record_gaps(base_record) != SHARED.gaps_from_hex(base_gaps[record_id]):
            raise RuntimeError(f"segment {segment} Base JP token skeleton drifted: {record_id}")
        if SHARED.record_gaps(pk_record) != SHARED.gaps_from_hex(pk_jp_gaps[record_id]):
            raise RuntimeError(f"segment {segment} PK JP token skeleton drifted: {record_id + 7}")

        for language in ("SC", "TC"):
            base_aux = base_context[language][(15, record_id)]
            pk_aux = pk_context[language][(15, record_id + 7)]
            base_aux_literals = tuple(
                literal.text for literal in ENGINE.parse_record_literals(base_aux)
            )
            pk_aux_literals = tuple(
                literal.text for literal in ENGINE.parse_record_literals(pk_aux)
            )
            if (
                base_aux_literals != pk_aux_literals
                or SHARED.record_gaps(base_aux) != SHARED.record_gaps(pk_aux)
            ):
                raise RuntimeError(
                    f"segment {segment} mapped {language} array/token drifted: {record_id}"
                )

        pk_en = pk_context["EN"][(15, record_id + 7)]
        if len(ENGINE.parse_record_literals(pk_en)) != pk_en_arities[record_id]:
            raise RuntimeError(f"segment {segment} PK EN arity drifted: {record_id + 7}")
        if SHARED.record_gaps(pk_en) != SHARED.gaps_from_hex(pk_en_gaps[record_id]):
            raise RuntimeError(f"segment {segment} PK EN token skeleton drifted: {record_id + 7}")


def assert_scope(
    prepared: Any,
    *,
    segment: int,
    raw_translations: dict[str, str],
    translations: dict[str, str],
    record_arities: dict[int, int],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    pk_en_arities: dict[int, int],
    pk_en_gaps: dict[int, tuple[str, ...]],
    ellipsis_coordinates: set[str],
    semantic_assertions: Callable[
        [dict[tuple[int, int], Any], dict[str, str], dict[str, str]], None
    ],
) -> None:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    source_records = ENGINE.archive_records(base.pristine_archive)
    current_records = ENGINE.archive_records(base.current_archive)
    pk_source_records = ENGINE.archive_records(pk.pristine_archive)
    base_context = {
        language: ENGINE.archive_records(archive)
        for language, archive in base.context_archives.items()
    }
    pk_context = {
        language: ENGINE.archive_records(archive)
        for language, archive in pk.context_archives.items()
    }
    assert_context_mapping(
        segment=segment,
        record_arities=record_arities,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
        pk_en_arities=pk_en_arities,
        pk_en_gaps=pk_en_gaps,
        source_records=source_records,
        pk_source_records=pk_source_records,
        base_context=base_context,
        pk_context=pk_context,
    )

    expected_coordinates = set()
    actual_current_ellipsis = set()
    for record_id, arity in record_arities.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        source_record_literals = ENGINE.parse_record_literals(source_record)
        current_record_literals = ENGINE.parse_record_literals(current_record)
        if len(source_record_literals) != arity or len(current_record_literals) != arity:
            raise RuntimeError(f"segment {segment} source/current arity drifted: 15:{record_id}")
        expected_gaps = SHARED.gaps_from_hex(base_gaps[record_id])
        if (
            SHARED.record_gaps(source_record) != expected_gaps
            or SHARED.record_gaps(current_record) != expected_gaps
        ):
            raise RuntimeError(f"segment {segment} Base dynamic skeleton drifted: 15:{record_id}")
        for literal_id, current_literal in enumerate(current_record_literals):
            coordinate = f"15:{record_id}:{literal_id}"
            if not ENGINE.is_visible_translation_candidate(source_record_literals[literal_id].text):
                raise RuntimeError(f"segment {segment} unexpected blank source literal: {coordinate}")
            if not ENGINE.is_visible_translation_candidate(current_literal.text):
                raise RuntimeError(f"segment {segment} unexpected blank current literal: {coordinate}")
            expected_coordinates.add(coordinate)
            if "…" in current_literal.text:
                actual_current_ellipsis.add(coordinate)

    if set(raw_translations) != expected_coordinates:
        raise RuntimeError(f"segment {segment} raw decision coordinate universe drifted")
    if set(translations) != expected_coordinates:
        raise RuntimeError(f"segment {segment} resolved decision coordinate universe drifted")
    if len(translations) != sum(record_arities.values()):
        raise RuntimeError(f"segment {segment} visible decision count drifted")
    if actual_current_ellipsis != ellipsis_coordinates:
        raise RuntimeError(f"segment {segment} current ellipsis coordinates drifted")

    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
        if SHARED.layout_signature(translation) != SHARED.layout_signature(current_text):
            raise RuntimeError(f"segment {segment} layout/outer signature drifted: {coordinate}")
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"segment {segment} forbidden script/control drifted: {coordinate}")
        if SHARED.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(
                f"segment {segment} retains banned fullwidth punctuation: {coordinate}"
            )
        if "…" in translation.replace("……", ""):
            raise RuntimeError(f"segment {segment} retains an unpaired ellipsis: {coordinate}")

    semantic_assertions(source_records, raw_translations, translations)


def build_segment_rows(
    *,
    output: Path,
    segment: int,
    raw_translations: dict[str, str],
    record_arities: dict[int, int],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    pk_en_arities: dict[int, int],
    pk_en_gaps: dict[int, tuple[str, ...]],
    ellipsis_coordinates: set[str],
    basis: str,
    semantic_assertions: Callable[
        [dict[tuple[int, int], Any], dict[str, str], dict[str, str]], None
    ],
) -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    translations = SHARED.resolved_translations(current_records, raw_translations)
    assert_scope(
        prepared,
        segment=segment,
        raw_translations=raw_translations,
        translations=translations,
        record_arities=record_arities,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
        pk_en_arities=pk_en_arities,
        pk_en_gaps=pk_en_gaps,
        ellipsis_coordinates=ellipsis_coordinates,
        semantic_assertions=semantic_assertions,
    )
    SHARED.assert_isolated_overlay_roundtrip(
        prepared,
        segment=segment,
        translations=translations,
        record_arities=record_arities,
    )
    rows = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
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
                "basis": basis,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, translations, rows


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if (
        source_literals(source_records, 510)[0]
        != source_literals(source_records, 489)[0]
        or source_literals(source_records, 510)[0] != "多少金品を贈って"
    ):
        raise RuntimeError("segment 824 15:510:0 cross-boundary exact source drifted")
    if raw_translations["15:510:0"] != "금품을 조금 보내":
        raise RuntimeError("segment 824 15:510:0 approved exact translation reuse drifted")
    if (
        source_literals(source_records, 511)[0]
        != source_literals(source_records, 492)[0]
        or source_literals(source_records, 511)[0] != "敵につくか、味方となるか…\n"
    ):
        raise RuntimeError("segment 824 15:511:0 cross-boundary exact source drifted")
    if raw_translations["15:511:0"] != "적의 편에 설지, 우리 편이 될지…\n":
        raise RuntimeError("segment 824 15:511:0 approved exact translation reuse drifted")
    for record_id in (512, 519, 520):
        if source_literals(source_records, record_id)[0] != "の":
            raise RuntimeError(f"segment 824 possessive source drifted: {record_id}")
        if translations[f"15:{record_id}:0"] != "의":
            raise RuntimeError(f"segment 824 possessive particle drifted: {record_id}")

    particle_expectations = {
        "15:508:1": "이(가) ",
        "15:509:0": "은(는) ",
        "15:510:1": "을(를)\n",
        "15:511:1": "의 ",
        "15:512:1": "을(를) ",
        "15:520:1": "을(를) ",
    }
    for coordinate, prefix in particle_expectations.items():
        if not translations[coordinate].startswith(prefix):
            raise RuntimeError(f"segment 824 dynamic group particle drifted: {coordinate}")

    joined = "\n".join(translations.values())
    for required in ("국인중", "회유", "물자", "원군", "우리 가문"):
        if required not in joined:
            raise RuntimeError(f"segment 824 fixed historical terminology drifted: {required}")
    if any(term in joined for term in ("호족", "길들이", "심복", "당가", "가신단에 편입")):
        raise RuntimeError("segment 824 retained a forbidden term or premature integration")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        pk_en_arities=EXPECTED_PK_EN_ARITIES,
        pk_en_gaps=EXPECTED_PK_EN_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 824 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S824",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
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
