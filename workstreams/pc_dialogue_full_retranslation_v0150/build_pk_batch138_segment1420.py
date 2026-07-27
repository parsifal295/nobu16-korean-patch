#!/usr/bin/env python3
"""Build source-redacted PK B138 segment 1420 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals
_ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE = (
    COMMON.BASE.base_and_assembly_evidence
)

TARGET_RECORD_IDS = tuple(range(312, 347))
MAIN_RECORD_IDS = tuple(range(313, 347))
TARGET_COORDINATES = (
    "17:312:1",
    "17:313:0",
    "17:313:1",
    "17:314:0",
    "17:315:0",
    "17:315:1",
    "17:316:0",
    "17:316:1",
    "17:317:0",
    "17:317:1",
    "17:318:0",
    "17:318:1",
    "17:318:2",
    "17:319:0",
    "17:319:1",
    "17:319:2",
    "17:320:0",
    "17:321:0",
    "17:321:1",
    "17:322:0",
    "17:322:1",
    "17:323:0",
    "17:324:0",
    "17:324:1",
    "17:325:0",
    "17:325:1",
    "17:326:0",
    "17:326:1",
    "17:327:0",
    "17:327:1",
    "17:328:0",
    "17:328:1",
    "17:329:0",
    "17:329:1",
    "17:330:0",
    "17:330:1",
    "17:331:0",
    "17:331:1",
    "17:331:2",
    "17:332:0",
    "17:332:1",
    "17:333:0",
    "17:334:0",
    "17:335:0",
    "17:336:0",
    "17:337:0",
    "17:337:1",
    "17:338:0",
    "17:338:1",
    "17:339:0",
    "17:340:0",
    "17:340:1",
    "17:341:0",
    "17:342:0",
    "17:343:0",
    "17:343:1",
    "17:343:2",
    "17:343:3",
    "17:344:0",
    "17:344:1",
    "17:344:2",
    "17:344:3",
    "17:345:0",
    "17:345:1",
    "17:346:0",
    "17:346:1",
)
MAIN_TARGET_COORDINATES = tuple(
    coordinate
    for coordinate in TARGET_COORDINATES
    if not coordinate.startswith("17:312:")
)
TRANSLATIONS = {
    "17:312:1": " 성공",
    "17:313:0": "부대를 격파하라",
    "17:313:1": " 실패",
    "17:314:0": "부대를 격파하라",
    "17:315:0": "부대를 격파하라",
    "17:315:1": " 성공",
    "17:316:0": "부대를 격파하라",
    "17:316:1": " 실패",
    "17:317:0": "부대를",
    "17:317:1": "부대에 접근시켜라",
    "17:318:0": "부대를",
    "17:318:1": "부대에 접근시켜라",
    "17:318:2": " 성공",
    "17:319:0": "부대를",
    "17:319:1": "부대에 접근시켜라",
    "17:319:2": " 실패",
    "17:320:0": "부대를 격파하라",
    "17:321:0": "부대를 격파하라",
    "17:321:1": " 성공",
    "17:322:0": "부대를 격파하라",
    "17:322:1": " 실패",
    "17:323:0": "부대를 격파하라",
    "17:324:0": "부대를 격파하라",
    "17:324:1": " 성공",
    "17:325:0": "부대를 격파하라",
    "17:325:1": " 실패",
    "17:326:0": "요시히로 ",
    "17:326:1": (
        "공만이라도 살아남으시면\n"
        "시마즈 가문은 무사할 것입니다……"
    ),
    "17:327:0": "도요히사",
    "17:327:1": "……\n정말 미안하구나……",
    "17:328:0": "요시쓰구",
    "17:328:1": "님을 위해 목숨을 버리는 건 아깝지 않았다……",
    "17:329:0": "다메히로",
    "17:329:1": "……저승길 어귀에서 기다려 다오……",
    "17:330:0": "모리",
    "17:330:1": "님, 무엇을 하는가!\n어서 군사를 움직이지 못할까!",
    "17:331:0": "그렇게 말해도,\n앞에 진을 친",
    "17:331:1": "깃카와",
    "17:331:2": "가 움직이지 않아서 말이지",
    "17:332:0": "깃카와",
    "17:332:1": "님은 뭘 하고 있는 거요!\n귀하는 모리의 대장이 아니오!",
    "17:333:0": "그게……\n지, 지금은 도시락을 먹는 중이라고 합니다",
    "17:334:0": "뭐라고?\n도시락이라고!?",
    "17:335:0": (
        "그렇다, 점심 도시락이다\n"
        "배가 고파서는 싸울 수 없다고 하지 않느냐"
    ),
    "17:336:0": (
        "그야 그렇지만…… 그렇다면 서두르시오!\n"
        "이 싸움에 늦으면 후대까지 수치로 남을 것이오"
    ),
    "17:337:0": "미쓰나리",
    "17:337:1": "!\n네놈 때문에 히데요리 님께서 슬퍼하실 것이다!",
    "17:338:0": "마사노리",
    "17:338:1": "……\n지금은 무사로서 일어서야만 한다!",
    "17:339:0": "나는 가능하다면 귀하와 싸우고 싶지 않았소……",
    "17:340:0": "나가마사",
    "17:340:1": "……\n이곳은 전장, 싸우는 것이 우리의 운명이다……",
    "17:341:0": "네놈 때문에 내 아내가 죽게 되었단 말이다!",
    "17:342:0": "이 싸움에서 이기기 위해 어쩔 수 없는 일이었다……",
    "17:343:0": "미쓰나리",
    "17:343:1": "! 나는 네놈이 싫다!\n",
    "17:343:2": "이에야스",
    "17:343:3": "님을 위해 그 목을 받아 가겠다!",
    "17:344:0": "나가마사",
    "17:344:1": "! ",
    "17:344:2": "이에야스",
    "17:344:3": "따위에게 붙다니\n도요토미의 은혜를 잊었나!",
    "17:345:0": "미쓰나리",
    "17:345:1": (
        "님……도요토미의 세상은 곧 끝난다\n"
        "어찌 그토록 매달리는가"
    ),
    "17:346:0": "다카토라",
    "17:346:1": "……\n네 부대의 철포대는 아직 더 강해질 수 있다",
}
EXPECTED_ARITY = {
    312: 2,
    313: 2,
    314: 1,
    315: 2,
    316: 2,
    317: 2,
    318: 3,
    319: 3,
    320: 1,
    321: 2,
    322: 2,
    323: 1,
    324: 2,
    325: 2,
    **{record_id: 2 for record_id in range(326, 333)},
    331: 3,
    333: 1,
    334: 1,
    335: 1,
    336: 1,
    337: 2,
    338: 2,
    339: 1,
    340: 2,
    341: 1,
    342: 1,
    343: 4,
    344: 4,
    345: 2,
    346: 2,
}
NEIGHBOR_COMPANION_TRANSLATIONS = {"17:312:0": "부대를 격파하라"}
SEMANTIC_BASE_CONTEXT = {
    **{record_id: ("9:2842:0",) for record_id in range(312, 326)},
    **{record_id: ("9:1006:0",) for record_id in range(326, 347)},
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ())
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1420,
    queue_start=134,
    queue_stop=200,
    slice_first="17:312:1",
    slice_last="17:346:1",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(),
    prefill_companion_donor={},
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (17, record_id) for record_id in range(270, 380)
    ),
    speaker_style=(
        *((record_id, "scenario_objective") for record_id in range(312, 326)),
        (326, "formal_self_sacrifice"),
        (327, "apologetic_lord_to_vassal"),
        (328, "resolute_loyal_death"),
        (329, "solemn_afterlife_farewell"),
        (330, "impatient_allied_advance_order"),
        (331, "deflecting_allied_explanation"),
        (332, "angry_allied_rebuke"),
        (333, "awkward_lunch_report"),
        (334, "incredulous_lunch_reaction"),
        (335, "calm_lunch_excuse"),
        (336, "exasperated_urgent_rebuke"),
        (337, "angry_personal_accusation"),
        (338, "resolute_warrior_reply"),
        (339, "regretful_duel_statement"),
        (340, "solemn_battlefield_fate"),
        (341, "furious_personal_accusation"),
        (342, "regretful_necessity_reply"),
        (343, "hostile_decisive_duel"),
        (344, "angry_loyalty_rebuke"),
        (345, "somber_old_order_warning"),
        (346, "measured_firearm_unit_praise"),
    ),
    terminology_policy=(
        ("unit", "부대"),
        ("defeat", "격파"),
        ("approach", "접근"),
        ("Shimazu house", "시마즈 가문"),
        ("Mori", "모리"),
        ("Kikkawa", "깃카와"),
        ("western title", "님"),
        ("warrior", "무사"),
        ("battlefield", "전장"),
        ("firearm unit", "철포대"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire B138 queue slice from zero-based ordinals one hundred "
        "thirty-four through one hundred ninety-nine because no approved "
        "Base prefill exists in the slice; pristine PK source is "
        "authoritative, all available multilingual same-record fragments "
        "were reviewed as auxiliary context, and records without auxiliary "
        "translations were reviewed from complete assemblies, colour "
        "controls and adjacent battle sequence; completed Base objective, "
        "battle and defeat rows are used only as semantic and glossary "
        "context and never contribute runtime or VM state; the split "
        "left-boundary unit-defeat success objective is completed with the "
        "manually reviewed fragment owned by optional segment 1419 and any "
        "landed neighbor decision must match that assembly; unit, defeat, "
        "approach, the Shimazu house, Mori and Kikkawa names, warrior, "
        "battlefield and firearm-unit terminology retain established "
        "project wording; dialogue preserves each formal, apologetic, "
        "resolute, solemn, impatient, angry, incredulous, regretful or "
        "hostile register; colour tags, inline names and role tokens, "
        "protected whitespace, line breaks, punctuation, terminators, "
        "complete record arity, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=21,
    pins={
        "expected_queue_universe_sha256": "4EDC588F91DEC58F97ACA4C16FF4150DCECBB90ED1372150DD2021A8EC01B24E",
        "expected_queue_slice_sha256": "BD2AD5058CF9A468DC64010BD527CC926A8DCB008D578ABE96AF409724377D5E",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "BD2AD5058CF9A468DC64010BD527CC926A8DCB008D578ABE96AF409724377D5E",
        "expected_source_target_sha256": "428F012BD74046E9EBBA16C827A2AC8E22FC8388CA76A6C4141DF04FB2015DED",
        "expected_current_target_sha256": "CDA4240B71508BC30AB46EFB4333E046476496409FC238BC0041A382461D5F32",
        "expected_context_corpus_sha256": "09CA07A2EEB63A33AAFF03821C355C81D5F91E090F8817DF174B573C93FC4623",
        "expected_gap_contract_sha256": "46B7B871BF8E39605CA85DF9554D4F7063E54A967EA453C1FC5D6B331D544B43",
        "expected_boundary_sha256": "94249C0430F9C98A452A8A4B8B6919FEA7ABBBD8EB2ABB5D72CF5AD6E67FEFA9",
        "expected_runtime_control_sha256": "F762C43D868080B859659FD74270FDFAF497A80D9F0107D5E68157A184EE93EC",
        "expected_base_search_sha256": "C6ED0AB3A3115FD642FF9F5D34BDD49ECC1B66C4C49B2EDAB19C8A6FCECAA162",
        "expected_complete_assembly_sha256": "AAC4CBFFDCE017ABD782653031DA42931375BA9519A4AA12D6EFE26A08D40E19",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "93A679CABBC1391DFB776CAF08FEF86E77A7DF2D76ED9A0A74666C8214D9C185",
        "expected_terminology_policy_sha256": "A078751CA082073A5F37648F96D0B5FB1DFE7D1F27CE5610AB28E5AFD869F32B",
        "expected_translation_policy_sha256": "E478FB38CBFFF45483148F7541EA9CF27167F61265E5618CD895CA4734E2E83B",
        "expected_candidate_sha256": "A80B25CA15E0294A76CAA1C765BCBAFA8D7644F1B5333A105BEF5703CF0B139C",
        "expected_combined_slice_candidate_sha256": "A80B25CA15E0294A76CAA1C765BCBAFA8D7644F1B5333A105BEF5703CF0B139C",
        "expected_combined_changed_literal_count": 21,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B138_S1420",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B138_S1420.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B138_S1418.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B138_S1419.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B138",
    "queue_row_count": 98,
    "queue_visible_count": 200,
    "queue_first": "17:249:0",
    "queue_last": "17:346:1",
})


def base_and_assembly_evidence_with_boundary(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard the main records plus the split left-boundary record."""
    original_globals = _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE.__globals__
    saved_record_ids = original_globals["TARGET_RECORD_IDS"]
    saved_coordinates = original_globals["TARGET_COORDINATES"]
    original_globals["TARGET_RECORD_IDS"] = MAIN_RECORD_IDS
    original_globals["TARGET_COORDINATES"] = MAIN_TARGET_COORDINATES
    try:
        base_evidence, assembly_evidence = (
            _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE(
                prepared,
                records_by_label,
            )
        )
    finally:
        original_globals["TARGET_RECORD_IDS"] = saved_record_ids
        original_globals["TARGET_COORDINATES"] = saved_coordinates

    base_source = COMMON.ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.BASE_PROMOTED)
    }
    neighbor_rows = {
        str(row["coordinate"]): row
        for path in CONFIG["optional_neighbors"]
        if path.is_file()
        for row in COMMON.read_jsonl(path)
    }
    key = (17, 312)
    source = records_by_label["jp"][key]
    current = records_by_label["current"][key]
    source_literals = COMMON.literal_texts(records_by_label["jp"], key)
    current_literals = COMMON.literal_texts(
        records_by_label["current"], key
    )
    raw_matches = tuple(
        coordinate
        for coordinate, record in base_source.items()
        if record.data == source.data
    )
    literal_matches = tuple(
        coordinate
        for coordinate in base_source
        if COMMON.literal_texts(base_source, coordinate) == source_literals
    )
    masked_matches = tuple(
        coordinate
        for coordinate, record in base_source.items()
        if (
            COMMON.literal_texts(base_source, coordinate) == source_literals
            and COMMON.CORE.mask_call_operands(record)
            == COMMON.CORE.mask_call_operands(source)
        )
    )
    references: list[tuple[Any, ...]] = []
    for donor_coordinate in SEMANTIC_BASE_CONTEXT[312]:
        donor = base_rows.get(donor_coordinate)
        if (
            donor is None
            or donor.get("semantic_review") != "approved"
            or donor.get("runtime_review")
            not in {"verified", "not_required"}
        ):
            raise RuntimeError(
                "segment 1420 Base context drifted: "
                f"{donor_coordinate}"
            )
        references.append((
            donor_coordinate,
            str(donor["translation"]),
            str(donor["runtime_review"]),
        ))
    neighbor_coordinate, expected = next(
        iter(NEIGHBOR_COMPANION_TRANSLATIONS.items())
    )
    neighbor = neighbor_rows.get(neighbor_coordinate)
    if (
        neighbor is not None
        and (
            neighbor.get("translation") != expected
            or neighbor.get("semantic_review") != "approved"
            or neighbor.get("runtime_review") != "pending"
        )
    ):
        raise RuntimeError(
            f"segment 1420 neighbor companion drifted: {neighbor_coordinate}"
        )
    assembled = (expected, TRANSLATIONS["17:312:1"])
    if (
        len(source_literals) != EXPECTED_ARITY[312]
        or raw_matches != EXPECTED_BASE_RAW_MATCHES[312]
        or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[312]
        or masked_matches != EXPECTED_BASE_MASKED_MATCHES[312]
        or assembled != ("부대를 격파하라", " 성공")
    ):
        raise RuntimeError("segment 1420 boundary assembly drifted")
    return (
        tuple(base_evidence) + ((
            312,
            COMMON.sha256_bytes(source.data),
            source_literals,
            current_literals,
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(source)
            ),
            raw_matches,
            literal_matches,
            masked_matches,
            tuple(references),
            "semantic_context_only",
        ),),
        tuple(assembly_evidence) + ((
            312,
            (
                "optional_previous_segment_manual_companion",
                "segment_manual_multilingual",
            ),
            assembled,
            None,
            COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current),
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ),),
    )


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = (
        base_and_assembly_evidence_with_boundary
    )
    COMMON.CORE.base_and_assembly_evidence = (
        base_and_assembly_evidence_with_boundary
    )


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
