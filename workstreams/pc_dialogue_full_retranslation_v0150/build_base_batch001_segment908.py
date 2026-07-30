#!/usr/bin/env python3
"""Build Base authoring segment 908 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment864 as CANONICAL_S864
import build_base_batch001_segment884 as COMMON
import build_base_batch001_segment907 as CANONICAL_S907


ENGINE = COMMON.ENGINE
UTIL = COMMON.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S908.private.v1.jsonl"
)
SEGMENT = 908
DURABILITY_RECOVERY = tuple(
    CANONICAL_S864.RAW_TRANSLATIONS[f"15:1089:{literal_id}"]
    for literal_id in range(4)
)
TALENT_INSTRUCTION_VISIBLE_IDS = (0, 1, 3, 4, 5)
TALENT_INSTRUCTION = tuple(
    CANONICAL_S907.RAW_TRANSLATIONS[f"15:1501:{literal_id}"]
    for literal_id in TALENT_INSTRUCTION_VISIBLE_IDS
)
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:1504:{literal_id}": translation
        for literal_id, translation in zip(
            TALENT_INSTRUCTION_VISIBLE_IDS,
            TALENT_INSTRUCTION,
        )
    },
    "15:1505:0": "최근,",
    "15:1505:1": (
        "의 거성 근처에서\n"
        "도적 무리가 기승을 부려 애를 먹고 있"
    ),
    "15:1505:2": (
        "\n조두를 파견해 무공을 세우게 하는 것은 어떻겠습니까?"
    ),
    "15:1506:0": (
        "유망한 조두를 이곳에 파견하여\n"
        "도적 토벌을 맡겨 보는 것은 어떻겠소?\n"
        "좋은 무공을 세울 기회도 될 것이오."
    ),
    "15:1507:0": "조두들에게 무공을 세우게 하고자\n우리",
    "15:1507:1": "의 근처에 나타난 도적 무리의\n토벌을 맡겨도 좋다",
    "15:1507:2": "인가?",
    "15:1508:0": "을(를) 비롯한",
    "15:1508:1": "명이",
    "15:1508:2": "(으)로 승진 가능",
    "15:1509:0": "농촌을 장악하여",
    "15:1509:1": "의 석고가",
    "15:1509:2": "증가",
    "15:1510:0": "시장을 장악하여",
    "15:1510:1": "의 상업이",
    "15:1510:2": "증가",
    "15:1511:0": "의",
    "15:1511:1": "에",
    "15:1511:2": "을(를) 건설",
    "15:1512:0": "을(를) 수복하",
    "15:1512:1": "\n이제 언제든 적을 맞아 싸울 수 있",
    **{
        f"15:1513:{literal_id}": translation
        for literal_id, translation in enumerate(DURABILITY_RECOVERY)
    },
}
RECORD_ARITIES = {
    1504: 6,
    1505: 3,
    1506: 1,
    1507: 3,
    1508: 3,
    1509: 3,
    1510: 3,
    1511: 3,
    1512: 2,
    1513: 4,
}
EXPECTED_BASE_JP = {
    1504: (
        "どうやら当家に優秀な",
        "がいるよう",
        "\n",
        "が少しばかり教えを授けると",
        "\nよろしい",
        "？",
    ),
    1505: (
        "最近、",
        "の居城の近辺にて\n野盗が活性化し、手を焼いてい",
        "\n組頭を派遣し、武功を稼がせては？",
    ),
    1506: (
        "見所のある組頭をこちらに派遣し\n"
        "野盗討伐にあたらせては？\n"
        "良き武功稼ぎともな",
    ),
    1507: (
        "組頭たちに武功を稼がせるため\n我が",
        "の近辺に出た野盗の\n討伐を任じても良い",
        "か？",
    ),
    1508: ("ら", "名が", "に昇進可能に"),
    1509: ("農村を掌握し", "の石高が", "増加"),
    1510: ("市を掌握し", "の商業が", "増加"),
    1511: ("の", "に", "を建設"),
    1512: ("を修復いたし", "\nこれならば、いつでも敵を迎え撃て"),
    1513: ("の耐久が", "回復(", "→", ")"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1504: (
        "",
        "023c",
        "014340030000",
        "014301000000",
        "014394000000",
        "014324010000",
        "050505",
    ),
    1505: ("", "014301000000", "01433c040000", "050505"),
    1506: ("", "01435a040000050505"),
    1507: ("", "02463f", "014356020000", "050505"),
    1508: ("024633", "0232", "023c", "050505"),
    1509: ("", "026432", "0233", "050505"),
    1510: ("", "026432", "0233", "050505"),
    1511: ("026432", "029632", "023c", "050505"),
    1512: (
        "026432",
        "0143140200000143fc010000",
        "01433c040000050505",
    ),
    1513: ("026432", "0232", "0233", "0234", "050505"),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_BASE_GAPS,
    1506: ("", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1504: (
        "",
        "023c",
        "01434c030000",
        "014301000000",
        "014394000000",
        "014324010000",
        "050505",
    ),
    1505: ("", "014301000000", "014348040000", "050505"),
    1506: ("", "014366040000050505"),
    1507: ("", "02463f", "014362020000", "050505"),
    1512: (
        "026432",
        "01431a020000014302020000",
        "014348040000050505",
    ),
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1504:2": "\n"}

SHARED_AUXILIARY = {
    ("SC", 1505): (
        (
            "最近在",
            "的居城附近\n有野盗乱窜，相当棘手。\n派组头到这儿来，让他们立立功如何？",
        ),
        ("", "014301000000", "050505"),
    ),
    ("TC", 1505): (
        (
            "最近在",
            "的居城附近\n有野盜亂竄，相當棘手。\n派組頭到這兒來，讓他們立立功如何？",
        ),
        ("", "014301000000", "050505"),
    ),
    ("SC", 1506): (
        ("派遣有能耐的组头来这儿，\n让他们对付野盗吧？\n也能立下大功吧。",),
        ("", "050505"),
    ),
    ("TC", 1506): (
        ("派遣有看頭的組頭到這兒來，\n讓他們討伐野盜吧？\n也能立下大功吧。",),
        ("", "050505"),
    ),
    ("SC", 1507): (
        (
            "为了让组头们立功，\n让他们讨伐出没在我的",
            "一带\n的野盗可以吗？",
        ),
        ("", "02463f", "050505"),
    ),
    ("TC", 1507): (
        (
            "為了讓組頭們立功，\n讓他們討伐出沒在我的",
            "一帶\n的野盜可以嗎？",
        ),
        ("", "02463f", "050505"),
    ),
    ("SC", 1508): (
        ("等", "名可以升级为", "。"),
        ("024633", "0232", "023c", "050505"),
    ),
    ("TC", 1508): (
        ("等", "名可晉升為", "。"),
        ("024633", "0232", "023c", "050505"),
    ),
    ("SC", 1509): (
        ("控制了农村，", "的石高增加", "。"),
        ("", "026432", "0233", "050505"),
    ),
    ("TC", 1509): (
        ("掌控農村，", "的石高增加", "。"),
        ("", "026432", "0233", "050505"),
    ),
    ("SC", 1510): (
        ("控制了城市，", "的商业增加", "。"),
        ("", "026432", "0233", "050505"),
    ),
    ("TC", 1510): (
        ("掌控市場，", "的商業增加", "。"),
        ("", "026432", "0233", "050505"),
    ),
    ("SC", 1511): (
        ("在", "的", "建设", "。"),
        ("", "026432", "029632", "023c", "050505"),
    ),
    ("TC", 1511): (
        ("在", "的", "建設", "。"),
        ("", "026432", "029632", "023c", "050505"),
    ),
    ("SC", 1512): (
        ("修复完成啦！\n这样便可随时迎击敌人了。",),
        ("026432", "050505"),
    ),
    ("TC", 1512): (
        ("修復完成啦！\n這樣又可隨時迎擊敵人了。",),
        ("026432", "050505"),
    ),
    ("SC", 1513): (
        ("的耐久恢复", "(", "→", ")。"),
        ("026432", "0232", "0233", "0234", "050505"),
    ),
    ("TC", 1513): (
        ("的耐久恢復", "(", "→", ")。"),
        ("026432", "0232", "0233", "0234", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1505: (
        (
            "Recently, IÖve struggled with the rising number of bandits in the area. "
            "Why donÖt you dispatch a chief to earn some glory through exploits?",
        ),
        ("", "050505"),
    ),
    1506: (
        (
            "LetÖs dispatch a promising chief here to subjugate the bandits. "
            "ItÖd be a good way for them to earn exploits and make a name for themself.",
        ),
        ("", "050505"),
    ),
    1507: (
        (
            "If we want the chiefs to earn some exploits, then we could entrust "
            "them with the task of subjugating the bandits around ",
            ".",
        ),
        ("", "02463f", "050505"),
    ),
    1508: (
        (" of ", "Ös people can now be promoted to ", "."),
        ("0232", "024633", "023c", "050505"),
    ),
    1509: (
        ("Seized the farm. ", "Ös crops increased by ", "."),
        ("", "026432", "0233", "050505"),
    ),
    1510: (
        ("Seized the fair. ", "Ös commerce increased by ", "."),
        ("", "026432", "0233", "050505"),
    ),
    1511: (
        ("Added ", " to ", "Ös ", "."),
        ("", "023c", "026432", "029632", "050505"),
    ),
    1512: (
        (
            "WeÖve repaired ",
            ". We should be ready to take on the enemy at any time now.",
        ),
        ("", "026432", "050505"),
    ),
    1513: (
        (" has restored ", " HP (", " Ð ", ")."),
        ("026432", "0232", "0233", "0234", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, language, record_id): expected
        for (language, record_id), expected in SHARED_AUXILIARY.items()
        for side in ("base", "pk")
    },
    **{
        ("pk", "EN", record_id): expected
        for record_id, expected in PK_EN_AUXILIARY.items()
    },
}
BASIS = (
    "review_queue_base_msggame_B109_pristine_base_pc_jp_authoritative_"
    "talent_instruction_chief_bandit_subjugation_promotion_settlement_"
    "construction_repair_and_durability_ui_with_explicit_plus_15_pk_"
    "mapping_base_pk_sc_tc_and_pk_en_auxiliary_context_s864_base1089_"
    "durability_ui_canonical_exact_reuse_game_rank_jodu_seokgo_terminology_"
    "hidden_lf_excluded_current1506_flattened_runtime_skeleton_recorded_"
    "source_opcode_boundaries_and_current_layout_preserved_runtime_pending"
)


def assert_scope_with_current_gaps(
    prepared: Any,
    *,
    segment: int,
    raw_translations: dict[str, str],
    translations: dict[str, str],
    record_arities: dict[int, int],
    pk_record_map: dict[int, int],
    expected_base_jp: dict[int, tuple[str, ...]],
    expected_pk_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    current_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    ellipsis_coordinates: set[str],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    excluded_nonvisible_coordinates: dict[str, str],
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
    COMMON.assert_context_mapping(
        segment=segment,
        record_arities=record_arities,
        pk_record_map=pk_record_map,
        expected_base_jp=expected_base_jp,
        expected_pk_jp=expected_pk_jp,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
        auxiliary_overrides=auxiliary_overrides,
        source_records=source_records,
        pk_source_records=pk_source_records,
        base_context=base_context,
        pk_context=pk_context,
    )

    if set(current_gaps) != set(record_arities):
        raise RuntimeError(f"segment {segment} current gap universe drifted")
    expected_coordinates: set[str] = set()
    actual_current_ellipsis: set[str] = set()
    for record_id, arity in record_arities.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(
                f"segment {segment} source/current arity drifted: 15:{record_id}"
            )
        if UTIL.record_gaps(source_record) != UTIL.gaps_from_hex(
            base_gaps[record_id]
        ):
            raise RuntimeError(
                f"segment {segment} Base pristine skeleton drifted: 15:{record_id}"
            )
        if UTIL.record_gaps(current_record) != UTIL.gaps_from_hex(
            current_gaps[record_id]
        ):
            raise RuntimeError(
                f"segment {segment} Base current skeleton drifted: 15:{record_id}"
            )
        for literal_id, (source_literal, current_literal) in enumerate(
            zip(source_literals, current_literals)
        ):
            coordinate = f"15:{record_id}:{literal_id}"
            if coordinate in excluded_nonvisible_coordinates:
                expected_text = excluded_nonvisible_coordinates[coordinate]
                if (
                    source_literal.text != expected_text
                    or current_literal.text != expected_text
                    or ENGINE.is_visible_translation_candidate(source_literal.text)
                    or ENGINE.is_visible_translation_candidate(current_literal.text)
                    or coordinate in raw_translations
                    or coordinate in translations
                ):
                    raise RuntimeError(
                        f"segment {segment} excluded nonvisible literal drifted: "
                        f"{coordinate}"
                    )
                continue
            if not ENGINE.is_visible_translation_candidate(source_literal.text):
                raise RuntimeError(
                    f"segment {segment} unexpected blank source literal: {coordinate}"
                )
            if not ENGINE.is_visible_translation_candidate(current_literal.text):
                raise RuntimeError(
                    f"segment {segment} unexpected blank current literal: {coordinate}"
                )
            expected_coordinates.add(coordinate)
            if "…" in current_literal.text:
                actual_current_ellipsis.add(coordinate)

    if set(raw_translations) != expected_coordinates:
        raise RuntimeError(
            f"segment {segment} raw decision coordinate universe drifted"
        )
    if set(translations) != expected_coordinates:
        raise RuntimeError(
            f"segment {segment} resolved decision coordinate universe drifted"
        )
    expected_count = sum(record_arities.values()) - len(
        excluded_nonvisible_coordinates
    )
    if len(translations) != expected_count:
        raise RuntimeError(f"segment {segment} visible decision count drifted")
    if actual_current_ellipsis != ellipsis_coordinates:
        raise RuntimeError(
            f"segment {segment} current ellipsis coordinates drifted"
        )

    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
        if UTIL.layout_signature(translation) != UTIL.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment {segment} layout/outer signature drifted: {coordinate}"
            )
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(
                f"segment {segment} forbidden script/control drifted: {coordinate}"
            )
        if UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(
                f"segment {segment} retains banned fullwidth punctuation: "
                f"{coordinate}"
            )
        if "…" in translation.replace("……", ""):
            raise RuntimeError(
                f"segment {segment} retains an unpaired ellipsis: {coordinate}"
            )

    semantic_assertions(source_records, raw_translations, translations)


def build_segment_rows_with_current_gaps(
    *,
    output: Path,
    segment: int,
    raw_translations: dict[str, str],
    record_arities: dict[int, int],
    pk_record_map: dict[int, int],
    expected_base_jp: dict[int, tuple[str, ...]],
    expected_pk_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    current_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    ellipsis_coordinates: set[str],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    excluded_nonvisible_coordinates: dict[str, str],
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
    translations = UTIL.resolved_translations(
        current_records,
        raw_translations,
    )
    assert_scope_with_current_gaps(
        prepared,
        segment=segment,
        raw_translations=raw_translations,
        translations=translations,
        record_arities=record_arities,
        pk_record_map=pk_record_map,
        expected_base_jp=expected_base_jp,
        expected_pk_jp=expected_pk_jp,
        base_gaps=base_gaps,
        current_gaps=current_gaps,
        pk_jp_gaps=pk_jp_gaps,
        ellipsis_coordinates=ellipsis_coordinates,
        auxiliary_overrides=auxiliary_overrides,
        excluded_nonvisible_coordinates=excluded_nonvisible_coordinates,
        semantic_assertions=semantic_assertions,
    )
    UTIL.assert_isolated_overlay_roundtrip(
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
                "source_record_raw_sha256": target[
                    "source_record_raw_sha256"
                ],
                "current_ko_utf16le_sha256": target[
                    "current_ko_utf16le_sha256"
                ],
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
    canonical_source = tuple(
        CANONICAL_S864.EXPECTED_JP[1089]
    )
    canonical_gaps = CANONICAL_S864.EXPECTED_BASE_GAPS[1089]
    if EXPECTED_BASE_JP[1513] != canonical_source:
        raise RuntimeError("segment 908 Base1089 durability source canonical drifted")
    if EXPECTED_BASE_GAPS[1513] != canonical_gaps:
        raise RuntimeError("segment 908 Base1089 durability gap canonical drifted")
    if tuple(
        raw_translations[f"15:1513:{literal_id}"]
        for literal_id in range(4)
    ) != DURABILITY_RECOVERY:
        raise RuntimeError("segment 908 Base1089 durability Korean canonical drifted")
    if tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(source_records[(15, 1513)])
    ) != canonical_source:
        raise RuntimeError("segment 908 pristine durability source drifted")
    if tuple(
        raw_translations[f"15:1504:{literal_id}"]
        for literal_id in TALENT_INSTRUCTION_VISIBLE_IDS
    ) != TALENT_INSTRUCTION:
        raise RuntimeError("segment 908 S907 Base1501 Korean canonical drifted")
    if any(
        raw_translations[f"15:1504:{literal_id}"]
        != CANONICAL_S907.RAW_TRANSLATIONS[f"15:1501:{literal_id}"]
        for literal_id in TALENT_INSTRUCTION_VISIBLE_IDS
    ):
        raise RuntimeError("segment 908 S907 Base1501 cross-record reuse drifted")
    if tuple(value.lower() for value in EXPECTED_BASE_GAPS[1504]) != tuple(
        value.lower() for value in CANONICAL_S907.EXPECTED_BASE_GAPS[1501]
    ):
        raise RuntimeError("segment 908 S907 Base1501 opcode skeleton drifted")
    for literal_id in (0, 1, 2, 4, 5):
        if (
            EXPECTED_BASE_JP[1504][literal_id]
            != CANONICAL_S907.EXPECTED_BASE_JP[1501][literal_id]
        ):
            raise RuntimeError(
                "segment 908 S907 Base1501 repeated instruction frame drifted"
            )
    if (
        EXPECTED_BASE_JP[1504][3]
        != "が少しばかり教えを授けると"
        or CANONICAL_S907.EXPECTED_BASE_JP[1501][3]
        != "が少し手ほどきすると"
    ):
        raise RuntimeError(
            "segment 908 S907/1504 instruction-wording variant drifted"
        )

    for record_id in (1505, 1506, 1507):
        if "組頭" not in "".join(EXPECTED_BASE_JP[record_id]):
            raise RuntimeError(f"segment 908 組頭 source guard drifted: {record_id}")
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "조두",
        "도적",
        "무공",
        "석고",
        "시장을 장악",
        "수복",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 908 required terminology drifted: {required}")
    for forbidden in ("당가", "조장", "지행"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 908 retained forbidden terminology: {forbidden}"
            )
    if raw_translations["15:1512:0"] != "을(를) 수복하":
        raise RuntimeError("segment 908 repair first opcode stem drifted")
    if not raw_translations["15:1512:1"].endswith("있"):
        raise RuntimeError("segment 908 repair final opcode stem drifted")
    if raw_translations["15:1506:0"].splitlines()[0] != (
        "유망한 조두를 이곳에 파견하여"
    ):
        raise RuntimeError(
            "segment 908 見所のある組頭 meaning drifted"
        )
    if (
        raw_translations["15:1507:1"]
        != "의 근처에 나타난 도적 무리의\n토벌을 맡겨도 좋다"
        or raw_translations["15:1507:2"] != "인가?"
    ):
        raise RuntimeError(
            "segment 908 record 1507 proven 014356 split drifted"
        )
    if EXCLUDED_NONVISIBLE_COORDINATES != {"15:1504:2": "\n"}:
        raise RuntimeError("segment 908 hidden LF exclusion drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return build_segment_rows_with_current_gaps(
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


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 30 or len(translations) != 30:
        raise RuntimeError("segment 908 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 908 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S908",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "hidden_lf_excluded": 1,
                "canonical_base1089_reuse": True,
                "explicit_pk_mapping": True,
                "current_flattened_opcode_records": [1506],
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
