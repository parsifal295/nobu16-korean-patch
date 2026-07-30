#!/usr/bin/env python3
"""Build source-redacted PK B137 segment 1417 residual decisions."""

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

TARGET_RECORD_IDS = tuple(range(216, 249))
MAIN_RECORD_IDS = tuple(range(217, 249))
TARGET_COORDINATES = (
    "17:216:3",
    "17:216:4",
    "17:217:0",
    "17:217:1",
    "17:217:2",
    "17:217:3",
    "17:217:4",
    "17:218:0",
    "17:218:1",
    "17:219:0",
    "17:219:1",
    "17:220:0",
    "17:221:0",
    "17:221:1",
    "17:221:2",
    "17:222:0",
    "17:222:1",
    "17:223:0",
    "17:224:0",
    "17:225:0",
    "17:225:1",
    "17:226:0",
    "17:226:1",
    "17:226:2",
    "17:226:3",
    "17:227:0",
    "17:228:0",
    "17:228:1",
    "17:228:2",
    "17:228:3",
    "17:229:0",
    "17:229:1",
    "17:230:0",
    "17:231:0",
    "17:232:0",
    "17:233:0",
    "17:233:1",
    "17:234:0",
    "17:234:1",
    "17:234:2",
    "17:235:0",
    "17:236:0",
    "17:236:1",
    "17:237:0",
    "17:237:1",
    "17:238:0",
    "17:239:0",
    "17:240:0",
    "17:241:0",
    "17:242:0",
    "17:243:0",
    "17:243:1",
    "17:244:0",
    "17:244:1",
    "17:244:2",
    "17:245:0",
    "17:245:1",
    "17:245:2",
    "17:246:0",
    "17:246:1",
    "17:247:0",
    "17:247:1",
    "17:248:0",
    "17:248:1",
    "17:248:2",
)
MAIN_TARGET_COORDINATES = tuple(
    coordinate
    for coordinate in TARGET_COORDINATES
    if not coordinate.startswith("17:216:")
)
TRANSLATIONS = {
    "17:216:3": "세키가하라",
    "17:216:4": (
        "로 끌어내는 데 성공했다\n"
        "이제 일격에 놈들을 섬멸할 뿐이다"
    ),
    "17:217:0": "역시 ",
    "17:217:1": "이시다",
    "17:217:2": " 측이 맞서 나왔군\n고사에 따라 결전의 땅은",
    "17:217:3": "세키가하라",
    "17:217:4": "인가",
    "17:218:0": "이시다",
    "17:218:1": (
        " 일파는 산세를 이용해\n"
        "우리를 에워싸듯 포진하고 있습니다"
    ),
    "17:219:0": "도쿠가와",
    "17:219:1": (
        "군을 포위진 안으로 유인했다고……\n"
        "그렇게 생각하고 있겠지요"
    ),
    "17:220:0": (
        "……역시 풋내기로군\n"
        "포진도는 읽어도 사람의 마음은 읽지 못하는가"
    ),
    "17:221:0": "우리 배후를 칠 ",
    "17:221:1": "모리",
    "17:221:2": (
        "군……\n"
        "그들과는 불전의 약정을 맺어 두었다"
    ),
    "17:222:0": "우리 측면을 쳐야 할",
    "17:222:1": "는\n때를 보아 이쪽으로 돌아서기로 했다",
    "17:223:0": (
        "인화도 갖추지 못한 채\n"
        "지리만 믿고 싸우다니, 어리석기 짝이 없구나"
    ),
    "17:224:0": (
        "……자, 우리가 할 일은\n"
        "돌아설 자들이 다시 변심하지 못하게 하는 것이다"
    ),
    "17:225:0": "도쿠가와",
    "17:225:1": (
        "의 진용이 반석과 같음을\n"
        "맞서는 적장들에게 똑똑히 알려라!"
    ),
    "17:226:0": ", ",
    "17:226:1": "은(는)",
    "17:226:2": "모리",
    "17:226:3": (
        "의 약정 파기에 대비하라\n"
        "만일의 사태도 있을 수 있으니"
    ),
    "17:227:0": "우리 손으로 세키가하라의 전황을 유리하게 이끌자!",
    "17:228:0": "이시다",
    "17:228:1": "측의 주력은",
    "17:228:2": "와",
    "17:228:3": "……\n그들을 쓰러뜨리면 전세가 기울 것입니다",
    "17:229:0": "역시 본진을 지키는 자는 그",
    "17:229:1": "인가……",
    "17:230:0": (
        "함정이 놓여 있어도 이상하지 않다\n"
        "잘 유인해 싸울 수 있다면 좋겠는데……"
    ),
    "17:231:0": (
        "요충지의 절반 이상을 제압했군\n"
        "우선은 성공적이라 할 만하다"
    ),
    "17:232:0": (
        "적 부대 격파도 순조롭군\n"
        "이 기세로 적을 압도하라!"
    ),
    "17:233:0": "도쿠가와",
    "17:233:1": "측의 기세가 이 정도일 줄이야……!",
    "17:234:0": "더는 버틸 수 없다……!\n",
    "17:234:1": "지부쇼유",
    "17:234:2": ", 미안하다!",
    "17:235:0": (
        "주군, 승리로 이끌지 못해……\n"
        "면목이 없습니다……"
    ),
    "17:236:0": "! 어떻게든 늦지 않았군!\n",
    "17:236:1": "주군은 어떻게 되셨나?",
    "17:237:0": "! 어떻게든 늦지 않았군!\n",
    "17:237:1": "님께서는 어떻게 되셨나?",
    "17:238:0": (
        "부르는 데는 성공했지만\n"
        "조금 더 늦는다고 합니다!"
    ),
    "17:239:0": "참전하실 때까지 적의 맹공을 버텨 냅시다!",
    "17:240:0": (
        "오합지졸인 줄 알았는데 제법이군……\n"
        "조금 물러난다!"
    ),
    "17:241:0": "이토록 거센 압박이라니!\n일단 물러난다!",
    "17:242:0": (
        "모처럼 여기까지 왔건만\n"
        "어째서 히데모토 일행은 움직이지 않는가!?"
    ),
    "17:243:0": "데루모토",
    "17:243:1": "님!\n제때 오셨군!",
    "17:244:0": "주군께서 ",
    "17:244:1": "서군",
    "17:244:2": "에 원군으로 오셨다고!\n어쩔 수 없군, 진군한다!",
    "17:245:0": "주군께서 오시자",
    "17:245:1": "히로이에",
    "17:245:2": "도 움직였군! 우리도 출진한다!",
    "17:246:0": "모리",
    "17:246:1": "군이 드디어 움직였군!\n우리도 뒤이어 출진한다!",
    "17:247:0": "난구산",
    "17:247:1": "의 아군도 움직이기 시작했군\n참으로 다행이다!",
    "17:248:0": "주군! ",
    "17:248:1": "히데요리",
    "17:248:2": "님께서 찾아오셨습니다!",
}
EXPECTED_ARITY = {
    216: 5,
    217: 5,
    218: 2,
    219: 2,
    220: 1,
    221: 3,
    222: 2,
    223: 1,
    224: 1,
    225: 2,
    226: 4,
    227: 1,
    228: 4,
    229: 2,
    230: 1,
    231: 1,
    232: 1,
    233: 2,
    234: 3,
    235: 1,
    236: 2,
    237: 2,
    238: 1,
    239: 1,
    240: 1,
    241: 1,
    242: 1,
    243: 2,
    244: 3,
    245: 3,
    246: 2,
    247: 2,
    248: 3,
}
NEIGHBOR_COMPANION_TRANSLATIONS = {
    "17:216:0": "예상대로, ",
    "17:216:1": "이시다",
    "17:216:2": " 일파를\n",
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ("9:3031:0",)
        for record_id in range(216, 233)
    },
    **{
        record_id: ("9:1006:0",)
        for record_id in range(233, 243)
    },
    **{
        record_id: ("9:3792:0",)
        for record_id in range(243, 249)
    },
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{
        record_id: ((), ())
        for record_id in TARGET_RECORD_IDS
    },
    220: ((), ("024833",)),
    222: ((), ("024833",)),
    226: ((), ("024834", "024934")),
    228: ((), ("024834", "024934")),
    229: ((), ("024833",)),
    236: ((), ("024735", "024835")),
    237: ((), ("024735", "024835")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1417,
    queue_start=134,
    queue_stop=199,
    slice_first="17:216:3",
    slice_last="17:248:2",
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
        (17, record_id) for record_id in range(180, 280)
    ),
    speaker_style=(
        (216, "confident_decisive_battle_plan"),
        (217, "reflective_historical_battle_recognition"),
        (218, "formal_encirclement_report"),
        (219, "formal_enemy_miscalculation_assessment"),
        (220, "contemptuous_reading_of_enemy"),
        (221, "confident_nonaggression_disclosure"),
        (222, "confident_defection_disclosure"),
        (223, "contemptuous_harmony_and_terrain_assessment"),
        (224, "calm_defector_retention_plan"),
        (225, "commanding_show_of_strength"),
        (226, "commanding_breach_contingency"),
        (227, "resolute_battlefield_advantage"),
        (228, "formal_enemy_main_force_report"),
        (229, "wary_main_camp_guard_assessment"),
        (230, "wary_lure_plan"),
        (231, "measured_strategic_point_progress"),
        (232, "commanding_enemy_unit_progress"),
        (233, "astonished_enemy_momentum"),
        (234, "apologetic_withdrawal"),
        (235, "formal_defeat_apology"),
        (236, "urgent_arrival_inquiry"),
        (237, "urgent_arrival_inquiry"),
        (238, "urgent_delayed_arrival_report"),
        (239, "resolute_hold_until_reinforcements"),
        (240, "impressed_tactical_withdrawal"),
        (241, "shocked_tactical_withdrawal"),
        (242, "confused_late_reinforcement"),
        (243, "relieved_lord_arrival"),
        (244, "reluctant_western_army_advance"),
        (245, "resolute_allied_advance"),
        (246, "resolute_followup_sortie"),
        (247, "relieved_allied_movement"),
        (248, "formal_visitor_report"),
    ),
    terminology_policy=(
        ("decisive battlefield", "세키가하라"),
        ("western army", "서군"),
        ("Ishida faction", "이시다 일파"),
        ("Tokugawa force", "도쿠가와군"),
        ("Mori force", "모리군"),
        ("nonaggression pact", "불전의 약정"),
        ("strategic point", "요충지"),
        ("main camp", "본진"),
        ("Nangusan", "난구산"),
        ("historical title", "지부쇼유"),
        ("dynamic particle", "은(는)"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire B137 queue slice from zero-based ordinals one hundred "
        "thirty-four through one hundred ninety-eight because no approved "
        "Base prefill exists in the slice; pristine PK source is "
        "authoritative, every available EN, SC and TC same-record fragment "
        "array was reviewed as auxiliary context, and records without "
        "auxiliary translations were reviewed from their complete "
        "assemblies, colour controls and adjacent battle sequence; "
        "completed Base battle, strategic-point, command and defeat rows "
        "are used only as semantic and glossary context and never "
        "contribute runtime or VM state; the left-boundary decisive-battle "
        "record is completed with three manually reviewed fragments owned "
        "by optional segment 1416 and any landed neighbor decision must "
        "match that assembly; Sekigahara, the western army, the Ishida, "
        "Tokugawa and Mori forces, the nonaggression pact, strategic "
        "points, main camp, Nangusan and the historical title retain "
        "established project wording; dialogue preserves each confident, "
        "formal, commanding, wary, apologetic, urgent, relieved or "
        "astonished register; colour tags, inline person and role tokens, "
        "protected full-width spaces, outer whitespace, line breaks, "
        "dynamic particles, punctuation, terminators, complete record "
        "arity, pins, reverse overlays, two-run reproduction, tamper "
        "rejection, outside-scope identity, optional neighbor decisions "
        "and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=28,
    pins={
        "expected_queue_universe_sha256": "AA6B64E39166A50CF7D456140DFC053DCB88E80C33120BAFFADE06C49C921E0D",
        "expected_queue_slice_sha256": "40F519EB690DA5DB15FE6EB63FBC1391FB13E83D25388F530788B668253A513F",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "40F519EB690DA5DB15FE6EB63FBC1391FB13E83D25388F530788B668253A513F",
        "expected_source_target_sha256": "EA54D072C1059C562375CF669F614778C89D25779C163357988AEE9F7E9647FD",
        "expected_current_target_sha256": "949815A4F0B9EF26246A3D23818DA383DB5265656B863DF758F28722E35D4CF4",
        "expected_context_corpus_sha256": "B542EDCA0F2044E694BE2A20C0C8015569380470245117D24C4B915CE072C772",
        "expected_gap_contract_sha256": "5D6A9E5EF3A3EC1E725BEA3A97FD45AED176C4690760DB65AA1E6A28EA187125",
        "expected_boundary_sha256": "FA9BD000B9001E367BCC287F4E0629D286F18274DBC58DBE18D608D1DD1F690C",
        "expected_runtime_control_sha256": "965ADAB0E3D7FBB4C838E7660CB73AF9B0F4CA811D1C76713941E93E685123AD",
        "expected_base_search_sha256": "2D23337C2779BBD51AAADDED26AA1B68BC283C3DDC66625DCC8739E42BE118C7",
        "expected_complete_assembly_sha256": "E98D6D10C0A3D653F7C0A87C444597247FAA3A80AAE51CEA8EBC8C565E55311F",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "0EF7D2AB0888014902C7BE24B91A8EE46656EFAEBE9650EB43E332FA190C74FC",
        "expected_terminology_policy_sha256": "B719FF306DE9C867FE8AEC51D848CA53E3EE9876AAEA5792AC350F19B0500110",
        "expected_translation_policy_sha256": "2A8A7ABBDCCEB7E0FBC28D9FF556BA79F97CBC54617138BD526974F6AE1D3757",
        "expected_candidate_sha256": "483391B7BEB0E083CB189706620BC3B4D7624F393DB32F4A187DB62F673887EA",
        "expected_combined_slice_candidate_sha256": "483391B7BEB0E083CB189706620BC3B4D7624F393DB32F4A187DB62F673887EA",
        "expected_combined_changed_literal_count": 28,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B137_S1417",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B137_S1417.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B137_S1415.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B137_S1416.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B137",
    "queue_row_count": 95,
    "queue_visible_count": 199,
    "queue_first": "17:154:0",
    "queue_last": "17:248:2",
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
    key = (17, 216)
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
    for donor_coordinate in SEMANTIC_BASE_CONTEXT[216]:
        donor = base_rows.get(donor_coordinate)
        if (
            donor is None
            or donor.get("semantic_review") != "approved"
            or donor.get("runtime_review")
            not in {"verified", "not_required"}
        ):
            raise RuntimeError(
                "segment 1417 Base context drifted: "
                f"{donor_coordinate}"
            )
        references.append((
            donor_coordinate,
            str(donor["translation"]),
            str(donor["runtime_review"]),
        ))
    for neighbor_coordinate, expected in (
        NEIGHBOR_COMPANION_TRANSLATIONS.items()
    ):
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
                "segment 1417 neighbor companion drifted: "
                f"{neighbor_coordinate}"
            )
    assembled = (
        *NEIGHBOR_COMPANION_TRANSLATIONS.values(),
        TRANSLATIONS["17:216:3"],
        TRANSLATIONS["17:216:4"],
    )
    if (
        len(source_literals) != EXPECTED_ARITY[216]
        or raw_matches != EXPECTED_BASE_RAW_MATCHES[216]
        or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[216]
        or masked_matches != EXPECTED_BASE_MASKED_MATCHES[216]
        or assembled != (
            "예상대로, ",
            "이시다",
            " 일파를\n",
            "세키가하라",
            "로 끌어내는 데 성공했다\n"
            "이제 일격에 놈들을 섬멸할 뿐이다",
        )
    ):
        raise RuntimeError("segment 1417 boundary assembly drifted")
    return (
        tuple(base_evidence) + ((
            216,
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
            216,
            (
                "optional_previous_segment_manual_companion",
                "optional_previous_segment_manual_companion",
                "optional_previous_segment_manual_companion",
                "segment_manual_multilingual",
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
