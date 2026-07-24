#!/usr/bin/env python3
"""Build Base authoring segment 972 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment896 as FAILED_RESULT_CANONICAL
import build_base_batch001_segment971 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S972.private.v1.jsonl"
)
SEGMENT = 972
CASTLE_TOKEN = PREVIOUS.CASTLE_TOKEN
OFFICER_TOKEN = "024633"
ACTION_RESULT_TOKEN = "023C"
FAILED_ACTION_TRANSLATION = (
    FAILED_RESULT_CANONICAL.RAW_TRANSLATIONS["15:1412:0"],
    FAILED_RESULT_CANONICAL.RAW_TRANSLATIONS["15:1412:1"],
)
TRANSLATIONS_BY_RECORD = {
    2172: (
        "듣자 하니",
        "에 새 시설을\n건설할 수 있게 되었다 하옵니다!",
    ),
    2173: (
        "군 시설이 갖춰진 듯하여,",
        "에\n새 시설을 건설할 수 있게 되었습니다",
    ),
    2174: PREVIOUS.FACILITY_COMPLETION_CANONICAL,
    2175: (
        "지원 대상 군단에\n우리 군단의 금전을 보내\n돕게 해",
    ),
    2176: (
        "여유가 있다면\n본거지에서 군 개발을 명하여\n"
        "기반을 다지는 것이 상책일 듯합니다",
    ),
    2177: (
        "노동력이 남는 듯하니…\n몸소 본거지의 군 개발에 착수하여\n"
        "나라를 부유하게 하심이",
    ),
    2178: (
        "본거지의 군 개발을 직접\n지시해 보심이 어떻겠습니까? 대관에게\n"
        "맡기는 것보다 빨리 진척될 것",
    ),
    2179: (
        "이(가)",
        "에 성공",
    ),
    2180: FAILED_ACTION_TRANSLATION,
    2181: (
        "의 병량에 불안이",
        "\n백성의 반감을 사",
        "겠지만\n병량을 부과하심이",
    ),
    2182: (
        "유비무환이라고",
        "\n다소 무리를 해서라도 병량을 부과하여\n비축해 두",
    ),
    2183: (
        "지금 병량을 다시 비축",
        "\n늘 유사시에 대비해 두면\n안심",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    2172: ("何やら", "に新しい施設が\n建設できるようになったとのこと！"),
    2173: (
        "郡の施設が整ったようで、",
        "に\n新しい施設を建設できるようになりました",
    ),
    2174: PREVIOUS.EXPECTED_BASE_JP[2166],
    2175: ("支援先の軍団に対し\n当軍団より金銭を送付し\n補助させて",),
    2176: ("余裕があるならば\n本拠にて郡の開発を指示し\n足元を固めるが上策かと",),
    2177: ("労力が余っている様子…\n自ら本拠の郡開発に着手し\n国を富ませては",),
    2178: (
        "本拠の郡開発に直接\n指示を出してみては？\u3000代官に\n"
        "任せるより早く進捗する",
    ),
    2179: ("が", "に成功"),
    2180: FAILED_RESULT_CANONICAL.EXPECTED_BASE_JP[1412],
    2181: ("の兵糧に不安が", "\n反感を買", "が\n兵糧を賦課しては"),
    2182: ("備えあれば憂いなしと", "\n多少無理をしても兵糧を賦課して\n蓄えてお"),
    2183: ("今のうちに兵糧を蓄え直", "\n常に有事に備えておけば\n安心"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2172: ("", CASTLE_TOKEN, "050505"),
    2173: ("", CASTLE_TOKEN, "050505"),
    2174: PREVIOUS.EXPECTED_BASE_GAPS[2166],
    2175: ("", "014342010000050505"),
    2176: ("", "050505"),
    2177: ("", "0143B0020000014356020000050505"),
    2178: ("", "014356020000050505"),
    2179: (OFFICER_TOKEN, ACTION_RESULT_TOKEN, "050505"),
    2180: FAILED_RESULT_CANONICAL.EXPECTED_BASE_GAPS[1412],
    2181: (
        "02463F",
        "014352000000",
        "0143CA000000",
        "0143B0020000014356020000050505",
    ),
    2182: ("", "014364000000", "01436C010000050505"),
    2183: ("", "01437E040000", "01431A020000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2174: PREVIOUS.EXPECTED_PK_JP_GAPS[2166],
    2177: ("", "0143BC020000014362020000050505"),
    2178: ("", "014362020000050505"),
    2181: (
        "02463F",
        "014352000000",
        "0143CA000000",
        "0143BC020000014362020000050505",
    ),
    2183: ("", "01438A040000", "014326020000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2177:0"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2175): (
        ("我方向寻求支援的军团\n捐助金钱，您意下如何？",),
        ("", "050505"),
    ),
    ("TC", 2175): (
        ("不妨從本軍團調度金錢，\n送往支援的軍團如何？",),
        ("", "050505"),
    ),
    ("SC", 2176): (
        ("有馀裕的话，\n在根据地指示开发郡，\n稳固地盘才是上策吧。",),
        ("", "050505"),
    ),
    ("TC", 2176): (
        ("有餘裕的話，\n在根據地指示開發郡，\n穩固地盤才是上策吧。",),
        ("", "050505"),
    ),
    ("SC", 2177): (
        ("劳力似乎有馀……\n亲自着手开发根据地的郡，\n富国裕民，如何？",),
        ("", "050505"),
    ),
    ("TC", 2177): (
        ("勞力似乎有餘……\n親自著手開發根據地的郡，\n富國裕民，如何？",),
        ("", "050505"),
    ),
    ("SC", 2178): (
        ("直接指示开发根据地的郡，\n如何？比起委任代官\n效率更高吧。",),
        ("", "050505"),
    ),
    ("TC", 2178): (
        ("直接指示開發根據地的郡，\n如何？比起委任代官\n效率更高吧。",),
        ("", "050505"),
    ),
    ("SC", 2179): (
        ("的", "成功。"),
        (OFFICER_TOKEN, ACTION_RESULT_TOKEN, "050505"),
    ),
    ("TC", 2179): (
        ("進行", "成功。"),
        (OFFICER_TOKEN, ACTION_RESULT_TOKEN, "050505"),
    ),
    ("SC", 2180): (
        ("的", "失败。"),
        (OFFICER_TOKEN, ACTION_RESULT_TOKEN, "050505"),
    ),
    ("TC", 2180): (
        ("進行", "失敗。"),
        (OFFICER_TOKEN, ACTION_RESULT_TOKEN, "050505"),
    ),
    ("SC", 2181): (
        ("的军粮令人不安，\n虽然会招致反感，\n但请考虑征收军粮。",),
        ("02463F", "050505"),
    ),
    ("TC", 2181): (
        ("的軍糧庫存堪憂。\n雖恐遭到反感，\n但不妨徵收軍糧。",),
        ("02463F", "050505"),
    ),
    ("SC", 2182): (
        ("俗话说有备而无患，\n即使稍微鲁莽，\n也该征收并储蓄军粮。",),
        ("", "050505"),
    ),
    ("TC", 2182): (
        ("俗話說，有備無患。\n縱使必需強行徵收，\n也務必貯存軍糧。",),
        ("", "050505"),
    ),
    ("SC", 2183): (
        ("趁现在重新储存军粮吧，\n凡事都留条后路，\n才能让人安心。",),
        ("", "050505"),
    ),
    ("TC", 2183): (
        ("趁現在重新儲存軍糧。\n未雨綢繆，方能有備無患",),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2175: (
        (
            "Please make it so this province sends funds to the target "
            "province for assistance.",
        ),
        ("", "050505"),
    ),
    2176: (
        (
            "If you have the time, it might be best to order the "
            "development of the main baseÖs counties to shore up defenses.",
        ),
        ("", "050505"),
    ),
    2177: (
        (
            "It seems we still have unused labor. Why not direct some "
            "development to take place in the counties of the main base? "
            "It would benefit the entire country.",
        ),
        ("", "050505"),
    ),
    2178: (
        (
            "Have you considered directly giving orders to develop the "
            "counties of the main base? It would progress faster than "
            "leaving it to your substitutes.",
        ),
        ("", "050505"),
    ),
    2179: (
        (" successfully completed ", "."),
        (OFFICER_TOKEN, ACTION_RESULT_TOKEN, "050505"),
    ),
    2180: (
        (" failed to complete ", "."),
        (OFFICER_TOKEN, ACTION_RESULT_TOKEN, "050505"),
    ),
    2181: (
        (
            "The amount of supplies in ",
            " doesnÖt look good. There might be some outcry, "
            "but we ought to levy supplies.",
        ),
        ("", "02463F", "050505"),
    ),
    2182: (
        (
            "Better safe than sorry, they say. The people might have to "
            "work harder, but we should levy supplies.",
        ),
        ("", "050505"),
    ),
    2183: (
        ("We must restock our supplies. Constant readiness brings peace of mind.",),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B116_C_pristine_base_pc_jp_authoritative_"
    "facility_unlock_county_development_legion_support_action_results_and_"
    "provision_levy_advice_with_explicit_base2172_2183_to_pk2202_2213_"
    "mapping_exact_base_pk_jp_sc_tc_literals_dynamic_castle_officer_"
    "action_result_and_morphology_tokens_direction_2166_2174_exact_tuple_"
    "alias_committed_1412_2180_failure_tuple_reuse_兵糧_as_byengnyang_"
    "賦課_as_bugwa_本拠_as_bongeoji_代官_as_daegwan_2178_source_u3000_"
    "normalized_to_current_ascii_layout_project_ellipsis_pair_all_base_pk_"
    "opcode_divergences_recorded_and_skeleton_preserved_runtime_fragment_"
    "pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    82: ("있습니다", "있다", "있사옵니다", "입니다", "이옵니다"),
    100: ("아룁니다", "말하다", "아뢴다", "아뢰옵니다"),
    202: ("있겠지요", "오"),
    322: ("주시오", "다오", "주소서"),
    364: ("겠습니다", "이렇게", "기로 하지"),
    502: PREVIOUS.EXPECTED_BASE_MORPHOLOGY_TERMINALS[502],
    538: PREVIOUS.EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    598: ("이겠지요", "이리라", "이겠지"),
    616: PREVIOUS.EXPECTED_BASE_MORPHOLOGY_TERMINALS[616],
    688: ("어떻게", "어떠하오"),
    1150: ("합시다", "그렇군"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    82: EXPECTED_BASE_MORPHOLOGY_TERMINALS[82],
    100: EXPECTED_BASE_MORPHOLOGY_TERMINALS[100],
    202: EXPECTED_BASE_MORPHOLOGY_TERMINALS[202],
    322: EXPECTED_BASE_MORPHOLOGY_TERMINALS[322],
    364: EXPECTED_BASE_MORPHOLOGY_TERMINALS[364],
    508: EXPECTED_BASE_MORPHOLOGY_TERMINALS[502],
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    628: EXPECTED_BASE_MORPHOLOGY_TERMINALS[616],
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
    1162: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1150],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if (
        TRANSLATIONS_BY_RECORD[2174]
        is not PREVIOUS.FACILITY_COMPLETION_CANONICAL
    ):
        raise RuntimeError("segment 972 Base2166/2174 canonical alias drifted")
    reference = source_records[(15, 2166)]
    repeated = source_records[(15, 2174)]
    if (
        tuple(x.text for x in ENGINE.parse_record_literals(reference))
        != tuple(x.text for x in ENGINE.parse_record_literals(repeated))
        or COMMON.UTIL.record_gaps(reference)
        != COMMON.UTIL.record_gaps(repeated)
    ):
        raise RuntimeError("segment 972 live Base2166/2174 exact reuse drifted")
    if TRANSLATIONS_BY_RECORD[2180] is not FAILED_ACTION_TRANSLATION:
        raise RuntimeError("segment 972 Base1412/2180 tuple reuse drifted")
    canonical_failure = source_records[(15, 1412)]
    repeated_failure = source_records[(15, 2180)]
    if (
        tuple(x.text for x in ENGINE.parse_record_literals(canonical_failure))
        != tuple(x.text for x in ENGINE.parse_record_literals(repeated_failure))
        or COMMON.UTIL.record_gaps(canonical_failure)
        != COMMON.UTIL.record_gaps(repeated_failure)
        or TRANSLATIONS_BY_RECORD[2180]
        != (
            FAILED_RESULT_CANONICAL.RAW_TRANSLATIONS["15:1412:0"],
            FAILED_RESULT_CANONICAL.RAW_TRANSLATIONS["15:1412:1"],
        )
    ):
        raise RuntimeError("segment 972 committed Base1412 canonical drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 972 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 972 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {2174, 2177, 2178, 2181, 2183}:
        raise RuntimeError("segment 972 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 972 pristine/current gap drifted")
    if EXPECTED_BASE_GAPS[2179] != EXPECTED_BASE_GAPS[2180]:
        raise RuntimeError("segment 972 action-result token direction drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 972 project ellipsis pair drifted: {coordinate}"
            )
    if (
        "\u3000" not in EXPECTED_BASE_JP[2178][0]
        or "\u3000" in raw_translations["15:2178:0"]
        or "? 대관에게\n" not in raw_translations["15:2178:0"]
    ):
        raise RuntimeError("segment 972 Base2178 ASCII layout normalization drifted")
    joined = "\n".join(translations.values())
    for required in ("군 시설", "본거지", "대관", "병량", "부과"):
        if required not in joined:
            raise RuntimeError(
                f"segment 972 historical terminology drifted: {required}"
            )
    for forbidden in ("식량", "부유케", "。", "！"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 972 forbidden wording retained: {forbidden}"
            )
    if TRANSLATIONS_BY_RECORD[2181][2] != "겠지만\n병량을 부과하심이":
        raise RuntimeError("segment 972 Base2181 conjunction が became a subject particle")
    if len(raw_translations) != 21 or len(translations) != 21:
        raise RuntimeError("segment 972 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared, translations, rows = COMMON.build_segment_rows_with_current_gaps(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        current_gaps=EXPECTED_CURRENT_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    for row in rows:
        if row["coordinate"] == "15:2176:0":
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "not_required"
    SUPPORT.annotate_morphology_evidence(
        prepared,
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_CURRENT_GAPS,
        pk_gaps=EXPECTED_PK_JP_GAPS,
        expected_base=EXPECTED_BASE_MORPHOLOGY_TERMINALS,
        expected_pk=EXPECTED_PK_MORPHOLOGY_TERMINALS,
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 972 validated count drifted")
    if any(
        (
            row["scope_classification"],
            row["runtime_review"],
        )
        != (
            ("retranslated", "not_required")
            if row["coordinate"] == "15:2176:0"
            else ("runtime_fragment_pending", "pending")
        )
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 972 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S972",
                "source_literal_count": 21,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "retranslated": 1,
                "runtime_fragment_pending": len(rows) - 1,
                "canonical_record_map": {2174: 2166, 2180: 1412},
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    2174,
                    2177,
                    2178,
                    2181,
                    2183,
                ],
                "pristine_current_gap_divergence_records": [],
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
                "lf_count": sum(text.count("\n") for text in translations.values()),
                "line_distribution": {
                    line_count: sum(
                        text.count("\n") + 1 == line_count
                        for text in translations.values()
                    )
                    for line_count in (1, 2, 3)
                },
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "target_runtime_skeleton_exact": True,
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
